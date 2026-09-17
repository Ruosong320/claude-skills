---
name: analyze-only
description: 当用户使用「分析、仅分析、只分析、帮我分析、分析一下、评估、看一下、analyze、analysis、analyze only」等词触发。Perform objective, evidence-led analysis without changing any file, code, configuration, data, or persistent state. Use when the user asks to inspect, audit, review, diagnose, compare, validate, or assess a requirement, workflow, design, code path, document, dataset, result, decision, incident, or risk while requesting analysis only, no edits, no implementation, or a report before changes. Reconstruct the main workflow, locate the exact analysis point, examine upstream and downstream context, use a task-specific checklist and fit-for-purpose analytical methods, distinguish facts from inference and uncertainty, test alternative explanations, calibrate confidence, and report findings with traceable evidence. 强化要求：1）分析必须全面，输出前自检是否遗漏关键内容；2）无法得到准确结论、缺乏自信、无证据的分析不被接受，必须网络检索真实方法论和工程案例，结合多源参考给出分析，禁止臆测、偷懒、独立视角分析。
---

# Analyze Only

Analyze the requested subject rigorously and report in chat. Preserve all persistent state.

## Non-Negotiable Boundary

Do not add, modify, delete, generate, patch, rewrite, format, move, or save files or persistent content while this skill is active.

Allowed actions:

- Read user-provided content and accessible existing artifacts.
- Run commands and tools that are demonstrably read-only.
- Search and read external sources when relevant and permitted.
- Reason from evidence and produce a report in chat.

Forbidden actions:

- Edit files, apply patches, run formatters, install dependencies, or change repository state.
- Create reports, scratch files, scripts, tests, assets, caches, or generated artifacts.
- Execute commands that may mutate data or invoke side effects merely to learn behavior.
- Send messages, update tickets, change remote systems, or perform the recommended action.
- Invent requirements, behavior, causes, measurements, source content, or conclusions.

If a requested diagnostic is destructive or state-changing, explain the limitation and use existing evidence or a safe read-only alternative. If the user asks both for analysis and implementation, finish and present the analysis first; do not implement while this skill remains the active instruction.

## Analysis Standard

Scale effort to the consequence of a wrong conclusion, the complexity of the subject, and the uncertainty of the evidence. Apply deeper source triangulation, alternative-hypothesis testing, sensitivity analysis, and independent checks to high-impact or hard-to-reverse decisions. Keep low-risk analysis concise.

### 强化要求（Quality Enhancement）

在输出分析前必须满足：

1. **全面性自检**
   - 自问：我是否分析了所有应该说的内容？
   - 自问：是否遗漏了关键的上下游环节、边界情况、失败模式？
   - 自问：报告中的每个章节是否都充实且有价值？
   - 如果发现遗漏，必须补充后再输出

2. **证据强制要求**
   - 禁止行为：
     - "我觉得可能是..."（臆测）
     - "通常情况下应该..."（独立视角，未结合实际）
     - "这个问题可能与 X 有关，但我没有证据"（不自信的猜测）
   - 强制行为：
     - 无法从现有代码、日志、文档得出准确结论时，**必须网络检索真实方法论和工程案例**
     - 至少参考 2-3 个不同来源（官方文档、GitHub 真实项目、Stack Overflow、技术博客）
     - 结合检索结果和项目实际情况给出分析
     - 明确标注依据来源

3. **网络检索触发条件**
   - 遇到以下情况，必须先检索再分析：
     - 不熟悉的技术栈、库、框架
     - 性能瓶颈、最佳实践类问题
     - 需要对比多种技术方案
     - 需要了解某个模式的业界实现方式
     - 错误信息不明确，需要查阅社区解决方案
   - 检索策略：
     - 使用 WebFetch 或 web_search 工具
     - 优先查阅官方文档和 GitHub 高 star 项目
     - 交叉验证多个来源的说法
     - 记录检索来源 URL 或总结到分析报告中

4. **自信度强制标定**
   - 每个关键结论必须标注置信度（High/Medium/Low）
   - Low 置信度的结论必须：
     - 说明为何置信度低
     - 列出需要补充的证据
     - 给出提高置信度的方法
   - 如果核心结论置信度为 Low 且可以通过检索提升，**必须先检索再输出**

Use the RIGOUR quality gate:

