---
name: xm-chat
description: "Use for any Matrix chat work via the `xm chat` CLI: messaging (text/markdown/emote/notice/reply/edit), files/stickers/locations, history, real-time listening, daemon sessions, ACP-based AI virtual personas (`xm chat persona`), E2E encryption keys, appservice virtual identities, profiles/presence, room members, and event-triggered commands with context injection, batching, and agent session continuity. Covers all `xm chat` subcommands, event filter config (prefix/domain/regex matching, room/sender exclusion, @mention detection), and bot development. Trigger on: chat, messaging, Matrix, IM, bot, daemon session, chat trigger, virtual user, virtual persona, AI persona, chatbot, DM, room members, trigger pipeline, agent mode, XM_AGENT_SESSION, Monitor mode, XM_CHAT_USERNAME, XM_CHAT_PASSWORD, XM_CHAT_TOKEN, multi-device login, file send, sticker, location, emote, edit message, event filter, prefix filter, domain filter, persona debugging, router check, event tracing, or any room-based communication task."
---

# xm-chat — Matrix 即时通讯 CLI 指南

## 概述

`xm chat` 是 `xm` CLI 的 Matrix 即时通讯子系统，提供终端内的消息收发、实时监听、持久守护进程、虚拟身份管理、E2E 密钥管理、事件触发命令等能力。

配置文件：`~/.xm/config.yaml`（可用 `--config` 指定路径，`--profile <name>` 切换到 `~/.xm/chat/profiles/<name>.yaml`）。

构建标签：项目使用 pure-Go Olm（`-tags goolm`，零 CGO）。所有 `go run` / `go build` 都必须带该标签，否则 `internal/matrix` 引用 `<olm/olm.h>` 失败。

## 子命令全景

```
xm chat <subcommand>

一次性操作        持久会话 (serve)         事件触发 (trigger)    身份与配置
─────────        ────────────────         ─────────────────    ─────────
login            serve --stdio            trigger --id <name>  config
logout           serve --id <name>        ├── list             profiles
status           ├── start                ├── kill             profile
e2e              ├── stop                 └── agent-reset      presence
e2e status       ├── restart              persona             appservice
e2e restore      ├── send/listen/typing   ├── create           ├── register
e2e verify       └── (全部动作经 socket)  ├── start/stop       ├── user-register
e2e export/import                          ├── edit/status/logs ├── user-deactivate
send            appservice                 ├── say/ask/allow   └── config
dm              user-register              ├── forget/del
	                                             ├── prompt edit/show
	                                             ├── check/ping/trace/watch
	                                             ├── explain/debug/open/agent-status
history         user-deactivate
rooms/listen/users/members
typing/join/upload/react/redact/edit
	search/context/download/notifications
	room/profile/presence/poll/widget
	profiles
	ban/kick/unban (room ban|kick|unban)
	account-data/pushrules         # Tier 2 additions
	pin/unpin/pinned (room pin|unpin|pinned)
	name/topic (room name|topic)
	power-levels (room power-levels)
	file/sticker/location
	emote (send --emote)
```

> 完整子命令清单与 flags 见 `xm chat <subcommand> --help`。常用参考见下方文档索引。

## 文档索引（按场景）

按用户意图路由到对应参考文件。每文件 < 500 行，专注于一类操作。

| 场景 | 参考 |
|---|---|
| 登录/登出、token、env 变量、多 device、profiles、`xm chat e2e` | [references/login-and-auth.md](references/login-and-auth.md) |
| 发消息/DM/历史/成员/上传/反应/撤回/房间管理/widget | [references/messaging.md](references/messaging.md) |
| listen 实时监听 + serve 守护进程 + stdio 模式 | [references/realtime.md](references/realtime.md) |
| trigger 事件触发命令 + agent 会话连续性 | [references/triggers.md](references/triggers.md) |
| persona AI 虚拟人（推荐，ACP 原生） | [references/persona.md](references/persona.md) |
| appservice 虚拟身份 + profile/presence | [references/virtual-identity.md](references/virtual-identity.md) |
| 旧式 claude --bg Monitor 编排（仍可用） | [references/monitor-mode.md](references/monitor-mode.md) |

