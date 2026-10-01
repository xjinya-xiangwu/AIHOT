# Agent 使用情报周报 v2

> 窗口 2026-09-25 ~ 10-01 ｜ 2026-10-01，kurtx/ZCode
> **本版起改用 AIHOT 底座执行采集**：主通道 = aihot.news 公开 API v1（`/api/v1/items?mode=selected&window=7d`，本周 40 条精选）+ fork domain-pack 三支柱信源配置；GitHub 周榜三路检索合并；harness 逐家拉发版正文。方法与上一版（v1r）的区别见文末。

## TL;DR：本周值得动手的七件事

1. **迁移推理价目到 GPT-6.1 Sol**——它上线仅 7 天就接替了 GPT-6 Sol，且 Artificial Analysis 实测 Cost per Task 比 GPT-6 Sol 低约 30%（$0.72/任务）。在 OpenAI 档位上跑批处理/评测的管线，这周切换是纯赚。
2. **DeepSeek V4 新价生效**（09-30）：输入 $2.50→$1.00、输出 $15→$6。中文抽取/周更类负载继续下移。
3. **升级四家 harness 并跑一遍 `asp doctor`**——Claude Code 连发两版修了会话恢复丢轮次的坑（详见支柱三），这周升级的收益实打实。
4. **装 jevgrep**（⭐1923）：用自然语言找代码在哪、干什么，agent 代码检索的上下文消耗直接砍一截。
5. **关注「Claude Code 视频技能」这个本周最大新品类**——5 个相关项目合计 2600+ 星（详见支柱二），做内容/营销的 agent 用户本周都在装这些。
6. **读 OpenRouter 的五篇 agent 工程教程**（CI 评测门禁 / 成本-质量选型 / 置信度分级路由 / golden 评测集 / 回归测试）——和我们自己在做的 §4.3 回归门几乎是同一套方法论，白捡的参考实现。
7. **本地推理用户装 AA-AgentPerf-Local**（Artificial Analysis 开源）：重放 8 个真实 agent 任务测你本机的推理性能，买卡/配环境前先跑一遍。

## 支柱一：模型与算力（换什么模型、迁去哪）

**OpenAI 档位换代提速。** GPT-6.1 Sol 上线 7 天即接替 GPT-6 Sol，智能指数距 GPT-6 Astra 仅 1 分，而每任务成本低约三成；Max 档在 Code Arena: WebDev 已到第 3（1759 分）。含义：OpenAI 内部的档位生命周期已经短到「等评测再切就晚了」——价目表按周核对成了基本操作。〔aihot 精选｜Artificial Analysis ×2、Arena ×2〕

**Google 重回第一梯队。** Gemini 4 Argon 发布，高推理档在 Artificial Analysis 评测中进入智能前三梯队，Agent Arena 排名第 8（净提升 +7.92%）；不过首发只对「可信网络防御者」（Fairwind Program）开放——普通用户先记档位，等开放再测。

**国产侧两条实料。** ① 蚂蚁百灵 Ling-3.1-flash：总参 560B/激活 25B、上下文 **1M**、混合线性架构——长文档批处理场景多了一个国产选项；② DeepSeek 开源了面向华为昇腾的一整套基础设施组件（TileLang/DeepGEMM/DeepEP 等）——如果有昇腾算力，迁移的地基这周刚铺好。

**自托管算力用户看两件。** vLLM 官方发了分离式推理（prefill/decode 分离、无 GPU replica）实用指南，v0.30.0+ 可用；AA-AgentPerf-Local 开源（见 TL;DR #7）。

## 支柱二：GitHub 周榜（agent-usage 过滤，12 项）

**本周最大信号：Claude Code 视频创作技能爆发**——一个品类 5 个项目、合计 2600+ 星，全是本周新建。做内容营销的 agent 用户值得关注：

