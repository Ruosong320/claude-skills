# AI 虚拟人（persona）— ACP 原生

`xm chat persona` 是推荐的 AI 虚拟人方案 —— 原生 ACP（Agent Client Protocol）持久 agent，零外部 orchestrator（不用 claude --bg Monitor、不用 FIFO）。

与 trigger agent 模式的关键区别：

| | trigger agent 模式 | persona |
|---|---|---|
| **agent 生命周期** | 每事件启动新进程 | 持久会话，跨消息复用 |
| **上下文** | 仅 `$XM_CONTEXT` 窗口 | 会话内全量上下文，跨消息记忆 |
| **人格一致性** | 每次靠 system prompt 重建 | 一次设定，会话内始终如一 |
| **适用场景** | 命令响应、一次性问答 | 多轮对话、角色扮演、长期陪伴 |
| **资源消耗** | 每次冷启动 | 持续占用一个 ACP session |

旧式 Monitor 编排仍可用但**不推荐**（见 [monitor-mode.md](monitor-mode.md)）。

## 子命令

```
xm chat persona
├── create <name>         新建 persona 配置
├── edit <name>           改 persona 配置字段
├── start <name>          启动 persona router（前台）
├── stop <name>           停止运行中的 persona
├── restart <name>        重启
├── list                  列出所有 persona
├── status <name>         状态详情（PID、队列深度、drop 计数）
├── logs <name>           操作日志（-f tail，--all 合并 router+event 日志）
├── say <name> <room> <msg>      以 persona 身份发消息
├── ask <name> [msg]      一次性 ACP 提示（cold process，hot session）
├── allow <name> <user...>       白名单用户（空 = 所有人）
├── forget <name>         清除 session 绑定（--room R 只清指定房间）
├── del <name>            删除 persona 配置
├── prompt {edit|show} <name>    编辑/查看人格文件（CLAUDE.md/AGENTS.md）
├── open <name>          在文件管理器中打开 persona 配置目录
│
└── 诊断与调试 ──────────────────────────────────────
├── check                 检测当前 profile 下的重复/孤儿 router
├── ping <name>          端到端可达性检查（daemon→router→agent）
├── trace <name> <event> 追踪单个事件的完整处理链路
├── watch <name>         实时流式查看 admit/skip 决策
├── explain <name>       模拟 admit/skip 决策（干跑，不影响运行中 router）
├── debug <name>         运行时切换 debug 日志（免重启）
└── agent-status <name>  查看 ACP agent 配置、持久会话与实时用量
```

## 快速上手

```bash
# 1. 创建 persona（默认 agent=claude via npx，--mentioned=true）
xm chat persona create reviewer

# 2. 启动 router
xm chat persona start reviewer

# 3. 状态 / 日志
xm chat persona status reviewer
xm chat persona logs reviewer -f           # tail 操作日志
xm chat persona logs reviewer --all -f     # 同时看 router + event 日志

# 4. 测试：让 persona 发消息 / 问它
xm chat persona say reviewer "#dev:server" "今天 status meeting 取消"
xm chat persona ask reviewer "今天天气怎么样"   # 一次性 ACP 提示

# 5. 停止 / 删除
xm chat persona stop reviewer
xm chat persona del reviewer
```

## CLAUDE.md 自动加载（人格最简姿势）

persona 默认 cwd 为 `~/.xm/chat/personas/<name>/`，`claude-agent-acp` 在该目录启动时会自动扫描 `CLAUDE.md` 并加载为 system prompt 的组成部分。**写人格内容到此文件即可生效，无需 `--system-prompt-file`**：

```bash
# 把人格写到 persona 的 cwd 顶部
mkdir -p ~/.xm/chat/personas/reviewer
cat > ~/.xm/chat/personas/reviewer/CLAUDE.md <<'EOF'
# 客服小美 🤖

## 你是谁
- Starmia 公司 AI 客服，负责回答产品使用问题
- 语气：亲切、简洁、专业

## 行为规则
- 不知道就说不知道，别编造
- 涉及账号 / 密码 / 支付时引导用户走工单系统
- 回复不超过 3 句话
EOF

xm chat persona create reviewer  # cwd 自动 = ~/.xm/chat/personas/reviewer/
xm chat persona start reviewer    # agent 启动时自动加载 CLAUDE.md
```

