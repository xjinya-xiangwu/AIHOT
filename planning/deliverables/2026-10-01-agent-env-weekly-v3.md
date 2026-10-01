# Agent 环境进化周报 v3

> 窗口 2026-09-25 ~ 10-01 ｜ 2026-10-01，kurtx/ZCode ｜ 规格见 `planning/L0-weekly-spec.md`（v2 起从「新闻摘要」改为「环境 diff 函数」：**周报 = 环境基线 × 外部 Δ → 进化动作**，每条动作必须答「改什么组件」）

## 0. 环境基线快照（C0）

| 组件 | 当前状态 |
|---|---|
| 主力 harness | ZCode（GLM-5.3，1M ctx）；协同端 Claude Code v2.1.28x / opencode / codex / gemini-cli；国内端 10 agent 体系（asp v0.8.1） |
| 管线模型 | AIHOT 实例（规划）：抽取走便宜档（DeepSeek 系），写作独立；asp 模型推荐档位表待 v1（见动作 E1） |
| MCP | 默认零（方案 B）；context7 可选第一（v0.7.0 起） |
| **成本画像** | 🔴 **遥测缺失（C0 缺口 #1）**：无按任务/模型的用量统计。本期成本动作基于任务规模估算，下期起补：aihot 回执 + 各端 usage 导出 + 一个月度成本快照表 |

## 1. 进化动作清单（本期核心产出）

### 降本（C1/C2）

| # | 动作 | 落点组件 | 预期收益 | 依据 |
|---|---|---|---|---|
| **D1** | **把「预筛/抽取/格式化」类批处理任务的价格锚点改到 GPT-6 Luna**（$0.10/$0.50 per M；batch 再半价 $0.05/$0.25）——比 Sol 便宜 **20×**，上下文同为 1.05M | asp 模型档位表「批量抽取」格；AIHOT 预筛模型配置 | 抽取类成本降一个数量级（估算，待用量数据验证） | OpenRouter 实拉价 |
| **D2** | DeepSeek V4 新价生效（09-30：$1/$6，-60%）——中文抽取/周更负载的另一个低价锚点，与 Luna 二选一按质量实测定 | 同上 + aihot 写作档复核 | 同任务口径 -60% | 厂商调价 |
| **D3** | 可延迟任务（评测重跑、周报汇编）**开 batch 通道**：Sonnet 5.5 batch $1/$5（正价一半）、Luna batch $0.05/$0.25（五折） | 管线调度：非实时 job 走 batch | 批处理类再 -50% | OpenRouter 实拉价 |
| **D4** | GPT-6.1 Sol 已接替 GPT-6 Sol 且 Cost per Task -30%——**仍在用 GPT-6 Sol 的档位全部改名**，避免按旧模型计费 | 档位表逐格 | 防过期档位多花钱 | aihot 精选（AA） |

### 增效（C3/C4）

| # | 动作 | 落点组件 | 预期收益 |
|---|---|---|---|
| **E1** | **asp 模型推荐档位表 v1 成文**（本报告 §3 即初稿）——D12 架构里 L1 包的组成部分，目前缺位 | asp packs（base 的模型档位文档） | 用户侧开箱即得降本配置 |
| **E2** | 装 **jevgrep**（⭐1923）为候选代码检索 skill 的评估对象 | asp base 技能清单（评估后入包） | 代码检索上下文消耗显著下降 |
| **E3** | 升级 **Claude Code 至 v2.1.286**（修 `--resume` 崩溃后丢轮次的数据丢失 bug）；其余三家按 §5 | 各端 update + `asp doctor` 复检 | 长会话可靠性 |

### 进化（C5/C3）

| # | 动作 | 落点组件 | 说明 |
|---|---|---|---|
| **V1** | **OpenRouter 五篇 agent 质量工程教程 → SOP 候选**（CI eval 门禁/成本-质量选型/置信度路由/golden 集/回归测试） | L2 `sops/`（经 ≥3 次验证后编译为 skill） | 与 §4.3 回归门逐条同构，业界参考实现 |
| **V2** | 「Claude Code 视频技能」品类爆发（5 项目 2600+ 星）→ 观察位：若 PM 包用户要内容产出能力，评估 motion-video-kit 入 ai-pm 包 | asp ai-pm 技能清单 | 品类级信号，非本周动作 |
| **V3** | ChatGPT 可直接构建并部署 MCP 服务器（Sites）→ 记档：MCP 生产消费闭环向普通用户开放，影响 asp「装什么 MCP」的判断 | positions（判断条目） | 生态位信号 |

## 2. 成本雷达（C1：仅盯在用/候选模型，OpenRouter 实拉）

