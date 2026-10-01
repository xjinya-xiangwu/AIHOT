#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""run-weekly-pipeline.py — AIHOT 式周报管线 v1.2（多通道采集 + 质量度量）

v1.2 变更（采集筛选质量专项）：
  ① 多通道采集：aihot API（https+域名白名单+公网 IP 校验+禁重定向）+ GitHub 三路检索
     + 四家 harness releases（后两者复用本机 gh CLI 鉴权；gh 子进程仅接受
     过白名单正则校验的固定格式 path，参数列表调用 shell=False——无注入面）
  ② --export-review：生成专家标注队列（10 分钟标注 → 筛选质量 ground truth）
  ③ --eval labeled.jsonl：对照标注算 precision/recall/误桶率（SelectBench 式校准）
  ④ --in 离线重放不变（校准对账）

用法：
  python3 run-weekly-pipeline.py --persona pm --out out                 # 全通道采集
  python3 run-weekly-pipeline.py --persona pm --in items.json --out out # 离线重放
  python3 run-weekly-pipeline.py --persona pm --out out --export-review
  python3 run-weekly-pipeline.py --eval out/labeled.jsonl --baseline v1.1
纯标准库。
"""
import argparse
import ipaddress
import json
import re
import shutil
import socket
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent  # domain-pack 根（keywords.json 所在）
CST = timezone(timedelta(hours=8))

# --- 出网白名单（仅自建 URL 通道适用）---
ALLOWED_HOSTS = {"aihot.news"}
ALLOWED_SCHEME = "https"

# gh CLI 子进程的 path 白名单格式：GitHub API 相对路径（字母数字与安全分隔符）
GH_PATH_RE = re.compile(r"^[A-Za-z0-9/_?&=%:.,\-=]+$")

GH_CANDIDATES = [
    shutil.which("gh"),
    r"C:\Users\kurtx\.dsh\bin\gh\gh.exe",
    "/c/Users/kurtx/.dsh/bin/gh/gh.exe",
    "/usr/local/bin/gh", "/usr/bin/gh",
]

GITHUB_SEARCHES = [
    "claude code skill created:>2026-09-24 stars:>30",
    "mcp server created:>2026-09-24 stars:>100",
    "ai agent cli OR harness created:>2026-09-24 stars:>200",
]
HARNESS_REPOS = ["anthropics/claude-code", "sst/opencode", "openai/codex", "google-gemini/gemini-cli"]


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError(f"拒绝重定向到 {newurl}")


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
        if (ip.is_private or ip.is_loopback or ip.is_link_local
                or ip.is_reserved or ip.is_multicast or not ip.is_global):
            raise ValueError(f"目标解析到受限/非公网地址 {ip}，拒绝")


def safe_fetch_json(url: str, timeout: int = 30):
    _assert_public_https(url)
    req = urllib.request.Request(url, headers={"User-Agent": "siae-weekly-pipeline/1.2"})
    opener = urllib.request.build_opener(NoRedirect)
    with opener.open(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def gh_path():
    for c in GH_CANDIDATES:
        if c and Path(c).exists():
            return c
    return None


def gh_api(path: str):
    """经本机 gh CLI 调 GitHub API。path 必须通过白名单格式校验；
    参数列表 + shell=False，无字符串拼接、无 shell 解释。"""
    if not GH_PATH_RE.match(path):
        raise ValueError(f"gh path 未过白名单格式校验：{path!r}")
    g = gh_path()
    if not g:
        return None
    r = subprocess.run([g, "api", path], capture_output=True, text=True,
                       timeout=60, shell=False)
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return None


def fetch_aihot(limit=40):
    d = safe_fetch_json("https://aihot.news/api/v1/items?mode=selected&window=7d"
                        f"&limit={limit}")
    items = d.get("items", d if isinstance(d, list) else [])
    return [{
        "id": it.get("publicId") or it.get("id") or it.get("url", "")[-16:],
        "title": it.get("title", ""),
        "summary": it.get("summary") or it.get("summaryZh") or "",
        "url": (it.get("links") or {}).get("source") or it.get("url") or "https://aihot.news",
        "source": "aihot",
    } for it in items]


def fetch_github():
    """P2 通道：三路检索（gh CLI 鉴权；query 仅来自常量列表）。"""
    out = []
    for q in GITHUB_SEARCHES:
        path = "search/repositories?q=" + urllib.parse.quote(q) + "&sort=stars&per_page=6"
        d = gh_api(path)
        for it in (d or {}).get("items", []):
            out.append({
                "id": f"gh-{it.get('id')}",
                "title": f"{it.get('full_name','')} ⭐{it.get('stargazers_count','?')}：{it.get('description') or ''}",
                "summary": (it.get("description") or "") + " | 新星（本周创建窗口）",
                "url": it.get("html_url", "https://github.com"),
                "source": "github",
            })
    return out


def fetch_releases():
    """P3 通道：四家 harness 最新 release（repo 名仅来自常量列表）。"""
    out = []
    for repo in HARNESS_REPOS:
        d = gh_api(f"repos/{repo}/releases?per_page=1")
        for rel in (d or [{}])[:1]:
            body = (rel.get("body") or "").strip().replace("\r", "")[:400]
            out.append({
                "id": f"rel-{repo.split('/')[-1]}",
                "title": f"{repo} {rel.get('tag_name','?')}（{rel.get('published_at','')[:10]}）",
                "summary": body or f"{repo} 新版本发布",
                "url": rel.get("html_url", f"https://github.com/{repo}/releases"),
                "source": "release",
            })
    return out


def load_cfg():
    return json.loads((HERE / "keywords.json").read_text(encoding="utf-8"))


PILLAR_ACTION_WORDS = {}
PILLAR_THRESHOLDS = {}
CHANNEL_PRIORITY = {}
CFG = {}


def apply_cfg_extras(cfg):
    global PILLAR_ACTION_WORDS, PILLAR_THRESHOLDS, CHANNEL_PRIORITY
    PILLAR_ACTION_WORDS = cfg.get("pillar_action_words", {})
    PILLAR_THRESHOLDS = cfg.get("pillar_thresholds", {})
    CHANNEL_PRIORITY = cfg.get("channel_pillar_priority", {})


def bucketize(item, cfg, persona):
    text = (item["title"] + " " + item["summary"]).lower()
    hits, matched = [], {}
    for p in cfg["pillars"]:
        if p.get("persona_only") and persona != "pm":
            continue
        negs = [n.lower() for n in p.get("negative_keywords", [])]
        if any(n in text for n in negs):
            continue
        for kw in p["keywords"]:
            if kw.lower() in text:
                hits.append(p["id"])
                matched[p["id"]] = kw
                break
    return hits, matched


def veto(item, cfg, persona):
    text = (item["title"] + " " + item["summary"]).lower()
    for rule in cfg["veto_rules"]:
        if persona in rule.get("persona_exempt", []):
            continue
        for kw in rule.get("keywords", []):
            if kw.lower() in text:
                return rule["id"], f"命中 {rule['id']}"
    return None


def score(item, pillar_id):
    text = (item["title"] + " " + item["summary"]).lower()
    s = {}
    action_words = ["降价", "发布", "上线", "开放", "修复", "开源", "release", "生效", "⭐"]
    action_words += PILLAR_ACTION_WORDS.get(pillar_id, [])
    s["action_clarity"] = 3 + (1 if any(w in text for w in action_words) else 0) \
                          + (1 if pillar_id.startswith(("P1", "P3", "P4")) else 0)
    has_num = bool(re.search(r"[\$¥]\d|\d+(\.\d+)?%|\d+(\.\d+)?(倍|×|x)|降\d+|⭐\d", text))
    s["cost_impact"] = 5 if has_num else (3 if any(w in text for w in ["价格", "成本", "免费", "价"]) else 1)
    s["timeliness"] = 5 if any(w in text for w in ["生效", "限时", "今天", "正式"]) \
        else (4 if any(w in text for w in ["发布", "上线", "release", "开放", "⭐"]) else 3)
    s["breadth"] = 4 if any(w in text for w in ["跨", "多 agent", "通用", "开放", "开源"]) else 3
    s["credibility"] = 5 if item["source"] in ("release", "github") or any(
        w in text for w in ["官方", "定价", "宣布"]) else 4
    s["total"] = sum(s.values())
    return s


def action_hint(item, pillar_id):
    return {
        "P1_model_compute": "核对价目表/评估换档（P1）",
        "P2_skills_tools": "入包评估/安装（P2）",
        "P3_harness_env": "升级对应端+doctor（P3）",
        "P4_method_quality": "SOP 候选（P4）",
        "PM_industry_intel": "PM 引用素材",
    }.get(pillar_id, "?")


def run_pipeline(items, cfg, persona):
    selected, vetoed = [], []
    for it in items:
        v = veto(it, cfg, persona)
        if v:
            vetoed.append({**it, "veto_rule": v[0], "veto_reason": v[1], "label_hint": "reject"})
            continue
        hits, matched = bucketize(it, cfg, persona)
        if not hits:
            vetoed.append({**it, "veto_rule": "V0_unbucketed",
                           "veto_reason": "未命中任何关键词支柱", "label_hint": "reject"})
            continue
        # 主桶选择：通道优先级（release→P3 / github→P2）优先于数组顺序（校准 v1.2）
        prefer = CHANNEL_PRIORITY.get(it.get("source", ""), "")
        pillar = prefer if prefer in hits else hits[0]
        sc = score(it, pillar)
        rec = {**it, "pillar": pillar, "extra_pillars": hits[1:],
               "score": sc, "action_hint": action_hint(it, pillar),
               "matched_kw": matched.get(pillar, "")}
        thr = PILLAR_THRESHOLDS.get(pillar, PILLAR_THRESHOLDS.get("default", 18))
        if sc["total"] >= thr:
            rec["label_hint"] = "accept"
            selected.append(rec)
        else:
            vetoed.append({**rec, "veto_rule": "V5_score",
                           "veto_reason": f"总分 {sc['total']}<{thr}({pillar})",
                           "label_hint": "reject"})
    return selected, vetoed


def compose(selected, vetoed, persona, items_count, ts):
    by_pillar = {}
    for r in selected:
        by_pillar.setdefault(r["pillar"], []).append(r)
    for p in by_pillar.values():
        p.sort(key=lambda r: -r["score"]["total"])
    lines = [f"# 周报管线生成版（{persona}）v6（多通道）", ""]
    chan = {s: sum(1 for r in selected if r["source"] == s)
            for s in {r["source"] for r in selected}}
    lines.append(f"> 生成：{ts} ｜ runner v1.2 多通道（aihot+github+releases）｜ "
                 f"输入 {items_count} 条 → 精选 {len(selected)} / 否决 {len(vetoed)} ｜ 通道：{chan}")
    lines.append("")
    names = {p["id"]: p for p in CFG["pillars"]}
    for pid in ["P1_model_compute", "P2_skills_tools", "P3_harness_env",
                "P4_method_quality", "PM_industry_intel"]:
        rows = by_pillar.get(pid, [])
        cfgp = names.get(pid, {})
        label = f"{cfgp.get('name', pid)}（动作出口：{cfgp.get('action', '-')}，{len(rows)} 条）"
        lines.append(f"## {label}")
        lines.append("")
        for r in rows:
            sc = r["score"]
            lines.append(f"- **{r['title'][:70]}**（{sc['total']} 分｜{r['action_hint']}｜{r['source']}）")
            lines.append(f"  - 命中：`{r['matched_kw']}`｜五维 动作{sc['action_clarity']} 成本{sc['cost_impact']} "
                         f"时效{sc['timeliness']} 适用{sc['breadth']} 可信{sc['credibility']}｜{r['url']}")
            lines.append("  - `AGENT-COMPOSE`：〔含义/动作 + 分级 + 落点——LLM 位待接〕")
        lines.append("")
    lines.append("## 否决清单（gold 负样本）")
    lines.append("")
    for r in vetoed[:25]:
        lines.append(f"- [{r.get('veto_rule')}] {r['title'][:60]} —— {r.get('veto_reason', '')}")
    return "\n".join(lines) + "\n", by_pillar


def export_review(selected, vetoed, outdir, ts):
    rows = []
    for r in selected:
        rows.append({"id": r["id"], "pillar": r["pillar"], "title": r["title"][:80],
                     "score": r["score"]["total"], "pipeline": "accept", "source": r["source"]})
    for r in vetoed:
        rows.append({"id": r["id"], "pillar": r.get("pillar", "-"), "title": r["title"][:80],
                     "score": r.get("score", {}).get("total", "-"), "pipeline": "reject",
                     "veto": r.get("veto_rule", ""), "source": r.get("source", "")})
    (outdir / "review-items.jsonl").write_text(
        "\n".join(json.dumps(x, ensure_ascii=False) for x in rows), encoding="utf-8")
    md = [f"# 专家标注队列（生成 {ts}）", "",
          "**10 分钟标注法**：逐行把 `[ ]` 改为 `[a]`（该收）/`[r]`（该拒）/`[bP1]`（改桶到 P1，类推）。",
          "完成后转存 `labeled.jsonl`（每行 {\"id\":..,\"label\":\"a\"}）跑 `--eval`。",
          "**管线 accept/reject 仅供参考——你的标注才是 ground truth。**", ""]
    for x in rows:
        md.append(f"- [ ] ({x['pipeline']}|{x['pillar']}|{x['score']}) {x['title']}")
    (outdir / "review-queue.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return len(rows)


def eval_selection(labeled_path, outdir):
    labels = {}
    for line in Path(labeled_path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            o = json.loads(line)
            labels[o["id"]] = o.get("label", "")
    rev = {}
    p = outdir / "review-items.jsonl"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                o = json.loads(line)
                rev[o["id"]] = o
    tp = fp = fn = 0
    misbucket = []
    for rid, lab in labels.items():
        pipe = rev.get(rid, {}).get("pipeline")
        acc_lab = lab.startswith("a") or lab.startswith("b")
        acc_pipe = pipe == "accept"
        if acc_lab and acc_pipe:
            tp += 1
            if lab.startswith("b"):
                want = lab[1:]
                got = rev[rid].get("pillar")
                if want != got:
                    misbucket.append({"id": rid, "want": want, "got": got})
        elif acc_pipe and not acc_lab:
            fp += 1
        elif acc_lab and not acc_pipe:
            fn += 1
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    res = {"labeled": len(labels), "tp": tp, "fp": fp, "fn": fn,
           "precision": round(prec, 3), "recall": round(rec, 3), "f1": round(f1, 3),
           "misbucket": misbucket}
    (outdir / "eval-result.json").write_text(
        json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return res


def main():
    global CFG
    ap = argparse.ArgumentParser()
    ap.add_argument("--persona", choices=["internal", "pm"], default="pm")
    ap.add_argument("--in", dest="infile")
    ap.add_argument("--out", default=str(HERE / "out"))
    ap.add_argument("--limit", type=int, default=40)
    ap.add_argument("--no-github", action="store_true", help="仅 aihot 通道")
    ap.add_argument("--export-review", action="store_true")
    ap.add_argument("--eval", metavar="labeled.jsonl")
    ap.add_argument("--baseline", default="")
    a = ap.parse_args()

    CFG = load_cfg()
    apply_cfg_extras(CFG)
    outdir = Path(a.out)
    outdir.mkdir(parents=True, exist_ok=True)

    if a.eval:
        return 0 if eval_selection(a.eval, outdir) else 1

    if a.infile:
        items = json.loads(Path(a.infile).read_text(encoding="utf-8"))
    else:
        try:
            items = fetch_aihot(a.limit)
        except ValueError as e:
            print(f"[error] aihot 通道校验失败：{e}", file=sys.stderr)
            return 2
        if not a.no_github:
            gh_items = fetch_github() + fetch_releases()
            items += gh_items
            print(f"[info] github/releases 通道 +{len(gh_items)} 条")
    if not items:
        print("[error] 无输入条目", file=sys.stderr)
        return 2

    ts = datetime.now(CST).strftime("%Y-%m-%d %H:%M")
    selected, vetoed = run_pipeline(items, CFG, a.persona)
    body, by_pillar = compose(selected, vetoed, a.persona, len(items), ts)
    (outdir / "weekly-v6.generated.md").write_text(body, encoding="utf-8")

    log = {"run_at": ts, "runner": "v1.2", "persona": a.persona,
           "input": len(items), "selected": len(selected), "vetoed": len(vetoed),
           "by_pillar": {k: len(v) for k, v in by_pillar.items()},
           "channels": {s: sum(1 for r in selected if r["source"] == s)
                        for s in {r["source"] for r in selected}},
           "baseline_tag": a.baseline}
    (outdir / "pipeline-run.log").write_text(
        json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    (outdir / "selection-items.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in selected), encoding="utf-8")

    n_rev = export_review(selected, vetoed, outdir, ts) if a.export_review else 0
    print(f"[ok] in={len(items)} selected={len(selected)} vetoed={len(vetoed)} "
          f"pillars={log['by_pillar']} channels={log['channels']}"
          + (f" review_rows={n_rev}" if n_rev else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