注：`claude-agent-acp` 在 persona Cwd 启动 `claude` CLI，后者默认自动加载该目录下的 `CLAUDE.md` 作为人格记忆。claude-agent-acp 本身没有关闭自动加载的 flag（不存在 `--bare`，v0.27 仅 `--cli`/`--claudeai`/`--console`/`--hide-claude-auth`）--不想自动加载就别在该 Cwd 放 `CLAUDE.md`，或用 `--dir` 指向别的目录。要在 `CLAUDE.md` 之外追加静态 system prompt，用 xm-cli 的 `--system-prompt-file`（见下文配置字段）。

### 用命令管理人格文件

- `xm chat persona prompt edit <name>` -- 在 `$EDITOR` 打开该 persona 的人格文件；不存在则从模板创建。文件名按 agent 类型：claude -> `CLAUDE.md`，codex -> `AGENTS.md`。
- `xm chat persona create <name> --scaffold-prompt` -- create 时顺带写入模板人格文件。**默认不 scaffold**，避免污染 `--dir` 指定的已有目录。
- **已存在的 `CLAUDE.md`/`AGENTS.md` 永不覆盖**：`--dir` 指向已有目录时，scaffold 检测到同名文件会跳过并提示 `reusing existing`，保留你的原有内容。

## Agent 环境变量

persona router 启动 ACP agent 进程时，会自动注入以下环境变量，供 agent 内部读取以感知自己的身份与运行上下文：

| 变量 | 说明 | 示例值 |
|------|------|--------|
| `XM_PERSONA_NAME` | persona 名称 | `小夜` |
| `XM_PERSONA_PROFILE` | 当前 chat profile 名 | `home` |
| `XM_PERSONA_DAEMON` | 共享 daemon session ID | `default` |
| `XM_MATRIX_USER` | 解析后的 Matrix 用户 ID | `@admin:chat.myhomedata.space` |

这些变量在 agent 进程**首次启动时**注入（`ensureClient` 阶段），不需要在 `agent.env` 里手动配置。`XM_MATRIX_USER` 在 daemon 连接成功后才解析到（之前为空），但 agent 启动在 daemon 连接之后，所以 agent 启动时该值已经可用。

**使用场景**：
- 在 `CLAUDE.md` 中引用 persona 身份：`你是 {{XM_PERSONA_NAME}}，在 {{XM_PERSONA_PROFILE}} 环境下运行`
- agent 工具中根据 `XM_MATRIX_USER` 判断"我是谁"，做权限或路由决策
- 日志/监控中打 persona 标签，区分不同实例

如果需要在 `agent.env` 里**覆盖**这些值（不推荐，会破坏一致性），直接在配置文件的 `agent.env` 中设置同名 key —— `mergePersonaEnv` 用 `mergeEnviron` 合并，`agent.env` 的 key 排在后面，会覆盖同名 key。

## 配置字段（persona create / edit）

完整字段见 `xm chat persona create --help` 与 `xm chat persona edit --help`。配置文件：`~/.xm/chat/personas/<name>.yaml`。

### 顶层

| 字段 | yaml key | 说明 |
|---|---|---|
| `DisplayName` | `display_name` | 显示名（写 Matrix profile） |
| `Avatar` | `avatar` | 头像 mxc:// URL |
| `E2E` | `e2e` | 启用加密（默认 false） |
| `AsUser` | `as_user` | appservice puppet user ID（`@<localpart>:<server>`） |
| `DaemonSession` | `daemon_session` | 共享 daemon session（默认 `default`；虚拟身份下忽略） |

### Agent（`agent.*`）

