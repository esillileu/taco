---
id: I-001
type: intent
title: I-001-intent-plan-mode
status: active
plan_ref: PLAN-MAIN
task_refs: [T-018]
links: [PROJ-INTENT-INDEX, PLAN-MAIN, ARCH-INDEX, T-018]
---

# Intent: I-001-intent-plan-mode

## Intent

- Keep planning flow intent-first so plan mode starts from intent, not directly from task execution.

## Scope

- Add and maintain `plan.intent.list/view/index` as the planning entry surface.
- Keep intent-to-task linkage explicit through `task_refs` in intent front matter.
- Reflect the same flow in overview, plan, architecture, and README.

## Expected Outcome

- Planner can call `plan.intent.index` to receive plan-scoped architecture/flow/schema coverage with linked executable task references.
- Build remains task-execution-centric through `task.pack` and task closeout tools.
