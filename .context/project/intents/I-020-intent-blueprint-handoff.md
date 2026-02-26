---
id: I-020
type: intent
title: I-020-intent-blueprint-handoff
status: active
plan_ref: PLAN-MAIN
task_refs:
- T-020
links:
- PROJ-INTENT-INDEX
- PLAN-MAIN
- ARCH-INDEX
- T-020
---

# Intent: I-020-intent-blueprint-handoff

## Intent

- Validate intent-to-task handoff where TACO provides blueprint metadata and agents author task content.

## Design Boundary

- TACO handles plan intent proposal/review/apply and queue metadata updates only.
- Task body content remains agent-authored and must satisfy pack readiness gates.
- Build execution starts only after authored task documents pass `task.pack` readiness.

## Expected Design Outcome

- `plan.intent.generate_tasks` returns blueprint requirements without task body text.
- `plan.intent.apply` updates intent/plan metadata with explicit approval and fingerprint checks.
- Build handoff remains deterministic and fails fast when authored content is missing.
