# 跨端凭证加密同步 · 详细规格（M-S2 Spec）v1.0

> 隶属：[sync-plane-design.md](sync-plane-design.md) §3 的实施级规格（D14 / L3b）。
> 状态：设计定稿 2026-10-01；实施待排（M-S2，3-5 天，两台真机互测验收）。
> 读者：实现者（sync.ps1 改造）、任何执行 seal/open/doctor 的 agent（配合 Agent-sync 仓库 `AGENTS.md` 硬性规则）。

## §1 目标与非目标

**目标**

1. 一份加密源，多端消费：凭证加密封存于 Agent-sync 仓库 `credentials/`，任一设备 clone 后可解密填充到该机所有 agent 的原生配置（ZCode / Codex / Claude Code / Cursor / OpenCode / WorkBuddy / VS Code / DSH…，按 `mcp/FORMATS.md` 的落位表）。
2. 明文终点唯一：解密后的明文只出现在两个受控位置——**填充后的各 agent 本地配置文件**（这些文件本来就持有凭证明文，是各 agent 的运行要求）和 **seal 前的本地暂存区**（用后即删）。仓库、git 历史、对话、日志、memory 中永不出现明文。
3. 可验证：`doctor` 对每项凭证做「密文可解 → 占位符已填 → 端点握手成功 → 有效期充足」四层体检，输出 PASS/FAIL/WARN。
4. 可恢复：密钥丢失、单凭证泄漏、设备丢失三种事故各有明确 runbook，不依赖任何单点。

**非目标**

- 不防拥有本机管理员权限的攻击者（设备被攻破时凭证已在各 agent 配置明文存在，本方案不恶化也不解决该层；建议全盘加密，出范围）。
- 不做凭证自动注册/自动续期（baidu 30 天 OAuth 仍需人工走浏览器授权后重新 seal；方案只负责提醒与快速封存）。
- 不替代密码管理器（age 私钥本身托管在密码管理器里——密码管理器是根信任，本方案是它到 agent 配置的自动化分发通道）。

## §2 威胁模型与信任边界

| 对手/信道 | 能力假设 | 对策（本方案内） |
|---|---|---|
| 远端仓库（GitHub / 未来任意 git host） | 可读全部对象与全部历史 | 仓库内只有 age 密文（§4）；明文一旦入库即视为泄漏（§10 runbook） |
| git 历史 | 永久、不可靠删除 | 预防为主：push 前 lint 网关（§9.1）拦截已知 token 形态与高熵串 |
| 对话/agent 上下文 | 会被记录、可能被同步 | agent 只调用 seal/open/doctor，工具永不回显明文（§9.3）；AGENTS.md 硬性规则 |
| 本机非特权进程 | 可读用户目录 | 暂存区仅存于 seal→push / pull→fill 的窗口内，用后即删（§9.2）；私钥不明文落盘于仓库外固定路径（§3.4 推荐 B 级以上） |
| 拿到仓库副本但无私钥的攻击者 | 全量密文 | age X25519（现代 AEAD，ChaCha20-Poly1305）；密文可公开 |
| 拿到私钥但无仓库的攻击者 | 可解密 | 仓库私有化（M-S1 待用户手动项）；密钥与密文分离托管 |
| 伪端点校验（钓鱼） | 诱导 doctor 把凭证发到非属主端点 | 校验端点在 secrets-map.json 中**固定**为各服务官方域名，不可由命令行参数注入（§9.4） |

信任分级：**设备端可信**（解密发生地）、**远端与对话不可信**（只见密文/不见任何文）、**agent 半可信**（可执行填值，规则禁止读取回显）。

## §3 密钥体系

### 3.1 算法与工具

