# Task: T-009-pack-readiness-performance

> Redesign `task.pack` for scalable readiness by resolving only required document slices through stable reference IDs.

## References

- [Intent](../../intent.md)
- [Architecture](../../architecture.md)
- [Plan](../../plan.md)
- [Glossary](../../glossary.md)
- [Task: T-003-pack-budget](./T-003-pack-budget.md)
- [Task: T-005-mcp-tools](./T-005-mcp-tools.md)

## Intent

- Prevent context explosion as docs grow while keeping one-call pack readiness.

## Goal

- Keep architecture/plan as global SSOT and make `task.pack` load only task-required sections via explicit reference IDs.

## Scope

- Introduce reference-addressable section model (`taco:ref`).
- Standardize task-level context declaration (`Context Requirements`).
- Change pack selection flow from broad selector/group sweep to reference resolution.
- Preserve current MCP/CLI contracts while improving pack precision and latency.
- Exclude summarization/ranking based on probabilistic heuristics.

## Context Requirements

- Common base references always included:
  - project objective/constraints
  - implementation principles
  - write-target guidance
- Task-declared references included on demand:
  - architecture slices required by the task scope
  - plan slices required by the task phase
  - optional glossary terms for ambiguous vocabulary

## Implementation Approach

- Parser/indexer:
  - parse and index `<!-- taco:ref=<ID> -->` markers.
  - enforce uniqueness and stable lookup by `ID`.
- Task document contract:
  - define machine-parseable `Context Requirements` section.
  - support `required` and `optional` reference lists.
- Pack assembly:
  - load `common_base_refs + task.required_refs + selected_optional_refs`.
  - fail deterministically when required refs are unresolved (`pack_not_ready`).
  - keep deterministic ordering and explicit drop reasons.
- Validation:
  - extend doc validation to detect duplicate refs and unresolved task requirements.
- Compatibility:
  - maintain `task.pack` tool name and response contract.
  - if payload evolves, use explicit `pack_version`.

## Verification Approach

- Add behavior tests for:
  - reference parsing/indexing correctness
  - deterministic pack assembly from declared refs
  - failure on unresolved required refs
  - stable output order across repeated runs
  - budget behavior with required-vs-optional refs
- Add doc validation tests for:
  - duplicate `taco:ref` detection
  - unresolved task `Context Requirements`
- Re-run:
  - `uv run --extra dev ruff check .`
  - `uv run --extra dev mypy .`
  - `uv run --extra dev pytest -q`
  - `uv run --extra dev python scripts/validate_docs.py`

## Implementation Result

- Pending (do not fill until the task is completed)

## Verification Result

- Pending (do not fill until the task is completed)
