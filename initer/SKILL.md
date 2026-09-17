---
name: initer
description: Clarify requirements before starting from-zero project builds or new feature work. Use when asked to create a complete new project, scaffold an app, design a system, add a new feature, introduce a new workflow, or make any change whose product, technical, UX, data, integration, security, deployment, or acceptance boundaries are unclear; generate a checklist from the user request, identify unclear boundaries, ask targeted multi-round questions, and begin implementation only after the checklist is sufficiently resolved.
---

## 一切提问优先使用弹窗工具让我点击选择，实在没办法弹窗再要求描述。

# Initer

Initer is a pre-implementation clarification gate. It prevents the agent from starting substantial project or feature work while the requirements, boundaries, constraints, or acceptance criteria are still ambiguous.

## Core Rule

Before building a new project or new feature, create a task-specific checklist, inspect each boundary, and ask questions for every item that is unclear enough to affect implementation. Do not begin implementation until the checklist has enough answers to support a responsible first build.

## Triggered Work

Use this skill for:

- Building a complete project from zero.
- Scaffolding a new app, service, library, CLI, plugin, skill, workflow, pipeline, dashboard, game, or website.
- Adding a new user-facing feature or major internal capability.
- Creating a new integration, data flow, automation, model pipeline, API, UI flow, deployment path, or persistence layer.
- Any request where success depends on unclear product behavior, target users, input/output contracts, security, data shape, UX, runtime, dependencies, or acceptance criteria.

For tiny edits, bug fixes with obvious expected behavior, copy changes, or narrow refactors, use normal engineering judgment instead of forcing a long clarification round.

## Workflow

### 1. Restate The Request

Summarize the user's request in 1-3 sentences. Identify whether the work is a from-zero project, new feature, integration, workflow, or other substantial change.

### 2. Generate The Checklist

Create a checklist tailored to the request. Start from the checklist categories below, then remove irrelevant items and add task-specific ones.

For each checklist item, mark one of:

- `Clear`: enough information is known.
- `Assumed`: a low-risk assumption can be made; state it.
- `Unclear`: implementation could diverge meaningfully without an answer.
- `Blocked`: cannot responsibly proceed without an answer.

### 3. Ask Targeted Questions

Ask only about `Unclear` and `Blocked` items that matter now. Prefer 3-7 concise questions per round. Group related questions. Avoid asking about details that can be safely inferred from repository conventions or inspected locally.

Questions must be specific enough that the user's answer can change implementation. Avoid broad questions like "Any preferences?" unless a concrete decision list would be misleading.

### 4. Iterate Until Boundaries Are Clear

After each user answer:

1. Update the checklist.
2. State newly resolved decisions and remaining unclear items.
3. Ask the next focused round if needed.

Continue until all blocking items are resolved and only safe assumptions remain.

### 5. Confirm The Build Brief

Before implementation, provide a concise build brief:

- Goal:
- Scope included:
- Scope excluded:
- Key decisions:
- Assumptions:
- Acceptance criteria:
- Implementation plan:

Then proceed unless the user corrects the brief or explicitly asks for more planning.

## Checklist Categories

Use these categories as the default checklist inventory.

### Product Boundary

- User goal and core problem.
- Target users or operators.
- Primary use cases and non-goals.
- Must-have vs nice-to-have capabilities.
- Success criteria and acceptance tests.
- Expected demo or delivery format.

### Functional Behavior

- Main workflows and user journeys.
- Inputs, outputs, and side effects.
- Business rules, calculations, states, and edge cases.
- Error handling and empty/loading/success states.
- Permissions, roles, ownership, and visibility.
- Import/export, search, filtering, sorting, notifications, history, undo, or audit needs when relevant.

### UX And Interaction

- Target platform: web, mobile, desktop, CLI, API, background job, plugin, or mixed.
- Required screens, commands, routes, or interaction surfaces.
- Layout density, tone, visual style, accessibility, and localization needs.
- Responsive behavior and device/browser support.
- Existing design system, component library, icons, assets, or brand rules.

### Data And State

- Data entities, fields, relationships, validation rules, and lifecycle.
- Persistence layer: local file, database, cache, browser storage, external service, or stateless.
- Seed/demo data and migration/backfill needs.
- Privacy, retention, audit, logging, and data deletion requirements.
- Concurrency, conflict resolution, and offline behavior when relevant.

### Technical Architecture

- Existing repository conventions and constraints.
- Runtime, framework, language, package manager, and versions.
- Module boundaries, ownership, APIs, and extension points.
- Build, test, lint, formatting, and deployment commands.
- Performance, scalability, reliability, and observability expectations.

### Integrations And Dependencies

- External APIs, credentials, rate limits, webhooks, files, queues, or model providers.
- Dependency preferences or restrictions.
- Network availability and offline fallbacks.
- Sandbox, permissions, secrets, and environment variable handling.

### Security And Compliance

- Authentication, authorization, and session requirements.
- Sensitive data, secrets, PII, legal, policy, or compliance constraints.
- Abuse cases, validation, injection risks, and safe failure behavior.

### Delivery And Maintenance

- Definition of done.
- Tests and manual verification required.
- Documentation and project record expectations.
- Backward compatibility and migration expectations.
- Timeline, priority, and phased rollout if scope is large.

## Minimum Readiness Standard

Implementation may start only when:

- The core user goal is clear.
- Included and excluded scope are stated.
- Main workflows are known.
- Inputs, outputs, and persistent state are defined or safely assumed.
- Target runtime and integration boundaries are known.
- Acceptance criteria or verification method is explicit.
- Any remaining assumptions are listed and low risk.

If any item above is missing, ask before coding.

## Question Style

Use concise, decision-oriented questions.

Good:

- `这个功能是只给管理员用，还是普通用户也能用？这会影响权限模型和 UI 入口。`
- `数据需要持久化到数据库，还是浏览器本地存储就够？`
- `MVP 是否只需要 CSV 导入，Excel 和 API 同步先排除？`

Avoid:

- `你还有什么想法吗？`
- `要不要做得更好看？`
- `请详细说明所有需求。`

## Build Brief Template

Use this before implementation once the checklist is resolved.

```markdown
## Build Brief

- Goal:
- Work type: from-zero project | new feature | integration | workflow | other
- Included scope:
- Excluded scope:
- Target users:
- Main workflows:
- Data/state:
- Interfaces:
- Technical choices:
- Dependencies/integrations:
- Security/privacy:
- Acceptance criteria:
- Verification plan:
- Assumptions:
- Open non-blockers:
- Implementation plan:
```
