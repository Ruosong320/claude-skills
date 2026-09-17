# Monitor 模式（claude --bg + listen pipe，备选方案）

⚠️ **推荐方案是 `xm chat persona`**（原生 ACP，零外部 orchestrator）。本节是**旧方案**，保留用于以下场景：
- 用户已有 claude/codex orchestrator 工作流，希望自行管理 agent 生命周期
- 需要在 `xm chat` 之外的工具链（自定义脚本、CI、监控面板）里消费 Matrix 事件
- 实验 / 调试目的

## 模式对比

| | persona（推荐） | Monitor + listen pipe（备选） |
|---|---|---|
| **Claude 生命周期** | persona router 管理 | 手动 `claude --bg` / `claude stop` |
| **事件源** | daemon 内部分发 | FIFO / daemon JSONL |
| **人格一致性** | persona config + system prompt | system prompt 写在 claude --append-system-prompt |
| **ACP session** | 内置（agent auto） | 无，靠 Claude Monitor 自维护 |
| **重启 / 升级** | `persona restart` 一条命令 | 多进程协调 |
| **多 persona 隔离** | config 隔离 | 每个独立 claude --bg + FIFO |

## 方式一：listen pipe（推荐 Monitor 变体）

`xm chat listen --json` 输出 JSONL 事件流到命名管道（FIFO），Claude Code Monitor 工具直接监控管道 —— 每条新事件即时送达，无需等待文件刷新，且 listen 的内置过滤器可以预处理事件流。

```
┌──────────────────────────────────────────────────┐
│  xm chat serve --id persona start                │
│       │                                          │
│       │ daemon socket 广播事件                     │
│       ▼                                          │
│  xm chat listen --id persona --json              │
│       │       --skip-self                         │
│       │       --mentions-only  (可选过滤器)        │
│       │                                          │
│       │ 写入 FIFO                                 │
│       ▼                                          │
│  /tmp/persona_events  (命名管道)                  │
│       │                                          │
│       │ Monitor 工具监控                           │
│       ▼                                          │
│  claude --bg --name "persona-bot"                │
│       │ "你是客服小美。监控 /tmp/persona_events，   │
│       │  读取每条 JSON 事件，判断是否需要回复，     │
│       │  用 xm chat send 发送回复"                 │
│       ▼                                          │
│  xm chat send <room> "<AI 生成的回复>"            │
└──────────────────────────────────────────────────┘
```

**为什么 listen pipe 优先于 daemon JSONL？**

- **即时送达**：FIFO 无缓冲，事件到达立刻被 Monitor 感知；daemon JSONL 依赖文件 sync 周期
- **预处理过滤**：`--skip-self` / `--mentions-only` / `--match` 等前置过滤，减少 Claude 无效判断
- **解耦**：listen 进程独立于 daemon 和 Claude，单独重启不影响其他组件
- **不落盘**：FIFO 是内存管道，不留历史文件，节省磁盘

### 第 1 步：登录并启动 daemon

```bash
xm chat login
xm chat serve --id persona start
xm chat serve --id persona status
```

### 第 2 步：设定虚拟人身份

```bash
xm chat serve --id persona profile --name "客服小美 🤖"
```

### 第 3 步：定义人格 prompt

创建 `~/.xm/chat/persona-prompt.md`：

```markdown
你是「客服小美」，通过 Matrix 聊天为客户提供技术支持。

## 你是谁
- 名字：小美
- 身份：Starmia 公司 AI 客服，负责回答产品使用问题
- 语气：亲切友好、专业简洁、适当使用 emoji

## 行为规则
- 收到消息后先判断：是否需要你回复？
- 不知道的就说不知道，别编造
- 每次回复前用 xm chat history 了解上下文
- 涉及账号、密码、支付时引导用户走工单系统
- 回复控制在 3 句话以内，别写小作文
- 不要回复你自己发出去的消息

## 工作方式
- 你用 xm chat send 命令发消息到消息所在的 room_id
- 用 xm chat history -n 10 <room_id> 查看最近聊天记录
- 你通过 Monitor 工具读取 /tmp/persona_events 管道中的新事件
```

### 第 4 步：创建 FIFO，启动 listen

```bash
mkfifo /tmp/persona_events

# 启动 listen → FIFO（后台运行）
# --skip-self 防止自己的回复被再次处理
# 可按需加 --mentions-only、--match 等过滤器
xm chat listen --id persona --json --skip-self > /tmp/persona_events &
```

### 第 5 步：启动 Claude Monitor

