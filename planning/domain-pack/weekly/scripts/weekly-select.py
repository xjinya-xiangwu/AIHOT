#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""weekly-select.py — SIAE 信息漏斗 L1：周筛选器

读素材库近 7 天 jsonl → 按 Codex 模板（agent-evolution-weekly.md）产出周报草稿：
  §1 外部 Δ 动作卡（kept 条目按支柱分组，含 A/B/C 建议与落点）
  §2 S 表（热门 skills/项目候选，供用户三态选择）
  §3 M 表（模型能力榜候选）
  §4 不采纳清单（vetoed/below_threshold 择要 = gold 负样本）
周报草稿供 agent 会话补「含义/建议」后入 Notion 09（GitHub canonical 存
aihot planning/deliverables/）。

用法：python3 scripts/weekly-select.py [--days 7] [--out archive/weekly-YYYY-MM-DD-draft.md]
"""
import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
CST = timezone(timedelta(hours=8))

PILLAR_NAMES = {
    "P1_model_compute": "模型与算力（换模型/迁算力）",
    "P2_skills_tools": "技能与工具（装技能/入包）",
    "P3_harness_env": "harness 与环境（升级）",
    "P4_method_quality": "方法与质量（SOP 候选）",
}
ACTION_HINTS = {
    "P1_model_compute": "核对价目/评估换档",
    "P2_skills_tools": "入包评估",
    "P3_harness_env": "升级+doctor",
    "P4_method_quality": "SOP 草案",
}


def load_rows(days):
    rows = []
    cutoff = datetime.now(CST) - timedelta(days=days)
    for f in sorted((HERE / "materials").glob("*.jsonl")):
        try:
            fdate = datetime.strptime(f.stem, "%Y-%m-%d").replace(tzinfo=CST)
        except ValueError:
            continue
        if fdate < cutoff:
            continue
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
    return rows


def grade_for(row):
    """A/B/C 分级建议（按 Codex 模板判据）。"""
    pillar, score = row["pillar"], row["score_total"]
    if pillar == "P4_method_quality":
        return "A", "方法采纳为实验口径（不花钱不动环境）"
    if pillar == "P3_harness_env":
        return "B", "沙箱回归通过再升级（可回滚）"
    if pillar == "P2_skills_tools":
        return "B", "许可证/OS 核验后试评"
    if pillar == "P1_model_compute":
        return ("B" if score >= 19 else "C",
                "先同题比质比价（B）；涉及开户/换主力档为 C 需拍板")
    return "?", ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--out", default="")
    a = ap.parse_args()

    rows = load_rows(a.days)
    if not rows:
        print("[error] 素材库窗口内无条目", file=sys.stderr)
        return 2

    kept = [r for r in rows if r["status"] == "kept"]
    vetoed = [r for r in rows if r["status"] in ("vetoed", "below_threshold", "unbucketed")]
    # 周内去重（同 URL 只留最新）
    seen, kept_dedup = set(), []
    for r in sorted(kept, key=lambda x: x["collected_at"], reverse=True):
        if r["url"] not in seen:
            seen.add(r["url"])
            kept_dedup.append(r)
    kept = kept_dedup

    by_pillar = defaultdict(list)
    for r in kept:
        by_pillar[r["pillar"]].append(r)
    for p in by_pillar.values():
        p.sort(key=lambda r: -r["score_total"])

    ts = datetime.now(CST).strftime("%Y-%m-%d %H:%M")
    s_cnt = 0
    lines = [f"# Agent 自进化周报·草稿（管线生成 {ts}）", ""]
    lines.append(f"> 窗口近 {a.days} 天；素材库输入 {len(rows)} 条 → 周报候选 {len(kept)} "
                 f"（去重后）/ 拒收 {len(vetoed)}。本稿为 weekly-select.py 产物；"
                 f"`AGENT-COMPOSE` 位由 agent 会话补含义与建议后按 Codex 模板成稿。")
    lines.append("")

    lines.append("## §1 外部 Δ 动作卡（按支柱）")
    lines.append("")
    for pid in ["P1_model_compute", "P2_skills_tools", "P3_harness_env", "P4_method_quality"]:
        plist = by_pillar.get(pid, [])
        if not plist:
            continue
        lines.append(f"### {PILLAR_NAMES[pid]}（{len(plist)} 条）")
        lines.append("")
        for r in plist:
            g, why = grade_for(r)
            lines.append(f"- **{r['title'][:70]}**（{r['score_total']} 分｜{r['source']}｜"
                         f"{r['collected_at'][:10]}）")
            lines.append(f"  - 建议分级：**{g}**（{why}）｜落点：{ACTION_HINTS[pid]}｜命中：`{r.get('matched_kw','')}`")
            lines.append(f"  - `AGENT-COMPOSE`：〔含义一句话 + 具体动作 + 验证方式〕｜{r['url']}")
        lines.append("")

    lines.append("## §2 S 表：热门 skills/项目候选（用户三态选择）")
    lines.append("")
    lines.append("| ID | 候选 | 星/分 | Agent 建议 | 你的选择（试评/观察/不考虑） |")
    lines.append("|---|---|---|---|---|")
    for i, r in enumerate([x for x in kept if x["pillar"] == "P2_skills_tools"][:8], 1):
        lines.append(f"| S{i:02d} | {r['title'][:55]} | {r['score_total']} | "
                     f"B：许可证核验后试评 | |")
    lines.append("")

    lines.append("## §3 M 表：模型能力榜候选（用户三态选择）")
    lines.append("")
    lines.append("| ID | 模型/价格信号 | 分 | Agent 建议 | 你的选择 |")
    lines.append("|---|---|---|---|---|")
    for i, r in enumerate([x for x in kept if x["pillar"] == "P1_model_compute"][:8], 1):
        lines.append(f"| M{i:02d} | {r['title'][:55]} | {r['score_total']} | "
                     f"B：同题比质比价后进档位建议 | |")
    lines.append("")

    lines.append("## §4 不采纳清单（gold 负样本，择要 ≤10）")
    lines.append("")
    for r in sorted(vetoed, key=lambda x: -x.get("score_total", 0))[:10]:
        lines.append(f"- [{r['status']}{'/'+r.get('veto_rule','') if r.get('veto_rule') else ''}] "
                     f"{r['title'][:60]}")

    out = Path(a.out) if a.out else HERE / "archive" / f"weekly-{datetime.now(CST).strftime('%Y-%m-%d')}-draft.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[ok] in={len(rows)} kept={len(kept)} draft -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
