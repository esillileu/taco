---
id: I-035
type: intent
title: I-035-intent-task-pack-srp-split
status: active
kind: refactor
design_impact: major
plan_ref: PLAN-MAIN
task_refs:
- T-028
links:
- PROJ-INTENT-INDEX
- PLAN-MAIN
- ARCH-INDEX
- T-028
---

# Intent: I-035-intent-task-pack-srp-split

## Intent

- Decompose `core/task/pack.py` into focused modules for selection, readiness validation, and pack assembly orchestration.

## Design Boundary

- Keep `task.pack` and `plan.pack` behavior and payload contracts unchanged.
- Preserve current dispatch imports and symbol names at facade boundary.
- Restrict changes to pack-related code and required architecture doc sync.

## Expected Design Outcome

- `core/task/pack.py` no longer mixes auto-selection, readiness checks, and assembly logic in one file.
- Readiness policy becomes reusable from plan review/support modules via dedicated helpers.
- Future pack policy changes can be made without touching unrelated execution logic.
