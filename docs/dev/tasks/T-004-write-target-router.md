# Task: T-004-write-target-router

> Define deterministic write target routing for task completion and issue records.

## References

- [Intent](../../intent.md)
- [Architecture](../../architecture.md)
- [Plan](../../plan.md)
- [Glossary](../../glossary.md)

## Intent
<!-- taco:pack=task.core -->

- Standardize where `task.record` writes across task lifecycle states.

## Goal
<!-- taco:pack=task.core -->

- Return precise file/section targets through `task.targets` without manual document lookup.

## Scope
<!-- taco:pack=task.core,pack.next_actions -->

- Route targets for:
  - implementation completion notes
  - verification results
  - issue/decision records
- Support configured task file contract headings.
- Exclude actual write execution semantics (handled by `task.record`).

## Implementation Approach
<!-- taco:pack=task.plans,pack.next_actions -->

- Keep routing core pure:
  - input: task id + route type + index/task DTOs
  - output: target DTOs (`path`, `heading`, `line_hint`, `mode`)
- Resolve headings by parser/index data, not raw string scan in tool handler.
- Keep route policy configurable for future section naming evolution.
- Normalize not-found and ambiguous-target cases to standard error types.

## Verification Approach
<!-- taco:pack=task.plans,pack.acceptance_checks,pack.verification_commands -->

- Add behavior tests for:
  - valid routing to `Implementation Result` and `Verification Result`
  - missing heading/malformed task contract detection
  - multiple matching headings disambiguation behavior
- Add golden tests for target DTO output stability.
- Add integration check with `task.record` contract expectations.

## Implementation Result

- Added write-target router module at `src/taco/router.py`.
- Implemented router policy/config DTO:
  - `RouterConfig` with configurable `heading_map` and `mode_map`
  - default route policy for:
    - `implementation_result`
    - `verification_result`
    - `issue_record`
- Implemented deterministic target resolver:
  - `resolve_write_target(task_id, route_type, index, config)`
  - returns `WriteTarget(path, heading, line_hint, mode)`
- Implemented standardized router error model:
  - `RouterError(code, message, details)`
  - invalid route type, missing task, missing task doc, missing heading, ambiguous heading
- Kept core behavior pure and index-driven:
  - no direct filesystem scan in route resolution
  - target resolution based on parsed headings in `IndexGraph`.

## Verification Result

- Added router behavior tests in `tests/test_router.py` covering:
  - implementation target resolution
  - verification target resolution
  - missing target heading failure
  - ambiguous target heading failure
  - issue route and output contract shape
- Verification commands:
  - `uv run --extra dev ruff check .` -> pass
  - `uv run --extra dev mypy .` -> pass
  - `uv run --extra dev pytest -q` -> pass
  - `uv run --extra dev python scripts/validate_docs.py` -> pass
