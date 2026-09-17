---
name: recoder
description: Maintain a durable project record for substantial work that spans sessions, changes architecture/interfaces/data, contains consequential decisions or failed approaches, or is explicitly requested for later handoff or methodology distillation. Capture both project state and the work path. Do not trigger for ordinary short or local changes, and do not require a record before such changes.
---

# Recoder

Recoder keeps one authoritative project record current while work happens. It records two layers:

- **State layer — what the system IS.** Architecture, flows, interfaces, data, dependencies, and a change log of what changed. So a newcomer can understand and continue the project.
- **Work-path layer — HOW the agent got there and WHY.** The problems encountered, the options weighed, the attempts that failed, the fix that worked, the root cause, and the generalizable method or pitfall learned. So that later a separate methodology-distillation skill can read many of these records and sediment them into reusable methodology skills.

The work-path layer is the priority and the differentiator. Most records capture only the final state; the value here is capturing the *journey* — especially the dead-ends and the reasoning — because that is where transferable method lives. A clean final diff teaches little; "we tried X, it failed because Y, so the rule is Z" teaches a lot.

## Activation And Record Path

First decide whether the work qualifies: it is substantial, cross-session, architecture/interface/data changing, contains a consequential decision or meaningful failed path, or the user explicitly requested a durable record. If it does not qualify, do not activate Recoder and do not block the task.

For qualifying work, resolve the record path from existing evidence:

- If the user gave a path in this conversation, use it.
- Search project instructions and conventions such as `PROJECT_RECORD.md`, `RECORDER.md`, `.codex/record.md`, or an existing documentation location; use an established path without asking for confirmation.
- If no convention exists and a new record is in scope, propose one concrete default such as `PROJECT_RECORD.md` and proceed when creation is reversible and authorized.
- Ask one question only when the location changes published project structure, ownership, permission, or task scope.

Keep using the same path for the project unless told to change.

**🔴 CHECKPOINT — before creating a record file, restructuring an existing one, or appending in a way that changes its structure, run this check. Any "yes": work from the named row of the `When The Record Cannot Be Maintained As Specified` table before writing, instead of writing first and reconciling later.**

- **Is the path a guess rather than a resolved value?** The precedence above or the user decides it, never a plausible-sounding default picked mid-task. → the row beginning *The record path is ambiguous*.
- **Is this user-authored content about to be restructured?** → the row beginning *The required change would restructure user-authored content*.
- **Is the target outside a writable area?** → the row beginning *The record would be created inside a directory the user marked read-only*.

## Record File Setup

1. Read the current record if it exists. If it exists but its structure differs from the template, take the row beginning *The record exists but its structure differs from the template* in `When The Record Cannot Be Maintained As Specified`.
2. If absent, create it from `<this skill's directory>/assets/record-template.md`. If that file is unreachable, take the row beginning *`<this skill's directory>/assets/record-template.md` is unreachable*.
3. Fill the `Metadata` fields as named in `<this skill's directory>/assets/record-template.md`: project, repository root, record file, created, last updated, maintainer agent, current task.
4. Single source of truth: scope/brief and architecture live HERE. Other skills (planner, README) should reference this record, not re-author it. Preserve user-authored content; append and update, do not rewrite history unless asked to clean up.

## What To Record — State Layer

Record every completed change point: added/modified/renamed/moved/deleted files; functions, classes, components, routes, commands, scripts, migrations, schemas, prompts, styles, tests, docs; dependency/config/build/deploy/tooling changes; architecture decisions, interface contracts, data-flow and behavioral changes; bug/test fixes and risks introduced or resolved.

Group tiny mechanical edits into one change point when they share intent and verification. Record user-facing behavior, shared interfaces, architecture, data models, and risky code separately.

## What To Record — Work-Path Layer (priority)

For qualifying work, capture an **episode** when a hypothesis was tested, an approach was chosen over meaningful alternatives, something failed before it worked, a non-obvious root cause was found, or an assumption was falsified. Routine commands and obvious local edits are not episodes.

For each episode, capture honestly — **including failures and abandoned paths** (these are the most valuable for methodology and must not be edited out to look clean):

- **Trigger / problem** — what prompted this, the symptom or goal.
- **Context & constraints** — what was true that shaped the choice (repo conventions, task size, user preference, environment limits).
- **Options considered** — the candidate approaches, and **why the rejected ones were rejected**.
- **Attempts & dead-ends** — what was tried, in order, including what failed and the observed failure (error, wrong output, blocked tool). Note the diagnostic step (search/command/read) that produced the insight.
- **Resolution** — what actually worked.
- **Root cause / why it worked** — the underlying reason, not just the surface fix.
- **Reusable method or pitfall** — the generalizable, project-independent lesson. Phrase it so a future agent on a *different* project could apply it. Tag it (see Methodology Signals).
- **Evidence** — command output, test result, screenshot, observed behavior.

Also record decision points that did not involve failure: a deliberate trade-off, a scoping call, a chosen abstraction level, a why-not. These are decisions worth transferring even when nothing broke.

## Methodology Signals (for downstream harvest)

So a later consolidation skill can scrape reusable knowledge mechanically, tag transferable lines with these inline markers. Keep them on their own line, one idea each, phrased project-independently:

- `#method:` a reusable technique or procedure that worked.
- `#pitfall:` a trap, failure mode, or anti-pattern to avoid, with the tell that signals it.
- `#decision:` a trade-off rule — when to choose A over B.
- `#heuristic:` a rule of thumb for judgment calls (e.g. when to abstract, when to verify visually).

