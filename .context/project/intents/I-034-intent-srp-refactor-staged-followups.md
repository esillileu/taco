---
id: I-034
type: intent
title: I-034-intent-srp-refactor-staged-followups
status: active
kind: refactor
design_impact: major
plan_ref: PLAN-MAIN
task_refs:
- T-027
links:
- PROJ-INTENT-INDEX
- PLAN-MAIN
- ARCH-INDEX
- T-027
---

# Intent: I-034-intent-srp-refactor-staged-followups

## Intent

- Continue SRP modular refactor through staged tasks focused on remaining large/high-responsibility files.

## Design Boundary

- Keep CLI/MCP public behavior and tool contracts unchanged.
- Execute split by domain phases: plan automation core, pack core, and test-suite modularization.
- Keep each build loop narrow and independently verifiable.

## Expected Design Outcome

- Remaining oversized files are split into cohesive modules without behavior regressions.
- Test layout is aligned with domain boundaries and fixture reuse.
- Plan/build workflow remains deterministic after each staged refactor.
