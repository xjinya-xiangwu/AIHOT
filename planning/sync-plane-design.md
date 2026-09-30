# 跨端同步底座设计（Sync Plane）v0 —— Agent-sync 并入 SIAE

> 决策号：D14（2026-10-01，已定）。本文档是 Agent-sync 并入 SIAE 后的顶层设计，**单一事实源**；各仓库 README 只放总览快照。
> 上游仓库：[xjinya-xiangwu/Agent-sync](https://github.com/xjinya-xiangwu/Agent-sync)（并入后转私有）。

## §0 背景与决策（D14）

Agent-sync 原是个人自用的跨端环境同步仓库（skills / 全局指令 / MCP 模板 / memory / workspace 文档，git 同步）。2026-09-30 新机恢复实测暴露两个结构性缺口：

1. **凭证同步靠手填**——模板占位符 + 人工从密码管理器粘贴，跨端恢复时凭证环节最慢、最易错，且曾发生 token 进对话的泄露（见 §8）；
2. **MCP 拉齐靠散装脚本**——canonical 注册表（`mcp/mcp-servers.json`）与翻译规则（`FORMATS.md`）已具备，但"拉齐"动作没有产品化，与 asp 的 MCP merge 各写各的，存在双源漂移风险。

**D14：Agent-sync 并入 SIAE，定位为 L3 协同层的「跨端同步底座」**，两大重点职责：①跨端凭证**加密**安全同步；②各端各 agent 的 MCP 能力快速拉齐。既有职能（全局指令/skills/memory/workspace 同步）保留不变。

## §1 定位与分工边界（与 asp 的关系——顶层关键契约）

| | **asp（ai-cold-start）** | **agent-sync** |
|---|---|---|
| 一句话 | **分发器**：装什么、装到哪 | **同步底座**：值怎么安全跨端 |
| 服务对象 | 客户（商品化，匿名品牌） | 专家本人 / 团队（自用优先） |
| MCP 职责 | 写**结构**：merge 服务器条目进各端配置（只增不覆盖，token 留占位符） | 填**值**：加密拉取凭证 → 解密填充 → 连通校验 |
| 凭证纪律 | 安装器**永不收集 key**（现状承诺，不变） | 凭证加密同步的唯一通道，明文永不入库/入对话 |
| 部署对象 | skills / AGENTS.md / prompts / MCP 结构 | credentials（加密）/ MCP 值 / 全局指令 / memory / workspace |

**咬合契约**：agent-sync 的填值动作发生在 asp 部署**之后**（asp 保证结构存在且占位符就位）；agent-sync 只填 asp 留下的占位符，不增删服务器条目。两边对同一配置文件都遵循"只增不覆盖 + 备份可回滚"纪律，字段级互斥（结构/值），不会打架。

**与 ONBOARDING-V2 W2 的关系**：agent-sync 是 W2「凭据钱包 + Doctor 体检」的**跨端通道实现**——钱包 = 本地 `credentials/` 加密库；Doctor = 解密后对各 MCP 端点做连通性体检（复用 2026-09-30 四服务验证的方法：凭据验证 + 端点握手两层）。

## §2 架构归属

```
L3 协同层
├── L3a 分发（asp）：skills / AGENTS.md / MCP 结构 → 各 agent     〔已有，商品化〕
└── L3b 同步（agent-sync）：凭证加密同步 · MCP 值拉齐 · 指令/memory/workspace 跨端一致 〔本设计〕
```

SIAE 仓库结构增加第三个子模块 `agent-sync/`（指针，内容在上游仓库）。进化闭环中 agent-sync 承担：**多端使用产生的偏好/记忆/凭证变更跨端一致**——任何一端的变更经 push 汇入，其余端 pull 拉齐，L2 沉淀不因换机器断档。

## §3 职责一：跨端凭证加密同步

### 3.1 威胁模型

- **仓库端点不可信**（GitHub、未来任何远端）：密文入库可接受（信封加密，公钥加密）；明文入库不可接受。
- **设备端可信**（专家本人机器）：解密只发生在设备内存/本地配置，不落日志、不进对话（沿用 Agent-sync AGENTS.md 硬性规则）。
- **对话通道不可信**：agent 协作时凭证不进上下文；agent 只执行"解密→填充→校验"，不回显值。
- **git 历史永久性**：一旦明文入库即视为泄露（历史删不掉）→ 预防为主，事件响应=轮换。

### 3.2 分区设计（仓库内）

```
credentials/
├── README.md              # 本分区纪律（先读）
├── recipients.txt         # age 公钥（可入库）
├── inventory.md           # 凭证清单：名称/用途/所在配置/过期时间——只记元数据，永无值
├── *.enc                  # age 加密的凭证文件（v0：按服务一文件，如 github-mcp.enc）
└── *.enc.sha256           # 完整性校验
```

- **私人层 P（SIAE §4.0）永不进入本分区**：健康信息、原始 memory、敏感偏好不在此同步范围。
- `inventory.md` 是审计入口：每条凭证记"在哪用、何时轮换"，不记值。

### 3.3 加密方案

- **v0（首发）：[age](https://github.com/FiloSottile/age)（X25519）**。理由：单文件二进制零依赖（契合 asp/agent-sync 零依赖传统）、现代加密、公钥模型简单；Windows/mac/Linux 全覆盖。
  - `agent-sync push`：检测 `credentials/*.dec`（本地明文暂存区，gitignore）→ age 加密 → 写 `*.enc` + sha256 → commit push → 删除暂存。
  - `agent-sync pull`：拉取 → 校验 sha256 → age 解密到暂存 → 按 `FORMATS.md`/各模板的占位符填充各端配置 → 暂存清除。
  - 私钥**永不入库**：新设备初始化用一次性渠道（当面/密码管理器安全笔记/分两段传输），`recipients.txt` 只放公钥。
- **v1 演进：SOPS + age**（按文件字段级加密、diff 友好、CI 可读密文）——当凭证条目 >10 或需要自动化时引入。
- **否决案**：git-crypt（Windows 支持差 + 历史明文风险）；DPAPI（Windows 绑定，违背跨端目标）；纯环境变量约定（无静态加密，误提交风险高）。

### 3.4 与 asp 填值契约（落地形态）

`sync.ps1` 新增子命令（保持零依赖 PowerShell 传统）：

```
sync.ps1 push            # 现有：收集 memory/workspace 回仓库
sync.ps1 pull            # 现有：git pull + install.ps1
sync.ps1 seal            # 凭证暂存 → age 加密封存 → push
sync.ps1 open            # 拉取 → 解密 → 占位符填充到各端配置（结构由 asp 先行部署）
sync.ps1 doctor          # 连通性体检：对已填凭证逐服务做"凭据验证+端点握手"（复用 2026-09-30 四服务验证法）
```

### 3.5 立即修复项（先于一切新功能）

- `zcode/cli.config.template.json` 中 baidu-pan 的 Authorization 值残留真实 token 尾巴（`_nIqKjdoW3J6Dyl9C8.KDd6KQ`）——已随本设计入库修复为纯占位符；**该尾巴已随公开仓库暴露，对应旧 token 建议轮换**（当前生效 token 与尾巴不匹配，但同源轮换更稳妥）。
- Agent-sync 仓库转回**私有**（含 workspace 业务文档与个人 memory，公开状态与 §4.0 数据边界冲突）。

## §4 职责二：MCP 能力快速拉齐

### 4.1 现状资产（直接复用）

- `mcp/mcp-servers.json`：canonical 注册表（唯一事实源，含 optional 标记）——保持不变。
- `mcp/FORMATS.md`：8 类 agent 的配置位置/格式差异/翻译规则（含 opencode command 数组、VS Code servers 键名等实测坑）——保持不变。
- `setup-mcp.ps1`：已能生成 cursor/vscode/opencode/claude 四端配置。

### 4.2 拉齐闭环（v0 目标形态）

```
canonical registry ──setup-mcp──▶ 各端配置结构（占位符）
        │                              ▲
        └── credentials/*.enc ──open──▶ 值填充（sync.ps1 open）
                                       ▼
                                  sync.ps1 doctor（端点握手验证）
```

- **扩 targets**：setup-mcp 在 v0 内补齐 zcode / codex（toml）/ workbuddy 三端生成（workbuddy 与 cursor 同构；格式规则已在 FORMATS.md），达成 **8 端一条命令拉齐**。
- **与 asp 的关系再强调**：asp 新机器装包时已写入 MCP 结构（它有 adapter 矩阵）；agent-sync 的 `open` 只做值填充。若某端 asp 未覆盖，`setup-mcp` 直接生成结构也兼容——两边都以 canonical registry 为源，无双源问题。
- **Doctor 报告格式**：每服务一行 `PASS/FAIL/WARN` + 端点状态码 + 过期提醒（凭 inventory 的过期时间）。

## §5 既有职能（保留不变）

全局指令分发（global/AGENTS.md → 5 端）、skills junction、ZCode/Codex memory、workspace 文档同步——全部按原 AGENTS.md 纪律运行。唯一变更：`projects/workspace-default` 的同步范围**须过 SIAE §4.0 数据边界**（工作层 W 可同步；商品层 C 候选不自动入；私人层 P 禁止），sync.ps1 push 前人工过目。

## §6 里程碑

| 里程碑 | 内容 | 规模 | 状态 |
|---|---|---|---|
| **M-S1 仓库转型** | 定位重写（本设计）、模板去密钥残留、转私有、AGENTS.md 增补 SIAE 上下文 | 0.5 天 | ✅ 2026-10-01 |
| **M-S2 加密同步 v0** | age 集成、credentials/ 分区、seal/open 命令、两台真机互测 | 3-5 天 | 待排 |
| **M-S3 MCP 拉齐** | setup-mcp 扩 8 端 + open 填值 + doctor 体检，真机全端验证 | 1 周 | 待排 |
| **M-S4 接入主线** | 与 ONBOARDING-V2 W2 凭据钱包联通（agent-sync 为其跨端通道）；A0 过线后进 asp 正式排期 | 随 W2 | 待排 |

## §7 风险与对策

| 风险 | 对策 |
|---|---|
| 私钥丢失 = 全部凭证锁死 | recipients.txt 支持多公钥（主+备设备）；私钥安全备份在密码管理器（加密笔记），不落裸文件 |
| 解密后明文暂存残留 | seal/open 后立即删除暂存 + gitignore 兜底 + doctor 校验后清理 |
| asp 与 agent-sync 同时写同一配置 | 字段级互斥契约（结构/值）+ 双方都只增不覆盖 + doctor 报告暴露冲突 |
| 仓库历史混入明文（既往或未来） | M-S1 起仓库私有；历史审计一次；一旦发现即轮换该凭证 |
| age 依赖分发 | 随 agent-sync 发对应平台二进制校验和；或首次使用引导下载（签名核对） |

## §8 安全事件记录

- **2026-09-30**：发现 `zcode/cli.config.template.json` 的 baidu-pan Authorization 值内嵌真实 token 尾巴（约 20 字符后缀），随仓库公开状态暴露。处置：模板修复为纯占位符（随 M-S1 入库）；旧 token 建议轮换（当前生效 token 与该尾巴不匹配，风险降级为"同源谨慎"）。教训入 AGENTS.md 硬性规则：**模板只允许完整占位符，禁止任何真实片段"以便对照"**。