Each tagged line should stand on its own without the surrounding episode — the consolidation skill may extract it in isolation. Bad: `#method: fixed it`. Good: `#method: to verify interactive UI without a test driver, drive the page with headless Chrome --screenshot via a throwaway probe page, then delete the probe.`

## Update Discipline

After each change point or episode, in the same turn before moving on:

1. Append the State-layer entry under `Change Log`.
2. Append the Work-path episode under `Work Path & Problem-Solving Log` (with tagged signals).
3. Update affected durable sections (`Architecture Map`, `Key Flows`, `Data Model & State`, `Public Interfaces`, `Dependency & Configuration Map`, `Testing & Verification`, `Known Risks, Assumptions, And Open Questions`) — the names as they appear in `<this skill's directory>/assets/record-template.md`.
4. Use concrete paths and the specific symbols/routes/commands/sections touched.
5. Record verification results; if a check was not run, say so and why ("not run" ≠ "passed").
6. Keep the final user response consistent with the record.

Failure conditions that surface at write time rather than at setup: When one appears, take its row of `When The Record Cannot Be Maintained As Specified` instead of forcing the entry through: the write itself fails or the file is locked (the row beginning *The write fails part-way*), the entry would carry a credential or private material, or the record already contains one (the row beginning *The work path contains a credential*), the record has grown past scanning (the row beginning *The record has grown too large to scan*), or the session is ending before the update lands (the row beginning *A session is ending with the record not yet updated*).

## When The Record Cannot Be Maintained As Specified

The discipline above assumes a single writable record, a reachable template, and a session that ends cleanly. When it does not hold, handle it by this table — never skip the record silently.

**This section is the exception clause for the discipline above: where it conflicts with "Keep using the same path for the project", "append and update, do not rewrite history", step 2 of Record File Setup ("create it from the template"), "ask one question only when the location changes published project structure, ownership, permission, or task scope", the "scope/brief and architecture live HERE" half of the single-source-of-truth rule in Record File Setup (its "other skills should reference this record" half stands), or any step of Update Discipline, this table governs. Any rule this table does not touch keeps its full force. When one situation matches more than one row, take the row whose first-line fix is the most conservative — a row that stops, asks, or declines to write outranks any row that proceeds. Every exception must still be stated in the final response.**

| Trigger | First-line fix | Fallback if that fails |
|---|---|---|
| The record path is ambiguous, or the repo already holds several candidate record files | Take the first match by the precedence order above and write the resolved path plus the reason why into the record metadata | If several files already carry real content, pick the richest as the single source of truth and add a one-line pointer in the others. Never double-write |
| The record exists but its structure differs from the template | Keep the existing structure; add only the template sections that are missing | If the structures cannot be reconciled, add one mapping section saying which existing section answers which template section. Do not restructure the user's sections |
| The required change would restructure user-authored content rather than append to it | Stop before writing. Name exactly what would be restructured and why, and get the user's confirmation for that specific restructure | If the user does not confirm, append alongside the existing content instead of rewriting it. Never rewrite their sections |
| `<this skill's directory>/assets/record-template.md` is unreachable | Build the skeleton inline from this skill's section names: `Change Log`, `Work Path & Problem-Solving Log`, `Reusable Methods & Pitfalls`, plus the durable sections | If the record still cannot be created, put its content in the final response and say it was not persisted. Do not discard it silently |
| A session is ending with the record not yet updated | Write the update before the final response, even if it is only "what changed + what was not verified" | If that is impossible, leave one line at the top: `pending: <summary of this session's changes>`, for the next session to backfill |
| The work path contains a credential, token, or user-private material | Record where the credential lives and what it was used for, never the value | If a value was already written, replace it with a placeholder and add a line under `Known Risks, Assumptions, And Open Questions`: plaintext credential entered the record, rotate it |
| The record has grown too large to scan | Fold finished episodes into their tagged `#method:` / `#pitfall:` lines under `Reusable Methods & Pitfalls`, move the full text to `archive/`, and link it | If it cannot be moved, record only the delta and mark the older block `frozen at YYYY-MM-DD` |
| The record would be created inside a directory the user marked read-only | Do not create it. Keep the record content in the final response and say why it was not persisted | If the user still wants it persisted, stop and ask where. Do not write outside the allowed area |
| The write fails part-way, or the file is locked — permission denied, read-only mount, disk full, a concurrent writer | Re-read the file to see what actually landed, then retry the same content | If it still fails, restore the file to its last complete state where possible and leave `pending: <this change point>` at the top for the next session to backfill. Never report the record as updated |

## Writing Standard

Write for a capable newcomer and for a future distillation skill, not for the agent who just did the work.

- Concrete facts over vague summaries; name files, symbols, commands.
- Explain why a change exists and how the pieces interact.
- Keep assumptions/constraints separate from facts.
- Preserve dead-ends truthfully — do not sanitize the path into a straight line.
- Dates in `YYYY-MM-DD`. Keep log chronology consistent (newest top or bottom, pick one).
- Concise but complete enough to reconstruct intent and method.

## Entry Checklists

Field layout: `<this skill's directory>/assets/record-template.md`. A State-layer entry is complete when it answers what changed, where, why, how implemented, what assumptions changed, how verified, what the next person should watch for. A Work-path episode is complete when it answers what problem, what was considered, what was tried and what failed, what worked, why it worked at root, and what reusable method/pitfall/decision/heuristic it yields (tagged).
