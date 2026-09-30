# L0 内容策略 · 三支柱（S3 首批批注结论 + 需求验证 + 组件映射）

> 2026-09-30 · 依据：专家 S3 首批批注（D12 标准下 12 条仅 2 条合规）+ 社媒现存内容检索 + AIHOT 组件盘点
> 关联：product-plan-v1.3.md §4.4（D12 窄化）、A0-protocol.md（S3）

## 一、S3 首批批注记录（2026-09-30，部分）

对简报 v0 的 12 条内容按 D12 标准（agent-usage 相关性一票否决）判定：

- **合规（gold 正样本，2 条）**：
  1. Claude Sonnet 5.5 发布，智能指数 56，仅低于 Opus 5.5 max 2 分〔媒体〕→ 模型能力变化，影响"该用哪档模型"
  2. H Company 发布 Holo4 系列（27B dense / 35B-A3B MoE）〔官方〕→ 新可选模型，影响私有化部署选型
- **不合规（gold 负样本，10 条）**：Agent 安全事件、IPO、听证会、算力采购传闻、Databricks 内部流程、基准审计、沙箱红队等——均为"行业资讯"，与 agent 使用无 immediate 关系，剔除
- **方向修正（专家原话）**：要的是「AIHOT LEADERBOARD、GitHub 周榜、Codex 必装插件集合这样的内容」

## 二、内容三支柱（L0 唯一收录范围）

| # | 支柱 | 回答的问题 | 形态 |
|---|---|---|---|
| P1 | **模型榜与模型动态** | 该用哪档模型？能力/价格变了什么？ | 榜单页 + 每日/每周变化摘要（发布、降价、能力跃迁） |
| P2 | **GitHub 周榜（agent-usage 过滤）** | 有什么新工具/新仓库能更好完成 agent 任务？ | 周榜 digest：trending 按"对 agent 使用有用"过滤 |
| P3 | **harness 必装集合** | CC/Codex/Cursor 该装什么 skills/插件/MCP？ | 按 harness 的精选集合 + 新增高价值条目动态 |

判断标准不变：**每条落到一个可执行动作（换模型 / 装技能 / 迁算力）**，否则剔除。

## 三、社媒需求验证（2026-09-30 检索）

**P3（必装集合）需求最强，内容供给已有但分散**：

- 知乎《Codex 最推荐的 15 个 skill》（2026-09）、《Codex 必装的 10 个 Agent Skills》（SegmentFault，2026-06）、《10 Best Codex CLI Skills — Installed and Tested》（agensi.io，2026-04）——"必装 N 个"是成熟选题模板
- GitHub：composio-community/awesome-codex-skills（官方风格 curated 清单）、openagentskill.com、AwesomeSkill.ai、UtilityHub（跨 CC/Cursor/Gemini 的 skills 收录站）
- 实践派内容也有市场：《装了 30 个 Skills 之后，我才搞清楚哪些在白浪费 context》（34→11 精简清单，context 成本视角）——**说明用户痛点不只是"装什么"，还有"该删什么"**
- Claude Code 官方已做 plugin marketplace 智能推荐（按用户工作内容推插件）——平台方在验证同一需求

**P2（GitHub 周榜）digest 形态被反复验证**：HelloGitHub、GitHubDaily、科技爱好者周刊（阮一峰）、CSDN 每周 GitHub 精选等存量刊物活跃；中文技术周刊索引站（shansan.top）收录数十种。**但全是泛技术视角——无人做"agent-usage 过滤"版，这是差异化空位**。

**P1（模型榜）**：AIHOT 自带（见下），无需外部验证。

结论：三支柱均有真实内容消费行为支撑；差异化 = **agent-usage 过滤 + 可执行动作层**，不做泛资讯。

## 四、AIHOT 组件映射（全部可覆盖，零新造轮子）

