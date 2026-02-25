# Task: T-002-indexer-foundation

> Define deterministic document indexing on top of parser DTOs.

## References

- [Intent](../../intent.md)
- [Architecture](../../architecture.md)
- [Plan](../../plan.md)
- [Glossary](../../glossary.md)

## Intent

- Create a stable doc/task/link index that can be shared by `pack`, `snippet`, and `targets`.

## Goal

- Produce a deterministic index graph from repository docs with minimal language/runtime coupling.

## Scope

- Build index DTOs for:
  - doc type classification (intent, architecture, plan, glossary, principles, task, todo, git docs)
  - task id extraction
  - cross-reference links
  - heading lookup map
- Exclude caching and parallel scan optimization from core logic.

## Implementation Approach

- Split I/O and core:
  - scanner adapter collects file contents
  - pure index builder creates index DTOs from parsed sections
- Keep rule tables (doc paths, task glob, required headings) in config (`taco.yaml`).
- Standardize index errors (missing key docs, malformed task id, invalid link references).
- Preserve deterministic ordering by canonical path sort.

## Verification Approach

- Add fixture tests for:
  - mixed valid/invalid task files
  - cross-file links and missing links
  - doc classification by configured paths/globs
- Add determinism tests on repeated scans with identical repo state.
- Add behavior tests for config overrides to ensure hardcoded path dependency is absent.

## Implementation Result

- Pending (do not fill until the task is completed)

## Verification Result

- Pending (do not fill until the task is completed)