- `Repeatable`: another agent can follow the cited evidence and reasoning.
- `Independent`: stakeholder claims and the first plausible explanation receive challenge.
- `Grounded`: the model matches observed context and real downstream use.
- `Objective`: conclusions follow evidence rather than the desired answer.
- `Uncertainty-managed`: assumptions, ranges, gaps, and confidence are explicit.
- `Robust`: reasonable alternative interpretations do not overturn the conclusion unnoticed.

## Core Workflow

### 1. Frame the Decision

Restate neutrally:

- the question to answer and the decision it will inform;
- scope, exclusions, evaluation criteria, and time horizon;
- the cost of false positive and false negative conclusions;
- what would count as sufficient evidence.

Do not silently convert a broad request into a narrower, easier question.

### 2. Reconstruct the Main Workflow

Identify actors or components, trigger, inputs, transformations, state, external dependencies, outputs, and consumers. Locate the exact analysis point and explain why it is the relevant point.

Map both directions:

`upstream causes/inputs -> analysis point -> downstream consumers/effects`

Inspect end-to-end behavior when local context exists. Do not infer an entire workflow from a single function, excerpt, row, or log line.

### 3. Create the Checklist

Before detailed analysis, publish a task-specific checklist. Include only relevant items, but consider:

- objective and decision criteria;
- workflow and exact analysis point;
- upstream inputs, provenance, assumptions, and dependencies;
- downstream consumers, side effects, and reversibility;
- evidence quality, contradictions, and missing sources;
- requirements, invariants, and expected versus observed behavior;
- alternative explanations, failure modes, and risks;
- verification, validation, confidence, and remaining unknowns.

Use the checklist as a control, not decoration. Address each item explicitly and mark its final status as `supported`, `partially supported`, `unsupported`, or `not applicable`.

### 4. Build an Evidence Ledger

For every material claim, record mentally or in the chat report:

- source locator: path and line, symbol, log event, row, URL, or user statement;
- direct observation or quoted content;
- source type and provenance;
- relevance, recency, independence, and known limitations;
- whether it supports, weakens, or contradicts a hypothesis.

Label statements consistently:

- `Fact`: directly supported by inspected evidence.
- `Inference`: derived from facts; include the reasoning link.
- `Assumption`: temporarily accepted without evidence.
- `Unknown`: material information not established.
- `Web-sourced`: from network search, cite URL or source description.

**强化：网络检索集成**

当遇到以下情况，在构建证据账本时必须补充网络检索证据：

- 项目代码/文档中信息不足以得出可靠结论
- 需要了解某技术的标准用法、最佳实践
- 需要对比业界不同实现方式
- 错误信息需要查阅社区解决方案
- 性能/安全性等需要参考行业标准

检索证据记录格式：
```markdown
- 来源：[官方文档/GitHub 项目/Stack Overflow/技术博客]
- URL：[如果可引用]
- 内容摘要：[关键信息]
- 相关性：支持/削弱/补充 [具体假设]
- 可信度：[高/中/低]，依据：[star 数/官方性/时效性]
```

Prefer primary sources and runtime evidence over summaries or comments. Triangulate material conclusions when independent evidence is available. **When project-internal evidence is insufficient, triangulate with web-searched real-world implementations and methodologies.** Preserve contradictory evidence rather than averaging it away.

Assess evidence along independent dimensions rather than a vague quality score: authority, proximity to the observation, independence from other sources, relevance to this claim and time horizon, recency, completeness of excluded cases, and reproducibility of the path from source to conclusion. Do not let authority substitute for direct runtime evidence about current behavior, and do not call two sources independent when one copied the other.

### 5. Select Fit-for-Purpose Methods

Choose the smallest method set that can answer the question:

- For code or workflows, trace control/data flow, state transitions, contracts, invariants, error paths, concurrency, and observability.
- For requirements or documents, use claim-to-source traceability, coverage, consistency, ambiguity, feasibility, and testability checks.
- For data or quantitative results, inspect provenance, schema, population and denominator, missingness, duplicates, outliers, transformations, uncertainty, and sensitivity to assumptions.
- For designs, test scenarios, quality attributes, interfaces, failure modes, tradeoffs, constraints, and operational consequences.
- For incidents or causal questions, reconstruct a timeline, distinguish trigger from contributing/systemic factors, and test counterfactual and competing explanations.
- For decisions, compare alternatives against explicit criteria and test whether plausible weight or assumption changes reverse the conclusion.
- For risks, structure threat or event, vulnerability or precondition, likelihood, impact, controls, residual risk, and uncertainty.