| 支柱 | AIHOT 现成组件 | 落地方式 |
|---|---|---|
| P1 模型榜 | **内建 leaderboard 模块**（`features.ts: leaderboard: true` 保留开启）：聚合 Artificial Analysis/LMArena/LiveBench/Epoch/EQ-Bench/Vals 六家，共识排名 v15，每天 02:05/08:05/14:05/20:05 抓 4 次，含官方 API 价格表与分类榜（编程/推理/知识）；`/leaderboard` 页 + `scripts/lb-round.ts --fetch` 手动触发 | ①保留模块不关（其他行业才关）②配置 `ARTIFICIAL_ANALYSIS_API_KEY`（可选，缺它该项缺位）③在日报 prompts 里加"榜单变化摘要"节：新进榜/排名跃迁/价格变动 |
| P1 Codex 额度监控 | **内建 codexResetMonitor 模块**：盯 @thsottiaux 的重置公告，`/api/v1/codex-resets` 机读接口 | 保留开启；需 `SOCIALDATA_API_KEY`，无 key 则关 |
| P2 GitHub 周榜 | **RSS 信源**：`mshibanami/GitHubTrendingRSS` 提供 `…/daily/all.xml` 与 `…/weekly/all.xml`（支持按语言分 feed），GitHub Pages 托管、社区维护 | sources.json 加 2 条 RSS 源（weekly 全量 + daily 观察）→ 走现有预筛评分，prompts 按 P2 判断标准过滤"agent-usage 相关" |
| P3 必装集合 | **多类信源组合**：①GitHub 仓库源（awesome-codex-skills、awesome-claude-code 等，经 commits/releases RSS 或 web_list）②skills 收录站（AwesomeSkill.ai / openagentskill.com / UtilityHub，web_list 或 json_list）③X 搜索（`x_search` 信源："Claude Code skill" / "Codex skill" / "MCP"）④公众号（Dajiala：AI 工具类公众号） | 信源分级 T2；prompts 增"P3 判断标准"：只收"能更好完成某任务的新 skills/插件/MCP"，营销水文压制；月度聚合产出《CC/Codex 必装集合》专页（复用 report-period 范式） |

**结论：三支柱全部可用现有 AIHOT 组件（内建模块 + 六类信源）覆盖，无需新造轮子**；工作集中在 sources 配置、prompts 改写（P1-P3 判断标准）、与 asp collector 的 trending 抓取合并（避免重复抓）。

## 五、落地清单（并入 Phase B）

1. `industry/features.ts`：leaderboard / codexResetMonitor 保持 true（AI pack 特有，与 D12 一致）
2. `industry/sources.json` 初版信源表（三支柱）：GitHubTrendingRSS ×2、awesome-codex-skills/awesome-claude-code 仓库源、skills 收录站 ×3、X 搜索 ×2-3、模型厂商官方博客/定价页（Anthropic/OpenAI/DeepSeek/智谱等）、tokens 中转与算力平台公告
3. `industry/prompts/`：selection-score.md 增 P1/P2/P3 判断标准与负样本示例（本文件第一节 10 条负样本 + 2 条正样本即首批 gold）
4. taxonomy 对齐三支柱：模型 / 环境（harness·工具）/ 技能（skills·MCP）/ 算力成本（D12 已定）
5. asp collector 的 trending 抓取与 P2 信源合并，避免双份
6. A0-S5 盲评前先用三支柱标准重做一份周报 v1（素材：模型榜快照 + 本周 trending + 必装集合候选）

## 参考（检索来源）

- 知乎《Codex 最推荐的 15 个 skill》· SegmentFault《Codex 必装的 10 个 Agent Skills》· agensi.io《10 Best Codex CLI Skills (Installed and Tested)》
- github.com/composio-community/awesome-codex-skills · openagentskill.com · awesomeskill.ai · utilityhub.site
- 博客园《装了 30 个 Skills 之后…白浪费 context》
- HelloGitHub / GitHubDaily / 科技爱好者周刊 / shansan.top 中文技术周刊索引（P2 digest 需求佐证）
- mshibanami.github.io/GitHubTrendingRSS（P2 RSS 通道）
- AIHOT 内建模块：docs/leaderboard.md、packages/backend/src/leaderboard/、features.ts