```bash
claude --bg \
  --name "persona-bot" \
  --append-system-prompt "$(cat ~/.xm/chat/persona-prompt.md)" \
  --allowedTools "Bash(xm chat *),Read" \
  "通过 Monitor 工具持续监控 /tmp/persona_events 管道。
   管道中是 JSONL 格式的 Matrix 事件流，每条一个 JSON 对象。
   你的工作流程：
   1. Monitor 推给你新事件时，读取 body 和 sender 字段
   2. 判断这条消息是否需要你回复
   3. 如需回复，用 xm chat history -n 10 <room_id> 了解上下文
   4. 根据人格设定生成回复
   5. 用 xm chat send <room_id> \"回复内容\" 发送到房间"
```

### 第 6 步：管理虚拟人

```bash
# 查看运行中的 Claude agent
claude agents --json | jq '.[] | select(.name=="persona-bot")'

# 附加会话看它在干什么
claude attach persona-bot

# 更新人格 prompt 后重启
claude stop persona-bot
claude respawn persona-bot

# 停止
claude stop persona-bot

# listen 进程也需清理
kill $(pgrep -f "xm chat listen.*persona")
```

## 方式二：Daemon JSONL 直读

零额外进程 —— 不启动 listen，Monitor 直接 tail daemon 的 JSONL 日志：

```bash
xm chat serve --id persona start

claude --bg --name "persona-bot" \
  --allowedTools "Bash(xm chat *),Read" \
  "使用 Monitor 工具监控 ~/.xm/chat/$(chatProfile)/persona.jsonl 文件的变化。
   每当你检测到新的事件行，读取 body 和 room_id 字段，判断是否需要回复，
   用 xm chat send 发送回复到对应房间。"
```

**何时选 daemon JSONL**：不想管 listen 进程生命周期，或 FIFO 在某些环境不可用。缺点是事件有文件 I/O 延迟，缺少 listen 的前置过滤能力 —— 所有判断都压在 Claude prompt 里。

## 方式三：trigger + agent（轻量替代）

不需要持久会话时，trigger agent 模式更轻量：

```bash
xm chat trigger --id persona --agent claude --mentioned --context 15 --auto-reply --typing -- \
  claude -p --output-format json \
    --system-prompt "$(cat ~/.xm/chat/persona-prompt.md)" \
    ${XM_AGENT_SESSION:+--resume "$XM_AGENT_SESSION"}
```

详见 [triggers.md](triggers.md)。

## 人格 Prompt 设计要点

| 要素 | 说明 | 示例 |
|------|------|------|
| **你是谁** | 名字、身份、背景 | "你是 DevOps Bot，负责 CI/CD 通知" |
| **语气风格** | 正式/随意、长短、emoji 偏好 | "简洁专业，不超过 50 字，不用 emoji" |
| **回复规则** | 何时回复、何时忽略 | "只在 @提及或被叫 'bot' 时回复" |
| **能力边界** | 能做什么、不能做什么 | "不知道就说不知道，别编造" |
| **工作方式** | 具体工具调用指引 | "回复前用 xm chat history -n 10 了解上下文" |

## 防循环

Monitor 模式下机器人自己发的消息也会被 Monitor 看到，可能导致回复循环。三道防线：

1. **listen `--skip-self`**：`xm chat listen --skip-self` 自动过滤自己发的消息
2. **prompt 规则**：在人格 prompt 中加"不要回复自己发的消息"
3. **xm chat send --notice**：用 `m.notice` 类型发消息，降低被其他 bot 处理优先级

## 何时迁移到 persona

如果你的 persona 是这种形态：
- 单一 Matrix 身份（无 appservice puppet）
- 一个人格、一个人设
- 希望"一键起停 / 改配置 / 看状态"

→ 直接迁到 `xm chat persona`，命令更短、生命周期更可控、原生 ACP session。

仅在以下情况保留 Monitor 模式：
- 需要在 Claude 之外的工作流里消费 Matrix 事件
- 需要多个 Matrix daemon 共享一个 Claude orchestrator
- appservice puppet 场景（persona 当前 v1.8.23 不开 E2E，需 workaround）

## 推荐

```bash
# 同样的人格 prompt 文件，直接迁到 persona
xm chat persona create reviewer \
  --system-prompt-file ~/.xm/chat/persona-prompt.md \
  --prompt-template '{{.Sender}}: {{.Body}}' \
  --mentioned

xm chat persona start reviewer
xm chat persona status reviewer
xm chat persona logs reviewer -f
xm chat persona stop reviewer   # 清理一条命令
```

详见 [persona.md](persona.md)。