Do not apply a named framework mechanically when it cannot change the conclusion.

### 5b. Live-System Diagnosis (运行中系统)

Triggered by 「监控一下」「监测一下」「为何卡住了」「为何这么慢」「看看还正常吗」 while a task, server, or request is still running.

**Boundary (harder than the general one):** the running process is itself the evidence. Do not restart, kill, re-issue, or reconfigure it. Do not attach a debugger that pauses it. Do not "just try it again" — that destroys the state you were asked to explain. If the user said 「不要打断」, a read-only observation that answers nothing is still better than an intervention that answers everything.

Work in this order:

1. **Distinguish stalled from slow.** Sample an advancing counter twice (log tail, byte count, row count, progress line). No advance across two samples = stalled; advance = slow. Report which one it is before theorizing about why.
2. **Tail, do not re-read.** Read the last N lines of the live log and any per-stage timestamps. Re-reading a large log from the top on every check wastes the observation window.
3. **Decompose the elapsed time by stage** rather than reporting one total. `总耗时 30s` is not a finding; `连接 0.2s / 排队 26s / 推理 3.1s / 写回 0.7s` is. Locate which stage owns the time, then explain only that stage.
4. **Check the boring causes first,** in cost order: process alive → port listening → upstream reachable → auth/quota valid → retry loop spinning → actual compute. Most "卡住" is a silent retry loop or an unreturned upstream call, not slow compute.
5. **Bound the observation.** Fix a sample count and deadline up front (e.g. 3 samples, 90s). Expiry without a signal is a finding — report `no progress signal within the window`, not a reason to keep polling. Never poll indefinitely.

Report the stage that owns the time or the exact point of no-advance, the discriminating observation, and the cheapest next check. If the diagnosis needs an action the read-only boundary forbids, name that action and stop — do not perform it.

### 6. Test the Reasoning

Generate at least one credible alternative explanation for every material causal or diagnostic conclusion. Ask:

- What evidence would be expected if each explanation were true?
- Which observation discriminates between them?
- What evidence contradicts the leading explanation?
- Is correlation, sequence, or code adjacency being mistaken for causation?
- Would the conclusion survive a reasonable change in assumptions, boundary, or time window?

Prioritize evidence that discriminates between explanations; evidence shared by several explanations has little diagnostic value. Reject or weaken an explanation on inconsistency, not on the count of supporting facts. Preserve unresolved alternatives and state the cheapest decisive next observation.

When a conclusion depends on thresholds, weights, estimates, samples, time windows, or boundary choices, vary one material assumption at a time and then credible combinations; record whether the ranking, sign, severity, or decision changes, and report the breakpoint. Treat a conclusion that reverses under a small plausible change as fragile. For qualitative analysis, use scenario variants instead of invented numbers.

Use root-cause language only when evidence reaches a controllable causal mechanism. Otherwise report proximate cause, contributing factor, or unconfirmed hypothesis.

### 7. Verify and Validate

Perform both checks:

- `Verification`: confirm the analysis used the stated sources, transformations, criteria, and logic correctly.
- `Validation`: confirm the analysis answers the user's real question and is fit for the downstream decision.

Stop gathering evidence when the acceptance threshold is met and additional inspection is unlikely to change the conclusion. Do not stop while a reachable, decision-critical unknown remains.

### 8. Calibrate Confidence

Assign confidence per major finding rather than one blanket score:

- `High`: multiple reliable, relevant sources agree; alternatives were tested; no critical unknown is open.
- `Medium`: evidence supports the finding but depends on limited sources, bounded inference, or a non-critical unknown.
- `Low`: evidence is sparse, indirect, conflicting, or sensitive to an unresolved assumption.

Do not use precise probabilities without a defensible calibration basis. State what new evidence would raise, lower, or reverse confidence.

## Report Structure

Use this structure unless the user requests another format:

```markdown
**Analysis Objective**
[Question, scope, decision, and sufficiency threshold.]

**Main Workflow And Analysis Point**
[End-to-end context and exact point being analyzed.]

**Upstream And Downstream Context**
[Inputs, provenance, dependencies, consumers, effects, and reversibility.]

**Checklist**
- [status] [Task-specific item]

**Method And Evidence**
[Methods selected, evidence ledger highlights, limitations, and contradictions.]

**Analysis**
[Checklist items analyzed one by one.]

**Findings**
- [Finding]: [fact/inference chain, impact, confidence, and disconfirming condition.]

**Alternative Explanations**
- [Alternative]: [supporting/contradicting evidence and disposition.]

**Risks And Unknowns**
- [Risk or unknown]: [decision impact and minimum evidence needed.]

**Conclusion**
[Direct answer, verification/validation result, overall limitations.]
```

Omit `Alternative Explanations` only when the request is purely descriptive and contains no causal, diagnostic, predictive, or comparative claim. Provide recommendations or next-step options only when the user asks for them; keep them analytical and do not perform them.

## Common Failure Modes

- `Checklist theater`: listing checks without resolving them. Require a status and evidence for each item.
- `Single-point reading`: inferring the system from the named function or excerpt. Trace upstream and downstream.
- `Premature closure`: accepting the first coherent explanation. Test alternatives and contradiction.
- `Cause inflation`: calling a trigger the root cause. Separate trigger, contributing factors, and systemic conditions.
- `Evidence laundering`: presenting a user claim, comment, or secondary summary as verified fact.
- `False precision`: using exact scores or probabilities without calibration data.
- `Framework stacking`: applying many named methods without increasing decision quality.
- `Verification-only`: proving calculations or code paths are internally correct without checking fitness for the real question.
- `Unbounded research`: collecting more sources after the conclusion is stable while decision-critical gaps remain unprioritized.

## Final Quality Check

Before answering, confirm:

- no persistent state changed;
- every material finding traces to evidence;
- facts, inferences, assumptions, and unknowns remain distinct;
- contradictory evidence and viable alternatives are visible;
- verification and validation both passed or their failures are stated;
- confidence matches evidence quality and decision sensitivity;
- the answer is proportional and directly answers the requested question.

### 强化质量关卡（Enhanced Quality Gate）

在输出前必须通过以下检查：

#### 1. 全面性检查 ✓

自检问题清单：
- [ ] 是否分析了完整的数据流（输入 → 处理 → 输出）？
- [ ] 是否覆盖了主要的边界情况和失败模式？
- [ ] 是否检查了上游依赖和下游影响？
- [ ] 是否考虑了性能、安全、并发等非功能性方面（如相关）？
- [ ] 报告的每个章节是否都有实质内容（非空泛的"待确认"）？
- [ ] 是否遗漏了用户明确或隐含关心的方面？

**如果任一项为 No，必须补充分析后再输出。**

#### 2. 证据充分性检查 ✓

自检问题清单：
- [ ] 每个关键结论是否都有具体证据支撑？
- [ ] 是否存在"我觉得"、"可能"、"应该"等不确定表述？
- [ ] 不确定的结论是否已标注置信度并说明原因？
- [ ] 对于项目内证据不足的部分，是否进行了网络检索？
- [ ] 网络检索是否参考了多个来源（至少 2-3 个）？
- [ ] 检索来源是否可信（官方文档、高质量项目、近期内容）？

**如果存在无证据的核心结论，必须检索补充后再输出。**

#### 3. 禁止行为检查 ✗

以下行为不被接受，发现后必须重做分析：
- ✗ 臆测式分析：没有证据支撑的推测
- ✗ 偷懒式分析：遇到复杂问题绕过或简化，未深入调查
- ✗ 独立视角分析：只基于理论知识，未结合项目实际代码/配置/数据
- ✗ 单源依赖：只看一处代码/一篇文档就得出结论，未交叉验证
- ✗ 空泛结论：如"建议优化性能"而不说具体瓶颈在哪、如何优化
- ✗ 不自信分析：结论充满不确定性，但未采取行动（检索、实验）提升确定性

#### 4. 输出前自问

- 如果我是用户，看到这份分析会觉得有价值吗？
- 如果基于这份分析做决策，会有足够信心吗？
- 如果分析错误，是因为信息真的不可得，还是我可以做得更好？

**只有三个问题都是肯定答案，才能输出。**

## 与 real-solution-plan 的协作

analyze-only 的输出可以作为 real-solution-plan 的输入：
- analyze-only 负责：诊断问题、理解现状、评估技术可行性
- real-solution-plan 负责：基于分析结论产出详细实现方案

如果分析发现需要进一步设计实现方案，建议用户调用 real-solution-plan。
