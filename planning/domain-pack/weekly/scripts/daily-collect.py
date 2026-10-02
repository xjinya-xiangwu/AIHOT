#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""daily-collect.py — SIAE 信息漏斗 L0：每日采集器

三通道（同 run-weekly-pipeline v1.2.1 安全基线）：
  aihot 精选流 24h（https+域名白名单+公网 IP 校验+禁重定向）
  GitHub 当日新星（gh CLI，path 正则白名单+shell=False）
  四家 harness 最新 release（gh CLI）
处理：全库去重（id+URL hash）→ keywords v1.2.1 分桶/否决/五维评分
输出：materials/YYYY-MM-DD.jsonl（追加当日新条目）
      notion/pending-sync.md（当日增量，供 agent 会话导入 Notion）
幂等：重复运行只增新条目。
纯标准库；被 Windows 计划任务每日 08:30 调用。
"""
import hashlib
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

HERE = Path(__file__).resolve().parent.parent  # SIAE-materials 根
CST = timezone(timedelta(hours=8))

ALLOWED_HOSTS = {"aihot.news"}
ALLOWED_SCHEME = "https"
GH_PATH_RE = re.compile(r"^[A-Za-z0-9/_?&=%:.,\-=]+$")
GH_CANDIDATES = [shutil.which("gh"),
                 r"C:\Users\kurtx\.dsh\bin\gh\gh.exe",
                 "/c/Users/kurtx/.dsh/bin/gh/gh.exe",
                 "/usr/local/bin/gh", "/usr/bin/gh"]

GITHUB_SEARCHES = [
    "claude code skill created:>2026-10-01 stars:>20",
    "mcp server created:>2026-10-01 stars:>50",
    "ai agent cli OR skill created:>2026-10-01 stars:>100",
]
HARNESS_REPOS = ["anthropics/claude-code", "sst/opencode", "openai/codex",
                 "google-gemini/gemini-cli"]


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError(f"拒绝重定向到 {newurl}")


def _assert_public_https(url: str):
    u = urllib.parse.urlsplit(url)
    if u.scheme != ALLOWED_SCHEME:
        raise ValueError(f"仅允许 {ALLOWED_SCHEME}：{url}")
    if u.hostname not in ALLOWED_HOSTS:
        raise ValueError(f"域名不在白名单：{u.hostname}")
    infos = socket.getaddrinfo(u.hostname, 443, proto=socket.IPPROTO_TCP)
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if (ip.is_private or ip.is_loopback or ip.is_link_local
                or ip.is_reserved or ip.is_multicast or not ip.is_global):
            raise ValueError(f"受限/非公网地址 {ip}")


def safe_fetch_json(url: str, timeout: int = 30):
    _assert_public_https(url)
    req = urllib.request.Request(url, headers={"User-Agent": "siae-daily/1.0"})
    opener = urllib.request.build_opener(NoRedirect)
    with opener.open(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def gh_path():
    for c in GH_CANDIDATES:
        if c and Path(c).exists():
            return c
    return None


def gh_api(path: str):
    if not GH_PATH_RE.match(path):
        raise ValueError(f"gh path 未过白名单：{path!r}")
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


def today_str():
    return datetime.now(CST).strftime("%Y-%m-%d")


def search_date_tag():
    """GitHub 检索窗口用当天日期（幂等重跑同一天窗口一致）。"""
    return datetime.now(CST).strftime("%Y-%m-%d")


def fetch_aihot():
    try:
        d = safe_fetch_json("https://aihot.news/api/v1/items?mode=selected&window=24h&limit=30")
    except ValueError as e:
        print(f"[warn] aihot 通道失败：{e}", file=sys.stderr)
        return []
    items = d.get("items", d if isinstance(d, list) else [])
    return [{"id": f"ah-{it.get('publicId') or it.get('id') or hashlib.md5((it.get('title','')).encode()).hexdigest()[:8]}",
             "title": it.get("title", ""),
             "summary": (it.get("summary") or it.get("summaryZh") or "")[:200],
             "url": (it.get("links") or {}).get("source") or it.get("url") or "https://aihot.news",
             "source": "aihot"} for it in items]


def fetch_github():
    out = []
    tag = search_date_tag()
    for q in GITHUB_SEARCHES:
        q2 = q.replace("2026-10-01", tag)
        path = "search/repositories?q=" + urllib.parse.quote(q2) + "&sort=stars&per_page=5"
        d = gh_api(path)
        for it in (d or {}).get("items", []):
            out.append({"id": f"gh-{it.get('id')}",
                        "title": f"{it.get('full_name','')} ⭐{it.get('stargazers_count','?')}：{(it.get('description') or '')[:100]}",
                        "summary": (it.get("description") or "")[:200],
                        "url": it.get("html_url", "https://github.com"),
                        "source": "github"})
    return out


def fetch_releases():
    out = []
    for repo in HARNESS_REPOS:
        d = gh_api(f"repos/{repo}/releases?per_page=1")
        for rel in (d or [{}])[:1]:
            out.append({"id": f"rel-{repo.split('/')[-1]}-{rel.get('tag_name','?')}",
                        "title": f"{repo} {rel.get('tag_name','?')}（{rel.get('published_at','')[:10]}）",
                        "summary": ((rel.get("body") or "").strip().replace("\r", " "))[:250],
                        "url": rel.get("html_url", f"https://github.com/{repo}/releases"),
                        "source": "release"})
    return out


# --- 传感器逻辑（与 domain-pack v1.2.1 一致） ---

def load_cfg():
    return json.loads((HERE / "config" / "keywords.json").read_text(encoding="utf-8"))


def bucketize(item, cfg):
    text = (item["title"] + " " + item["summary"]).lower()
    hits, matched = [], {}
    for p in cfg["pillars"]:
        if p.get("persona_only"):
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


def veto(item, cfg):
    text = (item["title"] + " " + item["summary"]).lower()
    for rule in cfg["veto_rules"]:
        for kw in rule.get("keywords", []):
            if kw.lower() in text:
                return rule["id"]
    return None


def score(item, pillar_id):
    text = (item["title"] + " " + item["summary"]).lower()
    aw = cfg_action_words().get(pillar_id, [])
    words = ["降价", "发布", "上线", "开放", "修复", "开源", "release", "生效", "⭐"] + aw
    s = {}
    s["action_clarity"] = 3 + (1 if any(w in text for w in words) else 0) \
                          + (1 if pillar_id.startswith(("P1", "P3", "P4")) else 0)
    has_num = bool(re.search(r"[\$¥]\d|\d+(\.\d+)?%|\d+(\.\d+)?(倍|×|x)|⭐\d", text))
    s["cost_impact"] = 5 if has_num else (3 if any(w in text for w in ["价格", "成本", "免费"]) else 1)
    s["timeliness"] = 5 if any(w in text for w in ["生效", "限时", "正式"]) \
        else (4 if any(w in text for w in ["发布", "上线", "release", "⭐"]) else 3)
    s["breadth"] = 4 if any(w in text for w in ["跨", "通用", "开源"]) else 3
    s["credibility"] = 5 if item["source"] in ("release", "github") else 4
    s["total"] = sum(s.values())
    return s


_CFG = {}


def cfg_action_words():
    return _CFG.get("pillar_action_words", {})


def cfg_threshold(pillar):
    t = _CFG.get("pillar_thresholds", {})
    return t.get(pillar, t.get("default", 18))


def cfg_channel_priority():
    return _CFG.get("channel_pillar_priority", {})


def dedup_key(item):
    return hashlib.sha256((str(item.get("id", "")) + "|" + str(item.get("url", ""))).encode()).hexdigest()[:32]


def load_existing_keys():
    keys = set()
    for f in sorted((HERE / "materials").glob("*.jsonl")):
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    keys.add(dedup_key(json.loads(line)))
                except json.JSONDecodeError:
                    continue
    return keys


def main():
    global _CFG
    _CFG = load_cfg()
    today = today_str()
    items = fetch_aihot() + fetch_github() + fetch_releases()
    existing = load_existing_keys()

    new_rows = []
    for it in items:
        k = dedup_key(it)
        if k in existing:
            continue
        v = veto(it, _CFG)
        if v:
            it.update(pillar="-", status="vetoed", veto_rule=v, score_total=0)
        else:
            hits, matched = bucketize(it, _CFG)
            if not hits:
                it.update(pillar="-", status="unbucketed", veto_rule="V0", score_total=0)
            else:
                prefer = cfg_channel_priority().get(it.get("source", ""), "")
                pillar = prefer if prefer in hits else hits[0]
                sc = score(it, pillar)
                thr = cfg_threshold(pillar)
                it.update(pillar=pillar, matched_kw=matched.get(pillar, ""),
                          score_total=sc["total"],
                          status="kept" if sc["total"] >= thr else "below_threshold",
                          score=sc)
        it["collected_at"] = datetime.now(CST).strftime("%Y-%m-%d %H:%M")
        it["dedup"] = k
        new_rows.append(it)
        existing.add(k)

    day_file = HERE / "materials" / f"{today}.jsonl"
    with day_file.open("a", encoding="utf-8") as f:
        for r in new_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    kept = [r for r in new_rows if r["status"] == "kept"]
    if new_rows:  # 幂等重跑不覆盖已有待同步文件
        md = [f"# 待同步 Notion · {today}", "",
              f"采集 {len(items)} 条，新增 {len(new_rows)}（去重后），过筛 {len(kept)}；"
              f"由 agent 会话导入 Notion「SIAE 素材库」（Status=未筛）。", "",
              "| 标题 | 支柱 | 分 | 来源 | 状态 | URL |", "|---|---|---|---|---|---|"]
        for r in new_rows:
            md.append(f"| {r['title'][:60]} | {r['pillar']} | {r['score_total']} | "
                      f"{r['source']} | {r['status']} | {r['url']} |")
        (HERE / "notion" / "pending-sync.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"[ok] {today}: fetched={len(items)} new={len(new_rows)} kept={len(kept)} "
          f"-> materials/{today}.jsonl (+notion/pending-sync.md)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