| 模型 | 输入/M | 输出/M | 上下文 | 备注 |
|---|---|---|---|---|
| z-ai/glm-5.3-prime | $2.80 | $8.80 | 1M | 本会话运行时档 |
| openai/gpt-6.1-sol（pro） | $2.00 | $10.00 | 1.05M | 已接替 GPT-6 Sol |
| anthropic/claude-sonnet-5.5 | $2.00 | $10.00（batch $1/$5） | 1M | 限时 Arena 直测中 |
| **openai/gpt-6-luna** | **$0.10** | **$0.50**（batch $0.05/$0.25） | 1.05M | **本周最大降本发现** |
| qwen/qwen3.8-max-prime | $4.00 | $12.00 | 1M | 贵于同档，非首选 |
| DeepSeek V4 | $1.00 | $6.00 | — | 09-30 新价（厂商侧） |
| 蚂蚁 Ling-3.1-flash | — | — | **1M** | 新发布，长文档批处理候选，价未采到（下期补） |

## 3. 任务-模型映射审计（C2：任务原型 → 当前 → 建议）

| 任务原型 | 当前 | 建议 | 依据 |
|---|---|---|---|
| 情报预筛/抽取（周更管线） | DeepSeek 系（规划中） | **Luna 或 DeepSeek V4 二选一**，跑同批素材比质量后定 | D1/D2 |
| 写作/汇编（周报/日报） | 独立写作档（规划中） | 维持独立档；候选 Sonnet 5.5（batch 可用于周报汇编） | §4.2 抽写分离 |
| 代码检索（会话内） | 各端内置 | 评估 jevgrep 补位（E2） | GitHub 信号 |
| 评审/难推理 | GLM-5.3 / Sonnet 档 | 维持；Opus 4.7（$15）仅难推理白名单 | 分层纪律 |
| 评测重跑（回归门） | 未建 | 建立时直接按 batch 价规划（D3） | V1 |

## 4. 技能生态 diff（C3，license 已过滤）

**新增候选**（装/评估）：jevgrep（E2）、logo-design-skill（⭐1200，跨 agent，PM 出图）、mcp-audit-tool（安全自检，多 MCP 用户）
**品类观察**：视频创作技能族（motion-video-kit ⭐685 / motion-graphics ⭐369 / awesome-claude-video-skills ⭐341 / claude-motion-design ⭐137）——V2
**淘汰信号**：无（上轮 asp-memory/seq-thinking 移可选已是先例；本轮 harness 无吞并性更新）
**其余新星**（观察不装）：dots（web agent ⭐1963）、universal-modder（skill+MCP 捆绑形态 ⭐1048）、SolidWorks MCP（工程样板 ⭐382）、yomiyasu（日文去 AI 味 ⭐652）

## 5. harness 变更（C4：只留影响工作流的）

- **Claude Code v2.1.286**：修 `--resume`/`--continue` 崩溃后丢并行调用后所有轮次（数据丢失级）——**升级即增益**（E3）
- **opencode v1.18.34**：macOS 27+ 签名修复（mac 必升）；命名空间会话头（多会话隔离更稳）
- **gemini-cli v0.64.0-nightly**：文件操作原子写入——并发写安全，多 agent 同仓协作相关
- **codex 0.161.0-alpha**：迭代期无实质说明，不动

## 6. 方法采纳（C5 → SOP 候选）

OpenRouter 五篇（详见 V1）中，**优先采纳顺序建议**：① golden 评测集五步法（我们 gold 体系直接可对标）→ ② CI eval 门禁（§4.3 落地时的工程参考）→ ③ 置信度路由（可进 asp 档位表逻辑）。Sarvam 入门视频收为「向新人解释 SIAE」的素材。

## 7. 不采纳清单（gold 负样本 → 传感器校准）

FTC 调查/参议院听证/白宫协议（监管新闻，无组件落点）｜OpenAI 融资估值/IPO（同前）｜ElevenLabs 回购、NYT 安全报道、HF CEO 私信（行业八卦）｜SynthID Bio、Ataraxos（领域研究，非 agent 使用）｜RAM/SSD 涨价（硬件行情，未触及算力采购决策线）｜GPT-6.1 Sol Arena 排名类纯榜单（已并入 D4 依据，不单列）

## 8. 数据缺口（C0 待办）

1. **成本遥测**：无按任务/模型用量统计——下期建立月度成本快照表（aihot 回执+各端 usage）
2. Ling-3.1-flash 价格未采到；HF trending 被墙（镜像通道待建）
3. asp 档位表 E1 成文后，本节 §2/§3 即其数据源

---
*规格：`planning/L0-weekly-spec.md` ｜ 信源：aihot.news API v1 精选流（40 条）+ OpenRouter /api/v1/models 实拉（462 模型）+ GitHub Search/Releases ｜ 本报告为 A0 S5 盲评素材（v3），同时是 §4.2 管线「入包项」产出的首次结构化实跑。*
