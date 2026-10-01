#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""run-weekly-pipeline.py — AIHOT 式周报管线实跑（domain-pack v1）

流程（对齐 AIHOT 范式）：采集 → 预筛（keywords.json 分桶+粗否决）→ 精选（五维评分+门槛）
→ 组装（模板渲染，LLM 增强位留 AGENT 区块）→ 输出周报 + 筛选日志（审计/校准用）。

规则引擎为确定性实现（关键词+规则评分）；「含义/动作一句话」由组装模板的 AGENT-COMPOSE
区块承载（agent 会话填充）——与 AIHOT「机器筛 + LLM 写」同构。

用法：
  python3 run-weekly-pipeline.py --persona pm --out <dir>       # 拉 aihot 精选 7 天
  python3 run-weekly-pipeline.py --persona pm --in items.json   # 离线重放（校准用）
纯标准库。
"""
import argparse
import ipaddress
import json
import re
import socket
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent  # domain-pack 根（keywords.json 所在）
CST = timezone(timedelta(hours=8))

# 出网白名单：协议 https + 域名白名单；解析后 IP 必须为公网单播
ALLOWED_HOSTS = {"aihot.news"}
ALLOWED_SCHEME = "https"


def _assert_public_https(url: str):
    u = urllib.parse.urlsplit(url)
    if u.scheme != ALLOWED_SCHEME:
        raise ValueError(f"仅允许 {ALLOWED_SCHEME}：{url}")
    if u.hostname not in ALLOWED_HOSTS:
        raise ValueError(f"域名不在白名单 {ALLOWED_HOSTS}：{u.hostname}")
    try:
        infos = socket.getaddrinfo(u.hostname, 443, proto=socket.IPPROTO_TCP)
    except OSError as e:
        raise ValueError(f"DNS 解析失败：{u.hostname}") from e
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if not (ip.is_global and isinstance(ip, ipaddress.IPv4Address) or
                (ip.is_global and isinstance(ip, ipaddress.IPv6Address))):
            raise ValueError(f"目标解析到非公网地址 {ip}，拒绝")
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            raise ValueError(f"目标解析到受限地址 {ip}，拒绝")


def safe_fetch_json(url: str, timeout: int = 30):
    _assert_public_https(url)  # 校验+解析一次
    req = urllib.request.Request(url, headers={"User-Agent": "siae-weekly-pipeline/1.0"})
    # 禁自动重定向（防绕过校验）；本管线预期 200 直返
    opener = urllib.request.build_opener(NoRedirect)
    with opener.open(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError(f"拒绝重定向到 {newurl}")


def load_cfg():
    return json.loads((HERE / "keywords.json").read_text(encoding="utf-8"))


PILLAR_ACTION_WORDS = {}
PILLAR_THRESHOLDS = {}


def apply_cfg_extras(cfg):
    """v1.1 校准：分支柱门槛与分支柱动作词（来源 keywords.json）。"""
    global PILLAR_ACTION_WORDS, PILLAR_THRESHOLDS
    PILLAR_ACTION_WORDS = cfg.get("pillar_action_words", {})
    PILLAR_THRESHOLDS = cfg.get("pillar_thresholds", {})


def fetch_aihot(limit=40):
    url = ("https://aihot.news/api/v1/items?mode=selected&window=7d"
           f"&limit={limit}")
    d = safe_fetch_json(url)
    items = d.get("items", d if isinstance(d, list) else [])
    out = []
    for it in items:
        out.append({
            "id": it.get("publicId") or it.get("id") or it.get("url", "")[-16:],
            "title": it.get("title", ""),
            "summary": it.get("summary") or it.get("summaryZh") or "",
            "category": it.get("category", ""),
            "url": (it.get("links") or {}).get("source")
                   or it.get("url") or "https://aihot.news",
            "source": "aihot",
        })
    return out


def bucketize(item, cfg, persona):
    """返回命中的支柱 id 列表（pm 人格含 PM 层）。"""
    text = (item["title"] + " " + item["summary"]).lower()
    hits = []
    for p in cfg["pillars"]:
        if p.get("persona_only") and persona != "pm":
            continue
        negs = [n.lower() for n in p.get("negative_keywords", [])]
        if any(n in text for n in negs):
            continue  # 负关键词：该支柱明确不收（校准 v1.1）
        for kw in p["keywords"]:
            if kw.lower() in text:
                hits.append(p["id"])
                break
    return hits


def veto(item, cfg, persona):
    """返回 (规则id, 理由) 或 None。"""
    text = (item["title"] + " " + item["summary"]).lower()
    for rule in cfg["veto_rules"]:
        if persona in rule.get("persona_exempt", []):
            continue
        for kw in rule.get("keywords", []):
            if kw.lower() in text:
                return rule["id"], f"命中 {rule['id']}（{rule['rule'][:24]}…）"
    return None


def score(item, pillar_id):
    """确定性五维评分（LLM 精评留 AGENT 区块；此为实现 v1 的规则近似）。"""
    text = (item["title"] + " " + item["summary"]).lower()
    s = {}

    action_words = ["降价", "发布", "上线", "开放", "修复", "开源", "release", "生效"]
    action_words += PILLAR_ACTION_WORDS.get(pillar_id, [])
    s["action_clarity"] = 3 + (1 if any(w in text for w in action_words) else 0) \
                          + (1 if pillar_id.startswith(("P1", "P3", "P4")) else 0)

    has_num = bool(re.search(r"[\$¥]\d|\d+(\.\d+)?%|\d+(\.\d+)?(倍|×|x)|降\d+", text))
    s["cost_impact"] = 5 if has_num else (3 if any(w in text for w in ["价格", "成本", "免费", "价"]) else 1)

    s["timeliness"] = 5 if any(w in text for w in ["生效", "限时", "今天", "正式"]) \
        else (4 if any(w in text for w in ["发布", "上线", "release", "开放"]) else 3)

    s["breadth"] = 4 if any(w in text for w in ["跨", "多 agent", "通用", "开放", "开源"]) else 3

    s["credibility"] = 5 if any(w in text for w in ["官方", "定价", "宣布", "发布"]) \
        else (4 if item["source"] == "aihot" else 3)

    s["total"] = sum(s.values())
    return s


def action_hint(item, pillar_id):
    m = {
        "P1_model_compute": "核对价目表/评估换档（P1）",
        "P2_skills_tools": "入包评估/安装（P2）",
        "P3_harness_env": "升级对应端+doctor（P3）",
        "P4_method_quality": "SOP 候选（P4）",
        "PM_industry_intel": "PM 引用素材",
    }
    return m.get(pillar_id, "?")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--persona", choices=["internal", "pm"], default="pm")
    ap.add_argument("--in", dest="infile", help="离线重放 JSON（校准）")
    ap.add_argument("--out", default=str(HERE / "out"))
    ap.add_argument("--limit", type=int, default=40)
    a = ap.parse_args()

    cfg = load_cfg()
    apply_cfg_extras(cfg)
    if a.infile:
        items = json.loads(Path(a.infile).read_text(encoding="utf-8"))
    else:
        try:
            items = fetch_aihot(a.limit)
        except ValueError as e:
            print(f"[error] 出网校验失败：{e}", file=sys.stderr)
            return 2
    if not items:
        print("[error] 无输入条目", file=sys.stderr)
        return 2

    outdir = Path(a.out); outdir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(CST).strftime("%Y-%m-%d %H:%M")

    selected, vetoed = [], []
    for it in items:
        v = veto(it, cfg, a.persona)
        if v:
            vetoed.append({**it, "veto_rule": v[0], "veto_reason": v[1]})
            continue
        hits = bucketize(it, cfg, a.persona)
        if not hits:
            vetoed.append({**it, "veto_rule": "V0_unbucketed",
                           "veto_reason": "未命中任何关键词支柱"})
            continue
        pillar = hits[0]
        rec = {**it, "pillar": pillar, "extra_pillars": hits[1:],
               "score": score(it, pillar), "action_hint": action_hint(it, pillar)}
        thr = PILLAR_THRESHOLDS.get(pillar, PILLAR_THRESHOLDS.get("default", 18))
        if rec["score"]["total"] >= thr:
            selected.append(rec)
        else:
            vetoed.append({**rec, "veto_rule": "V5_score",
                           "veto_reason": f"总分 {rec['score']['total']}<{thr}({pillar})"})

    by_pillar = {}
    for r in selected:
        by_pillar.setdefault(r["pillar"], []).append(r)
    for p in by_pillar.values():
        p.sort(key=lambda r: -r["score"]["total"])

    lines = []
    lines.append(f"# 周报管线生成版（{a.persona}）v5")
    lines.append("")
    lines.append(f"> 生成：{ts} ｜ 管线：run-weekly-pipeline.py（keywords.json v1 + 规则评分；"
                 f"LLM 写作位见 AGENT-COMPOSE 区块）｜ 输入 {len(items)} 条 → 精选 {len(selected)} / "
                 f"否决 {len(vetoed)}")
    lines.append("")
    for pid in ["P1_model_compute", "P2_skills_tools", "P3_harness_env",
                "P4_method_quality", "PM_industry_intel"]:
        rows = by_pillar.get(pid, [])
        if not rows:
            continue
        cfgp = next(p for p in cfg["pillars"] if p["id"] == pid)
        lines.append(f"## {cfgp['name']}（动作出口：{cfgp['action']}，{len(rows)} 条）")
        lines.append("")
        for r in rows:
            sc = r["score"]
            lines.append(f"- **{r['title'][:60]}**（{sc['total']} 分｜{r['action_hint']}）")
            lines.append(f"  - 摘要：{r['summary'][:100]}")
            lines.append("  - `AGENT-COMPOSE`：〔含义/动作一句话 + 分级 A/B/C + 落点组件——agent 会话填充〕")
            lines.append(f"  - 五维：动作{sc['action_clarity']} 成本{sc['cost_impact']} "
                         f"时效{sc['timeliness']} 适用{sc['breadth']} 可信{sc['credibility']}｜{r['url']}")
        lines.append("")
    lines.append("## 否决清单（gold 负样本回流）")
    lines.append("")
    for r in vetoed[:20]:
        lines.append(f"- [{r.get('veto_rule')}] {r['title'][:50]} —— {r.get('veto_reason', '')}")
    lines.append("")
    lines.append("## 数据缺口")
    lines.append("- 规则评分 v1 为近似（数字/时效词命中），LLM 精评位未启用；"
                 "GitHub/harness 通道本轮未注入（fixtures 化后自动并桶）")
    (outdir / "weekly-v5.generated.md").write_text("\n".join(lines), encoding="utf-8")

    log = {
        "run_at": ts, "persona": a.persona, "input": len(items),
        "selected": len(selected), "vetoed": len(vetoed),
        "by_pillar": {k: len(v) for k, v in by_pillar.items()},
        "veto_rules_used": sorted({r.get("veto_rule") for r in vetoed}),
    }
    (outdir / "pipeline-run.log").write_text(
        json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    (outdir / "selection-items.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in selected), encoding="utf-8")

    print(f"[ok] selected={len(selected)} vetoed={len(vetoed)} "
          f"pillars={ {k: len(v) for k, v in by_pillar.items()} }")
    print(f"     -> {outdir / 'weekly-v5.generated.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