| 字段 | 说明 |
|---|---|
| `Type` | agent 品牌 `claude` 或 `codex`（驱动默认 Command） |
| `Command` | agent 命令，默认 `["npx", "-y", "@agentclientprotocol/claude-agent-acp"]` 或 `["npx", "-y", "@agentclientprotocol/codex-acp"]` |
| `Cwd` | agent 工作目录（默认 `~/.xm/chat/personas/<name>/`，自动 mkdir） |
| `IdleTimeout` | 空闲超时（`10m`） |
| `Env` | 注入 agent 子进程的环境变量 |
| `McpServers` | MCP server 列表（v1.8.25 起生效）—— stdio 形式，逐项含 `name/command/args/env` |
| `Mode` | agent mode，如 `ask` / `code`（v1.8.25 起生效，调 `Session.SetMode`） |
| `Model` | model 覆盖（v1.8.25 起生效，调 `Session.SetModel`） |
| `SystemPromptFile` | 静态 system prompt 文件路径（v1.8.25 起生效，逐轮拼到 user-turn 前面） |
| `PromptTemplate` | per-message 模板（Go text/template） |
| `Provider` | `ccswitch://<id>` provider pinning |
| `SettingsOverlay` | 直接 overlay 文件路径（v1.8.25 起生效，拼到 system prompt 前面） |
| `Permission.Mode` | `deny-all` / `allow-all` / `auto-low-risk` / `ask-in-room` |
| `Permission.AskRoom` | `ask-in-room` 模式的目标房间 |
| `FsJail` | 文件访问限制目录（默认 = agent.cwd） |
| `TurnTimeout` | 单轮 agent 回复超时（如 `5m`），v1.8.34 起生效 |
| `FallbackModel` | 熔断后回退模型（v1.8.34 起生效） |
| `MaxConsecutiveFailures` | 连续失败阈值（默认 5），达到后熔断打开（v1.8.34 起生效） |

### Agent 回复格式（v1.8.26 起）

persona router 发送的 reply 默认走 **Markdown 渲染**：`body` 字段保留 markdown 原文，向后兼容旧 homeserver；同时附带 `formatted_body` (org.matrix.custom.html) 给 Element 等富文本客户端渲染富文本。无需额外 flag——所有 reply 一律渲染。

渲染失败 fallback 到纯文本（不丢消息，只是不渲染样式）；E2E 加密房间当前走 plain-text path，下版本补 `SendReplyMarkdownE2E`。

### Trigger（`trigger.*`，控制响应时机）

所有 trigger 字段是 AND 关系：事件必须满足每个指定条件。multi-value 字段（`rooms`、`froms`、`or_contains`、`or_match`）组内 OR，组间 AND。exclude 字段在所有 include 之后生效。

| 字段 | yaml key | 说明 | 默认 |
|---|---|---|---|
| `Room` | `room` | 限定房间（空 = 全部） | — |
| `From` | `from` | 限定发送者 | — |
| `Match` | `match` | 正则匹配 body | — |
| `Contains` | `contains` | 子串匹配 | — |
| `Mentioned` | `mentioned` | 仅 @ 提及 | `true` |
| `TriggerName` | `trigger_name` | 逗号分隔 @-name，配合 `mentioned` 按正文 `@name` 字面匹配 | — |
| `Prefix` | `prefix` | 消息正文前缀匹配 | — |
| `Rooms` | `rooms` | 房间白名单（至少一个匹配） | `[]` |
| `Froms` | `froms` | 发送者白名单（至少一个匹配） | `[]` |
| `OrContains` | `or_contains` | 子串 OR（至少一个匹配） | `[]` |
| `OrMatch` | `or_match` | 正则 OR（至少一个匹配） | `[]` |
| `ExcludeRoom` | `exclude_room` | 排除指定房间 | — |
| `ExcludeFrom` | `exclude_from` | 排除指定发送者 | — |
| `FromDomain` | `from_domain` | 按发送者 homeserver 域名过滤 | — |
| `MinBodyLen` | `min_body_len` | 最小消息正文长度（0 = 无限制） | 0 |
| `MaxBodyLen` | `max_body_len` | 最大消息正文长度（0 = 无限制） | 0 |
| `SelfMention` | `self_mention` | 放行"自己发的且 @了自己"的消息（self-trigger） | `false` |
| `Context` | `context` | context ring 大小（0 = 默认 20） | 20 |
| `Cooldown` | `cooldown` | 同房间冷却（`10s`） | — |
| `Batch.Size` | `batch.size` | 攒批阈值 | 1 |
| `Batch.Interval` | `batch.interval` | 攒批最大等待（`3s`） | 3s |
| `Queue.Capacity` | `queue.capacity` | 事件队列容量 | 256 |
| `Queue.DropPolicy` | `queue.drop_policy` | `low`（满载时丢低优先级） | low |
| `MaxConcurrency` | `max_concurrency` | 并发房间 worker 数上限（v1.8.34 起生效） | 1（串行） |