| 项目 | 星 | 是什么 / 谁该装 |
|---|---|---|
| [feder-cr/dots](https://github.com/feder-cr/dots) | 1963 | 自带浏览器的开源 web agent（OpenAI DevDay 同名产品的开源对应）；需要 agent 替你逛网页、做自动化的观察 |
| [dzhng/jevgrep](https://github.com/dzhng/jevgrep) | 1923 | 「这段代码在哪、干什么的」自然语言代码发现 CLI；所有 coding agent 用户都该试 |
| [kaankiziltug/logo-design-skill](https://github.com/kaankiziltug/logo-design-skill) | 1200 | 跨 agent（Claude/Gemini CLI/Codex）logo 设计 skill，含设计原则与工作流 |
| [rehan-remade/universal-modder](https://github.com/rehan-remade/universal-modder) | 1048 | skills+MCP 捆绑让 Claude 给任意游戏做 mod——「skill+MCP 组合交付」形态的社区验证 |
| [echris6/motion-video-kit](https://github.com/echris6/motion-video-kit) | 685 | Claude Code 商业视频 skill 套件，带独立评审循环 |
| [nanaism/yomiyasu](https://github.com/nanaism/yomiyasu) | 652 | 去 AI 味的日文改写 skill（中文化场景可借鉴其思路） |
| [amitshekhariitbhu/ai-system-design](https://github.com/amitshekhariitbhu/ai-system-design) | 480 | LLM/RAG/Agent 系统设计学习路径，面试与教学场景 |
| [CaptureGrubEnchant/SolidWorks](https://github.com/CaptureGrubEnchant/SolidWorks) | 382 | SolidWorks MCP Server：agent 直连运行中的 SolidWorks 画草图——工程领域 MCP 的样板 |
| [Barty-Bart/motion-graphics](https://github.com/Barty-Bart/motion-graphics) | 369 | Claude Code + Codex 通用的动效技能 |
| [zhuyansen/awesome-claude-video-skills](https://github.com/zhuyansen/awesome-claude-video-skills) | 341 | 视频技能清单站（本品类爆发的目录证据） |
| [openJiuwen-ai/iCode](https://github.com/openJiuwen-ai/iCode) | 282 | 完全离线的轻量开发平台/agent 工具箱——本地优先路线 |
| [graygnatconsole/mcp-audit-tool](https://github.com/graygnatconsole/mcp-audit-tool) | 124 | MCP 服务器安全审计 CLI，扫 agent 配置里的高危项；多 MCP 用户建议跑一次 |

一票否决剔除：纯资讯聚合、无使用含义的 hot 项目若干。

## 支柱三：harness 发版实录（升级什么、为什么）

**Claude Code v2.1.285→286（09-29/30，连发两版）**——本周最值得升级的一次：修复了 `--resume`/`--continue` 在会话崩溃后**丢失并行工具调用之后所有轮次**的数据丢失级 bug；修了多个进程同时弹登录浏览器的问题；权限弹窗加了 "2 of 5" 计数。**动作**：还在用旧版的直接升，长会话用户优先。

**opencode v1.18.34（09-30）**：macOS 27+ 二进制重签名（本地编译也能跑）；请求带命名空间会话头（多会话隔离更稳）；社区修正了 GPT-6.1 Sol 缓存定价文档。**动作**：mac 用户必升，其他随意。

**codex rust-v0.161.0-alpha.7/8（10-01，一天两版）**：alpha 快节奏迭代期，无正文说明。**动作**：stable 用户不动，追新者自便。

**gemini-cli v0.64.0-nightly（10-01）**：修了 `@` 符号引发的 CPU 挂起和引号吞字；文件工具操作串行化+原子写入（并发写不再撕文件）。**动作**：nightly 用户升级；@ 文件引用重度用户必升。

## 方法论精选（这周最好的「方法」内容，均来自 aihot 精选）

**OpenRouter 连发五篇 agent 工程教程**，正好是一套完整的质量工程链条，和我们 L4 回归门设计逐条对得上：
1. CI 中用 LLM eval 门禁拦截 PR（通过率低于阈值→非零退出码）↔ 我们的 §4.3 发布回归门
2. 成本-质量选型三步框架（按「最低成本达到质量门槛」选，不按排行榜）↔ 我们的分层用模纪律
3. 置信度分级路由（便宜模型自报置信度，低置信升级强模型）↔ 可直接抄进 asp 的模型推荐档位逻辑
4. 从生产流量构建 golden 评测集（五步：抽样→去重→…）↔ 我们的 gold-selection 体系
5. prompt/模型变更后的回归测试（锁定用例集+书面行为契约）↔ 同 1

另外：Sarvam AI 的 25 分钟 agent 第一性原理入门（「agent = 循环里调用工具的 LLM；技能、记忆、领域知识本质上都是上下文工程」）——给新人解释我们在做什么的最好素材。

## 值得观察的产品动态

- **ChatGPT 可以直接构建并部署 MCP 服务器**了（Sites 托管，可转插件安装）——MCP 生产消费闭环向普通用户开放，生态位信号
- **Factory Automations 正式开放**：Droid 按定时/事件（Slack、GitHub）自动执行工程工作流
- **Perplexity Computer 开放邮件委托**（computer@perplexity…转发即任务，限时免费）
- **Modal Clusters GA**：一个 `@modal.clustered` 装饰器拿到多节点 GPU 集群——训练/推理弹性算力的新姿势

## 本周判断

1. **模型档位生命周期缩短到「周」级**（GPT-6 Sol 仅活 7 天）——「每月核对价目」不够了，价目表核对本身就是周报的常设动作。
2. **技能生态出现品类级爆发**（视频创作 5 项目 2600+ 星）——skills.sh/市场上架的流量判断再次被验证；我们 W1 上架动作宜早不宜晚。
3. **质量工程方法论正在标准化**（OpenRouter 五篇 = 业界共识正在形成）——我们的回归门/gold 体系方向正确，且现在有公开参考实现可对标。

---
**方法说明（v2 vs v1r）**：v1r 用临时检索（gh search 单查询 + 网页搜索），信息量与稳定性不足。v2 起回到 **AIHOT 底座**：aihot.news API v1 精选流（40 条/周，天然去重+评分）为主通道，GitHub 三路检索补充新星，harness 逐家拉发版正文。这也是 Domain Pack 信源配置的首次实跑验证——支柱一/方法论/产品动态条目全部来自 aihot 精选。信源：aihot.news `/api/v1/items`（精选 7 天）、GitHub Search/Releases API。本报告为 A0 S5 盲评素材（v2）。
