# 事件触发命令（trigger）

`xm chat trigger` 是一等命令，将 Matrix 消息事件映射为 shell 命令执行。与 `xm chat serve --id X trigger [flags] -- <command>` 完全等价 —— 新路径更简洁，旧路径保留兼容。

trigger 连接到命名 daemon 的 socket，订阅事件流，匹配过滤器后执行命令。若 daemon 未运行则自动启动。

## 基本用法

```bash
xm chat trigger --id <session> [filters] [behavior] -- <command...>
xm chat trigger --id bot --match "^/deploy\b" --once -- bash deploy.sh
xm chat trigger --id bot --mentioned --context 15 --auto-reply --typing -- \
  llm --prompt "$XM_BODY" --context "$XM_CONTEXT"
```

`--` 之后的参数原样透传给要执行的命令。

## 过滤器（AND 逻辑 — 所有条件同时满足才触发）

所有 filter flag 之间是 AND 关系（全部满足才触发）。multi-value 字段（`--rooms`、`--froms`、`--or-contains`、`--or-match`）组内 OR，组间 AND。exclude 字段在所有 include 之后生效。

### 基础过滤

| Flag | 作用 | 示例 |
|---|---|---|
| `--in-room "<id>"` | 限定房间（支持裸名 / 别名 / 完整 ID） | `"Server"` |
| `--from "<user>"` | 限定发送者 | `"@alice:server"` |
| `--match "<regex>"` | 正则匹配消息正文 | `"^/deploy\b"` |
| `--contains "<str>"` | 子串匹配 | `"SEV1"` |
| `--mentioned` | 仅 @提及（可配合 `--trigger-name` 按 @name 字面匹配） | — |
| `--trigger-name "<names>"` | 逗号分隔 @-name 列表，配合 `--mentioned` 按正文 `@name` 字面匹配 | `"bot,xiaoye"` |
| `--msgtype "<type>"` | Matrix 消息类型 | `"m.notice"` |

`--in-room` 支持灵活匹配：完整 room ID（`!xxx:server`）、完整 alias（`#Server:server`）、裸名（`Server`）均可，大小写不敏感。

### 多值过滤（组内 OR，组间 AND）

| Flag | 作用 | 示例 |
|---|---|---|
| `--rooms <id>` | 房间白名单（可重复，至少一个匹配） | `--rooms "!dev:server" --rooms "!ops:server"` |
| `--froms <user>` | 发送者白名单（可重复，至少一个匹配） | `--froms "@alice:server" --froms "@bob:server"` |
| `--or-contains <str>` | 子串 OR（可重复，至少一个匹配） | `--or-contains "紧急" --or-contains "urgent"` |
| `--or-match <regex>` | 正则 OR（可重复，至少一个匹配） | `--or-match "^/deploy" --or-match "^/rollback"` |

### 排除过滤

| Flag | 作用 | 示例 |
|---|---|---|
| `--exclude-room "<id>"` | 排除指定房间 | `"!noisy:server"` |
| `--exclude-from "<user>"` | 排除指定发送者 | `"@bot:server"` |

### 高级过滤

| Flag | 作用 | 示例 |
|---|---|---|
| `--prefix "<str>"` | 消息正文前缀匹配 | `"!小夜"` |
| `--from-domain "<domain>"` | 按发送者 homeserver 域名过滤 | `"chat.myhomedata.space"` |
| `--min-body-len <N>` | 最小消息正文长度 | `10` |
| `--max-body-len <N>` | 最大消息正文长度（0 = 无限制） | `500` |

## 行为控制

| Flag | 作用 | 示例 |
|---|---|---|
| `--once` | 匹配一次后退出 | — |
| `--auto-reply` | stdout 回复到房间 | — |
| `--typing` | 命令执行期间显示"正在输入" | — |
| `--throttle <d>` | 最小触发间隔（防抖） | `5s` / `30s` |
| `--cooldown <d>` | 同房间冷却 | `30s` / `1m` |
| `--batch N` | 攒够 N 条事件才触发 | `5`（默认 1 = 逐条触发） |
| `--interval <d>` | 攒批最大等待时间，超时强制 flush | `10m` / `30s` |
| `--context N` | 注入最近 N 条消息为 `XM_CONTEXT` | `15` |
| `--skip-self` | 跳过会话自身消息（默认 `true`，防 `--auto-reply` 循环） | — |
| `--verbose` | 实时打印每条事件的匹配/跳过原因（调试 filter 必备） | — |

## Agent 模式（`--agent`，会话连续性）

实现 AI agent 的会话连续性 —— 从 stdout 提取 `session_id`，下次触发时注入环境变量。

```
首次触发 → 命令执行 → 提取 session_id → 保存 .agent.state
再次触发 → 加载 session_id → 设 XM_AGENT_SESSION → 命令以 --resume 续接
```

| Flag | 作用 |
|---|---|
| `--agent claude` | 内置 Claude 提取器：匹配 `$.session_id`，提取 `$.result` 为回复正文 |
| `--agent codex` | 内置 Codex 提取器：匹配 JSONL `$.thread_id`，提取最后 `agent_message.text` |
| `--agent <custom>` | 未知类型需配合 `--agent-session-pattern` 自定义正则 |
| `--agent-session-pattern '<re>'` | 自定义正则（含一个捕获组），覆盖内置提取器 |

