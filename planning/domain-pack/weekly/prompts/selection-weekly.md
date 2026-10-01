# 周报管线筛选 Prompt（selection-weekly）

> 从「帮助 agent 进化、降本增效」倒推。配合 `keywords.json`（支柱/否决/打分维度）使用。
> 三段式对齐 AIHOT：预筛（关键词）→ 精选（打分+一票否决）→ 输出（结构化条目）。

## 预筛（prescreen）

对每条候选（aihot 精选流 / GitHub 新星 / harness 发版）：

1. 按 `keywords.json.pillars` 关键词分桶：标题或摘要命中即入桶（可多桶）。
2. 全桶未命中 → internal 人格直接否决（记入 negative）；pm 人格再过 PM_industry_intel 桶。
3. 命中 `veto_rules` 粗筛关键词的 → 否决并记录规则号。

## 精选（selection，逐条打分）

对预筛通过的每条，按五维打分（各 0-5，总分 25）：

- **动作明确度**：能否一句话说清「改什么组件」（换模型/装技能/升级/改方法）？说不清 ≤2
- **成本影响面**：有量化数字（价格/倍数/百分比）= 4-5；定性描述 = 2-3；无 = 0-1
- **时效性**：本周生效 = 5；已发布可立即用 = 4；预告/等待开放 = 2-3；常青方法 = 3
- **适用面**：跨多 agent 端/多任务 = 4-5；单端单任务 = 2-3
- **可信度**：官方发布/定价页/API 实拉 = 5；权威媒体/榜单 = 3-4；社区传闻 = 1-2

**门槛**：总分 ≥ 3.5×5=17.5 入精选；13-17 待定（供组装阶段按版面取舍）；<13 否决。

**一票否决（任一命中即否决，无论总分）**：
① 无法落到任何动作出口（internal：换模型/装技能/升级/改方法；pm：另含「供 PM 引用」）
② 纯八卦（V2）
③ internal 人格的领域越界研究（V3）
④ 同一事件纯排名变体（V4，并入主条目）

## 输出（selection-items.jsonl 每行一条）

```json
{"id":"...", "title":"...", "pillar":"P1_model_compute", "score":{"action_clarity":5,"cost_impact":5,"timeliness":5,"breadth":4,"credibility":5,"total":24}, "action_hint":"抽取档价格锚改 Luna", "source":"aihot|github|release", "url":"...", "veto":null}
```

否决条目单独输出（`vetoed.jsonl`，含规则号与一句话理由）——**否决记录=传感器 gold 负样本，回流校准**。
