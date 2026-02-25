# Task: T-008-cli-entrypoint

> Add a runnable `taco` CLI entrypoint that maps commands to canonical MCP tools.

## References

- [Intent](../../intent.md)
- [Architecture](../../architecture.md)
- [Plan](../../plan.md)
- [Glossary](../../glossary.md)
- [Task: T-005-mcp-tools](./T-005-mcp-tools.md)
- [Task: T-006-integration-tests](./T-006-integration-tests.md)

## Intent
<!-- taco:pack=task.core -->

- Make tool-surface behavior directly executable via `taco <domain> <action>` command.

## Goal
<!-- taco:pack=task.core -->

- Provide a real CLI command entrypoint with stable JSON output and proper exit codes.

## Scope
<!-- taco:pack=task.core,pack.next_actions -->

- Add Python package script entrypoint for `taco`.
- Implement CLI argument parsing for canonical domains/actions.
- Map CLI arguments to existing tool handlers and response envelope.
- Add behavior tests for CLI main flow.

## Implementation Approach
<!-- taco:pack=task.plans,pack.next_actions -->

- Add `[project.scripts] taco = "taco.main:main"` in `pyproject.toml`.
- Implement `src/taco/main.py`:
  - parse CLI args (`task`, `doc`, `issue`, `convention` domains)
  - map args via `map_cli_to_tool`
  - call tools through `load_repo_state` and `call_tool`
  - print JSON response and return code (`0` for success, `1` for failure)
- Support task pack budget override (`--budget-tokens`) and task record apply mode (`--apply`).
- Keep error response aligned with standard envelope and codes.

## Verification Approach
<!-- taco:pack=task.plans,pack.acceptance_checks,pack.verification_commands -->

- Add CLI main tests with fixture repository setup.
- Validate:
  - `task list` success path
  - `task pack` and `doc snippet` success paths
  - invalid input returns non-zero exit code and structured error
- Re-run repository-wide lint, type, tests, and doc validation.

## Implementation Result

- Added package entrypoint in `pyproject.toml`:
  - `[project.scripts] taco = "taco.main:main"`
- Added executable CLI module `src/taco/main.py`:
  - argparse-based command parsing for canonical domains/actions
  - options mapping to tool payload via `map_cli_to_tool`
  - repo loading via `load_repo_state`
  - tool dispatch via `call_tool`
  - JSON response output with exit code contract (`0` success, `1` failure)
- Extended CLI mapper `src/taco/cli.py`:
  - support optional `budget_tokens` for `task pack`
  - preserve `dry_run`/`--apply` behavior mapping for `task record`

## Verification Result

- Added CLI behavior tests in `tests/test_cli_main.py`:
  - `task list` JSON output and task id assertion
  - `task pack` and `doc snippet` success flow
  - invalid input returns non-zero exit and structured error
- Verification commands:
  - `uv run --extra dev ruff check .` -> pass
  - `uv run --extra dev mypy .` -> pass
  - `uv run --extra dev pytest -q` -> pass
  - `uv run --extra dev python scripts/validate_docs.py` -> pass
