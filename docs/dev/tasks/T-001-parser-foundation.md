# Task: T-001-parser-foundation

> Define deterministic markdown parsing primitives that are portable from Python to Rust.

## References

- [Intent](../../intent.md)
- [Architecture](../../architecture.md)
- [Plan](../../plan.md)
- [Glossary](../../glossary.md)

## Intent

- Build a language-agnostic parser contract for heading/anchor based extraction.

## Goal

- Provide stable section slicing outputs for downstream `indexer` and `pack`.

## Scope

- Parse markdown into a simple DTO tree:
  - document path
  - heading level/text
  - anchor id
  - start/end line range
- Normalize anchor generation rules and edge cases.
- Exclude semantic ranking and budget decisions.

## Implementation Approach

- Keep parser core pure:
  - input: raw markdown text + path metadata
  - output: parser DTO list
  - no filesystem access in core parse function
- Keep DTO shape flat and language-agnostic for Rust parity.
- Keep parser rules configurable where appropriate (`prefer_anchors` and future heading policies).
- Define typed parse errors and map them to standard error envelope at tool boundary.

## Verification Approach

- Add fixture-based parsing tests for:
  - nested heading levels
  - duplicate heading names
  - missing heading cases
  - anchor normalization stability
- Add determinism tests: same input yields identical DTO output ordering.
- Add contract tests that compare parser DTO schema to documented shape.

## Implementation Result

- Pending (do not fill until the task is completed)

## Verification Result

- Pending (do not fill until the task is completed)
