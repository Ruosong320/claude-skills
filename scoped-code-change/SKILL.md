---
name: scoped-code-change
description: Use when an agent needs to modify a local, specific, or partial area of a program, script, app, config, test, or code-adjacent text. Trigger for fixing one feature, changing a function/module/component, adjusting bounded behavior, or making a minimal patch. Derive the boundary from the request and repository, ask only about unresolved consequential decisions, then locate the smallest change point, match local style, patch, and smoke test immediately.
---

# Scoped Code Change

## Core Rule

Derive the goal, scope, constraints, acceptance criteria, and verification method from the user's request, repository instructions, existing implementation, and tests. If the change is clear, reversible, authorized, and verifiable, investigate and implement without a questionnaire or confirmation round.

Ask one concrete question only when an unresolved answer would change business behavior, a consequential tradeoff, authority, permission, external impact, or an irreversible action. Do not ask the user for discoverable paths, local conventions, ordinary tool choices, relevant tests, or confirmation of reasonable reversible assumptions.

If the request is for read-only analysis, keep it read-only. If the user says "just do it", proceed within the stated and discoverable boundary unless a material decision still requires the user.

## Workflow

1. Establish the boundary.
   - Derive the clarification checklist from available evidence.
   - Inspect files and trace the current behavior when that can resolve uncertainty.
   - Ask only about a remaining material decision; otherwise proceed.

2. Locate the smallest change point.
   - Read the relevant code before proposing edits.
   - Use fast search first (`rg`, `rg --files`) to find symbols, routes, tests, configs, and call sites.
   - Trace behavior far enough to understand ownership boundaries and side effects.
   - Name the minimal edit surface before changing files: target files, relevant functions/classes/components, and why these are sufficient.

**🔴 CHECKPOINT — before the first write, and again whenever the edit surface changes, run this check. Any "yes": work from the named row of the `When The Scoped Workflow Breaks` table before patching, instead of patching first and reconciling later.**

- **Is this irreversible — something that cannot be undone?** → the row beginning *The edit turns out to be irreversible*.
- **Is the named change point one of several callers of the same broken logic?** → the row beginning *The named change point is one of several callers of the same broken logic*.
- **Has the investigation widened the scope past the request?** → the row beginning *The investigation widens the change beyond the request*.

3. Patch in the local style.
   - Match the surrounding file's programming habits: naming, control flow, abstraction level, error handling, comments, formatting, import order, and test style. If the file has no settled convention, or the surrounding style is inconsistent, take the row beginning *Local style is inconsistent* in `When The Scoped Workflow Breaks`.
   - Match the user's writing and language habits in strings, prompts, docs, comments, and commit-like text.
   - Keep changes narrow. Avoid drive-by refactors, broad rewrites, new dependencies, or style normalization unless required for the acceptance criteria.
   - Preserve unrelated user changes in the worktree. If unrelated user changes already sit on the files being patched, take the row beginning *Unrelated user changes already sit in the worktree*.

4. Smoke test immediately.
   - Run the smallest meaningful verification right after the edit: focused unit test, targeted command, lint/typecheck for touched area, local script invocation, or a manual/browser check for UI work.
   - If no existing test applies, perform a lightweight behavioral smoke test that exercises the changed path.
   - If the smoke test cannot run, explain the concrete blocker and say what the closest verification available actually covered. When nothing covered the changed path, take the row beginning *"Done" cannot be checked from anything available* in `When The Scoped Workflow Breaks` before reporting.

**🛑 STOP — report the outcome from the check that actually ran. A green result from a check that does not cover the changed path is not a pass; when no check covered it, name exactly what was left uncovered.**

5. Report tersely.
   - State what changed, where, and which acceptance criteria it covers.
   - Include the smoke test command/result.
   - Mention remaining risks only when they are real and actionable.

## Clarification Checklist

Use this checklist internally to identify the change boundary. It is not a mandatory user questionnaire. Ask only for an item that remains materially ambiguous after inspecting available context.

