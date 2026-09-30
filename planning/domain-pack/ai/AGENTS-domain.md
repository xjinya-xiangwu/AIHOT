# AGENTS-domain — Agent 使用情报站·领域规范摘要

> 本文件随 pack 装机后供 agent 会话加载（llms.txt / INDEX 模式）。数据边界与治理全文见产品规划 v1.3 §4.0/§4.1。

## 本站是什么

**Agent 使用情报传感器**：只回答一个问题——**此刻该把 agent 换成什么、装什么、迁去哪**。不含一般 AI 行业资讯（一票否决，见下）。

## 内容三支柱

1. **P1 模型榜与模型动态**（category=models）：闭源共识榜（/leaderboard）+ HuggingFace 开源 trending + 垂域站榜（按需）。判据=改变选型。
2. **P2 项目周榜**（category=environment）：GitHub trending 经 agent-usage 过滤 + 角色分榜（PM/开发者…）。判据=让 agent 更好完成某类任务。
3. **P3 必装集合**（category=skills）：各 harness 的 skills/插件/MCP 精选与新增动态，**含"该删什么"**（context 成本）。判据=值得进入装/删清单。

算力与成本（category=compute）：API 定价变动、tokens 中转、算力平台/额度——判据=迁移有净收益。

## 动作层铁律

每条精选必须落到：**换模型 / 装技能·插件 / 迁算力**。写不出动作的内容不精选；摘要须含具体模型名/仓库名/安装方式/价差。

## 一票否决负类

公司经营与融资、监管诉讼听证、安全八卦（除非改变使用决策）、格局评论、采购传闻、纯学术研究、企业内部流程案例。首批 10 条负样本见 gold-selection-seed.jsonl。

## 与环境体系的关系

- 本站是 **L0 传感器**；产出经内容更新管线沉淀为 **L1 技能包（Agent 执行环境）** 的包内内容（新技能候选/模型推荐档/MCP 清单/成本参数），用户使用反馈再沉淀 L2——见产品规划 §3 价值链。
- 传感器/提示词/门槛的变更属**行为变更**：合入前过 gold 切片 + held-out 发布回归门。

## 数据边界（红线）

- 只存链接 + 自写摘要（site_fulltext 默认关）
- 私人素材不入站；来源明确允许才开全文
- 无 LICENSE 仓库（如 awesome-codex-skills）只作信源引用，内容不复制进分发链
