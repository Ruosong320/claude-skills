---
name: ship-it-for-real
description: "Use only when the user explicitly invokes /ship-it-for-real or asks Claude to use ship-it-for-real for an authorized execution task that should be carried through implementation, recovery, and evidence-based completion. Use when there is NO pre-confirmed written plan — this skill supplies risk tiering, a retry budget, bounded monitoring, and terminal-state judgement. If a confirmed plan from real-solution-plan already exists and the job is to follow it faithfully, use ship-solution instead. Do not use for analysis-only requests, open-ended monitoring, or as permission for external or destructive actions."
---

# Ship It For Real

Carry the requested work to an evidenced terminal state without expanding its
scope or authority. This skill adds execution closure, not domain expertise or
background execution.

## Establish The Contract

Before changing state, derive the goal, scope, invariants, acceptance criteria,
and evidence from the request and inspected context. Keep this implicit for
simple work; use a table only when several criteria affect completion.

Discover technical details without asking. Ask one decision-ready question only
when the answer changes business truth, authorization, irreversible impact, or
a material tradeoff. Do not shrink acceptance scope to fit a chosen budget.

## Scale Assurance To Risk

Apply only the highest applicable level:

- **Local reversible:** ordinary workspace edits and read-only inspection.
  Inspect the target and proceed; keep rollback diff-based and run the smallest
  direct check.
- **Shared recoverable:** persistent or shared state with a practical reversal.
  Confirm the target, prefer an idempotent or isolated unit, define rollback and
  its success signal, then verify post-change health.
- **High impact:** destructive or irreversible work, production writes,
  privileged changes, material paid actions, or meaningful data-loss risk.
  Require explicit authorization for the exact action; do not ask again when
  the current instruction already provides it. Require a usable backup, dry
  run, staged execution, or equivalent safeguard; define abort criteria and a
  post-change observation window.

External read-only access stays at the lowest level unless privacy, privilege,
or material cost raises it. Permission is not proof of success. If a safeguard
is unavailable, do not act — take the row beginning *A required safeguard is
unavailable at the level the action needs* in `When The Execution Cannot Proceed
As Specified`. Never expose secrets or unnecessary personal data.

On an abort criterion or health regression, stop and run the prepared rollback
when authorized and safer, then verify its signal. Otherwise preserve evidence
and mark the action blocked rather than improvising a riskier recovery.

**🔴 CHECKPOINT — run this before the first state-changing action, and again whenever the working unit grows. Any "yes" to 1-2: apply the named level above, in full. Any "yes" to 3: stop and get the expansion authorized.**

1. **Is the action destructive, irreversible, production-facing, privileged, or materially paid, or does it carry meaningful data-loss risk?** → *High impact*.
2. **Is the target shared or persistent state with a practical reversal?** → *Shared recoverable*.
3. **Would the next unit expand the scope or the authority the request actually granted?** → stop; take the row beginning *The action cannot succeed without authority the request did not grant* in `When The Execution Cannot Proceed As Specified` — state the real boundary and get that expansion authorized before acting.

## Work In Verified Units

Use a small-batch feedback loop:

1. Inspect the real state, actual entry point, and relevant downstream effects.
2. Make the smallest coherent change that advances the goal.
3. Verify that unit immediately with evidence appropriate to its risk.
4. Continue only after interpreting the result; recover or stop if advancing
   would compound uncertainty.

Prefer project-native tools and tests. Preserve user changes and avoid unrelated
cleanup.

Before substantial work, bound elapsed work, command duration, external cost,
concurrency, and unresolved failure mechanisms according to risk. Keep ordinary
local bounds implicit, honor stricter user limits, and stop at any bound — take
the row beginning *A bound is reached with the work incomplete* in `When The
Execution Cannot Proceed As Specified` for what to report.

For one failure mechanism, permit one baseline attempt and at most two retries.
Every retry must change a condition capable of producing new evidence. Diagnosis
does not reset the count; only evidence of a different mechanism does. Do not
stack speculative patches, repeat an unchanged command, or poll indefinitely —
take the row beginning *The retry budget is exhausted and the failure mechanism
is unchanged* in `When The Execution Cannot Proceed As Specified`.

When a check fails:

1. Preserve the evidence and state expected versus actual behavior.
2. Trace to the earliest confirmed divergence across callers, state, consumers,
   and error paths; test the suspected cause against a credible alternative.
3. Fix the earliest shared cause, then verify the reported case and a relevant
   sibling or boundary case when material.

## Verify, Then Validate

Keep two questions distinct:

- **Verification:** does the result satisfy the specified requirement?
- **Validation:** does it work for the user's intended purpose in the real use
  context?

Map each criterion to direct evidence from the real entry point and target. Use
observed behavior, artifacts, diffs, tests, metrics, or screenshots, with
isolated reproducible checks when feasible.
Compilation, mocks, exit status, source inspection, model confidence, and user
silence prove only what they directly cover. If the real check is unavailable,
state the evidence gap instead of substituting a weaker check without notice —
take the row beginning *The real check for a required criterion is unavailable*
in `When The Execution Cannot Proceed As Specified`.

