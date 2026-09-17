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

Prefer primary sources and runtime evidence over summaries or comments. Triangulate material conclusions when independent evidence is available. Search external sources with `WebFetch` or web search — before answering, not after — when project-internal evidence is insufficient, when the stack or the error is unfamiliar, when comparing approaches, or when a performance, security, or best-practice claim needs an industry baseline. Use at least two or three independent sources (official docs, high-star real projects, community reports) and record each one in this format:

```markdown
- 来源：[官方文档/GitHub 项目/Stack Overflow/技术博客]
- URL：
- 内容摘要：[关键信息]
- 相关性：支持/削弱/补充 [具体假设]
- 可信度：[高/中/低]，依据：[star 数/官方性/时效性]
```

If a core conclusion has no supporting evidence, search and supplement before answering. Preserve contradictory evidence rather than averaging it away.

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

Do not use precise probabilities without a defensible calibration basis. State what new evidence would raise, lower, or reverse confidence. A `Low` finding must name why the confidence is low, what evidence is missing, and how to obtain it; if a core conclusion is `Low` and a search could raise it, search before answering rather than shipping the hedge. An unsupported statement is an `Unknown`, not a confidence level: do not hedge with "I think maybe", "usually it should", or "this may relate to X but I have no evidence" — either ground it, label it `Unknown`, or drop it.

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

These are defects, not style preferences: a report that exhibits any of them is redone, not annotated.

- `Checklist theater`: listing checks without resolving them. Require a status and evidence for each item.
- `Single-point reading`: inferring the system from the named function or excerpt. Trace upstream and downstream.
- `Premature closure`: accepting the first coherent explanation. Test alternatives and contradiction.
- `Cause inflation`: calling a trigger the root cause. Separate trigger, contributing factors, and systemic conditions.
- `Evidence laundering`: presenting a user claim, comment, or secondary summary as verified fact.
- `False precision`: using exact scores or probabilities without calibration data.
- `Framework stacking`: applying many named methods without increasing decision quality.
- `Verification-only`: proving calculations or code paths are internally correct without checking fitness for the real question.
- `Unbounded research`: collecting more sources after the conclusion is stable while decision-critical gaps remain unprioritized.
- `Complexity avoidance`: simplifying or routing around a hard problem instead of investigating it.
- `Theory-only reasoning`: concluding from general principles without checking the project's actual code, configuration, or data.
- `Single-source reliance`: concluding from one file or one document without cross-verification.
- `Un-actioned low confidence`: declaring low confidence without naming the evidence that would resolve it.
- `Vague conclusion`: recommending a direction ("optimize performance") without naming the bottleneck, the mechanism, or the measurable target.

## Final Quality Check

Before answering, run this gate — the RIGOUR check: `Repeatable`, `Independent`, `Grounded`, `Objective`, `Uncertainty-managed`, `Robust`.

- **Repeatable** — no persistent state changed, and every material finding traces to evidence another agent could follow;
- **Independent** — stakeholder claims and the first plausible explanation were both challenged;
- **Grounded** — the model matches observed context and real downstream use; verification and validation both passed or their failures are stated;
- **Objective** — the conclusion follows the evidence rather than the hoped-for answer;
- **Uncertainty-managed** — facts, inferences, assumptions, and unknowns remain distinct, and confidence matches evidence quality and decision sensitivity;
- **Robust** — contradictory evidence and viable alternatives are visible; a reasonable alternative interpretation does not overturn the conclusion unnoticed;
- the data flow (input → processing → output), the boundary and failure cases, upstream dependencies and downstream effects, and any relevant performance, security, or concurrency aspect were each examined;
- every report section carries substance rather than an empty "to be confirmed";
- nothing the user asked about, explicitly or implicitly, was left unexamined;
- the answer is proportional and directly answers the requested question.

If any item above fails, fix it and re-analyze before answering — do not emit the report with an unresolved item.

## 与 real-solution-plan 的协作

analyze-only 的输出可以作为 real-solution-plan 的输入：
- analyze-only 负责：诊断问题、理解现状、评估技术可行性
- real-solution-plan 负责：基于分析结论产出详细实现方案

如果分析发现需要进一步设计实现方案，建议用户调用 real-solution-plan。
