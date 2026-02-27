---
id: T-031
type: task
title: T-031-i-038-intent-test-suite-srp-refactor-over-200-lines-phase2
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
- I-038
- ARCH-INDEX
- GOV-CODE-PRINCIPLES
---

# Task: T-031-i-038-intent-test-suite-srp-refactor-over-200-lines-phase2

## Intent

- Decompose oversized test suites into functional test modules with reusable fixtures while preserving behavior.

## Goal

- Refactor large test files into domain-focused modules and fixture layers without changing assertion semantics.

## Scope

- Target oversized test areas:
  - `tests/test_task_complete.py`
  - `tests/tools/fixture_state.py`
  - `tests/test_pack.py`
  - `tests/tools/test_dispatch_and_pack.py`
  - `tests/cli/fixture_repo.py`
  - `tests/cli/test_plan_intent_flow.py`
  - `tests/integration/test_tool_surface_parity.py`
  - `tests/integration/fixture_repo.py`
- Sync related architecture/flow docs if test boundary contracts are clarified.

## Implementation Approach

1. Split tests by behavior domain (`task`, `tools`, `cli`, `integration`) and avoid line-window slicing.
2. Extract duplicated repo/setup builders into shared fixture modules.
3. Keep compatibility shim files when legacy test entry names are still referenced.
4. Preserve all existing assertion intent and deterministic run order.

## Verification Approach

- `uvx ruff check tests`
- `uv run pytest -q tests/task tests/tools tests/cli tests/integration`
- `uv run pytest -q`
- `uv run taco plan validate`
- `uv run python scripts/validate_docs.py`

## Implementation Result

- Pending implementation updates.

- Modularized oversized tests into domain packages: moved task-complete suite into tests/task (fixture_repo.py, test_complete.py, test_block.py) and pack suite into tests/pack (fixture_graph.py, test_build_pack_core.py, test_build_pack_budget_and_shape.py); kept legacy entry files as compatibility shims (tests/test_task_complete.py, tests/test_pack.py).
- Split remaining oversized test surfaces: extracted tests/tools/fixture_state.py into fixture_state_docs.py + fixture_state_core.py + fixture_state_refactor.py with fixture_state.py shim; converted tests/fixtures/repo_snippets.py into re-export shim backed by repo_task_docs.py and new repo_config.py; moved tests/test_indexer.py suite into tests/indexer package (fixture_index.py, test_index_build.py, test_index_io_and_config.py) with compatibility shim.
- Removed legacy oversized integration test file tests/integration/_legacy_test_integration_mcp_cli_full.py after modular successors were already in place and no runtime references remained.
- refactored oversized test suites and removed legacy integration suite. design-sync: .context/project/architecture/index.md
## Verification Result

- Pending verification results.

- Passed uvx ruff check tests; uv run pytest -q tests/task tests/pack tests/tools tests/cli tests/integration; uv run pytest -q; uv run taco plan validate; uv run python scripts/validate_docs.py.
- Verified after refactor: uvx ruff check tests; uv run pytest -q tests/task tests/pack tests/tools tests/cli tests/integration tests/indexer; uv run pytest -q; uv run taco plan validate; uv run python scripts/validate_docs.py.
- Post-removal verification passed: uvx ruff check tests; uv run pytest -q; uv run taco plan validate; uv run python scripts/validate_docs.py.
- uvx ruff check tests; uv run pytest -q; uv run taco plan validate; uv run python scripts/validate_docs.py
