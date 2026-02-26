---
id: I-021
type: intent
title: refactor-plan-gate-task-generation
status: active
plan_ref: PLAN-MAIN
task_refs:
- T-025
- T-026
- T-027
links:
- PROJ-INTENT-INDEX
- PLAN-MAIN
- ARCH-INDEX
---

# Intent: I-021-refactor-plan-gate-task-generation

## Intent

- Add a plan-mode quality gate so refactor flow cannot proceed without explicit refactor-plan evidence.
- Keep generated task documents limited to executable code-change scope.

## Scope

- Require refactor intent docs to include `## Refactor Plan` before task generation/apply passes.
- Ensure task generation does not place design-level change requests into task scope sections.
- Keep the gate deterministic and compatible with existing non-refactor intent flow.

## Expected Outcome

- Planner receives a clear fail reason when refactor plan evidence is missing.
- After plan evidence is present, intent review/apply can generate executable tasks cleanly.
- Task docs remain implementation-focused while design updates stay in intent/architecture/plan surfaces.
