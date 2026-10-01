# 周报管线生成版（internal）v5

> 生成：2026-10-01 17:38 ｜ 管线：run-weekly-pipeline.py（keywords.json v1 + 规则评分；LLM 写作位见 AGENT-COMPOSE 区块）｜ 输入 40 条 → 精选 20 / 否决 20

## 模型与算力（动作出口：换模型 / 迁算力 / 改价目，14 条）

- **Arena 开放限时测试 Claude Sonnet 5.5，Direct Mode 可用 48 小时**（24 分｜核对价目表/评估换档（P1））
  - 摘要：Arena 宣布在 Direct Mode 限时开放 Anthropic 的 Claude Sonnet 5.5（High），截止 10 月 2 日上午 8 点（太平洋时间），之后仍可在 Battle
  - `AGENT-COMPOSE`：〔含义/动作一句话 + 分级 A/B/C + 落点组件——agent 会话填充〕
  - 五维：动作5 成本5 时效5 适用4 可信5｜https://aihot.news
- **OpenAI DevDay 2026 发布 Dots、GPT-6.1 Sol、500美元订阅等一揽子更新**（22 分｜核对价目表/评估换档（P1））
  - 摘要：作者总结OpenAI DevDay 2026的发布：个人Agent产品Dots向ChatGPT Pro、Business Premium和Enterprise用户推出，支持4000多个应用协作；新模型
  - `AGENT-COMPOSE`：〔含义/动作一句话 + 分级 A/B/C + 落点组件——agent 会话填充〕
  - 五维：动作5 成本5 时效4 适用3 可信5｜https://aihot.news
- **OpenRouter 发布 Agent 模型成本与质量权衡选型框架**（20 分｜核对价目表/评估换档（P1））
  - 摘要：OpenRouter 发布一个三步框架，用于为 Agent 任务选出以最低成本达到质量门槛的模型，而不是按排行榜排名选最高分模型。方法是先按任务设定质量门槛，再用 20 到 50 条自己的示例运行廉价
  - `AGENT-COMPOSE`：〔含义/动作一句话 + 分级 A/B/C + 落点组件——agent 会话填充〕
  - 五维：动作5 成本3 时效4 适用3 可信5｜https://aihot.news
- **Modal Clusters 正式发布，通过 @modal.clustered 提供多节点 GPU 集群**（19 分｜核对价目表/评估换档（P1））
  - 摘要：Modal 宣布 Modal Clusters 正式可用，通过一个装饰器 @modal.clustered 即可获得多节点集群，节点间经 InfiniBand verbs 通信可达 6.4 Tbps，
  - `AGENT-COMPOSE`：〔含义/动作一句话 + 分级 A/B/C + 落点组件——agent 会话填充〕
  - 五维：动作5 成本1 时效5 适用3 可信5｜https://aihot.news
- **Artificial Analysis：GPT-6.1 Sol 的 Cost per Task 较 GPT-6 Sol **（19 分｜核对价目表/评估换档（P1））
  - 摘要：Artificial Analysis 数据显示，GPT-6.1 Sol 的 Cost per Task 约 $0.72，比 GPT-6 Sol（$1.05）低约 30%，后者已约为 GPT-5.6 
  - `AGENT-COMPOSE`：〔含义/动作一句话 + 分级 A/B/C + 落点组件——agent 会话填充〕
  - 五维：动作4 成本5 时效3 适用3 可信4｜https://aihot.news
- **GPT-6.1 Sol (Max) 以 1759 分登上 Code Arena: WebDev 第 3 名**（19 分｜核对价目表/评估换档（P1））
  - 摘要：Arena 评测榜单显示，OpenAI 的 GPT-6.1 Sol (Max) 以 1759 分位列 Code Arena: WebDev 第 3 名，混合价格为 $8/MToken。相比 GPT-6
  - `AGENT-COMPOSE`：〔含义/动作一句话 + 分级 A/B/C + 落点组件——agent 会话填充〕
  - 五维：动作4 成本5 时效3 适用3 可信4｜https://aihot.news
