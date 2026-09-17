# 实时监听与守护进程（serve / listen）

涵盖 `xm chat listen`、`xm chat serve` 的 daemon 模式、stdio 模式，以及如何通过 socket 向 daemon 分发动作。

## 实时监听（listen）

```bash
xm chat listen                                    # 全部房间，文本格式
xm chat listen --json                             # JSONL (AI 消费)
xm chat listen --json --mentions-only             # 仅 @提及
xm chat listen -r "#dev" -r "#ops"                # 限定房间
xm chat listen -n 10 -r "#dev"                    # 先展示 10 条历史再监听
xm chat listen --skip-old                         # 跳过已有消息
xm chat listen --ignore-notices                   # 过滤 m.notice（默认，防 AI 循环）
xm chat listen --include-notices                  # 包含 m.notice

# 订阅指定 daemon session
xm chat listen --id persona --json --skip-self
```

`--ignore-notices` 默认开启 —— 防止 AI-AI 对话循环（两个 bot 互相收到对方的消息并回复）。

`--json` 输出 JSONL（每行一个完整事件对象），给 AI / 脚本消费。

`-r` 可重复指定多房间。

`--id` 接 daemon session 名 —— 复用已运行 daemon 的事件流而不开新连接。

### listen 过滤器（与 trigger 同语义，AND 逻辑）

| Flag | 作用 |
|---|---|
| `--in-room "<id>"` | 限定房间 |
| `--from "<user>"` | 限定发送者 |
| `--match "<regex>"` | 正则匹配 body |
| `--contains "<str>"` | 子串匹配 |
| `--mentioned` | 仅 @提及（可配合 `--trigger-name`） |
| `--trigger-name "<names>"` | 逗号分隔 @-name，配合 `--mentioned` 按正文 `@name` 字面匹配 |
| `--msgtype "<type>"` | Matrix 消息类型 |
| `--prefix "<str>"` | 消息正文前缀匹配 |
| `--rooms <id>` | 房间白名单（可重复，组内 OR） |
| `--froms <user>` | 发送者白名单（可重复，组内 OR） |
| `--or-contains <str>` | 子串 OR（可重复） |
| `--or-match <regex>` | 正则 OR（可重复） |
| `--exclude-room "<id>"` | 排除指定房间 |
| `--exclude-from "<user>"` | 排除指定发送者 |
| `--from-domain "<domain>"` | 按发送者 homeserver 域名过滤 |
| `--min-body-len <N>` | 最小消息正文长度 |
| `--max-body-len <N>` | 最大消息正文长度 |
| `--verbose` | 打印每条事件的匹配/跳过原因（调试 filter 必备） |
| `--skip-self` | 跳过当前用户自己的消息 |

**AND/OR 语义**：所有 flag 之间 AND；`--rooms`/`--froms`/`--or-contains`/`--or-match` 组内 OR。exclude 在所有 include 后生效。

```bash
# 典型组合：监听来自特定域名的 @提及，排除 bot 消息
xm chat listen --json --mentioned --trigger-name "bot" \
  --from-domain "chat.myhomedata.space" --exclude-from "@bot:server" --skip-self
```

## 守护进程模式（serve）

后台进程，跨进程复用，通过 Unix socket 通信（macOS/Linux：`~/.xm/chat/<name>.sock`；Windows：见 `internal/chat/chat_serve_daemon_windows.go`）。

daemon 只持有连接状态（token、sync loop、since cursor、订阅者列表），**不碰业务逻辑**（冷却、对话记忆、路由都在 trigger / persona 里）。

### 生命周期管理

```bash
xm chat serve --id bot start --room "#dev"                        # 启动
xm chat serve --id bot start --room "#dev" --as "@virt:server"    # 虚拟身份
xm chat serve --id bot status                                     # 检查状态
xm chat serve --id bot stop                                       # 停止
xm chat serve --id bot restart                                    # 重启（保留参数）
xm chat serve --list                                              # 列出所有活跃 session
```