### Self-trigger（`self_mention`，未发布）

默认 persona 跳过自己发的消息（own-message guard），避免回声。开 `trigger.self_mention` 后**仅**放行"自己发的且 @了自己"的消息（`sender == self && evt.Mentions`），其余自发消息照旧跳过。场景：用另一个身份 @persona 触发它，或让 persona 响应自己之前 @自己的消息。

**防回环**：放行的 self-mention 走 **normal** 优先级（不是 high），仍受 per-room cooldown 约束--即便 persona 回复正文里含自己的 MXID 被识别为 mention，也会被冷却挡住，不会无限自回复。high（绕过 cooldown）只留给"别人 @自己"。

```bash
xm chat persona create selfbot --self-mention
xm chat persona edit selfbot --self-mention        # 开
xm chat persona edit selfbot --no-self-mention     # 关（覆盖 --self-mention）
```

### Per-message 模板（`PromptTemplate`）

Go `text/template` 包装每条入站事件为发给 agent 的 user-turn：

```
Persona 在 {{.Room}} 收到 {{.Sender}} 的消息：{{.Body}}

最近上下文：
{{.Context}}
```

占位符：
- `{{.Body}}` — 事件消息体
- `{{.Sender}}` — 发送者 MXID
- `{{.Room}}` — 房间 ID
- `{{.Context}}` — context ring 文本

未设置时保持 `promptBody = first.Body` 默认行为。

### 虚拟身份模式（`AsUser`）

设了 `AsUser`（appservice puppet）后：
- persona 跑**自己的** appservice puppet daemon：`persona-<name>`
- 不与共享 daemon 抢 device_id
- puppet 当前不开 E2E（v1.8.19 路线 B 未实现，详见 backlog AB-anye-037）

未设 `AsUser` 时 persona **订阅**共享 daemon session（默认 `default`，同 `xm chat trigger --id`），避免双 daemon 抢同一 device。

## Priority Queue（AB-anye-039）

v1.8.20 起，事件摄取与 agent 分发解耦：

```
scanner → eventCh(128) → [ingest: filter+priority → PQ(有界 heap)]
                          → [dispatcher goroutine: pop 最高优先 → flushBatch(同步 Reply)]
```

- **优先级派生**：`matrix.Event.Mentions` 为 high（`@提及`），其余 normal
- **非抢占**：进行中 agent 回合不被中断；high 仅在下一轮分发时插队
- **背压**：队列满时按 `drop_policy=low` 丢低优先级；incoming high 可驱逐最旧 normal
- **cooldown**：high（提及）绕过 per-room cooldown 必回；normal 维持现有冷却语义
- **batch**：默认 `batchSize=1` 行为不变；`batchSize>1` 时按同 room 合并；high 立即分发不等待 `batchInterval`

drop 计数入日志与 `persona status` 输出。

## 并发 Dispatch（v1.8.34 起）

`trigger.max_concurrency`（默认 1）控制多房间并发 agent 回复：

```
├─ 房间 A ──→ roomWorker(A) ──→ flushBatch(A) → after reply pick pending
├─ 房间 B ──→ roomWorker(B) ──→ flushBatch(B)
├─ 房间 C ──→ semaphore cap ──→ queued（max_concurrency）
```