- **ElevenLabs 完成 3 亿美元员工股份回购，估值升至 220 亿美元**（19 分｜核对价目表/评估换档（P1））
  - 摘要：ElevenLabs 完成 3 亿美元员工 tender offer，估值达 220 亿美元，是 2026 年 2 月 Series D 估值的两倍，由 Wellington 和 T. Rowe Pr
  - `AGENT-COMPOSE`：〔含义/动作一句话 + 分级 A/B/C + 落点组件——agent 会话填充〕
  - 五维：动作4 成本5 时效3 适用3 可信4｜https://aihot.news
- **Artificial Analysis 开源 AA-AgentPerf-Local，测试笔记本与工作站上本地 AI 智能**（19 分｜核对价目表/评估换档（P1））
  - 摘要：Artificial Analysis 发布开源工具 AA-AgentPerf-Local，通过重放 8 个真实智能体任务（168 轮、上下文增长至约 56K tokens）测试本地推理性能，并上线笔
  - `AGENT-COMPOSE`：〔含义/动作一句话 + 分级 A/B/C + 落点组件——agent 会话填充〕
  - 五维：动作5 成本1 时效4 适用4 可信5｜https://aihot.news
- **GamersNexus 分析内存厂商以长期协议锁定产能，消费级 RAM 与 SSD 价格一年大涨**（19 分｜核对价目表/评估换档（P1））
  - 摘要：GamersNexus 撰文指出，Micron、Samsung、SK Hynix 等内存厂商正以 3-5 年长期协议（LTA）把 50%-70% 产能分配给最大的 5-16 家客户，试图消除行业原有的
  - `AGENT-COMPOSE`：〔含义/动作一句话 + 分级 A/B/C + 落点组件——agent 会话填充〕
  - 五维：动作4 成本5 时效3 适用3 可信4｜https://aihot.news
- **蚂蚁百灵发布 Ling-3.1-flash，面向真实世界长任务升级**（18 分｜核对价目表/评估换档（P1））
  - 摘要：蚂蚁百灵推出 Ling-3.1-flash，总参数约 560B，每个 Token 激活约 25B，上下文窗口上限 1M，延续混合线性架构并提高线性 Attention 层比例（7 层 KDA 配 1 
  - `AGENT-COMPOSE`：〔含义/动作一句话 + 分级 A/B/C + 落点组件——agent 会话填充〕
  - 五维：动作5 成本1 时效4 适用3 可信5｜https://aihot.news
- **vLLM 分离式推理（Disaggregated Serving）实用指南**（18 分｜核对价目表/评估换档（P1））
  - 摘要：vLLM 官方博客发布分离式推理实用指南，讲解 vLLM v0.30.0 及以上版本中 prefill/decode 分离、无 GPU render 前端及两者组合的原理与运行方法。
  - `AGENT-COMPOSE`：〔含义/动作一句话 + 分级 A/B/C + 落点组件——agent 会话填充〕
  - 五维：动作5 成本1 时效4 适用3 可信5｜https://aihot.news
- **Sarvam AI 发布从第一性原理构建 AI 智能体的入门指南**（18 分｜核对价目表/评估换档（P1））
  - 摘要：Sarvam AI 发布 25 分钟长的智能体构建指南，核心观点是智能体就是在循环中运行、能调用工具的语言模型，而技能、记忆和领域知识本质上都是在合适时机把合适文本放进上下文窗口。指南围绕在线商店客服
  - `AGENT-COMPOSE`：〔含义/动作一句话 + 分级 A/B/C + 落点组件——agent 会话填充〕
  - 五维：动作5 成本1 时效4 适用3 可信5｜https://aihot.news
- **GPT-6.1 Sol 发布 7 天后接替 GPT-6 Sol，智能指数距 GPT-6 Astra 仅 1 分**（18 分｜核对价目表/评估换档（P1））
  - 摘要：OpenAI 发布 GPT-6.1 Sol，接替仅上线 7 天的 GPT-6 Sol，Artificial Analysis 智能指数比 GPT-6 Sol 高 4 分、比 GPT-6 Astra 低
  - `AGENT-COMPOSE`：〔含义/动作一句话 + 分级 A/B/C + 落点组件——agent 会话填充〕
  - 五维：动作5 成本1 时效4 适用3 可信5｜https://aihot.news
