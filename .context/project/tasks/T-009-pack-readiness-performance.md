---
id: T-009
type: task
title: T-009-pack-readiness-performance
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

# Task: T-009-pack-readiness-performance

> Redesign `task.pack` for scalable readiness by resolving only required document slices through stable reference IDs.

## References

- [Overview](../overview.md)
- [Architecture Index](../architecture/index.md)
- [Plan](../plan.md)
- [Glossary](../architecture/schemas/glossary.md)
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

- required: ARCH-REFMODEL-001, PLAN-PHASE2-001
- optional: GLOSSARY-TERMS-001

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

- Migrated canonical documentation root from legacy `docs/*` to `.context/*`.
- Added front matter-based node indexing (`id`, `type`, metadata) in index graph.
- Added node-level reference resolution (`node_index`) in pack selection flow.
- Added task front matter requirement resolution (`plan_ref`, `references.*`) to pack.
- Kept heading-slice based extraction and deterministic ordering/budget behavior.
- Expanded architecture/index/plan/overview docs to reflect actual runtime structure:
  - `main`, `cli-mapper`, `tools-dispatch`, `parser`, `indexer`, `pack`, `router`
  - tool dispatch and task record flows
  - tool envelope and tool error schemas
- Removed outdated `docs/` tree and standardized on `.context` paths.
- Updated README and runtime defaults to `.context` conventions.

## Verification Result

- `uv run --extra dev ruff check .` passed
- `uv run --extra dev mypy .` passed
- `uv run --extra dev pytest -q` passed
- `uv run --extra dev python scripts/validate_docs.py` passed
- `uv run --extra dev taco task pack --task-id T-009` returned `ok: true`
