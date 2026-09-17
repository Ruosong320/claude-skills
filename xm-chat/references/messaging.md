# 一次性消息操作

涵盖 `send`、`dm`、`history`、`rooms`、`members`、`users`、`typing`、`join`、`upload`、`react`、`redact`、`room`、`widget`、`presence` 等无需 daemon 的单次命令。

## 发送消息

### 基本发送

```bash
xm chat send "#dev:server" "build passed"                  # 基础文本
xm chat send "#dev" --markdown "**bold**"                  # Markdown 转富文本
xm chat send "#dev" --emote "deploy done"                  # /me 动作 (m.emote)
xm chat send "#dev" --notice "维护通知"                     # 低优先级 m.notice
xm chat send "#dev" --reply "$event_id" "已处理"           # 回复特定事件
xm chat send "#dev" --location "Beijing" --geo "geo:39.9,116.4"  # 位置消息
xm chat send "#dev" -f /path/to/msg.txt                    # 从文件读取
echo "multi\nline" | xm chat send "#dev"                   # stdin 输入
xm chat send "#dev" "hello" --as "@virt:server"            # 虚拟身份发送
```

房间格式必须是 `!roomid:server` 或 `#alias:server`。

`--markdown` 自动将 Markdown 转为 Matrix HTML（支持表格、删除线、任务列表等 GFM 扩展），客户端直接渲染为富文本。

`--notice` 走 `m.notice` 类型，被 `listen --ignore-notices` 默认过滤（防 AI-AI 互相回复循环）。Bot 通知建议都加 `--notice`。

`--emote` 走 `m.emote` 类型（/me 动作），客户端通常渲染为斜体或无气泡样式。不能和 `--notice` 同时使用。

`--reply` 把消息关联为 `$event_id` 的回复（Matrix m.in_reply_to）。

`--location` + `--geo <geo_uri>` 发送位置消息（`m.location`），`geo_uri` 格式为 `geo:<lat>,<lon>`。`--geo` 是 `--geo-uri` 的快捷别名。

### 直聊 (DM)

自动查找或创建一对一私聊房间并发送消息：

```bash
xm chat dm @bob:server "hello"                              # 发送私信
xm chat dm @bob:server "deploy done" --notice               # 低优先级通知
xm chat dm @bob:server "**bold**" --markdown                # Markdown
xm chat dm @bob:server -f ./report.md --markdown            # 从文件读取
xm chat dm @bob:server "hello" --as "@virt:server"          # 虚拟身份发送
echo "patch file" | xm chat dm @bob:server                  # stdin
```

`FindOrCreateDM` 先查 `m.direct` 账户数据复用已有 DM 房间，不存在则自动创建带 `is_direct: true` 的新房间。

## 查看历史

```bash
xm chat history "#dev" -n 20                              # 最近 20 条 (JSON)
xm chat history "#dev" --json                             # --json 等效 --format json
xm chat history "#dev" -n 50 --format compact             # 简洁文本
xm chat history "#dev" -n 10 --format prompt              # LLM 对话格式
xm chat history "#dev" --since "$cursor"                  # 增量翻页 (batch token)
xm chat history "#dev" --before "$event_id"               # 某事件之前
xm chat history "#dev" --since-time "2026-07-17"          # 时间窗口起点
xm chat history "#dev" --since-time "2026-07-17T10:00" --before-time "2026-07-18"
```

### 三种输出格式

| `--format` | 用途 | 形态 |
|---|---|---|
| `json` (默认) | 脚本消费 / jq | `{"events": [...], "next_batch": "..."}` 对象 |
| `compact` | 人工阅读 / bot 脚本 | `[HH:MM] sender: body` |
| `prompt` | 喂给 LLM | sender 映射为 `user:` / `assistant:` |

`--since-time` / `--before-time` 支持 ISO 8601（`2026-07-17` 或 `2026-07-17T15:00:00`）。客户端自动分页直到凑够 `-n` 条或超出时间窗口。

`--since` 接 server 返回的 batch token，做增量翻页（避免重复拉取）。

## 房间与成员

```bash
xm chat rooms                       # 列出已加入的房间
xm chat rooms --json                # JSON 格式

xm chat members "#dev:server"       # 列出房间所有成员（JSON）
xm chat members "!abc123:server"    # 通过房间 ID

xm chat join "#general:server"      # 加入房间（别名）
xm chat join "!abc123:server"       # 加入房间（ID）
```

`members` 输出 JSON 数组，含 `user_id`、`display_name`、`avatar_url`、当前 `power_level`。

## 用户目录

```bash
xm chat users search "alice"           # 模糊搜索用户目录
xm chat users search "alice" --limit 5 # 限制返回数量
xm chat users list                     # 管理员列出所有用户（需 Synapse admin）
xm chat users list --from 100          # 分页偏移
```

