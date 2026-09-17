# 虚拟身份（appservice）+ Profile + Presence

涵盖 appservice 注册、虚拟用户管理、配置，以及以虚拟身份运行 daemon / 发送消息。

## Appservice 概述

Appservice 让 Matrix homeserver 信任 `xm` 作为 puppet master —— 自动接受 appservice 注册的虚拟用户（无需正常注册流程）。

需要 homeserver 管理员配合：
1. 把生成的 `registration.yaml` 放到 homeserver 的 `app_service_config_files` 配置项
2. 重启 homeserver（Synapse 通常需要）

虚拟用户 ID 格式：`@<localpart>:<server>`，由 appservice namespace 规则控制（如 `@virt-.*:<server>` 表示所有以 `virt-` 开头的本地部分都属于该 appservice）。

## 子命令

```
xm chat appservice
├── register      生成 registration.yaml（提供 token + namespace + url）
├── user-register 注册虚拟用户（@<localpart>:<server>）
├── user-deactivate  停用虚拟用户（--erase 永久擦除）
└── config        查看 / 设置 appservice 配置（as_token + namespace）
```

## 生成注册文件

```bash
xm chat appservice register "@virt-.*:chat.fxbusiness.cn" --sender-localpart xm-bot
xm chat appservice register "@virt-.*:server" --url "https://myapp.example.com"
```

生成的 `registration.yaml` 交给 Matrix 管理员放入 homeserver 配置。

| 参数 | 说明 |
|---|---|
| `<namespace>` | 正则匹配用户 ID，如 `@virt-.*:server` |
| `--sender-localpart` | appservice 自身的本地部分（如 `xm-bot` → `@xm-bot:server`） |
| `--url` | appservice 的 URL（homeserver 通过该 URL 推事件给 appservice） |

## 注册虚拟用户

```bash
xm chat appservice user-register virt-bot              # 注册 @virt-bot:server
xm chat appservice user-register ai-reviewer            # 注册 @ai-reviewer:server
```

注册后虚拟用户立即可用于 appservice 操作。无需密码。

## 停用虚拟用户

```bash
xm chat appservice user-deactivate virt-bot            # 停用（保留历史）
xm chat appservice user-deactivate virt-bot --erase    # 永久擦除（GDPR 合规）
```

## 配置

```bash
xm chat appservice config                                    # 查看（token 脱敏）
xm chat appservice config --as-token "syt_xxx"               # 设置
xm chat appservice config --namespace "@virt-.*:server"      # 设置 namespace
```

也可用环境变量 `XM_APPSERVICE_AS_TOKEN` 注入（**优先级低于配置文件**，适合 CI 临时覆盖）。

配置存于 `~/.xm/config.yaml` 的 `matrix.appservice` 段。

## 以虚拟身份操作

### 一次性发送

```bash
xm chat send "#dev" "hello" --as "@virt-bot:server"
xm chat dm @bob:server "hi" --as "@virt-bot:server"
```

`--as` 让本次命令通过 appservice 身份发送，对方看到的是 `@virt-bot:server`。

### 守护进程以虚拟身份启动

```bash
xm chat serve --id bot start --room "#dev" --as "@virt-bot:server"
xm chat serve --id bot send "#dev" "hello"           # 之后所有操作以该身份
```

`--as` 在 start 时确定身份，daemon 内所有分发动作都继承。

### persona 以虚拟身份运行

```bash
xm chat persona create ai-reviewer --as-user "@ai-reviewer:server"
xm chat persona start ai-reviewer
```

设 `--as-user` 后 persona 跑**自己的** appservice puppet daemon `persona-<name>`，不订阅共享 daemon。详见 [persona.md](persona.md)。

## Profile（显示名 / 头像）

```bash
xm chat profile                                # 查看当前 profile
xm chat profile --name "AI Reviewer"           # 设置显示名
xm chat profile --avatar "mxc://server/abc"    # 设置头像（mxc:// URI）
xm chat profile --device alice --name "Phone"  # 多 device：设指定 device
```

`--device` 用于多 device 场景（详见 [login-and-auth.md](login-and-auth.md)）。

虚拟身份的 profile：
```bash
xm chat serve --id bot profile --name "AI Bot"
xm chat serve --id bot profile --avatar "mxc://server/abc"
xm chat persona edit ai-reviewer --display-name "AI Reviewer"
xm chat persona edit ai-reviewer --avatar "mxc://server/abc"
```

## Presence

```bash
xm chat presence online --status "工作中"      # 在线 + 状态消息
xm chat presence unavailable --status "离开"   # 暂时离开
xm chat presence offline                       # 离线
xm chat presence                               # 查看当前 presence
```

通过 daemon 改：
```bash
xm chat serve --id bot presence online --status "工作中"
```

虚拟身份 presence 由 appservice daemon 维护，通常无需手动设。

## 完整命令速查

```bash
xm chat appservice register <namespace> [--sender-localpart LP] [--url URL]
xm chat appservice user-register <localpart>
xm chat appservice user-deactivate <localpart> [--erase]
xm chat appservice config [--as-token T] [--namespace REGEX]

xm chat profile [--name N] [--avatar MXC] [--device D]
xm chat presence [online|unavailable|offline] [--status T]
xm chat serve --id NAME profile [--name N] [--avatar MXC]
xm chat serve --id NAME presence [STATE] [--status T]

# 以虚拟身份
xm chat {send|dm|...} --as "@user:server"
xm chat serve --id NAME start --as "@user:server"
xm chat persona create NAME --as-user "@user:server"
```