- `max_concurrency=1`（默认）：所有房间串行，完全向后兼容
- `max_concurrency>1`：多房间并发，**同房间内仍串行**（保证消息顺序）
- 信号量 cap：同时最多 `max_concurrency` 个 worker 运行
- 新消息到达时若房间 worker 已在运行，消息排队到 `pending` 批次，worker 完成后立即处理

```bash
xm chat persona create reviewer --max-concurrency 3
xm chat persona edit reviewer --max-concurrency 5
```

## 熔断器 + 模型回退（v1.8.34 起）

`agent.max_consecutive_failures` + `agent.fallback_model` 组成熔断保护：

- 连续失败达到阈值 → 熔断打开，后续 dispatch 直接跳过（不浪费 API 调用）
- 熔断期间新消息以 `m.notice` 回复："agent 暂时不可用，请稍后再试"
- 首次成功回复 → 熔断自动关闭（重置计数器）
- `fallback_model` 设置后，可重试的错误（超时/网络）自动用 fallback 模型重试一次

```bash
xm chat persona edit reviewer --fallback-model "claude-haiku-4-5"
xm chat persona edit reviewer --max-consecutive-failures 3
```

## 轮次超时（v1.8.34 起）

`agent.turn_timeout` 用 `context.WithTimeout` 包裹每轮 `backend.Reply`，超时后 agent 进程收到 ctx 取消信号。

```bash
xm chat persona edit reviewer --turn-timeout "10m"
```

## 守护进程自动重连（v1.8.34 起）

daemon 连接断开后 router 不会崩溃——ingest 连接在指数退避循环中自动重连：

- 退避：1s → 2s → 4s → ... → 30s（上限）
- 控制 socket 和 dispatch loop 在重连期间存活，已排队消息不丢

## 跨会话事件去重（Watermark，v1.8.54 起）

persona router 重启后不再重复处理已回复过的消息。每房间持久化最后派发的 event ID 到 `~/.xm/chat/personas/<name>.watermarks.json`，启动时自动跳过 daemon replay 中已处理的旧事件。

- **空间**：每房间一条 ID，常驻 < 3KB
- **正确性**：利用 daemon replayBuf 的时序性 —— 若 watermarked 事件在 replay 中，其之前的所有事件也已被处理过
- **自动管理**：每次成功回复后更新 watermark，无需手工维护
- **transparent**：重启时在日志中标注 "skipped (watermark)" 而非静默丢弃

## ask-in-room 权限模式（v1.8.34 完成）

`ask-in-room` 模式发权限请求到 Matrix 房间，等待人工审批：

- 发送消息："Agent wants to run tool (kind). Reply y/n"
- 解析 y/yes/ok/allow（批准）或 n/no/deny/reject（拒绝）
- 60s 超时 → 默认拒绝

```bash
xm chat persona create reviewer --permission ask-in-room --ask-room "!ops:server"
```

## ACP Agent 配置示例

### Claude（默认 — 走 npm `claude-agent-acp`）

```bash
xm chat persona create reviewer \
  --agent claude \
  --cmd "npx,-y,@agentclientprotocol/claude-agent-acp" \
  --prompt-template '{{.Sender}} 在 {{.Room}} 说：{{.Body}}' \
  --permission ask-in-room \
  --ask-room "!ops:server" \
  --mentioned
```

> v1.8.25 起默认 cmd 改为 `npx -y @agentclientprotocol/claude-agent-acp`。早期版本（v1.8.23 之前）默认是 `claude --acp`，但 Claude Code CLI 实际没有 `--acp` flag —— 老 persona.yaml 若显式写了 `command: ["claude", "--acp"]` 会启动失败，需用 `persona edit --cmd` 改成 npx 形式。

### Claude（走 npm 上的 `claude-agent-acp`）

`@agentclientprotocol/claude-agent-acp` 是 Agent Client Protocol 官方发布的独立包，与 Claude Code CLI 共享协议但实现更精简。两种拉起方式：

