# Task: T-006-integration-tests

> Define end-to-end and cross-runtime behavior tests for MCP and CLI.

## References

- [Intent](../../intent.md)
- [Architecture](../../architecture.md)
- [Plan](../../plan.md)
- [Glossary](../../glossary.md)

## Intent
<!-- taco:pack=task.core -->

- Lock external behavior so Python implementation can be safely ported to Rust.

## Goal
<!-- taco:pack=task.core -->

- Provide behavior-based acceptance tests for all canonical tools and CLI mappings.

## Scope
<!-- taco:pack=task.core,pack.next_actions -->

- Cover MCP tools:
  - `task.list`
  - `task.pack`
  - `task.targets`
  - `task.record`
  - `doc.snippet`
  - `issue.triage`
  - `convention.get`
- Cover CLI mapping parity (`taco <domain> <action>` -> MCP tool).
- Cover success and standardized error envelope behavior.
- Exclude micro-benchmarking and load tests from this task.

## Implementation Approach
<!-- taco:pack=task.plans,pack.next_actions -->

- Build reusable fixture repositories and expected outputs (golden files).
- Write behavior assertions against public I/O only (no internal function coupling).
- Separate test layers:
  - contract tests (DTO schema)
  - e2e tests (CLI/MCP behavior)
  - parity tests (Python vs Rust same fixture, same expected output)
- Keep test data language-neutral (JSON/YAML fixtures) to reuse in Rust test harness.

## Verification Approach
<!-- taco:pack=task.plans,pack.acceptance_checks,pack.verification_commands -->

- Required scenarios:
  - happy path for each tool
  - invalid input schema per tool
  - missing docs/task id/heading conditions
  - deterministic repeatability checks
- Add parity gate definition:
  - Rust migration cannot switch default runtime until golden parity is complete.
- Capture test execution instructions in task completion notes for repeatability.

## Implementation Result

- Added CLI-to-tool mapping module at `src/taco/cli.py`:
  - `map_cli_to_tool(domain, action, options)` for canonical command mapping
  - standardized CLI error model `CliError`
- Added integration test suite at `tests/test_integration_mcp_cli.py` with fixture-repo setup.
- Integration tests cover:
  - all canonical MCP tools happy path
  - invalid input and missing resource errors
  - deterministic repeatability for `task.pack`
  - CLI mapping parity against direct MCP tool calls
- Kept tests behavior-focused at tool boundary and response envelope level.

## Verification Result

- Verification commands:
  - `uv run --extra dev ruff check .` -> pass
  - `uv run --extra dev mypy .` -> pass
  - `uv run --extra dev pytest -q` -> pass
  - `uv run --extra dev python scripts/validate_docs.py` -> pass
- Current parity gate status:
  - Python-side golden behavior tests are in place.
  - Rust parity remains pending until Rust runtime implementation starts.