`users list` 调用 `/_synapse/admin/v2/users`，需要服务器管理员权限。

`users search` 走 Matrix `user_directory/search` API，普通用户可用。

## 输入通知

```bash
xm chat typing "#dev" --on            # 发送"正在输入"通知
xm chat typing "#dev" --off           # 停止
```

`typing` 在用户敲键盘时持续发送，对方客户端会显示"XXX 正在输入..."。命令发完自动 off。

## 文件上传

```bash
xm chat upload "#dev" ./screenshot.png                # 上传图片
xm chat upload "#ops" ./error.log --caption "日志"    # 文件带附言
```

上传本地文件到 Matrix 媒体仓库并发送为 `m.image` / `m.video` / `m.file` 消息（按 MIME 自动判定）。

输出示例：
```
✓ 已上传 → !room:server  ($event_id)
  mxc:// server/media_id
```

`--caption` 在文件消息后追加一条文本附言。

## 表情反应

```bash
xm chat react "#dev" "$event_id" "👍"
xm chat react "#dev" "$event_id" "🚀"
```

发送 `m.reaction` 事件，是已有消息的表情 / emoji 反应。无需文字即可快速确认，减少消息噪音。

## 消息撤回

```bash
xm chat redact "#dev" "$event_id"                   # 撤回消息
xm chat redact "#dev" "$event_id" --reason "有误"    # 撤回并标注原因
```

撤回（redact）自己发送的消息。`--reason` 是可选撤回原因。

## 消息编辑

编辑已发送的消息，发送 `m.replace` 事件。原消息仍保留在 timeline，客户端渲染替换后的内容。

### 直接编辑（无需 daemon）

```bash
xm chat edit "#dev" "$event_id" "修正后的内容"              # 直接编辑
xm chat edit "#dev" "$event_id" "**bold fix**" --markdown   # Markdown 转富文本
echo "new text" | xm chat edit "#dev" "$event_id"           # stdin 输入
```

`--markdown` 把新内容渲染为 Matrix HTML（富文本），客户端直接显示格式化效果。

### serve daemon 模式

```bash
xm chat serve --id S edit "#dev" "修正后的内容" --edit-event "$event_id"
xm chat serve --id S edit "#dev" "**bold fix**" --edit-event "$event_id" --markdown
```

`--edit-event` 指定要编辑的原始事件 ID。

> `xm chat edit` 是独立的一级子命令，无需启动 daemon 即可使用；`serve --id X edit` 走 daemon RPC，适合已有持久会话的场景。

## 文件/贴纸/位置（serve daemon 模式）

这些类型需要通过 `xm chat serve --id <session>` 走 daemon RPC 发送：

```bash
# 文件上传（自动按 MIME 选 m.image / m.video / m.audio / m.file）
xm chat serve --id S file "#dev" /path/to/screenshot.png

# 贴纸
xm chat serve --id S sticker "#dev" /path/to/sticker.png

# 位置共享
xm chat serve --id S location "#dev" --geo "geo:51.5,-0.12" "London"
```

`file` 根据文件扩展名自动判定 msgtype：图片 `m.image`、视频 `m.video`、音频 `m.audio`、其他 `m.file`。
`sticker` 走 `m.sticker` 类型（独立于 `m.room.message`）。
`location` 需要 `--geo` 指定 geo: URI，body 为位置标签。

## 消息搜索

```bash
xm chat search "#dev" "deploy failed"                  # 全文搜索房间消息
xm chat search "#dev" "bug" --limit 20                 # 限制返回条数
xm chat search "#dev" "error" --order rank              # 按相关性而非时间排序
xm chat search "#dev" "keyword" --json                  # JSON 输出
```

走 Matrix `/search` API，返回匹配的事件 ID、高亮词和事件内容。

## 事件上下文

```bash
xm chat context "#dev" "$evt_abc"                       # 查看某事件前后文（各 5 条）
xm chat context "#dev" "$evt_abc" --limit 10            # 各方向取 10 条
xm chat context "#dev" "$evt_abc" --json                # JSON 输出
```

类似 Slack 的"查看上下文"，看一条通知发生时的前后对话。

## 媒体下载

```bash
xm chat download "mxc://server/abc123"                  # 下载到当前目录
xm chat download "mxc://server/abc123" --output ./img.png  # 指定文件名
xm chat download "mxc://server/abc123" --output ./out/  # 下载到指定目录
```

从 Matrix 媒体仓库下载文件。`--output` 为目录时自动用 `server_mediaId` 作为文件名。

## 通知列表

```bash
xm chat notifications                                   # 获取通知列表
xm chat notifications --limit 5                          # 限制条数
xm chat notifications --only highlight                   # 仅高亮
xm chat notifications --from "$next_token"               # 翻页
xm chat notifications --json                             # JSON 输出
```