1. Trigger or bug: what exact behavior is wrong, or what local change is requested.
2. Scope: which feature, file, route, function, component, script, or config is in bounds — and what is explicitly out of bounds.
3. Expected result: what output, UI behavior, API response, data shape, or side effect should happen after the change.
4. Inputs/outputs: the concrete inputs, outputs, and edge cases the changed path must handle.
5. Constraints: what must stay unchanged (compatibility, public API shape, data format, performance, dependencies, style).
6. Style/language: which existing code, writing, and language conventions to match.
7. Verification: how success should be checked, and which smoke test or command counts as "done".
8. Acceptance criteria: the user's explicit definition of done.

Rules for using the checklist:

- Prefer one decision-ready question with concrete options when user input is necessary; if options cannot be offered, ask for a short description instead.
- Do not dump the checklist, repeat answered questions, or ask for confirmation merely because an assumption exists.
- State non-consequential assumptions while proceeding when they help the user review the result.

## Minimal Change Heuristics

- Prefer changing an existing local function over introducing a new abstraction.
- Prefer adapting an existing test over adding a broad new test suite.
- Prefer existing helper APIs over reimplementing logic.
- Prefer data-structure-aware parsing over ad hoc string edits when the file format has a parser already used by the project.
- Prefer a tiny compatibility wrapper only when call sites are numerous and changing them would increase risk.

## Smoke Test Selection

Choose the first available verification that directly covers the changed path:

1. Focused existing test for the touched function/module/component.
2. Targeted script or command that reproduces the behavior.
3. Typecheck/lint/build for the smallest relevant package.
4. Browser/manual check for changed UI behavior.
5. Minimal ad hoc invocation when the project has no ready test.

Do not claim full validation from a weak smoke test. Say exactly what was and was not covered.

## When The Scoped Workflow Breaks

The workflow assumes the change stays small, reversible, and verifiable. When it turns out otherwise, handle it by this table — do not keep patching and hope.

**This section is the exception clause for the workflow above: where it conflicts with the Core Rule ("investigate and implement without a questionnaire or confirmation round"), step 2's "before changing files", step 3's "keep changes narrow", or step 4's "run the smallest meaningful verification", this table governs — but only where one of its rows actually conflicts with that rule; a rule no row conflicts with keeps its full force. When one situation matches more than one row, take the row whose first-line fix is the most conservative — a row that stops, asks, or declines to write outranks any row that proceeds. Every exception must still be named in the report.**

| Trigger | First-line fix | Fallback if that fails |
|---|---|---|
| The named change point is one of several callers of the same broken logic | Fix it once at the shared function every caller routes through, and list the affected callers in the report | If the shared fix would change behavior for callers outside the stated scope, stop and state the blast radius before patching |
| The investigation widens the change beyond the request — multi-file, architectural, or a public-interface change | Stop and report the real scope together with the evidence that widened it, then ask whether to proceed scoped or expand | If the user is unreachable and the work is reversible, do the narrowest slice that stands on its own and state explicitly what was left out |
| Local style is inconsistent, or the file has no settled convention | Match the dominant pattern within the same file, then the nearest sibling file | If it is still ambiguous, match the surrounding block and say which convention was chosen |
| The edit turns out to be irreversible — schema migration, file deletion, public-interface or published-data change | Stop before writing. Name what cannot be undone, what the rollback would cost, and get confirmation | If it was already applied, say so immediately with the exact reversal steps. Never attempt a second silent edit to cover it |
| Unrelated user changes already sit in the worktree on the files being patched | Read the current content first and patch around them; never revert or reformat them | If the user's edits conflict with the required change, stop and show the conflict rather than picking a side |
| "Done" cannot be checked from anything available | Before patching, propose one concrete check and agree on what counts as done. If the patch already landed and no available check covers it, do not substitute a weaker claim — name exactly what was left uncovered | If no check is possible at all, say the change is unverifiable and state what a reviewer should inspect by hand |
