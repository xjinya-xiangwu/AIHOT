# planning/ — 产品规划与试验记录

本目录存放 AIHOT fork 的产品化路线文档，属于本 fork 自有新增目录（不改动上游代码，保持与上游 KKKKhazix/AIHOT 可合并）。**本目录是 SIAE 总项目的规划单一事实源**；SIAE 总控仓库（github.com/xjinya-xiangwu/SIAE）只是总览快照。

## 文件

| 文件 | 说明 |
|---|---|
| product-plan-v1.4.md | 《Agent环境 · 产品规划 v1.4》——定位与价值链 / 五层架构 / 数据边界 P0 / GAP 模块 v0 设计 / 现有资产整合地图（§5，含外部组件选型 §5.1）/ 商业化 / 路线图 go-no-go / 决策记录 D1-D14 |
| sync-plane-design.md | **跨端同步底座设计 v0**（D14）——Agent-sync 并入 SIAE 的顶层设计：凭证加密同步（age 信封加密）+ MCP 能力快速拉齐 + 与 asp 的字段级分工契约 |
| agent-env-architecture.drawio | 五层架构图源文件（可用 app.diagrams.net 打开编辑） |
| A0-protocol.md | Phase A0 最小闭环试验协议（盲评前后对照 + 付费意向验证） |
| L0-content-strategy.md | L0 内容策略 v1.1（三支柱 + 产品化 IA） |
| domain-pack/ | AI Domain Pack 初稿 v0.1（taxonomy / sources / gold seed） |

## 边界与合规

- 本目录只放规划与方法文档；**任何私人素材（健康信息、在职机构材料、原始对话/记忆）不得进入本仓库**——数据分层规则见 product-plan §4.0。
- 仓库公开，商业假设数据仅供参考，不代表已验证的需求证据。
- 上游规则继续适用：不提交 .env / 密钥 / .data/；不使用 AIHOT 名称与 Logo 作自有品牌。

## 相关仓库

- SIAE 总控（本项目的顶层视图与子模块挂载点）：https://github.com/xjinya-xiangwu/SIAE
- AI-cold-start（L1 技能包 + L3a 分发器，asp 安装器/周更器）：https://github.com/xjinya-xiangwu/AI-cold-start
- Agent-sync（L3b 跨端同步底座，D14 并入；私有）：https://github.com/xjinya-xiangwu/Agent-sync