获取当前用户的通知（未读提到、邀请等）。含分页 token 可翻页。

## 房间管理

```bash
# 创建
xm chat room create                                    # 空白房间
xm chat room create --name "oncall" --topic "on-call"  # 带名称 + 主题
xm chat room create --invite "@alice:server,@bob:server"  # 创建后自动邀请

# 邀请
xm chat room invite "!abc123:server" "@charlie:server"
xm chat room invite "#dev:server" "@alice:server" --reason "需要协助"

# 踢人（被踢后可重新加入）
xm chat room kick "!abc123:server" "@bad:server"
xm chat room kick "#dev:server" "@user:server" --reason "不活跃"

# 封禁（被禁后无法加入，需解封）
xm chat room ban "!abc123:server" "@spammer:server"
xm chat room ban "#dev:server" "@bad:server" --reason "违规"

# 解封
xm chat room unban "!abc123:server" "@user:server"
```

`room create` 默认 `private_chat` 预设（仅被邀请者可加入）。

`room invite` 向已有房间邀请新成员，`--reason` 是可选邀请备注。

`room kick` / `room ban` 需要管理员权限。`kick` 是临时移除（可重进），`ban` 是永久封禁（需显式 `unban` 才能再进入）。`--reason` 是可选原因。

`room name` / `room topic` 管理房间名和主题（`m.room.name` / `m.room.topic` state event）。

`room power-levels` 查看/修改房间权限（`m.room.power_levels` state event），支持 `--users`、`--kick`、`--ban`、`--events` 等 flag。

`room pin` / `room unpin` / `room pinned` 管理置顶消息（`m.room.pinned_events` state event）。

## Widget 管理

Matrix widget 通过房间的 `im.vector.modular.widgets` state event 注册（Element 里嵌 Jitsi / Etherpad 等用的同一套协议）。`--room` 接房间 ID 或 alias。

```bash
# 注册 widget（省略 --id 时自动生成 widget-<type>-<unixnano>）
xm chat widget register --room "#dev:server" --name "Jitsi" --type jitsi --url "https://meet.example.com/room"
xm chat widget register --room "#dev:server" --name "Etherpad" --type etherpad --url "https://pad.example.com/p/abc"

# 列出房间内所有 widget
xm chat widget list --room "#dev:server"            # 表格
xm chat widget list --room "#dev:server" --json     # JSON（脚本消费）

# 取单个 widget（按 state_key / widget ID）
xm chat widget get --room "#dev:server" --id "widget-jitsi-1234"
xm chat widget get --room "#dev:server" --id "widget-jitsi-1234" --json

# 删除 widget（清空 state event 内容）
xm chat widget remove --room "#dev:server" --id "widget-jitsi-1234"
```

`register` 必填 `--type`（如 `jitsi` / `etherpad` / `m.custom`）和 `--url`；`--name` 是展示名，`--id` 省略时按 `widget-<type>-<unixnano>` 自动生成。`list` / `get` 支持 `--json` 给脚本消费。widget JSON 字段：`id` / `name` / `type` / `url` / `creatorUserId` / `waitForIframeLoad` / `data`。

## Presence

```bash
xm chat presence online --status "工作中"      # 在线 + 状态消息
xm chat presence unavailable --status "离开"   # 暂时离开
xm chat presence offline                       # 离线
xm chat presence                               # 查看当前 presence
```

设置后其他用户看你就是对应状态。daemon 运行时通过 `serve --id X presence <state>` 改。

## Profile

```bash
xm chat profile                                # 查看当前 profile
xm chat profile --name "AI Reviewer"           # 设置显示名
xm chat profile --avatar "mxc://server/abc"    # 设置头像（mxc:// URI）
xm chat profile --device alice --name "Phone"  # 多 device 设指定 device
```

`--device` 用于多 device 场景。`profile`（单数）操作顶层 / 指定 device 的 profile；`profiles`（复数）管理 chat profile YAML。

## 账号数据 (Account Data)

Bot 持久化 key-value 状态，跨 session 保留。类型名（如 `m.direct`、`m.widgets`、自定义 `com.example.bot_state`）由调用方定义。

```bash
xm chat account-data get m.direct                         # 查看直接聊天映射
xm chat account-data get com.example.bot_config            # 读取自定义配置
xm chat account-data set com.example.config '{"k":"v"}'    # 写入 JSON 数据
```

走 Matrix `/_matrix/client/v3/user/{userId}/account_data/{type}` API。

## 推送规则 (Push Rules)

自定义通知过滤规则，控制哪些消息触发推送通知。