## 启动流程（最小可运行）

```bash
# 1. 登录（默认走浏览器；env 变量或 --token 可走非交互）
xm chat login
# CI / 脚本化场景：
XM_CHAT_USERNAME=alice XM_CHAT_PASSWORD=secret xm chat login

# 2. 验证
xm chat status
xm chat rooms

# 3. 发消息 / 加监听
xm chat send "#dev:server" "build passed"
xm chat listen --json --skip-self --mentions-only
```

完整登录模式、env 变量、多 device、E2E 详见 [login-and-auth.md](references/login-and-auth.md)。

## 选型决策（核心岔路）

| 需求 | 推荐 | 说明 |
|---|---|---|
| 长跑 AI 虚拟人（多轮对话、人格一致） | `xm chat persona create` + `start` | 原生 ACP，自动持久 agent session，自带触发/队列/权限 |
| 一次性命令响应 / 上下文注入 / 跨进程编排 | `xm chat trigger --agent` | 每事件启动 agent 进程，适合 shell 命令 + LLM 一次性回复 |
| 持续监听外部 LLM orchestrator（claude --bg Monitor 等） | listen pipe + 自管进程 | 见 monitor-mode.md，persona 之前的旧方案 |
| E2E 加密房间 | `xm chat e2e restore` 恢复密钥备份 | 新 device 登录后必须 restore 才能看历史加密消息 |
| 虚拟身份（appservice puppet） | `xm chat appservice config` + `user-register` | 需要 homeserver 配 `app_service_config_files`，详见 virtual-identity.md |

## 凭据与环境变量速查

| 变量 | 用途 | 适用命令 |
|---|---|---|
| `XM_CHAT_USERNAME` | 登录用户名（无 positional arg 时） | `xm chat login` |
| `XM_CHAT_PASSWORD` | 跳过浏览器/终端密码输入 | `xm chat login` |
| `XM_CHAT_TOKEN` | access_token（替代 `--token`） | `xm chat login` |
| `XM_CHAT_RECOVERY_KEY` | E2E 密钥恢复 Security Key | `xm chat e2e restore` |
| `XM_PROFILE` | 切换 chat profile | 全部 |
| `XM_APPSERVICE_AS_TOKEN` | appservice as_token（次优先于配置文件） | `xm chat appservice` |

优先级：flag/arg > env > 交互提示。凭据不得进 argv（暴露给 shell history），env 变量 + 进程注入是脚本/CI 的标准做法。

## 关键约束

- **凭据安全**：配置文件 0600，token 不得打印到 stdout。`xm chat status --verify` 会校验 token 但**不**打印明文。
- **零 CGO**：构建必须 `-tags goolm`（pure-Go Olm），跨平台 Windows / macOS / Linux 全覆盖。
- **跨平台差异**：守护进程用 Unix socket（macOS/Linux）；Windows 下 socket 路径与文件锁走 `internal/chat/chat_serve_daemon_windows.go` 与 `persona_store_flock_windows.go` 分支（`//go:build windows`）。
- **E2E 必须 `--e2e`**：`xm chat login --e2e` 才会初始化 Olm/Megolm；不启用登录后无法在加密房间发送。
- **新 device 需 SAS 验证**：登录第二个 device 后 `xm chat e2e verify @<other_user>:<server>` 与原设备做 emoji 比对确认。
- **token 在 env 变量时仍走非交互**：v1.8.24 起，`XM_CHAT_PASSWORD` 或 `XM_CHAT_TOKEN` 任何一个存在都跳过浏览器/终端输入。

## 典型使用模式（速查）

### 快速通知
```bash
xm chat send "#dev" "CI build passed"
xm chat send "#dev" --emote "deploy done"      # /me 动作
xm chat send "#dev" --notice "维护通知"          # 低优先级
xm chat send "#dev" --reply "$EID" "已处理"     # 回复
```