```bash
# 方式一：npx -y 免安装直接跑（适合临时测试 / CI）
xm chat persona create reviewer-npx \
  --agent claude \
  --cmd "npx,-y,@agentclientprotocol/claude-agent-acp" \
  --mentioned

# 方式二：全局安装后直接跑
npm install -g @agentclientprotocol/claude-agent-acp
xm chat persona create reviewer-global \
  --agent claude \
  --cmd "claude-agent-acp" \
  --mentioned
```

注意：
- `npx -y` 首次会拉包（冷启动慢几秒），之后会缓存到 `~/.npm/_npx`
- 路径走 `exec.LookPath("npx")`，Windows 下需 `npx.cmd`
- 与 cc-switch 联动：`acp.NewFromCCSwitch` 内部就是调 `claude-agent-acp`（详见 `internal/acp/presets.go`），通过 `--provider ccswitch://<id>` 即可走 provider 配置
- 凭据（`ANTHROPIC_API_KEY` 等）从当前 daemon 进程的环境变量继承，无需额外注入

### Codex

```bash
xm chat persona create reviewer-codex \
  --agent codex \
  --cmd "codex,exec,--acp" \
  --model "gpt-5" \
  --permission auto-low-risk
```

### 沙盒（fs-jail）

```bash
xm chat persona create reviewer-sandbox \
  --agent claude \
  --fs-jail /tmp/persona-sandbox
```

`--fs-jail` 限制 agent 的文件操作只能访问该目录及其子目录。

### MCP servers（v1.8.25 起生效）

`--mcp-servers` 接受分号分隔的 shorthand `name=command,arg1,arg2`：

```bash
xm chat persona create reviewer \
  --agent claude \
  --mcp-servers "github=npx,-y,@modelcontextprotocol/server-github;slack=npx,-y,@modelcontextprotocol/server-slack" \
  --mentioned
```

完整写法（yaml）支持 per-server env：

```yaml
agent:
  mcp_servers:
    - name: github
      command: npx
      args: ["-y", "@modelcontextprotocol/server-github"]
    - name: slack
      command: /usr/local/bin/slack-mcp
      env:
        SLACK_TOKEN: "***"
```

### Mode / Model（v1.8.25 起生效）

```bash
xm chat persona create reviewer \
  --agent claude \
  --mode ask             # agent mode（ask / code / architect 等）
  --model claude-opus-4-5  # model 覆盖
  --mentioned
```

## 编辑配置（edit）

