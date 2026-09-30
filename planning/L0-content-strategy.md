# L0 内容策略 · 三支柱（S3 首批批注结论 + 需求验证 + 组件映射）

> v1.1（2026-09-30）：按专家反馈深化——P1 扩为**三层模型榜**（闭源共识 / 开源 HF trending / 垂域站榜）；P2 增**角色分榜**（如"PM 本周最火项目"）；新增 **§六 产品化 IA**（AIHOT 式分 tab 榜单页）。垂域通道已实测：HF trending API ✅（`?sort=trendingScore`，含 pipeline_tag 天然分类）、Civitai API ✅（公开无 key）。
> v1.0（2026-09-30）：三支柱确立 + 社媒需求验证 + AIHOT 组件映射。

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
| P1 | **模型榜（三层）** | 该用哪档模型？能力/价格变了什么？ | **①闭源共识榜**（内建 leaderboard：六家评测共识+价格表）**②开源 trending**（HuggingFace `?sort=trendingScore`，按任务类型 pipeline_tag 分组呈现）**③垂域站榜**（Civitai 类垂域模型站周榜，按需开启）+ 每日/每周变化摘要 |
| P2 | **项目周榜（全量 + 角色分榜）** | 有什么新工具/新仓库能更好完成 agent 任务？**我的角色（PM/开发者/设计师…）本周最火的是什么？** | 全量榜（trending 按 agent-usage 过滤）+ **角色分榜**（每角色 curated 信源集 + 角色视角过滤） |
| P3 | **harness 必装集合** | CC/Codex/Cursor 该装什么 skills/插件/MCP？ | 按 harness 分组的精选集合 + 新增高价值条目动态 |

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
| P1 模型榜·①闭源共识 | **内建 leaderboard 模块**（聚合 6 家评测、共识 v15、每天 4 抓、官方价格表） | 保留开启 + `ARTIFICIAL_ANALYSIS_API_KEY`（可选）；日报 prompts 加"榜单变化摘要"节 |
| P1 模型榜·②开源 trending | **HuggingFace API**（`https://huggingface.co/api/models?sort=trendingScore&direction=-1&limit=30`，2026-09-30 实测✅：返回 trendingScore/下载量/点赞/pipeline_tag，无 key） | AIHOT **json_list 信源**直接接入；pipeline_tag（任务类型）映射 taxonomy 的"模型"子分类；prompt 按"可本地部署替代闭源档"角度过滤出 actionable 条目 |
| P1 模型榜·③垂域站榜 | **Civitai API**（`/api/v1/models?sort=…&period=Week`，2026-09-30 实测✅公开无 key；图像生成垂域） | 同为 json_list 信源；**默认关闭、按需开启**（AI pack v1 只上 ①②，垂域等对应领域 pack 启用——机制已验证，成本为零增量）；可扩展 OpenRouter rankings（真实用量榜）等 |
| P1 Codex 额度监控 | **内建 codexResetMonitor 模块** | 保留开启；需 `SOCIALDATA_API_KEY`，无 key 则关 |
| P2 GitHub 周榜·全量 | **RSS 信源**：`mshibanami/GitHubTrendingRSS`（daily/weekly，实测✅） | sources.json 加 2 条 RSS 源 → 预筛评分 → prompts 按 agent-usage 过滤 |
| P2 周榜·**角色分榜** | **每角色 curated 信源集**（json_list/web_list/rss）+ 角色过滤 prompt：PM 角色示例——Product Hunt RSS（producthunt.com/feed）、awesome-product-management 类清单、PM 工具站 changelog、GitHub topics（product-management 等） | 每角色一组 sources + taxonomy 加角色 category（URL key 如 `/all?category=pm`）；**承载用现成 categories/topics 机制，零代码**；角色榜聚合呈现见 §六 |
| P3 必装集合 | 多类信源组合（awesome 仓库源 / skills 收录站 / X 搜索 / 公众号） | 同 v1.0；月度聚合《必装集合》专页复用 report-period 范式 |

**结论：三支柱全部可用现有 AIHOT 组件（内建模块 + 六类信源）覆盖，无需新造轮子**；工作集中在 sources 配置、prompts 改写（P1-P3 判断标准）、与 asp collector 的 trending 抓取合并（避免重复抓）。

