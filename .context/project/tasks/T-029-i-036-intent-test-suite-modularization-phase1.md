---
id: T-029
type: task
title: T-029-i-036-intent-test-suite-modularization-phase1
status: done
plan_ref: PLAN-MAIN
scope:
  in:
  - tests
  - .context/project
  out: []
references:
  modules:
  - ARCH-INDEX
  flows:
  - PLAN-MAIN
  schemas:
  - GOV-CODE-PRINCIPLES
links:
- PLAN-MAIN
- I-036
- ARCH-INDEX
- GOV-CODE-PRINCIPLES
---

# Task: T-029-i-036-intent-test-suite-modularization-phase1

## Intent

- Decompose oversized integration test file into domain-focused modules with shared fixtures.

## Goal

- Split `tests/test_integration_mcp_cli.py` into reusable fixture module + focused test modules.
- Preserve existing behavior and contract assertions.

## Scope

- Introduce `tests/integration/` package with:
  - shared fixture/repo builder module
  - CLI/MCP parity tests module
  - MCP runtime lifecycle/error tests module
- Remove or slim legacy monolithic integration test file.
- Keep test command behavior unchanged.

## Implementation Approach

1. Extract reusable `_write_fixture_repo` into fixture helper module.
2. Move parity/contract tests into one module and MCP runtime protocol tests into another.
3. Keep imports stable (`taco.apps.composition`, `taco.apps.mcp.main`) and avoid assertion drift.
4. Run targeted integration tests and full regression.

## Verification Approach

- `uv run ruff check tests`
- `uv run pytest -q tests/test_integration_mcp_cli.py tests/integration`
- `uv run pytest -q`
- `uv run taco plan validate`

## Implementation Result

- Pending implementation updates.

- - Split monolithic tests/test_integration_mcp_cli.py into modular integration package files: fixture_repo.py, test_tool_surface_parity.py, and test_mcp_runtime_protocol.py.\n- Replaced legacy test_integration_mcp_cli.py with a compatibility shim to keep command paths stable while moving real coverage into tests/integration/.\n- Added tests/integration/__init__.py so relative fixture imports resolve deterministically under pytest collection.\n- Synced mode-transition flow intent refs for I-036.
- Integration test suite phase-1 modularization completed with fixture extraction and protocol/parity test split. design-sync: FLOW-MODE-TRANSITION intent_refs updated for I-036.
## Verification Result

- Pending verification results.
- - uv run ruff check tests : pass\n- uv run pytest -q tests/test_integration_mcp_cli.py tests/integration : pass\n- uv run pytest -q : pass\n- uv run taco plan validate : pass
- ruff tests, targeted integration pytest, full pytest, and plan validate passed.
