# planning/ — 产品规划与试验记录

本目录存放 AIHOT fork 的产品化路线文档，属于本 fork 自有新增目录（不改动上游代码，保持与上游 KKKKhazix/AIHOT 可合并）。

## 文件

| 文件 | 说明 |
|---|---|
| product-plan-v1.1.md | 《Agent环境 · 产品规划 v1.1》——把本框架作为「领域情报传感器」接入五层 Agent 环境架构的总规划（含数据准入矩阵、GAP 模块 v0 设计、路线图 go/no-go） |
| agent-env-architecture.drawio | 五层架构图源文件（可用 app.diagrams.net 打开编辑） |
| A0-protocol.md | Phase A0 最小闭环试验协议（盲评前后对照 + 付费意向验证） |

## 边界与合规

- 本目录只放规划与方法文档；**任何私人素材（健康信息、在职机构材料、原始对话/记忆）不得进入本仓库**——数据分层规则见 product-plan-v1.1.md §4.0。
- 仓库公开，商业假设数据仅供参考，不代表已验证的需求证据。
- 上游规则继续适用：不提交 .env / 密钥 / .data/；不使用 AIHOT 名称与 Logo 作自有品牌。

## 相关仓库

- AI-cold-start（asp 安装器/技能包，未来 Domain Pack 分发渠道）：https://github.com/xjinya-xiangwu/AI-cold-start