## 五、落地清单（并入 Phase B）

1. `industry/features.ts`：leaderboard / codexResetMonitor 保持 true（AI pack 特有，与 D12 一致）
2. `industry/sources.json` 初版信源表（三支柱）：GitHubTrendingRSS ×2、awesome-codex-skills/awesome-claude-code 仓库源、skills 收录站 ×3、X 搜索 ×2-3、模型厂商官方博客/定价页（Anthropic/OpenAI/DeepSeek/智谱等）、tokens 中转与算力平台公告
3. `industry/prompts/`：selection-score.md 增 P1/P2/P3 判断标准与负样本示例（本文件第一节 10 条负样本 + 2 条正样本即首批 gold）
4. taxonomy 对齐三支柱：模型 / 环境（harness·工具）/ 技能（skills·MCP）/ 算力成本（D12 已定）
5. asp collector 的 trending 抓取与 P2 信源合并，避免双份
6. A0-S5 盲评前先用三支柱标准重做一份周报 v1（素材：模型榜快照 + 本周 trending + 必装集合候选）

## 六、产品化 IA：AIHOT 式分 tab 榜单页（2026-09-30 专家要求）

**原则**：榜单页 = 常驻结构化呈现（库形态），周报 = 变化摘要（流形态），两者同源——都从 AIHOT 单一 publication 读取层出，不另建数据通道。

```
站点 IA（tab 导航）
├── 首页（日报流：三支柱动态卡片，AIHOT 现成）
├── 模型榜 /models
│   ├── 闭源共识榜（内建 /leaderboard 平移：榜 + 价格表 + 分类榜）
│   ├── 开源 trending（HF 榜，按 pipeline_tag 分组：LLM/图像/ASR/…）
│   └── 垂域榜（Civitai 等，按需开启，默认隐藏）
├── 项目周榜 /trending
│   ├── 全量（agent-usage 过滤）
│   ├── PM（角色分榜）
│   ├── 开发者（角色分榜）
│   └── …角色扩展（每角色一组 curated 信源）
├── 必装集合 /must-have
│   ├── Claude Code  │ Codex  │ Cursor  │ 通用 MCP
│   └── （含"该删什么"精简建议——社区验证的差异化点）
└── 日报/周报 /daily /weekly（AIHOT 现成）
```

**承载机制分层（最小化开发）**：

| 层级 | 机制 | 工作量 |
|---|---|---|
| 数据/过滤 | categories（角色 key 进 URL：`/all?category=pm`）+ topics 主题页 + json_list/RSS 信源 | **零代码**（纯 industry/ 配置，Phase B 主体） |
| 榜单呈现 | 内建 /leaderboard 直接复用（闭源榜）；开源/垂域榜与角色榜的**聚合榜单页**（tab 容器 + 排序表格）需新增 2-3 个 route（`apps/web/app/routes/`），复用 leaderboard 的页面组件风格与分类筛选交互 | **小开发**（Phase B 内，预计 1-2 天；fork 新增路由不动上游既有文件，符合硬分叉纪律） |
| 周报 | 现成 /daily /weekly + prompts 增三支柱分节 | 零代码 |

**上线顺序**：v1 = 零代码层（categories+topics+信源+内建 leaderboard，先以"分类筛选+主题页"形态可用）→ v1.1 = 榜单聚合 route（真 tab 页）。**先内容后皮肤**：信源与过滤标准（gold 校准）先行，页面开发在内容跑通后做。

## 参考（检索来源）

- 知乎《Codex 最推荐的 15 个 skill》· SegmentFault《Codex 必装的 10 个 Agent Skills》· agensi.io《10 Best Codex CLI Skills (Installed and Tested)》
- github.com/composio-community/awesome-codex-skills · openagentskill.com · awesomeskill.ai · utilityhub.site
- 博客园《装了 30 个 Skills 之后…白浪费 context》
- HelloGitHub / GitHubDaily / 科技爱好者周刊 / shansan.top 中文技术周刊索引（P2 digest 需求佐证）
- mshibanami.github.io/GitHubTrendingRSS（P2 RSS 通道）
- AIHOT 内建模块：docs/leaderboard.md、packages/backend/src/leaderboard/、features.ts
