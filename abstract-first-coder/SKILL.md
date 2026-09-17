---
name: abstract-first-coder
description: "Write Python code in the abstraction-first style used by knowledge_graph_xm: define domain data models, abstract interfaces, strategy classes, default implementations, pipeline orchestration, dependency injection, async contracts, and verification hooks before adding concrete behavior. Use when creating or modifying project code that should be extensible, replaceable, and readable by future agents."
---

# Abstract First Coder

This skill guides agents to write code in the style observed in `/Users/ruosongchen/PyCharmMiscProject/knowledge_graph_xm`: everything starts from a stable abstraction, then concrete implementations are plugged into a pipeline.

## Core Principle

Do not start by writing a one-off function that directly solves the current case. First identify the concept, define its contract, then implement the current strategy behind that contract.

Preferred shape:

1. `dataclass` / `BaseModel` defines the data.
2. `ABC` interface defines the capability.
3. Concrete classes implement strategies.
4. `Default` implementation provides a safe baseline.
5. Pipeline or service class orchestrates injected capabilities.
6. Tests or single-point checks verify each unit and the composed flow.

## Scale Abstraction To Task Size

Abstraction is a tool for *anticipated variation and replacement*, not a tax paid on every task. Match the depth of abstraction to how likely the code is to change, vary, or be swapped. Over-abstracting a one-off is as much a defect as under-abstracting a core capability.

Decide depth before coding, using this ladder:

- **One-off, single call site, no foreseeable variant** → a plain function or a passive `dataclass` is the correct and complete abstraction. Do not add an `ABC`, strategy class, or `Default` fallback. A two-function module is a valid end state.
- **One concept, but a second strategy is plausible soon, or it crosses a domain boundary** → define the `dataclass` + a thin `ABC`, implement the single concrete strategy now. Defer `Default`/injection until the second strategy actually appears.
- **Core capability, replaceable, multiple strategies, or an agent/human/code decision point** → full shape: data model + interface + strategies + default + injection. This is where the layering below earns its cost.

Guardrails so the abstraction-first habit does not become ceremony:

- Every interface, strategy class, or injection point must name the *concrete second case* or *replacement* it exists to enable. If you cannot name one, collapse it to a function until one exists.
- Do not build configurability, extension hooks, or error handling for scenarios that cannot currently occur.
- Prefer the smallest shape that still makes the abstraction boundary obvious; expand it the moment a real second case arrives, not before.
- Self-check: would a senior engineer call this structure premature for the task as scoped? If yes, drop a level on the ladder.

When in doubt for substantial, long-lived, or pipeline code, lean toward the abstraction. For scripts, glue, single-use transforms, and small features, lean toward the plain function. State which rung you chose and why before implementing. If the rung turns out too high once built, or the user disagrees with it, take the matching row of `Execution Failures And Recovery`.

## Architecture Pattern

Use this layering unless the repo already has a stronger local convention. When the repo's convention conflicts with it, take the row beginning *Repo has a stronger local convention* in `Execution Failures And Recovery` rather than choosing on the user's behalf.

```text
*_definitions/         domain data structures and abstract processors
ability_ext/           generic capability interfaces and code-side adapters
data_process/          domain processing strategies
utils/                 infrastructure adapters and reusable utilities
pipeline.py            orchestration only, minimal business details
scripts/               executable entrypoints
single_points_test/    focused checks for individual abilities
```

## Naming Pattern

Use names that reveal the abstraction boundary.

- Abstract capability: `Classification`, `Pile`, `Chunker`, `Download`, `LLM`, `GraphResult`.
- Concrete strategy: `ClassificationByDefault`, `PileByInfoDensity`, `ChunkTextByRecursive`, `DownloadTextFiles`.
- Default fallback: `XDefault` or `DefaultX` when it is a safe baseline.
- Data definition: noun-centered names such as `InputData`, `Document`, `KGTriple`, `TriplesForChecking`.
- Capability adapter: `CodeFilter`, `CodeFillForm`, `CodeDecision`, `CodeKGExtractionDecision`.
- Pipeline method: verb phrase for one stage, such as `prepare_run_context`, `prepare_sample_chunks`, `run_recursive_extraction`.

## Required Design Pass Before Coding

