---
id: T-011
type: task
title: T-011-feature-precision
status: todo
plan_ref: PLAN-MAIN
priority: p1
estimate: m
scope:
  in:
    - src/taco/pack.py
    - src/taco/tools.py
    - .context/project/architecture/index.md
  out:
    - major tool surface rename
references:
  modules: [MOD-PACK, MOD-TOOLS-DISPATCH]
  flows: [FLOW-TASK-PACK]
  schemas: [SCH-PACK-RESULT]
  governance: [GOV-CODE-PRINCIPLES]
deliverables: []
verification: []
links: [PLAN-MAIN]
---

# Task: T-011-feature-precision

## Intent

- Ensure all core user-facing features work end-to-end without missing workflow steps.

## Goal

- Improve feature completeness and consistency across task pack, record, closeout, and plan/task state transitions.

## Scope

- close functional gaps discovered after T-010 closeout automation
- ensure all documented tool flows are actually executable
- unify behavior and error semantics across CLI and MCP paths
- avoid introducing breaking tool surface changes

## Context Requirements

- required: ARCH-INDEX, PLAN-MAIN

## Implementation Approach

- build a feature matrix from architecture/index + plan + tool surface
- for each feature, verify: command entrypoint, handler coverage, error model, dry-run/apply behavior
- patch missing transitions or handler gaps before adding new scope
- keep docs and validation rules aligned with actual runtime behavior

## Verification Approach

- run feature-level scenarios for:
  - `task.pack`
  - `task.targets`
  - `task.record`
  - `task.complete`
  - `doc.snippet`
  - `issue.triage`
  - `convention.get`
- verify that each feature has deterministic success/error envelope behavior
- run:
  - `uv run --extra dev ruff check .`
  - `uv run --extra dev mypy .`
  - `uv run --extra dev pytest -q`
  - `uv run --extra dev python scripts/validate_docs.py`

## Implementation Result

- Pending (do not fill until the task is completed)

- Updated Phase 5 from placeholders to executable tasks (T-012~T-014) and linked mode-transition flow into plan/architecture/overview
## Verification Result

- Pending (do not fill until the task is completed)
- Dogfooding run succeeded for task.list/task.pack(T-012)/task.targets/doc.snippet/issue.triage/convention.get/task.complete(dry-run)