**提取器做两件事**：
1. `Extract(output)` — 提取 `session_id`，保存并下次注入 `XM_AGENT_SESSION`
2. `ExtractResponse(output)` — 用于 `--auto-reply`，从 JSON 输出剥离正文，只发纯文本到房间

### ⚠️ Shell 参数展开（关键）

首次触发 `XM_AGENT_SESSION` 为空，直接传 `--resume ""` 会让 claude/codex 报错。必须用 `${VAR:+...}` 让空值时整个参数消失：

```bash
# ✅ 正确：空值时 --resume 参数不出现
xm chat trigger --id bot --agent claude --match "^/ask" --auto-reply -- \
  claude -p --output-format json ${XM_AGENT_SESSION:+--resume "$XM_AGENT_SESSION"}

# ✅ 正确：codex 同理
xm chat trigger --id bot --agent codex --match "^/ask" --auto-reply -- \
  codex exec --json ${XM_AGENT_SESSION:+resume "$XM_AGENT_SESSION"}

# ❌ 错误：空值时变成 --resume "" 导致报错
xm chat trigger --id bot --agent claude --match "^/ask" --auto-reply -- \
  claude -p --output-format json --resume "$XM_AGENT_SESSION"
```

## 环境变量（命令执行时可用）

| 变量 | 说明 |
|---|---|
| `XM_ROOM` | 房间 ID |
| `XM_SENDER` | 发送者用户 ID |
| `XM_BODY` | 消息正文 |
| `XM_EVENT_ID` | 触发事件 ID |
| `XM_MATCH` | 正则匹配文本（仅 `--match`） |
| `XM_SESSION` | daemon session 名（`--id` 的值） |
| `XM_CONTEXT` | 最近 N 条消息 compact 文本（仅 `--context N`） |
| `XM_AGENT_SESSION` | 上次提取的 session_id（仅 `--agent`，首次为空） |

`XM_CONTEXT` 注入 trigger 的滑动窗口，零网络开销 —— 事件本来就流经 trigger，无需额外调 `xm chat history`。

## 生命周期管理

```bash
xm chat trigger list --id bot          # 列出运行中的 trigger（PID、存活、命令）
xm chat trigger kill --id bot 12345    # 终止指定 PID（发 SIGINT）
xm chat trigger agent-reset --id bot   # 清除 agent session，下次启动新会话
```

旧路径等价：
```bash
xm chat serve --id bot trigger-list           # 同 trigger list
xm chat serve --id bot trigger-kill 12345     # 同 trigger kill
xm chat serve --id bot trigger-agent-reset    # 同 trigger agent-reset
```

## 典型场景

```bash
# CI 部署：匹配 /deploy 触发部署脚本
xm chat trigger --id bot --match "^/deploy\b" --once -- bash deploy.sh

# AI 回复：被 @ 时调 LLM，注入上下文 15 条，自动回复到房间
xm chat trigger --id bot --mentioned --context 15 --auto-reply --typing -- \
  llm --prompt "$XM_BODY" --context "$XM_CONTEXT"

# Agent 模式：Claude 会话连续性
xm chat trigger --id bot --agent claude --match "^/ask" --auto-reply -- \
  claude -p --output-format json ${XM_AGENT_SESSION:+--resume "$XM_AGENT_SESSION"}

# Agent 模式：Codex 会话连续性
xm chat trigger --id bot --agent codex --match "^/ask" --auto-reply -- \
  codex exec --json ${XM_AGENT_SESSION:+resume "$XM_AGENT_SESSION"}

# 常驻 + 节流 + 冷却
xm chat trigger --id bot --match "deploy" --throttle 5s --cooldown 30s -- deploy.sh

# 攒批：每 5 条或 10 分钟超时触发
xm chat trigger --id bot --match "deploy" --batch 5 --interval 10m -- ./batch-deploy.sh

# 调试：verbose 看每条事件匹配/跳过原因
xm chat trigger --id bot --in-room Server --match "deploy" --verbose -- bash deploy.sh
```

## 编写上下文感知 Bot 脚本

```bash
#!/usr/bin/env bash
# bot.sh — 上下文感知的 AI 回复
response=$(ai chat \
  --system "你是团队助手，根据聊天上下文回答" \
  --context "$XM_CONTEXT" \
  --query "$XM_BODY")
echo "$response"
```

```bash
xm chat trigger --id bot --mentioned --context 15 --auto-reply --typing -- bash bot.sh
```

## 防循环

`--auto-reply` 会让 trigger 自己发回的消息又被 trigger 处理。三道防线：

1. **`--skip-self`**（默认 `true`）：自动跳过 bot 自己发的消息 → 无需在脚本里手动检查 `XM_SENDER`
2. **`listen --ignore-notices`**：trigger 用 `--notice` 发通知，对方 listen 端默认过滤
3. **prompt 规则**：人格 prompt 写明"不要回复自己发的消息"

## trigger vs persona

trigger 适合**每事件启动新进程**的轻量场景；persona 适合**持久 agent 会话**（多轮记忆、人格一致）。

详见 [persona.md](persona.md)。