---
name: mission-spliter
description: Split clarified requirements into phased missions AND accept each phase as it completes. Plans stage goals, deliverables, dependencies, task order, and a per-phase acceptance gate; then, after each phase is implemented, runs that gate against real evidence (Pass/Partial/Fail) before the next phase may start, and finally rolls phase verdicts up into one delivery acceptance. Use after requirements are clarified (by the user or Initer), before and during implementation of a project, major feature, workflow, integration, refactor, or multi-step task. If requirements are still unclear, hand back to clarification before splitting.
---

# Mission Spliter & Acceptor

This skill owns two jobs that used to be split across planning and a final acceptance gate:

1. **Plan** — turn clarified requirements into an executable phased plan.
2. **Accept per phase** — verify each phase against real evidence at its own gate, the moment that phase is implemented, before the next phase starts. The final delivery acceptance is a rollup of the phase verdicts plus cross-cutting checks, not a separate end-of-project scramble.

Verification is pushed to where the work happens. "Not run" is never "pass." A phase is not done until its gate is green.

## Core Rule

Do not split vague work. First verify the requirement boundary is clear enough to plan. If goal, scope, acceptance criteria, main workflows, data/state, or technical constraints are unclear, ask targeted questions or hand back to Initer before creating stages.

Once planning starts, every phase must carry a **concrete, executable acceptance gate** defined up front — the exact command, check, screenshot, or observation that will prove the phase works. A gate you cannot execute is not a gate; rewrite it until it is checkable.

## Required Inputs

Collect or infer: original request; clarified requirements or Initer build brief; included/excluded scope; acceptance criteria; technical constraints and repo conventions; known dependencies, blockers, risks, deadlines; verification expectations.

If an input is missing but low risk, state the assumption. If it can change the plan meaningfully, ask before splitting.

## Workflow

### 1. Confirm Planning Readiness

State: `Ready` | `Needs Clarification` | `Blocked`. Do not split a `Blocked` mission.

### 2. Define The Mission

Summarize goal, final deliverable, success criteria, out-of-scope items, primary risks. Reference the single source of truth (the build brief / project record) — do not re-author scope prose that already exists elsewhere; link to it and note only deltas.

### 3. Split Into Phases

Prefer 3-6 phases for substantial work; fewer for small features. Each phase must be an **independently inspectable unit of real behavior** — not a template slot. If two "phases" touch the same file with no separately verifiable outcome between them, merge them.

Each phase includes:

- Objective.
- Deliverables.
- Tasks (ordered by dependency).
- Dependencies (what must exist first).
- **Acceptance gate** — the concrete, executable check that proves this phase, with its expected result. Specify the method (command/test/screenshot/observed behavior) and the pass condition.
- Exit criteria.
- Risks / unknowns.

### 4. Order Tasks By Dependency

Within each phase: discovery → architecture/interface decisions → data model/contracts → core implementation → external surfaces/UI → verification → record update → phase acceptance. Adjust to fit the project.

### 5. Execute Each Phase With Its Gate

For every phase, in order:

1. Implement the phase tasks.
2. Update the Recoder record for the phase's change points (including the work path / problem-solving notes Recoder now captures).
3. **Run the phase acceptance gate against real evidence** using the rubric below. Capture the evidence (command output, test result, screenshot, observed behavior) — do not assert success from code reading alone when the behavior is observable.
4. Mark the phase `Pass` / `Partial` / `Fail`. Only a `Pass` (or an explicitly user-accepted `Partial`) unlocks the next phase. A `Fail` stays in the current phase until fixed.

This replaces the old "verify everything at the end" model. By the time the last phase passes, delivery is already substantially verified.

### 6. Final Rollup Acceptance

After the last phase, produce the delivery acceptance as a **rollup**, not a re-do:

- Aggregate the per-phase verdicts.
- Run only the cross-cutting checks that no single phase covered: end-to-end workflow, security/privacy constraints, handoff readiness, and that excluded scope was not accidentally built.
- Confirm the Recoder record is complete and non-contradictory.
- Decide overall status: `Pass` | `Conditional Pass` | `Fail`.

## Per-Phase Acceptance Rubric

Apply at each phase gate and at the final rollup.

Mark each checked item:

- `Pass`: implemented and verified with real evidence.
- `Partial`: works with a stated, non-blocking limitation.
- `Fail`: missing, broken, or contradicted by evidence.
- `Not Verified`: likely done but unchecked — treat as not done; either verify now or justify explicitly.
- `Out Of Scope`: explicitly excluded/deferred.

Evidence standard (match verification to risk):

- Run automated tests / build / lint / typecheck where available.
- Exercise the main workflow manually when behavior is observable.
- For visual or interactive work, capture a screenshot or drive the running app — do not accept "the code looks right."
- Cover edge cases and failure states that were in scope.
- Every `Partial` / `Fail` / `Not Verified` gets a concrete reason and next action.

Be strict about user-facing correctness, data integrity, security, and that the record matches reality.

## Decision Statuses (Final Rollup)

- `Pass`: all acceptance-critical items implemented, verified, recorded; only low-risk follow-ups remain.
- `Conditional Pass`: core goal works; non-blocking gaps remain (partial docs, deferred scope, minor polish) — state exactly what is and isn't accepted.
- `Fail`: any acceptance-critical item missing, broken, unverified at unacceptable risk, undocumented enough to block handoff, or contradicted by the record. State the minimum fixes required.

## Splitting Heuristics

- Put uncertain or high-risk work early.
- Put irreversible migrations, destructive changes, and public-interface changes behind explicit gates.
- Separate foundation from feature behavior; keep phases small enough to validate, large enough to matter.
- Mark tasks parallel-safe only when files/data/responsibilities are disjoint.
- Fold the Recoder update and the acceptance gate into each phase — they are phase work, not afterthoughts.
- Where it helps execution, emit the phases as tasks via your environment's task tracker instead of keeping a parallel markdown list, so plan and tracker are one thing.

## Output Template

Use `assets/mission-split-plan-template.md`. It carries the per-phase acceptance gate and the rollup section.

## Final Planning Rules

- If the user asked for execution, start after presenting the plan when no blocking clarification remains; then execute phase-by-phase with gates.
- If the plan depends on user approval (preference/product judgment), stop after the plan and ask.
- Log plan creation and each phase's completion + acceptance verdict in the Recoder record.
- The final response leads with the rollup decision, names the strongest evidence and the most important gap, and never hides skipped checks or unresolved risks.
