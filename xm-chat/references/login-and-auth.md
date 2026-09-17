# 登录、登出、Profile 与 E2E 密钥管理

涵盖 `xm chat login`、`logout`、`status`、`config`、`profile`/`profiles`、`e2e` 全部子命令、多 device（`--device`）、环境变量非交互登录、E2E 密钥恢复与跨设备验证。

## 登录（login）

### 基本模式

```bash
xm chat status                       # 查看登录状态
xm chat status --verify              # 含 token 有效性校验
xm chat login                        # 弹出浏览器窗口输入用户名 + 密码（默认安全模式）
xm chat login alice                  # 指定用户名，浏览器输入密码
xm chat login -i=false               # 终端模式输入密码（不弹出浏览器）
xm chat login --token "syt_xxx"      # 直接注入 token，跳过密码
xm chat login --force                # 强制重登（覆盖旧 token）
xm chat login --e2e                  # 登录后初始化 Olm/Megolm 设备密钥
```

从 v1.3 起，`-i`（浏览器交互式输入）默认启用。密码不再经过终端回显，避免泄露到 shell history。如需恢复旧版终端输入：`-i=false`。

### 环境变量（非交互 / CI）

v1.8.24 起支持 `XM_CHAT_*` 系列环境变量。优先级：**flag / arg > env > 交互提示**。

| 变量 | 用途 |
|---|---|
| `XM_CHAT_USERNAME` | 用户名（无 positional arg 时使用） |
| `XM_CHAT_PASSWORD` | 密码（设了则跳过浏览器/终端输入） |
| `XM_CHAT_TOKEN` | access_token（等价于 `--token`，跳过密码登录） |

```bash
# 非交互密码登录（CI 友好）
XM_CHAT_USERNAME=alice XM_CHAT_PASSWORD=secret xm chat login

# 通过 env 注入 token
export XM_CHAT_TOKEN="syt_xxx"
xm chat login   # 自动用 $XM_CHAT_TOKEN，等价 --token "$XM_CHAT_TOKEN"

# 凭据不出 argv → 不进 shell history
# 配合 secret manager（vault / SOPS / CI secret store）使用更安全
```

**典型 CI 流水线**：

```bash
# vault 拿凭据 → 环境变量 → 登录
USERNAME=$(vault kv get -field=username secret/matrix/ci)
PASSWORD=$(vault kv get -field=password secret/matrix/ci)
XM_CHAT_USERNAME="$USERNAME" XM_CHAT_PASSWORD="$PASSWORD" xm chat login --e2e
```

用户名必须非空（无 positional arg 且 `XM_CHAT_USERNAME` 也未设会报错退出）。

### E2E 设备初始化

加密房间必须先初始化设备密钥：

```bash
xm chat login --e2e                            # 新设备首次登录直接启用
xm chat login --e2e --force                    # 已有 token 也强制重建
```

未启用 E2E 时加入加密房间会立即报错。

## 登出（logout）

```bash
xm chat logout                                   # 清除 default device 凭据
xm chat logout --device alice                    # 精准清除指定 device
```

无 `--device` 时清 default；多 device 场景必须显式 `--device` 避免误清其他。

## 多 device（v1.8.19+）

每个 daemon session 可绑定独立的真实 Matrix device —— 独立 `device_id` + `access_token` + 独立 crypto store 文件。**根因是 `persona AB-anye-035` 暴露的多 daemon 抢同一 device 导致 sync 游标 / OTK 冲突**。

### 多 device 登录

```bash
xm chat login                       # 默认设备（保留兼容：顶层 token + sessions.default）
xm chat login --device alice        # 独立 device alice（写 sessions.alice）
xm chat login --device bob --e2e    # bob 设备并初始化加密
xm chat login --device charlie --force   # charlie 设备强制重建
```

**硬约束**：`--device` 默认值是 `default`，无 flag 时所有行为保持单 device 兼容。

### 多 device daemon 并存

每个 session 自动绑定独立 daemon：

```bash
xm chat serve --id alice start      # alice daemon → alice device
xm chat serve --id bob start        # bob daemon → bob device
xm chat serve --list                # 列出所有 daemon session
```

不同 device 持有独立：
- `device_id` / `access_token`
- sync 游标（since token）
- OTK（one-time keys）
- crypto store 文件（`~/.xm/chat/store/<user>/<device>.db`）

→ 多个 daemon 并存互不冲突（不再因 sync 互踩）。

### 多 device 的 E2E / profile / logout

```bash
xm chat e2e status --device alice               # 操作 alice 的 crypto store
xm chat e2e restore --device alice --key "$K"   # 给 alice 恢复备份
xm chat profile --device alice --name "Phone"   # 设 alice 的 display name
xm chat logout --device alice                   # 清 alice（不动 bob）
```

无 `--device` 时操作 default。

### 验证流程（新 device 必走）

新 device 登录后服务端信任但**未交叉验证**，在加密房间看不到他人消息直到 SAS 完成：

```bash
# 在 alice 设备发起验证请求
xm chat e2e verify @<bob_user>:<server>

# 在 bob 设备确认
xm chat e2e confirm

# 流程：两端展示 7 个 emoji → 用户比对 → 都确认 → cross-sign 完成
# 旧路径等价：`xm chat serve --id alice trigger e2e-verify-start/confirm`（兼容）
```

`e2e verify` 与 `e2e confirm` 默认绑定 `--device default`；多 device 场景加 `--device <name>` 指定。

### 旧 config 兼容