- **Gary Marcus 评论 OpenAI 在 Hugging Face 事件前数月已收到安全预警**（18 分｜核对价目表/评估换档（P1））
  - 摘要：Gary Marcus 转述纽约时报独家报道，指 OpenAI 两名员工在事件发生前数月以邮件警示高管，称最新模型测试期监控不足、安全防护不严，高管回应要求尽快推进发布，未增加安全协议。报道称 Ope
  - `AGENT-COMPOSE`：〔含义/动作一句话 + 分级 A/B/C + 落点组件——agent 会话填充〕
  - 五维：动作5 成本1 时效4 适用3 可信5｜https://aihot.news

## 方法与质量工程（动作出口：采纳为 SOP / 改评测体系，6 条）

- **OpenRouter 指南：用置信度阈值实现模型分级升级路由**（20 分｜SOP 候选（P4））
  - 摘要：OpenRouter 发布教程，讲解如何让廉价模型通过结构化输出返回 0 到 1 的置信度字段，低置信度的请求再升级到更强模型。文章强调置信分数只是自报、不是校准概率，应基于自己流量的分数段错误率排序
  - `AGENT-COMPOSE`：〔含义/动作一句话 + 分级 A/B/C + 落点组件——agent 会话填充〕
  - 五维：动作5 成本3 时效4 适用3 可信5｜https://aihot.news
- **OpenRouter 教程：如何从生产流量构建 golden 评测集并跨模型复测**（19 分｜SOP 候选（P4））
  - 摘要：OpenRouter 发布教程，讲解如何从生产流量构建 golden 评测集，作为每次部署前的回归测试。内容涵盖五步流程（抽样生产流量、去重聚类、添加预期输出、首轮评估修正 rubric、提交 Git
  - `AGENT-COMPOSE`：〔含义/动作一句话 + 分级 A/B/C + 落点组件——agent 会话填充〕
  - 五维：动作5 成本1 时效4 适用4 可信5｜https://aihot.news
- **OpenRouter 教程：如何在 CI 中用 LLM eval 门禁拦截 Pull Request**（18 分｜SOP 候选（P4））
  - 摘要：OpenRouter 发布教程，讲解如何用固定的 eval 集在 CI 中门禁 pull request，当通过率低于阈值时脚本以非零退出码阻止合并，做法与单元测试门禁一致。
  - `AGENT-COMPOSE`：〔含义/动作一句话 + 分级 A/B/C + 落点组件——agent 会话填充〕
  - 五维：动作5 成本1 时效4 适用3 可信5｜https://aihot.news
- **OpenRouter 教程：如何测试 AI Agent 的工具调用准确性**（18 分｜SOP 候选（P4））
  - 摘要：OpenRouter 发布教程，讲解如何测试 AI Agent 的工具调用准确性，将失败拆分为工具选择错误和参数错误两类分别测试。
  - `AGENT-COMPOSE`：〔含义/动作一句话 + 分级 A/B/C + 落点组件——agent 会话填充〕
  - 五维：动作5 成本1 时效4 适用3 可信5｜https://aihot.news
- **OpenRouter 教程：提示词或模型变更后如何对 AI Agent 做回归测试**（18 分｜SOP 候选（P4））
  - 摘要：OpenRouter 发布 AI Agent 回归测试教程：每次提示词、模型、工具定义或检索设置变更后，重跑锁定的用例集并对照书面行为契约检查。
  - `AGENT-COMPOSE`：〔含义/动作一句话 + 分级 A/B/C + 落点组件——agent 会话填充〕
  - 五维：动作5 成本1 时效4 适用3 可信5｜https://aihot.news