```bash
xm chat pushrules list                                    # 列出所有规则
xm chat pushrules list --json                             # JSON 格式
xm chat pushrules enable override .m.rule.suppress_notices  # 启用规则
xm chat pushrules disable content .m.rule.contains_user_name # 禁用规则
xm chat pushrules delete override .m.rule.custom_rule      # 删除自定义规则
```

`kind` 可选：`override`、`content`、`room`、`sender`、`underride`。

## 房间元数据 (Name / Topic)

```bash
xm chat room name "#dev"                                  # 获取房间名称
xm chat room name "#dev" "新名称"                         # 设置房间名称
xm chat room topic "#dev"                                 # 获取房间主题
xm chat room topic "#dev" "新的讨论主题"                   # 设置房间主题
```

走 `m.room.name` / `m.room.topic` state event，空房间可能无此 state 返回空字符串。

## 权限等级 (Power Levels)

```bash
xm chat room power-levels "#dev"                          # 查看当前 power levels (JSON)
xm chat room power-levels "#dev" --users-default 10       # 新用户默认等级
xm chat room power-levels "#dev" --users "@alice:50"      # 设置特定用户等级
xm chat room power-levels "#dev" --kick 50 --ban 50       # 设置管理阈值
xm chat room power-levels "#dev" --events "m.room.name:50,m.room.topic:50"  # 事件权限
```

走 `m.room.power_levels` state event。多个 user 用逗号分隔：`--users "@u1:50,@u2:100"`。

## 消息置顶 (Pinned Events)

```bash
xm chat room pinned "#dev"                                # 列出置顶事件 ID
xm chat room pin "#dev" "$event_id"                       # 置顶消息
xm chat room unpin "#dev" "$event_id"                     # 取消置顶
```

走 `m.room.pinned_events` state event。置顶操作需管理员权限（默认 power level 50）。

## 完整命令速查

```bash
xm chat send <room> [msg] [--markdown] [--emote] [--notice] [--reply ID] [--location] [--geo GEO] [-f file] [--as USER]
xm chat dm <user> [msg] [同上]
xm chat history <room> [-n N] [--format json|compact|prompt] [--since T] [--before T] [--since-time T] [--before-time T]
xm chat rooms [--json]
xm chat members <room>
xm chat users {search Q [--limit N] | list [--from N]}
xm chat typing <room> [--on | --off]
xm chat join <room>
xm chat upload <room> <file> [--caption TXT]
xm chat react <room> <event_id> <emoji>
xm chat redact <room> <event_id> [--reason T]
xm chat edit <room> <event_id> [new_body] [--markdown]
xm chat search <room> <query> [--limit N] [--order recent|rank] [--json]
xm chat context <room> <event_id> [--limit N] [--json]
xm chat download <mxc://...> [--output PATH]
xm chat notifications [--limit N] [--only highlight] [--from T] [--json]
xm chat room {create [--name N] [--topic T] [--invite users] | invite <room> <user> [--reason T] | ban <room> <user> [--reason T] | kick <room> <user> [--reason T] | unban <room> <user>}
xm chat widget {register --room R --type T --url U [--name N] [--id I] | list --room R [--json] | get --room R --id I [--json] | remove --room R --id I}
xm chat presence [online|unavailable|offline] [--status T]
xm chat profile [--name N] [--avatar MXC] [--device D]
# serve daemon 模式额外动作：
xm chat serve --id S edit <room> [msg] --edit-event <EID> [--markdown]
xm chat serve --id S file <room> <file_path>
xm chat serve --id S sticker <room> <file_path>
xm chat serve --id S location <room> --geo <geo_uri> [label]
xm chat serve --id S ban <room> <user> [--reason T]
xm chat serve --id S kick <room> <user> [--reason T]
xm chat serve --id S unban <room> <user>
# 账号数据
xm chat account-data get <type>
xm chat account-data set <type> <json>
# 推送规则
xm chat pushrules list [--json]
xm chat pushrules {enable|disable|delete} <kind> <rule_id>
# 房间元数据
xm chat room name <room> [new_name]
xm chat room topic <room> [new_topic]
# 权限等级
xm chat room power-levels <room> [--users @u:s:50 --kick 50 --ban 50 ...]
# 消息置顶
xm chat room pin <room> <event_id>
xm chat room unpin <room> <event_id>
xm chat room pinned <room>
# serve daemon 模式额外动作：
xm chat serve --id S room-name <room> [new_name]
xm chat serve --id S room-topic <room> [new_topic]
xm chat serve --id S room-pin <room> <event_id>
xm chat serve --id S room-unpin <room> <event_id>
xm chat serve --id S room-pinned <room>
xm chat serve --id S room-power-levels <room>
xm chat serve --id S account-data-get <type>
xm chat serve --id S account-data-set <type> <json>
```