```bash
xm chat persona edit reviewer --no-mentioned        # 响应所有消息（覆盖 --mentioned=true）
xm chat persona edit reviewer --prompt "新模板..."   # 改 per-message 模板
xm chat persona edit reviewer --reset-prompt        # 清空模板，恢复默认行为
xm chat persona edit reviewer --permission ask-in-room --ask-room "!ops:server"
xm chat persona edit reviewer --e2e                 # 启用加密
xm chat persona edit reviewer --no-e2e              # 关闭加密（覆盖 --e2e）
xm chat persona edit reviewer --display-name "新名字"
xm chat persona edit reviewer --avatar "mxc://server/abc"
xm chat persona edit reviewer --from "@alice:server,@bob:server"  # 用户白名单
xm chat persona edit reviewer --contains "SEV1"      # 加 contains 过滤
xm chat persona edit reviewer --match "^/ask\b"      # 加正则过滤
xm chat persona edit reviewer --prefix "!小夜"        # 前缀过滤
xm chat persona edit reviewer --trigger-name "小夜,assistant"  # @name 触发词
xm chat persona edit reviewer --or-contains "紧急,urgent"     # 子串 OR 过滤
xm chat persona edit reviewer --or-match "^SEV,^ALERT"       # 正则 OR 过滤
xm chat persona edit reviewer --from-domain "chat.myhomedata.space"  # 域名过滤
xm chat persona edit reviewer --exclude-room "!noisy:server" # 排除房间
xm chat persona edit reviewer --exclude-from "@bot:server"   # 排除发送者
xm chat persona edit reviewer --min-body-len 10             # 最小消息长度
xm chat persona edit reviewer --max-body-len 500            # 最大消息长度
xm chat persona edit reviewer --trigger-rooms "!dev:server,!ops:server"  # 多房间白名单
xm chat persona edit reviewer --trigger-froms "@alice:server,@bob:server"  # 多发送者白名单
xm chat persona edit reviewer --cooldown "10s"
xm chat persona edit reviewer --batch-size 5 --batch-interval 10s
xm chat persona edit reviewer --queue-capacity 512 --queue-drop-policy low
xm chat persona edit reviewer --trigger-room "!ops:server"
xm chat persona edit reviewer --self-mention                # 开 self-trigger（响应自己 @自己）
xm chat persona edit reviewer --no-self-mention             # 关 self-trigger（覆盖 --self-mention）
xm chat persona edit reviewer --model "opus-4-8"
xm chat persona edit reviewer --provider "ccswitch://prod"
xm chat persona edit reviewer --mcp-servers "github,slack"  # 逗号分隔
xm chat persona edit reviewer --system-prompt-file /path/to/prompt.md
xm chat persona edit reviewer --settings-overlay /path/to/overlay.json
xm chat persona edit reviewer --cmd "claude,--acp,--model,opus-4-8"   # 空格分隔 token
xm chat persona edit reviewer --dir /path/to/cwd
xm chat persona edit reviewer --fs-jail /path/to/jail
xm chat persona edit reviewer --mode "ask"
xm chat persona edit reviewer --as-user "@ai-bot:server"               # 启用虚拟身份
xm chat persona edit reviewer --as-user ""                             # 清空虚拟身份
xm chat persona edit reviewer --id "team-shared"                       # 改共享 daemon session
```

所有 flag 默认只在显式提供时覆盖；未指定的字段保持不变。`--no-mentioned` / `--no-e2e` 是特殊反向 flag（覆盖对应的正向默认）。

## 一次性 ACP 提示（ask）

```bash
xm chat persona ask reviewer "今天天气怎么样"           # 走 hot session（复用现有会话）
xm chat persona ask reviewer "重新开始" --new          # 强制开新会话
xm chat persona ask reviewer --daemon                 # 走运行中的 router（更轻量）
xm chat persona ask reviewer --room "#dev" --sender "@alice"  # 指定 session key
```

`ask` 默认冷启动 agent 进程，但**复用 hot session state**（`session_id` 保持）；`--daemon` 走运行中的 router（最轻量，但要 persona 先 `start`）。

## 状态与日志

### status

```bash
xm chat persona status reviewer
```

输出：
- 状态（running / stopped / error）
- PID / 端口 / daemon session
- 队列深度 + drop 计数
- 当前 ACP session_id

### logs

```bash
xm chat persona logs reviewer                # 操作日志（router log）
xm chat persona logs reviewer -f             # tail
xm chat persona logs reviewer --events       # 事件日志（JSONL）
xm chat persona logs reviewer --all          # 合并 router + event 日志（[router]/[event] 前缀）
xm chat persona logs reviewer --all -f       # 合并 tail
```

`--all` 把 router 日志和 event 日志合并到一个流，前缀区分，给调试 agent 处理流程用。

## 诊断与调试命令

以下是 persona 运行时诊断、问题排查和可达性检查子命令。

### check — 检测重复/孤儿 router

```bash
xm chat persona check
```

扫描当前 profile 下的所有 persona，检测两类异常：
- **双 router 抢占**：同一 persona 有两个进程争用同一个 daemon session，导致消息重复回复
- **孤儿 ctl socket**：persona 进程已退出但 Unix control socket 残留，下次启动可能连接失败

内部用 `lsof` + daemon clients 交叉验证。发现异常时输出具体路径和 PID，不会自动清理。

### ping — 端到端可达性检查

```bash
xm chat persona ping reviewer
```

验证**完整链路**是否畅通：daemon session → persona router → ACP agent。内部发一个轻量 `ping` 请求到 router 的 control socket，router 转发给 agent 做一次空送（不产生房间消息）。返回延迟和各段状态。