- **Jensen Huang 称行业领袖在白宫签署超级智能协定**（16 分｜SOP 候选（P4））
  - 摘要：多家行业公司的领袖在白宫签署 White House Accord on Super Intelligence，约定开发该技术的公司负有安全部署和担责的首要责任。协定要求四层控制：训练和部署期间的稳健
  - `AGENT-COMPOSE`：〔含义/动作一句话 + 分级 A/B/C + 落点组件——agent 会话填充〕
  - 五维：动作5 成本1 时效3 适用3 可信4｜https://aihot.news

## 否决清单（gold 负样本回流）

- [V5_score] ChatGPT 现可直接构建并部署 MCP 服务器 —— 总分 14<18(P2_skills_tools)
- [V0_unbucketed] Transluce 报告 AI 智能体以激进手段访问美加政府网站 —— 未命中任何关键词支柱
- [V4_ranking_only] Gemini 4 Argon (High) 登 Arena Agent Arena 第 8 名，净提 —— 命中 V4_ranking_only（纯排名无价格或能力增量的 → 降权（并入相关条目…）
- [V0_unbucketed] Artificial Analysis 评测 Gemini 4 Argon：Google 重回智能前 —— 未命中任何关键词支柱
- [V0_unbucketed] Google DeepMind 发布 Gemini 4 Argon，面向可信网络防御者先行开放 —— 未命中任何关键词支柱
- [V0_unbucketed] METR 主席 Chris Painter 就 AI 智能体事件向美国参议院作证 —— 未命中任何关键词支柱
- [V0_unbucketed] Perplexity 开放 Computer 邮件委托入口并限时免费运行任务 —— 未命中任何关键词支柱
- [V3_offdomain_internal] Trump 推动二十余家科技公司签署自愿性 AI 安全协议 —— 命中 V3_offdomain_internal（（internal 人格）与 agent 使用无…）
- [V0_unbucketed] OpenAI 披露并处置一起有组织的模型蒸馏攻击行动 —— 未命中任何关键词支柱
- [V0_unbucketed] Factory Automations 正式开放：Droid 可定时或按事件自动执行工程工作流 —— 未命中任何关键词支柱
- [V3_offdomain_internal] Anthropic 研究测算机器人对岗位的暴露度：机器人可做 74% 的物理任务但仅 0.3% 具备 —— 命中 V3_offdomain_internal（（internal 人格）与 agent 使用无…）
- [V3_offdomain_internal] MIT 等机构发布 Ataraxos，以极低成本战胜顶级人类 Stratego 选手 —— 命中 V3_offdomain_internal（（internal 人格）与 agent 使用无…）
- [V3_offdomain_internal] Google DeepMind 发布 SynthID Bio，为 AI 生成的蛋白质嵌入可验证水印 —— 命中 V3_offdomain_internal（（internal 人格）与 agent 使用无…）
- [V0_unbucketed] FTC 以消费者保护为由对 OpenAI、Anthropic 等 AI 实验室启动全面调查 —— 未命中任何关键词支柱
- [V2_gossip] Hugging Face CEO 称收到数千条私信，将花几天逐一处理 —— 命中 V2_gossip（纯人物八卦/私人动态（如 CEO 私信、离职传闻…）
- [V5_score] PromptArmor 披露 Copilot Cowork AI 网关被劫持绕过沙箱外传文件漏洞 —— 总分 14<18(P2_skills_tools)
- [V5_score] DeepSeek 开源面向华为昇腾平台的基础设施组件 —— 总分 17<18(P1_model_compute)
- [V0_unbucketed] Anthropic 与 SpaceX 签署最高 845 亿美元算力协议，可提前 90 天通知解除 —— 未命中任何关键词支柱
- [V0_unbucketed] 纽约时报报道 OpenAI 在 AI 失控前已接到员工安全警告但被无视 —— 未命中任何关键词支柱
- [V0_unbucketed] OpenAI 据报道洽谈以约 1.4 万亿美元估值融资至少 300 亿美元 —— 未命中任何关键词支柱

## 数据缺口
- 规则评分 v1 为近似（数字/时效词命中），LLM 精评位未启用；GitHub/harness 通道本轮未注入（fixtures 化后自动并桶）