- [age](https://github.com/FiloSottile/age) v1.2+（BSD-3）：X25519 + ChaCha20-Poly1305，单二进制 `age.exe` / `age-keygen.exe`，无运行时依赖，符合 Agent-sync「零依赖 PowerShell」传统。
- 二进制随仓库分发：`credentials/bin/age.exe`、`age-keygen.exe` + `bin.sha256`（发布页校验和核对后入库）；mac/Linux 用同版本 `age` / `age-keygen`。

### 3.2 身份结构

```
主身份（每台工作设备各持一把）   age1xxx…  ↔  AGE-SECRET-KEY-1xxx…
备份身份（离线保存，passphrase 包裹）  age1yyy…  ↔  AGE-SECRET-KEY-1yyy…（外层再 age -p 加密）
```

- `recipients.txt`（入库）：注释行 + 每设备一行公钥 + 备份公钥。加密时 `age -R recipients.txt` 天然多收件人——**任何一把私钥可解，缺谁都不影响别人**。
- 设备只持有自己的私钥；备份私钥以 passphrase 加密形态存于密码管理器安全笔记（强口令）+ 纸质打印两份异地。**私钥永不入库、永不进对话、永不进 agent memory**。

### 3.3 密钥生命周期

| 事件 | 操作 | 密文影响 |
|---|---|---|
| 加设备 | 新设备 `keygen` → 公钥追加 recipients.txt → `sync.ps1 rotate-key`（全部 .enc 重加密到新收件人集） | 重写，无明文往返 |
| 弃用/失窃设备 | recipients.txt 删该行 → `rotate-key` → **该设备可触达的凭证全部轮换**（它本地有明文配置，仅踢密钥不解决） | 同上 |
| 私钥疑似泄漏 | 同「失窃设备」处理该身份 | 同上 |
| 备份口令遗忘 | 备份身份作废；新设备走「凭原生渠道重建凭证」路径（§7 恢复列），重建后重 seal | 部分凭证需重发 |

### 3.4 私钥落盘策略（分级）

| 级别 | 做法 | 适用 |
|---|---|---|
| A（推荐） | 私钥只在密码管理器安全笔记；seal/open 时释放到 `%TEMP%` 随机名文件，命令结束即删 | 低频操作（轮换/新机）完全够用 |
| B（可接受） | 私钥存 `~/.age/key.txt`，目录 ACL 仅本用户 | 每周频繁 open 的主力机 |
| 禁止 | 私钥放仓库、放同步盘、放对话、打印不带口令包裹的明文私钥 | — |

## §4 数据模型

### 4.1 目录（Agent-sync 仓库内）

```
credentials/
├── README.md               # 分区纪律（M-S1 已建）
├── recipients.txt          # age 公钥集（入库）
├── inventory.md            # 凭证台账：id/服务/目标端/有效期/last_rotated（入库，无值）
├── secrets-map.json        # ★ 占位符→目标映射 + 校验器声明（入库，无值）
├── github-mcp.enc          # 单服务单文件（dotenv 密文）
├── notion.enc
├── baidu-pan.enc
├── feishu-app.enc
├── codex-bearer.enc
├── files/                  # 整文件型 secret（非占位符模式）
│   └── lark-cli-config.json.enc
├── local/                  # ★ 本地暂存（gitignore，seal 输入源，用后即删）
└── bin/                    # age 二进制 + sha256
```

### 4.2 单凭证文件格式（.enc 内明文结构）

dotenv，UTF-8 无 BOM，PS 5.1 零依赖可解析：

```
# github-mcp.enc 解密后
GITHUB_MCP_PAT=github_pat_xxxx
```

一服务一文件的理由：轮换单项只重写单文件、git diff 粒度清晰、baidu 30 天周期不影响其他凭证。

### 4.3 secrets-map.json（核心映射，入库）

```json
{
  "$schema-note": "占位符→各端目标映射与校验器声明。占位符在 asp/模板侧先行部署；open 只做值替换。",
  "GITHUB_MCP_PAT": {
    "enc": "github-mcp.enc",
    "targets": [
      {"agent": "zcode",   "file": "~/.zcode/cli/config.json",        "placeholders": ["${GITHUB_MCP_PAT}"]},
      {"agent": "claude",  "file": "~/.claude.json",                  "placeholders": ["${GITHUB_MCP_PAT}"]},
      {"agent": "cursor",  "file": "~/.cursor/mcp.json",              "placeholders": ["${GITHUB_MCP_PAT}"]},
      {"agent": "opencode","file": "~/.config/opencode/opencode.json","placeholders": ["${GITHUB_MCP_PAT}"]},
      {"agent": "workbuddy","file": "~/.workbuddy/mcp.json",          "placeholders": ["${GITHUB_MCP_PAT}"]}
    ],
    "validate": {
      "type": "http",
      "request": {"method": "GET", "url": "https://api.github.com/user",
                   "headers": {"Authorization": "Bearer {value}"}},
      "pass": {"http": 200, "json_path": "login"}
    },
    "expires": null,
    "recovery": "GitHub → Settings → Developer settings → PAT 重新生成（fine-grained，仅必要仓库）"
  },
  "BAIDU_PAN_MCP_TOKEN": {
    "enc": "baidu-pan.enc",
    "targets": [
      {"agent": "zcode",   "file": "~/.zcode/cli/config.json", "placeholders": ["${BAIDU_PAN_MCP_TOKEN}"]},
      {"agent": "workbuddy","file": "~/.workbuddy/mcp.json",   "placeholders": ["${BAIDU_PAN_MCP_TOKEN}"]}
    ],
    "validate": {
      "type": "http",
      "request": {"method": "GET", "url": "https://pan.baidu.com/api/quota?access_token={value-urlenc}"},
      "pass": {"http": 200, "json_path": "errno", "json_equals": 0}
    },
    "expires": "30d-from-seal",
    "recovery": "openapi.baidu.com OAuth 授权页重新扫码（baidu-pan skill 记录流程）→ 本机 seal"
  }
}
```

（NOTION_TOKEN / FEISHU_APP_SECRET / CODEX_BEARER_TOKEN 同构；FEISHU 校验走 tenant_access_token 内部接口只验形状不落 token；整文件型见 §4.4。）

约束：**url 与 headers 里的域名是白名单常量**，命令行不可传入；`{value}` 只出现在请求构造时内存拼接，不落任何文件。

### 4.4 整文件型 secret

不适配占位符的凭据（lark-cli 的 `~/.lark-cli/config.json` 含 app_id+secret、lark-mcp 的 `credentials.env`）：整文件加密封存于 `files/*.enc`，`open` 解密后**带时间戳备份目标→覆盖写入**。此类目标不适用"只替换占位符"规则，备份是唯一回滚线。

### 4.5 inventory.md 模板

```markdown
| id | 服务 | 密文 | 有效期 | last_rotated | 备注 |
|---|---|---|---|---|---|
| github-mcp | GitHub PAT (MCP) | github-mcp.enc | 长期（建议 90d） | 2026-10-01 | fine-grained |
| baidu-pan | 百度网盘 OAuth | baidu-pan.enc | 30d | … | 每月轮换 |
| feishu-app | 飞书应用凭据 | feishu-app.enc | 长期 | … | OAuth 会话不同步（§8.1） |
```

seal 时自动更新 last_rotated（台账与密文同一 commit，永不记值）。

## §5 命令规格（sync.ps1 新增子命令）

### `sync.ps1 keygen`
生成年龄密钥对到 `credentials/local/`（gitignored），回显**公钥**与「追加 recipients.txt + rotate-key」提示。私钥按 §3.4 分级安置后从 local/ 删除。

### `sync.ps1 seal [-Only <id>[,<id>]]`
1. 读 `credentials/local/<id>.dec`（用户手放的明文暂存）；缺文件则逐项 `Read-Host -AsSecureString` 交互收取。
2. 校验值形状（如 github_pat_ 前缀、长度）——形状不符拒收，防放错文件。
3. `age -R recipients.txt` 加密 → 写 `<id>.enc` + `<id>.enc.sha256`；更新 inventory last_rotated / expires。
4. **立即删除 local/ 暂存**；打印（仅）id 与字节数。
5. 询问后 commit+push；push 前强制过 `lint`（§9.1）。

### `sync.ps1 open [-Agent <a,b>] [-Only <id>]`
1. `git pull --ff-only`；逐项 sha256 校验密文完整性。
2. 解密选中项到 `%TEMP%` 随机目录（仅限本次）。
3. 按占位符算法（§6）逐目标填充；整文件型走备份→覆盖。
4. 删除临时目录；输出报告：每 agent×每凭证 = filled / already / no-placeholder（该端未装或 asp 未部署结构）/ skipped（-Only 排除）。

### `sync.ps1 doctor [-All]`
四层体检，表格输出 + 退出码（FAIL=1）：

| 层 | 检查 | 失败示例 |
|---|---|---|
| L1 密文 | .enc 存在、sha256 一致、本机私钥可解 | 私钥缺失 → 提示 §3.4 |
| L2 落位 | 各目标文件中占位符已消失且值形状正确 | 某端未 open / asp 未部署结构 |
| L3 端点 | secrets-map.validate 对**官方域**握手 | token 失效 / 网络断 |
| L4 时效 | inventory expires 对比当日 | <7d WARN；过期 FAIL |

### `sync.ps1 rotate-key`
recipients.txt 变更后全部 .enc 重加密（解密走本机私钥→内存/临时→重加密→删临时）。设备增删的标准收尾动作。

### `sync.ps1 lint`（push 网关内建，也可单跑）
对 staged diff 与 credentials/local 之外的新增文件跑模式扫描（§9.1 清单）；命中即阻断 push 并输出文件:行。**这是 2026-09-30 模板残留事件的技术化防复发。**

## §6 占位符填充算法

```
for target in selected_targets(credential, agent 过滤):
    text = read(target.file)                     # 不存在 → 记 no-target（该端未装），跳过
    new  = text
    for ph in target.placeholders:
        if ph in new:  new = new.replace(ph, value)   # 仅替换字面占位符
    if new == text:
        if value_shape_present(text): 报 already      # 幂等：已是真值
        else: 报 no-placeholder                        # asp 未部署结构 → 提示先跑 asp install
        continue
    backup(target.file, "agent-id")                   # _backup/<agent>-<name>.<ts>.bak（asp 同约定）
    write_no_bom(new)                                  # PS5.1 BOM 坑：JSON 必须 WriteAllText(UTF8Encoding($false))
```

三条铁律：只替换占位符（用户自填的其他值永不动）；写前必备份；无变化不写。幂等：重复 open 结果恒为 already。

## §7 初始凭证登记表（随 M-S2 实施录入）

| id | 值 | 目标端 | 校验端点 | 有效期 | 原生恢复渠道 |
|---|---|---|---|---|---|
| github-mcp | GitHub PAT | zcode/claude/cursor/opencode/workbuddy | api.github.com/user | 建议自定 ≤90d | 重新生成 PAT |
| notion | Notion integration token | zcode（本地 MCP env）/ 未来各端 | api.notion.com/v1/users/me | 长期 | 重新生成 integration token |
| baidu-pan | OAuth access_token | zcode/workbuddy | pan.baidu.com/api/quota | **30d，硬周期** | 授权页重扫（skill 有流程） |
| feishu-app | App ID+Secret | files/lark-cli-config.json（整文件） | open-apis auth/v3 tenant_access_token（验形状） | 长期 | 开放平台重置 Secret |
| codex-bearer | CODEX_BEARER_TOKEN | codex/config.toml | （按 provider 配，可 null） | 按 provider | provider 控制台 |
| ~~feishu-oauth~~ | 用户 access/refresh token | **不同步** | — | — | 见 §8.1 |

## §8 特殊决策（记录理由，防将来误改）

### 8.1 飞书 OAuth 会话不跨端
lark-cli 的 user_access_token/refresh_token 绑定设备会话且刷新可能轮换失效，跨端搬运会出现两端互相踢。**只同步 app 凭据（feishu-app 整文件）**，新设备首次用 `lark-cli auth login` 走 device-flow 一次性授权（2026-09-30 已验证流程）。凭证同步解"配置就绪"，会话授权保持每设备独立。

### 8.2 baidu-pan 月度节奏
30 天硬过期是上游设计，无 refresh。节奏固化：doctor 在 <7d 时 WARN 提醒 → 到期重扫 → `seal -Only baidu-pan` → open。整链 <5 分钟。

### 8.3 .enc 冲突策略
密文二进制无法合并。规则：**轮换单写者**——某凭证的更新只在拿到新值的机器上做；seal 前 `git pull --ff-only`，冲突则保留对方版本、本机值重新 seal（凭证不是协作文本，后 seal 者胜，以 inventory last_rotated 判新旧）。

### 8.4 与 asp 的时序契约（重申）
新机标准顺序：`asp install`（结构+占位符就位）→ `agent-sync open`（填值）→ `doctor`。open 见到 no-placeholder 即回报"先装 asp"，不自行创建结构——结构职责唯一属于 asp（D14 字段级互斥）。

## §9 安全机制清单

### 9.1 lint 模式（可扩展数组）
`github_pat_[A-Za-z0-9_]{20,}`、`ghp_[A-Za-z0-9]{30,}`、`ntn_[A-Za-z0-9]{25,}`、`121\.[0-9a-f]{30,}\.[A-Za-z0-9.]{20,}`（baidu）、`sk-[A-Za-z0-9]{20,}`、`AKIA[0-9A-Z]{16}`、`AGE-SECRET-KEY-1`、`BEGIN (RSA|EC|OPENSSH) PRIVATE KEY`、`Authorization:\s*Bearer\s+[A-Za-z0-9_\-\.]{30,}`、熵>4.5 的 ≥32 连续 base64 串（启发式，白名单豁免 .enc/.sha256/lock 文件）。

### 9.2 暂存清理
local/ 与 %TEMP% 解密目录：open/seal 正常与**异常**路径（try/finally）都执行删除；Windows 下尽力覆写一次（PS 5.1 无 shred，先写随机再删，已足够对付误恢复类威胁；防取证级恢复不在威胁模型内）。

### 9.3 工具与 agent 行为规则（写入 Agent-sync AGENTS.md，实施时同步）
任何 seal/open/doctor 的执行者（人或 agent）：不回显解密值、不把值写入 memory/日志/commit message、不复制到剪贴板、校验只发往 secrets-map 白名单域。工具自身所有输出只含 id/状态码/字节数。

### 9.4 端点白名单
validate 的 url 来自入库的 secrets-map.json 且实现里校验 host ∈ {api.github.com, pan.baidu.com, api.notion.com, open.feishu.cn}（常量集）；CLI 参数永远无法注入 url。

### 9.5 分层兜底汇总
明文暴露面 = 各 agent 配置文件（既有事实，各 agent 运行必需）＋ seal/open 的分钟级暂存窗口。其余一切位置（仓库/历史/对话/日志/memory/剪贴板）均有机制性阻断：加密（§3）、lint 网关（§9.1）、try-finally 清理（§9.2）、行为规则（§9.3）、白名单（§9.4）。

## §10 事件响应 runbook

**明文疑似入库**（lint 漏网/人工误提交）：① 立即在该服务原生渠道轮换该凭证（这是唯一有效动作，git 历史不指望抹除）；② 新值 seal；③ 事后补 lint 模式；④ 记入 sync-plane-design §8 事件记录。

**私钥泄漏**：按 §3.3「失窃设备」处理——踢收件人 + rotate-key + 全量凭证轮换。

**设备丢失**：同上；若设备有 FDE 则降级为评估后处理。

**密钥全灭**（私钥+备份全丢）：密码管理器若在则无损；否则逐凭证走 §7 恢复列原生渠道重建，重 seal（流程等同新机初始化，半天内完成）。

## §11 实施注记

- PS 5.1：JSON 读写显式 `-Encoding UTF8`；写配置 `WriteAllText + UTF8Encoding($false)`；age 调用 `& $ageBin -R ...`，路径含空格加引号；`%TEMP%` 随机目录 `[guid]::NewGuid()`。
- age 分发：`credentials/bin/`（.gitignore 排除 local/ 但保留 bin/），首次使用校验 `bin.sha256`。
- 零依赖红线不动：不引入 SOPS/Python；SOPS 评估留给 v1（>10 凭证或需 CI 读密文时）。
- doctor 输出机器可读态（`--json`）供未来 W2 流量灯复用。

## §12 测试计划（M-S2 验收）

| # | 场景 | 通过标准 |
|---|---|---|
| T1 | 机 A keygen+seal 全部 6 项+push | 仓库仅 .enc；lint 通过；local/ 已清 |
| T2 | 机 B clone+open+doctor | 5 端配置占位符全消；doctor 全 PASS；%TEMP% 无残留 |
| T3 | 幂等 | 连续两次 open → 全 already，零写入 |
| T4 | 不覆盖 | 预置用户自有同名 server/值 → open 后原样保留 |
| T5 | lint 演练 | 构造含假 github_pat_ 的 staged 文件 → push 被阻断 |
| T6 | 密钥演练 | 删机 B 私钥 → doctor L1 FAIL 且提示恢复路径；恢复后 PASS |
| T7 | baidu 轮换演练 | 假 token seal → doctor L3 FAIL → 重扫真值 seal → PASS |
| T8 | 冲突 | 双机改同一 .enc → pull 冲突 → 按 §8.3 收敛，inventory 判新旧 |

## §13 开放问题

1. CODEX_BEARER_TOKEN 的 provider 端点未定（用户 codex 未配置）——先 null，配时补 validate。
2. WorkBuddy 的 mcp.json 当前持有真实 PAT（2026-09-30 手工部署）——M-S2 实施时将其占位符化并纳入 seal 流程，属**存量明文收编**，验收含此项。
3. 未来 team 场景（多专家多收件人）下 inventory 审计流——v1 再议。
