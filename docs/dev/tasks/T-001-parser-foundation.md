# Task: T-001-parser-foundation

> Define deterministic markdown parsing primitives that are portable from Python to Rust.

## References

- [Intent](../../intent.md)
- [Architecture](../../architecture.md)
- [Plan](../../plan.md)
- [Glossary](../../glossary.md)

## Intent
<!-- taco:pack=task.core -->

- Build a language-agnostic parser contract for heading/anchor based extraction.

## Goal
<!-- taco:pack=task.core -->

- Provide stable section slicing outputs for downstream `indexer` and `pack`.

## Scope
<!-- taco:pack=task.core,pack.next_actions -->

- Parse markdown into a simple DTO tree:
  - document path
  - heading level/text
  - anchor id
  - start/end line range
- Normalize anchor generation rules and edge cases.
- Exclude semantic ranking and budget decisions.

## Implementation Approach
<!-- taco:pack=task.plans,pack.next_actions -->

- Keep parser core pure:
  - input: raw markdown text + path metadata
  - output: parser DTO list
  - no filesystem access in core parse function
- Keep DTO shape flat and language-agnostic for Rust parity.
- Keep parser rules configurable where appropriate (`prefer_anchors` and future heading policies).
- Define typed parse errors and map them to standard error envelope at tool boundary.

## Verification Approach
<!-- taco:pack=task.plans,pack.acceptance_checks,pack.verification_commands -->

- Add fixture-based parsing tests for:
  - nested heading levels
  - duplicate heading names
  - missing heading cases
  - anchor normalization stability
- Add determinism tests: same input yields identical DTO output ordering.
- Add contract tests that compare parser DTO schema to documented shape.

## Implementation Result

- Added parser foundation module at `src/taco/parser.py`.
- Implemented deterministic heading-based section slicing with DTO output:
  - `SectionSlice` (`document_path`, `level`, `heading`, `anchor_id`, `start_line`, `end_line`)
  - `ParseConfig` (`prefer_anchors`)
- Implemented anchor normalization features:
  - explicit anchor extraction (`{#custom-id}`)
  - slug generation for headings
  - duplicate anchor deduplication (`-2`, `-3`, ...)
- Implemented typed parse error model:
  - `ParserError(code, message, details)`
  - invalid heading handling for empty heading text.
- Ensured parser core remains pure (text + path input, DTO output, no filesystem access).
- Added package source layout support with `src/taco/__init__.py`.

## Verification Result

- Added parser behavior tests in `tests/test_parser.py` covering:
  - nested heading slices and line boundaries
  - duplicate heading anchor deduplication
  - explicit anchor preference toggle
  - missing heading case
  - deterministic output
  - DTO contract serialization via `to_dict()`
- Verification commands:
  - `uv run --extra dev ruff check .` -> pass
  - `uv run --extra dev mypy .` -> pass
  - `uv run --extra dev pytest -q` -> pass
