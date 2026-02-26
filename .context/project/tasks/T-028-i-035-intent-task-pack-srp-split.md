---
id: T-028
type: task
title: T-028-i-035-intent-task-pack-srp-split
status: done
plan_ref: PLAN-MAIN
scope:
  in:
  - src/taco/core/task
  - src/taco/core/usecases/task
  - src/taco/core/usecases/plan
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
- I-035
- ARCH-INDEX
- GOV-CODE-PRINCIPLES
---

# Task: T-028-i-035-intent-task-pack-srp-split

## Intent

- Split task pack logic by concern: selection, readiness, and assembly orchestration.

## Goal

- Keep `task.pack` and `plan.pack` external behavior unchanged.
- Remove mixed responsibility concentration in `core/task/pack.py`.

## Scope

- Introduce dedicated modules under `src/taco/core/task/`:
  - selection (`task_id` resolution and auto-pick policy)
  - readiness (front matter/heading/actionability checks)
  - assembly (budget override + `build_task_pack` bridge)
- Keep `pack.py` as compatibility facade exposing:
  - `_task_list`
  - `_task_pack`
  - `_plan_pack`
  - `_task_pack_readiness_missing`
- Update architecture module docs for new internal boundaries.

## Implementation Approach

1. Extract reusable readiness checks consumed by plan review/support modules.
2. Extract selection logic (`active_tasks`/`next_tasks` policy) into dedicated selector module.
3. Extract assembly/budget override logic into dedicated builder module.
4. Convert `pack.py` into thin orchestrator + backward-compatible exports.
5. Validate no regression in CLI/MCP integration tests and plan-intent review flows.

## Verification Approach

- `uv run ruff check src/taco/core/task/*.py src/taco/core/usecases/plan/*.py`
- `uv run pytest -q tests/test_tools.py tests/test_cli_main.py tests/test_integration_mcp_cli.py`
- `uv run pytest -q`
- `uv run taco plan validate`

## Implementation Result

- Pending implementation updates.

- - Decomposed core/task/pack.py into focused modules: pack_selector.py (task-id resolution), pack_readiness.py (pack readiness policy), and pack_builder.py (budget override + pack assembly bridge).\n- Kept core/task/pack.py as compatibility facade exposing existing symbols (, , , ).\n- Preserved plan-support and intent-review dependencies by keeping  export path stable while delegating to extracted readiness module.\n- Synced mode-transition flow intent refs for I-035.
- Task pack SRP split completed with stable pack contracts and extracted readiness/selection/assembly modules. design-sync: FLOW-MODE-TRANSITION intent_refs updated for I-035.
- Record correction: facade exports kept stable (`_task_list`, `_task_pack`, `_plan_pack`, `_task_pack_readiness_missing`) after pack module decomposition.
## Verification Result

- Pending verification results.
- - uv run ruff check src/taco/core/task/pack*.py src/taco/core/usecases/plan/*.py : pass\n- uv run pytest -q tests/test_tools.py tests/test_cli_main.py tests/test_integration_mcp_cli.py : pass\n- uv run pytest -q : pass\n- uv run taco plan validate : pass
- ruff targeted, focused pytest, full pytest, and plan validate passed.
