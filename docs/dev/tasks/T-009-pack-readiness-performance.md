# Task: T-009-pack-readiness-performance

> Redesign `task.pack` so one call provides a ready-to-execute context packet with deterministic section targeting.

## References

- [Intent](../../intent.md)
- [Architecture](../../architecture.md)
- [Plan](../../plan.md)
- [Glossary](../../glossary.md)
- [Task: T-003-pack-budget](./T-003-pack-budget.md)
- [Task: T-005-mcp-tools](./T-005-mcp-tools.md)

## Intent
<!-- taco:pack=task.core -->

- Make `task.pack` sufficient for immediate agent execution without additional document exploration.

## Goal
<!-- taco:pack=task.core -->

- Improve pack usefulness and precision by selecting only task-relevant architecture/plan/principles sections using explicit structured selectors.

## Scope
<!-- taco:pack=task.core,pack.next_actions -->

- Introduce a deterministic "ready pack" payload profile as default.
- Add section-selection rules for:
  - task file (required execution fields)
  - architecture
  - plan
  - principles
  - glossary (optional support terms)
- Define markup/selector strategy in docs for precise extraction (anchor/comment/tag based).
- Improve budget behavior for execution-critical fields first.
- Exclude probabilistic summarization or LLM-dependent ranking.

## Implementation Approach
<!-- taco:pack=task.plans,pack.next_actions -->

- Evolve pack payload to execution-oriented shape:
  - `task_id`
  - `next_actions` (ordered executable steps)
  - `acceptance_checks`
  - `verification_commands`
  - `write_targets`
  - `context_snippets` (with source + anchor + reason)
  - `unknowns` (explicit unresolved decisions)
- Add deterministic selector model for structured docs:
  - Prefer explicit anchor/tag markers in markdown headings.
  - Add selector conventions (example: `<!-- taco:pack=task.core -->` or heading suffix marker) and parse them in parser/indexer.
  - Enforce strict selector requirements for required groups.
- Expand pack candidate sourcing:
  - include `plan` sections by selector group (currently missing in effective selection)
  - include architecture/principles only when tagged as relevant to task execution.
- Budget policy refinement:
  - reserve budget for required execution fields before optional context
  - deterministic drop order with explicit reason codes.
- Missing required selector groups fail pack with `pack_not_ready`.
- Keep tool contract stable:
  - `task.pack` remains the same tool name
  - payload shape versioning handled via explicit `pack_version` field if needed.

## Verification Approach
<!-- taco:pack=task.plans,pack.acceptance_checks,pack.verification_commands -->

- Add behavior tests for:
  - one-call readiness (required fields always present for valid task)
  - selector-driven inclusion/exclusion from architecture/plan/principles
  - strict failure when selectors are missing (`pack_not_ready`)
  - deterministic output across repeated runs
  - budget enforcement for required-vs-optional sections
- Add fixture tests with tagged markdown examples.
- Add regression tests to ensure legacy documents still produce usable pack output.
- Re-run:
  - `uv run --extra dev ruff check .`
  - `uv run --extra dev mypy .`
  - `uv run --extra dev pytest -q`
  - `uv run --extra dev python scripts/validate_docs.py`

## Implementation Result

- Extended parser selector support in `src/taco/parser.py`:
  - parse `<!-- taco:pack=... -->` markers adjacent to headings
  - persist selector groups in `SectionSlice.pack_groups`
- Extended indexer heading metadata in `src/taco/indexer.py`:
  - carry selector groups in `HeadingRef.pack_groups`
- Reworked pack assembly in `src/taco/pack.py` to readiness-focused output:
  - new pack payload fields:
    - `pack_version`
    - `next_actions`
    - `acceptance_checks`
    - `verification_commands`
    - `write_targets`
    - `context_snippets`
    - `unknowns`
    - `coverage`
  - strict required-group gate with `pack_not_ready`
  - selector-driven candidate sourcing across task/architecture/plan/principles/glossary
  - required-group-first budget behavior with deterministic drop
- Updated `BudgetConfig` contract:
  - added `required_groups` configuration support
- Updated tool boundary in `src/taco/tools.py`:
  - propagate `required_groups` when overriding `budget_tokens`
- Applied selector tags to core docs and task docs for immediate compatibility:
  - `docs/architecture.md`, `docs/plan.md`, `docs/dev/principles.md`, `docs/glossary.md`
  - `docs/dev/tasks/T-*.md` headings used by pack.

## Verification Result

- Updated tests to selector/readiness model:
  - `tests/test_parser.py`: selector extraction assertions
  - `tests/test_pack.py`: readiness payload, strict missing-selector failure, budget semantics
  - `tests/test_tools.py`, `tests/test_integration_mcp_cli.py`, `tests/test_cli_main.py`:
    selector-tagged fixtures + `required_groups` config
- Verification commands:
  - `uv run --extra dev ruff check .` -> pass
  - `uv run --extra dev mypy .` -> pass
  - `uv run --extra dev pytest -q` -> pass
  - `uv run --extra dev python scripts/validate_docs.py` -> pass
