# Task: T-003-pack-budget

> Define task-centric pack assembly and token budget policy.

## References

- [Intent](../../intent.md)
- [Architecture](../../architecture.md)
- [Plan](../../plan.md)
- [Glossary](../../glossary.md)

## Intent

- Assemble minimal and deterministic context packs by Task ID using indexed sections.

## Goal

- Deliver stable `task.pack` behavior with predictable budget trimming and priority.

## Scope

- Assemble pack payload from:
  - task core sections
  - related plan/architecture snippets
  - principles/glossary excerpts
- Apply budget trimming with configured priority order.
- Exclude adaptive LLM summarization and probabilistic ranking.

## Implementation Approach

- Keep assembler pure:
  - input: task id + index DTO + config budget policy
  - output: pack DTO with selected snippets and truncation metadata
- Keep token estimate strategy pluggable behind a simple interface to allow Rust replacement.
- Record why each snippet was included/dropped for explainability and deterministic audits.
- Keep budget policy fully config-driven (`default_tokens`, `priority_order`).

## Verification Approach

- Add behavior tests for:
  - pack construction for valid task ids
  - missing task id error behavior
  - budget boundary behavior (below, equal, above limit)
  - stable snippet selection order
- Add golden tests of `task.pack` payloads for representative tasks.
- Add parity test hooks so Python and Rust outputs can be compared with same fixtures.

## Implementation Result

- Pending (do not fill until the task is completed)

## Verification Result

- Pending (do not fill until the task is completed)