Add security, performance, concurrency, durability, migration, or rollback
checks only when the changed contract or risk calls for them.

## Bound Monitoring And Continuation

Monitor only toward a terminal state. Define the signal, success and failure
thresholds, deadline, no-data rule, and stop action. A missing signal or expired
deadline is evidence, not a reason to keep polling — take the row beginning *The
monitoring signal never arrives, or the observation window ends with no data* in
`When The Execution Cannot Proceed As Specified`. For resumable work, reuse
existing project logs; on resume, inspect current instructions and actual state
before continuing — when the actual state contradicts them, take the row
beginning *On resume, the actual state contradicts the record or the
instructions*.

## Assign The Terminal State

Give each required criterion one state: `PASS`, `FAILED`, `BLOCKED`, or
`NOT_VERIFIED` (`PARTIAL` below is an overall state, not a criterion state).
Determine the overall state in this order:

1. `FAILED` if evidence disproves any required criterion and no safe permitted
   recovery remains within the execution bounds.
2. `PASS` if every required criterion and applicable safety check passes.
3. `PARTIAL` if a safe coherent unit passes but required work remains blocked or
   unverified.
4. `BLOCKED` if no coherent unit can proceed because a prerequisite is missing.
5. `NOT_VERIFIED` if output exists but evidence is inadequate to establish a
   reliable result.

**🛑 STOP — assign the state before writing the final report. A `PASS` requires direct evidence covering that criterion. When the covering check was unavailable, that criterion is `NOT_VERIFIED`; when it was unavailable because a prerequisite is missing, it is `BLOCKED`. Never `PASS`.**

Use the first matching state. Never present a non-`PASS` result as complete.

## When The Execution Cannot Proceed As Specified

The workflow above assumes the required safeguard exists, the real check is
reachable, the bounds hold, and the authority covers the action. When that does
not hold, handle it by this table — never improvise a riskier path.

**This section is the exception clause for the workflow above: where it
conflicts with "If a safeguard is unavailable, do not act", the retry budget in
Work In Verified Units, "stop at any bound", "state the evidence gap instead of
substituting a weaker check", the no-data rule in Bound Monitoring And
Continuation, or the authority boundary in Scale Assurance To Risk, this table
governs — but only where one of its rows actually conflicts with that rule; a
rule no row conflicts with keeps its full force. When one situation matches
more than one row, take the row whose first-line fix is the most conservative —
a row that stops, asks, or declines to act outranks any row that proceeds.
Every exception must still be stated in the final report.**

| Trigger | First-line fix | Fallback if that fails |
|---|---|---|
| A required safeguard is unavailable at the level the action needs | Do not act. Find a lower-risk equivalent that still meets the goal, or substitute a genuine safeguard — a dry run, staged apply, verified backup, or isolated copy | If nothing can substitute, mark `BLOCKED` and name exactly what would have to change for the action to become safe |
| The real check for a required criterion is unavailable | State the evidence gap, mark that criterion `NOT_VERIFIED`, and say what the closest available check actually covered | If the criterion is required and cannot be verified at all, the overall state cannot be `PASS`; report `PARTIAL` and name the exact remainder |
| The retry budget is exhausted and the failure mechanism is unchanged | Stop. Preserve the evidence, state expected versus actual, and report the earliest confirmed divergence | If the user grants more budget, proceed only behind a changed condition capable of producing new evidence — never a repeat of the same attempt |
| A bound is reached with the work incomplete | Stop at the bound and report the coherent completed unit | Mark `PARTIAL`, name the exact remainder, and let the user decide whether to extend the bound. Do not extend it silently |
| The action cannot succeed without authority the request did not grant | Stop before acting. Name the exact authority needed and what it would enable | Deliver the in-authority portion, mark the rest `BLOCKED`, and state the boundary explicitly |
| On resume, the actual state contradicts the record or the instructions | Re-derive from the actual state before continuing, and say what diverged | If the divergence is material and cannot be resolved, report it as the finding rather than proceeding on the stale assumption |
| The monitoring signal never arrives, or the observation window ends with no data | Treat the missing signal as evidence. Stop monitoring and report what was and was not observed | If the no-data rule leaves the outcome undetermined, assign `NOT_VERIFIED` rather than assuming success |

## Do Not

- Do not act first and reconcile the checkpoint afterwards — a check run after the action it guards is not a check.
- Do not act at any level while that level's required safeguard is unavailable.
- Do not present a non-`PASS` result as complete, and do not substitute a weaker check for an unavailable real one without saying so and stating the evidence gap.
- Do not shrink the acceptance scope to fit the budget you chose.
- Do not expand scope or authority past what the request granted.

## Report Only What Matters

Report only meaningful progress, evidence, risk, and the next action. Finally
state the outcome, checks, exact remainder, applicable rollback evidence, and
remaining risk or user decision.

For `FAILED` or `BLOCKED`, include the verified facts, attempts and changed
conditions, unresolved cause, exact boundary, and cheapest next evidence. For
`PARTIAL`, name the coherent completed unit and exact remainder.
