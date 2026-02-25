---
id: T-002
type: task
title: T-002-indexer-foundation
status: todo
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

# Task: T-002-indexer-foundation

> Define deterministic document indexing on top of parser DTOs.

## References

- [Overview](../overview.md)
- [Architecture Index](../architecture/index.md)
- [Plan](../plan.md)
- [Glossary](../architecture/schemas/glossary.md)

## Intent
<!-- taco:pack=task.core -->

- Create a stable doc/task/link index that can be shared by `pack`, `snippet`, and `targets`.

## Goal
<!-- taco:pack=task.core -->

- Produce a deterministic index graph from repository docs with minimal language/runtime coupling.

## Scope
<!-- taco:pack=task.core,pack.next_actions -->

- Build index DTOs for:
  - doc type classification (intent, architecture, plan, glossary, principles, task, todo, git docs)
  - task id extraction
  - cross-reference links
  - heading lookup map
- Exclude caching and parallel scan optimization from core logic.

## Implementation Approach
<!-- taco:pack=task.plans,pack.next_actions -->

- Split I/O and core:
  - scanner adapter collects file contents
  - pure index builder creates index DTOs from parsed sections
- Keep rule tables (doc paths, task glob, required headings) in config (`taco.yaml`).
- Standardize index errors (missing key docs, malformed task id, invalid link references).
- Preserve deterministic ordering by canonical path sort.

## Verification Approach
<!-- taco:pack=task.plans,pack.acceptance_checks,pack.verification_commands -->

- Add fixture tests for:
  - mixed valid/invalid task files
  - cross-file links and missing links
  - doc classification by configured paths/globs
- Add determinism tests on repeated scans with identical repo state.
- Add behavior tests for config overrides to ensure hardcoded path dependency is absent.

## Implementation Result

- Added indexer foundation module at `src/taco/indexer.py`.
- Implemented deterministic index DTO model:
  - `IndexConfig`, `DocumentInput`, `HeadingRef`, `IndexedDocument`, `IndexGraph`
- Implemented config-driven indexing primitives:
  - `IndexConfig.from_dict()` for loading path/glob rules
  - doc classification by config paths and task glob
  - task id extraction from task document paths
- Implemented link graph and heading lookup generation:
  - local markdown link extraction
  - heading key format `<path>#<anchor_id>`
- Implemented I/O-separated adapter functions:
  - `scan_markdown_files(root)` for markdown discovery
  - `load_documents(root, paths)` for file loading
  - pure `build_index(documents, config)` core assembly
- Implemented standardized indexer error model:
  - `IndexerError(code, message, details)`
  - missing required SSOT docs and invalid config validation

## Verification Result

- Added indexer behavior tests in `tests/test_indexer.py` covering:
  - doc classification and task index generation
  - local link extraction graph
  - required-doc validation failure behavior
  - stable markdown scan ordering
  - file load adapter behavior
  - config override behavior
  - `IndexedDocument.to_dict()` contract shape
- Verification commands:
  - `uv run --extra dev ruff check .` -> pass
  - `uv run --extra dev mypy .` -> pass
  - `uv run --extra dev pytest -q` -> pass