`serve restart` = `stop + start`，保留所有 `--room` / `--as` / `--filter` 参数。

### 多 device daemon

```bash
xm chat serve --id alice start                                    # alice daemon → alice device
xm chat serve --id bob start                                      # bob daemon → bob device
xm chat serve --list                                              # 全部 session（含 device）
```

不同 session 自动绑定不同 device（来自 `matrix.sessions.<id>` 或顶层 default），各自独立 sync 游标 / OTK / crypto store。

### 向 daemon 分发动作

所有一次性 chat 命令都可通过 daemon socket 执行（不重新开 Matrix 连接）：

```bash
# 消息发送
xm chat serve --id bot send "#dev" "build passed"
xm chat serve --id bot send "#dev" "**bold**" --markdown
xm chat serve --id bot send "#dev" "handled" --reply "$event_id"

# 实时监听
xm chat serve --id bot listen [--mentions-only]

# 打字 / 加入 / 已读 / 自定义事件
xm chat serve --id bot typing "#dev" --on
xm chat serve --id bot join "#general:server"
xm chat serve --id bot read "#dev" "$event_id"
xm chat serve --id bot send-event "#dev" --type "com.example.event" --data '{}'

# 身份管理
xm chat serve --id bot profile --name "AI Reviewer"
xm chat serve --id bot profile --avatar "mxc://server/abc"
xm chat serve --id bot presence online --status "工作中"
xm chat serve --id bot presence unavailable --status "离开"
xm chat serve --id bot presence offline

# 反应 / 撤回
xm chat serve --id bot react "#dev" "$event_id" "👍"
xm chat serve --id bot redact "#dev" "$event_id"
xm chat serve --id bot redact "#dev" "$event_id" --reason "mistake"

# 房间管理
xm chat serve --id bot create-room --room-name "oncall" --invite "@alice:server"
xm chat serve --id bot invite "#dev" "@bob:server" --invite-reason "需要协助"
```

> serve 子命令与顶层一次性命令同名（`send` / `react` / `redact` 等），行为完全一致 —— 区别仅在是否复用已有 daemon。

## Stdio 模式

```bash
xm chat serve --stdio -r "#dev:server"
```

单进程：stdin 收 JSON 动作，stdout 输出 JSONL 事件，进程退出 = 会话结束。适合一次性脚本。

### stdin 动作格式

```jsonl
{"action":"send","room":"#dev","body":"hello"}
{"action":"typing","room":"#dev","on":true}
{"action":"react","room":"#dev","event_id":"$abc","key":"👍"}
```

### stdout 事件格式

```jsonl
{"type":"event","room":"#dev","sender":"@alice:server","body":"hi","event_id":"$xyz","ts":1234567890}
{"type":"status","connected":true}
{"type":"error","message":"..."}
```

## 旧路径兼容

`xm chat serve --id X trigger [flags] -- <command>` 等价于 `xm chat trigger --id X [flags] -- <command>`。

旧路径保留是为了不破坏现存脚本 —— **新代码应使用 trigger 子命令**（见 [triggers.md](triggers.md)）。

## 完整命令速查

```bash
# 一次性 listen
xm chat listen [--json] [--mentions-only] [-r ROOM...] [-n N] [--skip-old] [--ignore-notices|--include-notices] [--id SESSION]

# daemon 生命周期
xm chat serve --id NAME start [--room R] [--as USER] [--id DAEMON_SESSION]
xm chat serve --id NAME stop
xm chat serve --id NAME restart
xm chat serve --id NAME status
xm chat serve --list

# daemon 分发动作（任何一次性 chat 命令都可加 --id NAME）
xm chat serve --id NAME {send|dm|history|rooms|listen|react|redact|typing|profile|presence|...}

# stdio 模式
xm chat serve --stdio -r ROOM [--id NAME]
```