三种失败模式：
- daemon 无响应 → daemon session 未启动或 session ID 不匹配
- router 无响应 → persona 没有在运行
- agent 无响应 → ACP agent 进程可能挂死，需重启 persona

### trace — 事件追踪

```bash
xm chat persona trace reviewer "$event_id"
```

追踪一个 Matrix 事件在 router 内的完整处理链路：`admit/skip 决策 → 入队 → 分发 → agent prompt → agent reply → 发送结果`。合并 router 日志和 event 日志中的匹配行，时间线展示。

### watch — 实时 admit/skip 流

```bash
xm chat persona watch reviewer
```

实时流式输出 router 对每条入站事件的 `admit`（受理）或 `skip`（过滤）决策，以及跳过原因（未 @、房间不匹配、冷却中等）。适合调 trigger 过滤规则时观察调整效果。

### explain — 模拟 admit/skip 决策

```bash
xm chat persona explain reviewer --room "#dev:server" --sender "@alice:server" --body "!小夜 帮我查一下"
```

**干跑**（dry-run）admit/skip 决策，不经过运行中的 router，不影响线上。用于验证 trigger 过滤规则——改完 `match`/`contains`/`prefix` 等字段后，用 `explain` 构造一个合成事件看会被 admit 还是 skip，以及原因。无需启动 persona。

### debug — 运行时切换 debug 日志

```bash
xm chat persona debug reviewer          # 切换到 debug 级别
xm chat persona debug reviewer --off    # 切回 info 级别
```

免重启切换 router 日志级别。debug 模式下 router 输出详细处理路径（事件过滤详情、agent prompt 内容、reply 耗时等）。

### open — 打开配置目录

```bash
xm chat persona open reviewer
```

用系统文件管理器（macOS Finder / Linux xdg-open / Windows Explorer）打开 `~/.xm/chat/personas/reviewer/` 目录。方便浏览 `CLAUDE.md`、session 文件、其他 agent 产物。

### agent-status — ACP agent 状态

```bash
xm chat persona agent-status reviewer
```

输出：
- agent 配置摘要（type / command / cwd / model / mode）
- 持久 session 列表（session_id、绑定的房间、最后活跃时间）
- 当前 agent 进程是否存活、空闲时长
- 熔断器状态（open/closed、连续失败计数）

## 完整命令速查

```bash
xm chat persona create <name>
  [--agent TYPE] [--cmd TOKENS] [--dir DIR] [--fs-jail DIR]
  [--id DAEMON_SESSION] [--mentioned] [--self-mention] [--permission MODE] [--ask-room ROOM]
  [--prompt TEMPLATE] [--provider URL] [--model MODEL]

xm chat persona edit <name>
  [--agent TYPE] [--cmd TOKENS] [--dir DIR] [--display-name N] [--avatar MXC]
  [--as-user USER] [--e2e|--no-e2e] [--id DS]
  [--mentioned|--no-mentioned]
  [--self-mention|--no-self-mention]
  [--match REGEX] [--contains STR] [--from USERS] [--trigger-room ROOM]
  [--trigger-name NAMES] [--prefix STR] [--or-contains LIST] [--or-match LIST]
  [--trigger-rooms LIST] [--trigger-froms LIST]
  [--exclude-room ROOM] [--exclude-from USER]
  [--from-domain DOMAIN] [--min-body-len N] [--max-body-len N]
  [--context N] [--cooldown DUR]
  [--batch-size N] [--batch-interval DUR]
  [--queue-capacity N] [--queue-drop-policy POL]
  [--permission MODE] [--ask-room ROOM]
  [--prompt TPL] [--reset-prompt] [--system-prompt-file PATH]
  [--model MODEL] [--mode MODE] [--provider URL] [--settings-overlay PATH]
  [--mcp-servers LIST] [--fs-jail DIR]

xm chat persona {start|stop|restart|status|logs|say|ask|allow|forget|del} <name> [args...]
```