无 `matrix.sessions` 字段的旧 `~/.xm/config.yaml` 自动透明回退：
- `EffectiveDevice("default")` → 顶层 `DeviceID/AccessToken`
- 所有命令行为不变
- 配置文件权限保持 600

## Profiles（多账号 / 多 homeserver）

`profiles` 子命令管理 `~/.xm/chat/profiles/<name>.yaml` 中的独立配置：

```bash
xm chat profiles list                              # 列出所有 profile
xm chat profiles add team-a                        # 交互式新增
xm chat profiles show team-a                       # 查详情（token 脱敏）
xm chat profiles rm team-a                         # 删除

# 使用方式一：--profile flag
xm chat --profile team-a status

# 使用方式二：XM_PROFILE 环境变量
XM_PROFILE=team-b xm chat send "#dev" "hi"
```

每个 profile 是独立 YAML（独立 homeserver + 凭据），与 `~/.xm/config.yaml` 隔离。

`XM_PROFILE` 与 `--profile` 等价，flag 优先。

## 配置管理（config）

```bash
xm chat config                                          # 查看全部（token 脱敏）
xm chat config --homeserver "https://matrix.example.com"  # 设置 homeserver URL
xm chat config --server-name "example.com"               # 设置 server name
```

配置文件：

| 路径 | 用途 |
|---|---|
| `~/.xm/config.yaml` | 默认配置 |
| `~/.xm/chat/profiles/<name>.yaml` | profile 隔离配置 |
| `~/.xm/chat/store/<user>/<device>.db` | crypto store（按 device 分文件） |
| `~/.xm/chat/personas/<name>.yaml` | persona 配置 |
| `~/.xm/chat/personas/<name>.sessions.json` | persona ACP session 绑定 |

权限保持 0600。

## E2E 密钥管理（e2e 子命令）

`xm chat e2e` 管理端到端加密的设备密钥、密钥备份、设备验证、跨设备迁移。

```
xm chat e2e
├── status       设备密钥信息 + 服务器备份状态
├── restore      从服务器备份恢复房间密钥（需要 recovery key）
├── verify       与另一设备做 SAS emoji 验证
├── confirm      确认正在进行的设备验证
├── export       导出 E2E 数据库到文件
├── import       从文件导入 E2E 数据库
└── reset        重置损坏的 E2E 设备身份
```

### status

```bash
xm chat e2e status                    # 设备指纹 + 备份版本/状态
xm chat e2e status --device alice     # 指定 device
xm chat e2e status --json             # JSON 输出（脚本消费）
```

输出包含：
- `device_id` / `fingerprint`（7 个 emoji 序列，给 SAS 比对）
- `backup_version` / `backup_enabled`（服务端密钥备份状态）
- `cross_signing`（交叉签名状态）

### restore（新 device / 重置后）

```bash
# 交互模式（浏览器输入 recovery key）
xm chat e2e restore

# 命令行传 key
xm chat e2e restore --key "EsTu xxx yyy zzz"

# CI / 脚本化：env 变量（v1.8.24+）
XM_CHAT_RECOVERY_KEY="EsTu xxx yyy zzz" xm chat e2e restore

# 终端交互（不弹浏览器）
xm chat e2e restore -i=false --key "$KEY"

# 配合多 device
xm chat e2e restore --device alice --key "$KEY"
```

输入模式优先级：**`--key` flag > `$XM_CHAT_RECOVERY_KEY` env > `-i=true` 浏览器 > `-i=false` 终端**。

恢复完成后即可解密服务器备份的历史 Megolm 消息。

### verify / confirm（设备间 SAS 验证）

```bash
# alice 发起验证 @bob（两端都会看到 7 个 emoji）
xm chat e2e verify @bob:server --session alice

# 用户肉眼比对 emoji 一致 → alice 端确认
xm chat e2e confirm --session alice
```

emoji 完全一致时两端 cross-sign 完成，可看到对方加密房间历史。

### export / import（跨设备迁移）

```bash
xm chat e2e export /tmp/alice-e2e.db        # 导出当前 device 的 E2E 数据库
xm chat e2e import /tmp/alice-e2e.db        # 在另一台机器导入
xm chat e2e import /tmp/alice-e2e.db --force   # 跳过确认（脚本化）
```

E2E 数据库含设备密钥 + Megolm session。export → import 是"无服务器密钥备份时的替代方案"。

### reset（损坏的设备身份）

```bash
xm chat e2e reset --force --session default   # 强制重置 default device 的 E2E
xm chat e2e reset --force --session alice     # 指定 device
```

⚠️ reset 后**该 device 的所有 Megolm session 失效**，加密房间对其他人可见但自己看不到历史（必须重新 SAS + key share，或从备份 restore）。这是设备身份不可逆变更的代价。

## 完整命令参考

```bash
xm chat login [username] [--token T] [--e2e] [--force] [--device NAME] [-i=true]
xm chat logout [--device NAME]
xm chat status [--verify] [--json]
xm chat config [--homeserver URL] [--server-name NAME]
xm chat profiles {list|add|rm|show}
xm chat e2e status [--device NAME] [--json]
xm chat e2e restore [--key K] [--device NAME] [-i=true]
xm chat e2e verify [user] [--session NAME] [--device NAME]
xm chat e2e confirm [--session NAME] [--device NAME]
xm chat e2e export [path] [--device NAME]
xm chat e2e import <path> [--force] [--device NAME]
xm chat e2e reset [--force] [--session NAME] [--device NAME]
```

完整 flag 见 `xm chat <subcommand> --help`。