# Task: T-014-cli-human-context-view

> Add a CLI mode that shows human-readable context only, without full tool envelope noise.

## References

- [Intent](../../intent.md)
- [Architecture](../../architecture.md)
- [Plan](../../plan.md)
- [Glossary](../../glossary.md)
- [Task: T-003-pack-budget](./T-003-pack-budget.md)
- [Task: T-008-cli-entrypoint](./T-008-cli-entrypoint.md)
- [Task: T-009-pack-readiness-performance](./T-009-pack-readiness-performance.md)

## Intent
<!-- taco:pack=task.core -->

- Let users inspect context content directly from CLI when they want readability over machine envelopes.

## Goal
<!-- taco:pack=task.core -->

- Add a stable CLI option that outputs only human-focused context text for pack/snippet workflows.

## Scope
<!-- taco:pack=task.core,pack.next_actions -->

- Add a global CLI option for human-context output mode:
  - proposed flag: `--human-context`
- Support this mode for:
  - `taco task pack`
  - `taco doc snippet`
- Keep default JSON envelope behavior unchanged when flag is not provided.
- Exclude changes to MCP tool payload/response contracts.

## Implementation Approach
<!-- taco:pack=task.plans,pack.next_actions -->

- Extend `src/taco/main.py` parser with `--human-context` boolean flag.
- Add output renderer layer in CLI path only:
  - default renderer: JSON response envelope
  - human renderer: plain text context content
- Rendering rules:
  - `task.pack`: print ordered snippet blocks (`[group] path#anchor`, then snippet content)
  - `doc.snippet`: print heading + snippet content
  - unsupported commands with `--human-context` return structured error (invalid mode)
- Keep tool invocation unchanged (`call_tool` stays canonical).
- Ensure deterministic ordering in human output follows pack snippet order.

## Verification Approach
<!-- taco:pack=task.plans,pack.acceptance_checks,pack.verification_commands -->

- Add CLI behavior tests for:
  - `task pack --human-context` output content/ordering
  - `doc snippet --human-context` output content
  - default mode still emits JSON
  - unsupported command + `--human-context` returns error
- Re-run full validation:
  - `uv run --extra dev ruff check .`
  - `uv run --extra dev mypy .`
  - `uv run --extra dev pytest -q`
  - `uv run --extra dev python scripts/validate_docs.py`

## Implementation Result

- Pending (do not fill until the task is completed)

## Verification Result

- Pending (do not fill until the task is completed)
