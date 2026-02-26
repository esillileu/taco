---
id: T-003
type: task
title: T-003-pack-budget
status: done
plan_ref: PLAN-MAIN
priority: p1
estimate: m
scope:
  in: []
  out: []
references:
  modules: [MOD-PACK, MOD-INDEXER]
  flows: [FLOW-TASK-PACK]
  schemas: [SCH-PACK-RESULT]
  governance: [GOV-CODE-PRINCIPLES, GOV-GIT-INDEX]
deliverables: []
verification: []
links: []
---

# Task: T-003-pack-budget

> Define task-centric pack assembly and token budget policy.

## References

- [Overview](../overview.md)
- [Architecture Index](../architecture/index.md)
- [Plan](../plan.md)
- [Glossary](../architecture/schemas/glossary.md)

## Intent
<!-- taco:pack=task.core -->

- Assemble minimal and deterministic context packs by Task ID using indexed sections.

## Goal
<!-- taco:pack=task.core -->

- Deliver stable `task.pack` behavior with predictable budget trimming and priority.

## Scope
<!-- taco:pack=task.core,pack.next_actions -->

- Assemble pack payload from:
  - task core sections
  - related plan/architecture snippets
  - principles/glossary excerpts
- Apply budget trimming with configured priority order.
- Exclude adaptive LLM summarization and probabilistic ranking.

## Implementation Approach
<!-- taco:pack=task.plans,pack.next_actions -->

- Keep assembler pure:
  - input: task id + index DTO + config budget policy
  - output: pack DTO with selected snippets and truncation metadata
- Keep token estimate strategy pluggable behind a simple interface to allow Rust replacement.
- Record why each snippet was included/dropped for explainability and deterministic audits.
- Keep budget policy fully config-driven (`default_tokens`, `priority_order`).

## Verification Approach
<!-- taco:pack=task.plans,pack.acceptance_checks,pack.verification_commands -->

- Add behavior tests for:
  - pack construction for valid task ids
  - missing task id error behavior
  - budget boundary behavior (below, equal, above limit)
  - stable snippet selection order
- Add golden tests of `task.pack` payloads for representative tasks.
- Add parity test hooks so Python and Rust outputs can be compared with same fixtures.

## Implementation Result

- Added pack assembly module at `src/taco/pack.py`.
- Implemented budget policy DTO and parsing:
  - `BudgetConfig(default_tokens, priority_order)`
  - `BudgetConfig.from_dict()` for config-driven budget settings
- Implemented deterministic task pack builder:
  - `build_task_pack(task_id, index, budget, token_estimator)`
  - strict ordering by priority group, path, and heading line
  - stable include/drop decision based on fixed budget
- Implemented pack result DTOs with audit metadata:
  - `PackResult`, `PackSnippet`, `DroppedSnippet`
  - inclusion reason and dropped reason (`budget_exceeded`) tracking
- Implemented standardized error model:
  - `PackError(code, message, details)`
  - errors for missing task id, missing task doc, missing document text, invalid config
- Extended index graph for pack assembly input:
  - added `document_texts` to `IndexGraph` in `src/taco/indexer.py`
- Kept token estimator pluggable to support later Rust parity.

## Verification Result

- Added pack behavior tests in `tests/test_pack.py` covering:
  - valid task pack construction
  - missing task id failure
  - budget boundary behavior (low/equal/high)
  - deterministic/stable ordering
  - golden output shape contract (`to_dict()`)
- Existing parser/indexer tests continue to pass after `IndexGraph` extension.
- Verification commands:
  - `uv run --extra dev ruff check .` -> pass
  - `uv run --extra dev mypy .` -> pass
  - `uv run --extra dev pytest -q` -> pass
  - `uv run --extra dev python scripts/validate_docs.py` -> pass