### 媒体与文件
```bash
xm chat upload "#dev" ./screenshot.png          # 上传图片/文件/视频
xm chat upload "#dev" ./error.log --caption "日志"
```

### 通过 daemon session 发送
```bash
# serve 守护进程模式（配合 --id）
xm chat serve --id bot send "#dev" "hello"
xm chat serve --id bot send "#dev" --emote "waves"        # m.emote
xm chat serve --id bot file "#dev" /path/to/image.png     # 发送文件
xm chat serve --id bot sticker "#dev" /path/to/sticker.png # 贴纸
xm chat serve --id bot location "#dev" --geo "geo:51.5,-0.12" "London"
xm chat serve --id bot edit "#dev" --edit-event "$EID" "new text"
xm chat serve --id bot react "#dev" "$EID" "👍"
xm chat serve --id bot redact "#dev" "$EID" --reason "误发"
```

### 持久 Bot（trigger 模式）
```bash
xm chat serve --id bot start --room "#dev"
xm chat serve --id bot profile --name "CI Bot"
xm chat trigger --id bot --context 15 --auto-reply -- bash bot.sh
xm chat serve --id bot restart   # 更新脚本后无需手动 kill + start
```

### AI 虚拟人（persona 模式，推荐）
```bash
xm chat persona create reviewer --agent claude --prompt-template '{{.Sender}}: {{.Body}}'
xm chat persona start reviewer
xm chat persona status reviewer
xm chat persona logs reviewer -f   # tail 日志
```

详见 [persona.md](references/persona.md)。

### 虚拟身份 Bot
```bash
xm chat appservice config --as-token "syt_xxx" --namespace "@virt-.*:server"
xm chat appservice user-register ai-reviewer
xm chat serve --id reviewer start --room "#dev" --as "@ai-reviewer:server"
```

### E2E 加密设备恢复
```bash
xm chat login --e2e                                  # 初始化加密
xm chat e2e status                                   # 查备份状态
xm chat e2e restore --key "$MATRIX_RECOVERY_KEY"     # CI 场景用 env：XM_CHAT_RECOVERY_KEY
xm chat e2e verify @<other_user>:<server>            # 与原设备 SAS 验证
```

### 多 device 并存
```bash
xm chat login --device alice                        # 独立 device_id
xm chat login --device bob                          # 共存，互不冲突
xm chat logout --device alice                       # 精准清理
xm chat e2e --device bob status                     # 按 device 操作 crypto store
```

## 测试

```bash
bash tests/e2e/chat-e2e.sh        # E2E 加密（需 XM_CHAT_E2E_USER/PASS）
bash tests/e2e/chat-env-login.sh  # env 变量登录（需 E2E_HOMESERVER/USER/PASS）
bash tests/e2e/chat-multi-device.sh  # 多 device 并存
bash tests/e2e/chat-e2e-reset.sh  # 加密身份重置
bash tests/e2e/chat-persona-say.sh  # persona say 发送回环（需 E2E_HOMESERVER/USER/PASS/ROOM）
bash tests/e2e/run-all.sh         # 一键回归
```

所有 E2E 脚本默认 SKIP（缺少凭据即跳过），仅在 CI 或本地显式配置时跑。

## 反模式

- ❌ 把 token / 密码塞进 `xm chat login --token "..."` 的 argv（shell history 泄露）
- ✅ 用 `XM_CHAT_TOKEN=<token> xm chat login` 或 stdin 注入
- ❌ 多人共享同一 device（sync 游标 / OTK 互踩，persona AB-anye-035 暴露的不稳定根因）
- ✅ 每人/每角色独立 device：`xm chat login --device <name>`
- ❌ 不带 `-tags goolm` 直接 `go build` → `fatal error: 'olm/olm.h'`
- ❌ E2E 房间新 device 不 restore 直接发消息 → 历史消息全丢