Before implementing a new feature, write or mentally settle these answers:

- What is the domain object? Define it first.
- What is the capability being added? Define an abstract interface.
- Which concrete strategy is needed now?
- What is the default or fallback behavior?
- Where will the pipeline inject and call it?
- What data enters and leaves the capability?
- What errors should be raised vs tolerated?
- What focused verification proves the capability works?

**🛑 STOP — do not write implementation code while any answer above is unsettled. A contract guessed now is redefined later at the cost of every caller already written against it. Resolve it, or ask the user.**

## Data First

Define data contracts close to the domain.

Use `dataclass` for simple internal records:

```python
from dataclasses import dataclass

@dataclass
class Document:
    link: str
    local_path: str | None = None
```

Use `BaseModel` when validation, schema metadata, or structured LLM/tool input matters.

Keep data classes mostly passive. Put transformation logic in processors, strategies, or pipeline stages.

## Interface First

Every replaceable capability should have an `ABC`.

```python
from abc import ABC, abstractmethod

class Chunker(ABC):
    @abstractmethod
    async def chunk(self, text: str) -> list[str]:
        pass
```

Then add concrete strategies:

```python
class ChunkTextByRecursive(Chunker):
    async def chunk(self, text: str) -> list[str]:
        ...

class ChunkerDefault(Chunker):
    def __init__(self, length: int = 512, overlap: int = 0):
        self.chunker = ChunkTextByRecursive(length, overlap)

    async def chunk(self, text: str) -> list[str]:
        return await self.chunker.chunk(text)
```

## Capability Injection

Prefer passing implementations into pipeline methods instead of hard-coding behavior inside the orchestration.

Good:

```python
chunked_result = await self.chunk(run_context["chunker"], documents)
```

Avoid:

```python
chunker = ChunkTextByRecursive(...)
chunked_result = await chunker.chunk(documents)
```

Creating defaults in `prepare_run_context` is acceptable because it centralizes runtime choices. If a capability that must be injected has no implementation available at the call site, take the row beginning *A capability that must be injected is unavailable* in `Execution Failures And Recovery`; never reach for a hard-coded internal instance.

## Pipeline Style

Pipeline methods should read like a workflow and delegate details.

Good orchestration:

```python
run_context = await self.prepare_run_context(input_datas)
await self.prepare_and_confirm_template(input_datas)
pile_result = await self.prepare_documents_and_piles(input_datas, run_context)
sample_chunks = await self.prepare_sample_chunks(input_datas, pile_result, run_context)
```

Each stage should:

- Accept explicit inputs.
- Return explicit outputs.
- Call abstract capabilities or helper methods.
- Record important intermediate artifacts when the project expects traceability.
- Keep low-level parsing, scoring, IO, and formatting in helpers or strategy classes.

## Async Contract

If a capability may call IO, LLMs, network, files, user/agent review, or long-running work, make the interface async from the beginning. Keep async signatures consistent across abstract and concrete classes.

Use small helpers such as `_await_if_needed` only at adapter boundaries where both sync and async handlers are intentionally supported.

## Strategy Classes

When adding a new algorithm, do not replace the old one in place. Add a new strategy class under the same abstraction.

Example pattern:

```python
class Pile(ABC):
    @abstractmethod
    async def pile(self, sampling_accuracy, input_datas):
        pass

class PileByInfoDensity(Pile):
    async def pile(self, sampling_accuracy, input_datas):
        ...

class PileByDefault(Pile):
    async def pile(self, sampling_accuracy, input_datas):
        ...
```

This lets the pipeline choose strategies without changing downstream contracts. If the contract turns out to force callers to pass irrelevant arguments, take the row beginning *Contract does not hold once you write the implementation* in `Execution Failures And Recovery`.

## Defaults And Fallbacks

Every important capability should have a baseline:

- `Default` returns simple deterministic behavior.
- Code catches optional integration failures only where fallback is intentional.
- Fallbacks must preserve the interface contract.
- If fallback may reduce quality, log or record that fact.

Do not silently swallow errors in core correctness paths.

## Agent Ability Pattern

For agent/human/code decision points, separate the ability interface from the code-side implementation.

Use generic capability interfaces:

- `IFilter[T]`
- `IFillForm[T]`
- `IDecision[I, O]`
- `IJudgingOption[T]`

Then adapt code functions into those interfaces:

- `CodeFilter`
- `CodeFillForm`
- `CodeDecision`
- `CodeJudgingOption`

This makes later replacement by UI, human review, tool calls, or model decisions straightforward.

## Error Handling And Logging

- Wrap pipeline-stage errors with stage/function context.
- Log retries and final failures for external calls.
- Raise meaningful errors when required capabilities are not injected.
- Validate input contracts early with `check_*` functions.
- Keep recoverable fallback behavior local and explicit.

## File And Artifact Discipline

For data pipelines, write intermediate artifacts when they help debugging or review:

- classification result
- sample chunks and similarity scores
- template change history
- extraction history
- metrics
- final result

Generated files should live under a run-specific temp/output path instead of polluting source directories.

## Implementation Checklist

**🔴 CHECKPOINT — run this list against the code that actually exists, not against the plan. A structure that satisfies the list only in intent does not satisfy it.**

- A domain data model exists for new structured data.
- A replaceable capability has an abstract interface.
- The concrete implementation satisfies the interface.
- A default/fallback exists when appropriate.
- Pipeline orchestration is readable and not overloaded with low-level details.
- Dependencies are injected or centralized in a run context.
- Errors and retries are handled at the correct boundary.
- Inputs are validated before processing.
- Outputs are saved or returned in a traceable shape.
- A focused test, script, or single-point check exists for the new capability.

## Execution Failures And Recovery

This skill itself goes wrong in predictable ways. Handle by table, never continue silently.

| Trigger | First-line fix | Fallback if that fails |
|---|---|---|
| Abstraction level turns out too high (interface/strategy has one implementation and no second case) | Drop one rung on the ladder; collapse the interface back to a function | Collapse to the plainest shape (plain function + passive `dataclass`) and record the downgrade and its reason in the delivery note |
| Contract does not hold once you write the implementation (interface forces callers to pass irrelevant arguments) | Return to the Design Pass and redefine the contract without changing caller semantics | If redefining would disturb existing strategies, add a new strategy and keep the old one; never replace in place |
| Repo has a stronger local convention that conflicts with this layering | Follow the repo convention; treat this layering as reference only | If the conflict cannot be reconciled, report the conflict explicitly for the user to decide; do not choose on their behalf |
| A capability that must be injected is unavailable at the call site | Build the default implementation centrally in the run context / prepare stage | If it cannot be built, raise explicitly naming the missing capability; do not fall back to a hard-coded internal instance |
| The reference project named in this skill's opening paragraph is unavailable, or the repo you are in shows a different style | Work from the naming patterns and examples inside this skill; do not claim to be following the reference project's style | If the repo documents conventions of its own, those win outright — say which part of the reference could not be checked |
| You and the user disagree on task scale | State the rung you chose and why, with the cost of the adjacent rung | If the user insists, follow their choice and mark in the delivery note that the level was user-specified |

## What To Avoid

- Large procedural functions that mix input validation, algorithm logic, IO, LLM calls, persistence, and formatting.
- Hard-coded concrete classes scattered across many pipeline stages.
- Adding behavior directly to a data class.
- Changing an existing strategy in a way that removes previous behavior without adding a new strategy or compatibility path.
- Sync interfaces for capabilities likely to require async IO later.
- Unnamed dictionaries where a dataclass or model would clarify the contract.
- Hidden global state for pipeline decisions.

## Minimal Example Shape

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class ScoreInput:
    text: str
    topic: str

@dataclass
class ScoreResult:
    value: float
    reason: str

class Scorer(ABC):
    @abstractmethod
    async def score(self, source: ScoreInput) -> ScoreResult:
        pass

class ScorerByKeywordDensity(Scorer):
    async def score(self, source: ScoreInput) -> ScoreResult:
        value = source.text.count(source.topic) / max(1, len(source.text))
        return ScoreResult(value=value, reason="keyword_density")

class ScorerDefault(Scorer):
    async def score(self, source: ScoreInput) -> ScoreResult:
        return ScoreResult(value=0.0, reason="default")
```

Use this shape as the default starting point when adding new capabilities.
