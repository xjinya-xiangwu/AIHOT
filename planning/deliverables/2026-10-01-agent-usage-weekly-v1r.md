# Agent 使用情报周报 v1r（重制版）

> 窗口：2026-09-25 ~ 2026-10-01 ｜ 生成：2026-10-01，kurtx/ZCode ｜ 纪律：agent-usage 相关性一票否决（与「此刻该换什么模型、装什么技能、迁去哪算力」无直接关系的内容一律不收）
> 说明：原 v1（09-30 产出）仍在 xujinya 机本地未入库，本版为按同一标准重制，信源窗口更新至 10-01。三支柱信源：模型榜 / GitHub 周榜 / harness 必装集合。

## ⚡ 本周动作清单（TL;DR）

| # | 动作 | 事项 | 为什么 |
|---|---|---|---|
| 1 | **迁算力** | DeepSeek API 切 V4 新价（生效日 09-30：输入 $2.50→$1.00，输出 $15→$6，约 -60%） | 同质推理成本立省六成；重度用 DeepSeek 的周更/抽取管线优先改价目表 |
| 2 | **装技能** | [dzhng/jevgrep](https://github.com/dzhng/jevgrep)（⭐1923，本周新星） | 「问代码在哪做什么」的 agent 专用代码发现 CLI——装上后代码检索类任务少烧上下文 |
| 3 | **装技能** | [kaankiziltan/logo-design-skill](https://github.com/kaankiziltan/logo-design-skill)（⭐1184） | 跨 agent（Claude/Gemini CLI/Codex）通用的设计类 skill，PM 侧出图场景即插即用 |
| 4 | **观察** | 自家赛道：AIHOT 框架冲上 GitHub 本周新星 ⭐4213 | 上游热度=流量窗口，L1 上架动作（Claude 市场/skills.sh）宜趁势提前 |

## 🏛 支柱一：模型榜（换模型 / 迁算力）

- **DeepSeek V4 新价目生效（09-30）**：输入 $1.00/M、输出 $6.00/M（原 $2.50/$15）——同级推理里性价比再度拉大。**动作**：检查自有管线（周更抽取、评测脚本）的模型价目配置，非旗舰任务可整体下移一档；对比 tokenr.co 等比价页确认中转站跟进幅度。〔来源：[santageai 09-15 比对](https://santageai.com)，生效日 09-30〕
- **Claude Opus 4.7 定位 $15/M**（Sonnet 4.6 维持 $3/M）：旗舰与主力档差距拉到 5×，进一步坐实「分层用模」纪律——探索/写作用 Sonnet 档，难推理才上 Opus。**动作**：asp packs 的模型推荐档位表核对一遍。〔来源：[tokenr.co](https://tokenr.co)〕
- 通道备注：HF trending API 本周被墙未采到，模型榜 pillar 降级为价格/发布信号——下周补 HF 镜像通道。

## 🏗 支柱二：GitHub 周榜（agent-usage 过滤后）

- **[feder-cr/dots](https://github.com/feder-cr/dots)（⭐1961）**：自带浏览器的 web agent。**含义**：浏览器自动化是本周 agent 主战场之一；对做 web 侧 PM 工作流（竞品巡查/数据抓取）者值得观察，暂不装（与我们管线重叠度低）。
- **[dzhng/jevgrep](https://github.com/dzhng/jevgrep)（⭐1923）**：见动作清单 #2。同类信号：代码发现类工具起飞=「agent 干重活」需求上探。
- **AIHOT 框架 ⭐4213 登顶本周新星**（上游 KKKKhazix 仓库）：热点站框架被市场验证。**含义**：① 我们选它做 L0 传感器的判断被外部印证；② 借势窗口——L1 上架（skills.sh 通道已 live）配套内容帖可引用「AIHOT 星榜」背书。**动作**：W1 上架素材发布时机提前。
- 过滤掉的：纯热点资讯类、无 agent 使用含义的项目若干（一票否决）。

## 🧰 支柱三：harness 必装集合（装技能 / 升级）

- **Claude Code v2.1.285/286 连日发版（09-29/30）**、**opencode v1.18.34**、**codex 0.161.0-alpha 快节奏**、**gemini-cli v0.64.0 nightly**：harness 高频发版周。**动作**：跑一遍各端 `update`（asp update 一键）；升级后跑 `asp doctor` 验证 MCP 连通——v0.8.1 的 doctor 正是为此准备的。
- **[rehan-remade/universal-modder](https://github.com/rehan-remade/universal-modder)（⭐1024）**：skills+MCP 组合让 Claude 改任意游戏 mod。**含义**：「skill+MCP 捆绑交付」的形态被社区跑通，与 asp packs 结构同向；收藏观察，不装。
- awesome 通道同前（无 LICENSE 仅信源）。

## 📌 本周判断

1. 算力端降价是本周唯一「立即动作」级事件（迁 DeepSeek 价目）。
2. GitHub 侧 skill 生态（设计/代码发现/modding）连续两周出四位数新星——skills.sh 通道的流量判断成立，上架宜快。
3. harness 连日发版=升级纪律的价值证明；doctor 体检从此是每周动作。

---
*信源：GitHub Search/Releases API（gh CLI）、HF API（降级）、tokenr.co / santageai.com 比对页。生成管线：agent 预筛 → 三支柱归类 → 动作标注。本报告为 A0 S5 盲评素材（v1r 重制版）。*
