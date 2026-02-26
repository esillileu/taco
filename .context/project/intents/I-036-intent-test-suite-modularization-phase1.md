---
id: I-036
type: intent
title: I-036-intent-test-suite-modularization-phase1
status: active
kind: refactor
design_impact: major
plan_ref: PLAN-MAIN
task_refs:
- T-029
links:
- PROJ-INTENT-INDEX
- PLAN-MAIN
- ARCH-INDEX
- T-029
---

# Intent: I-036-intent-test-suite-modularization-phase1

## Intent

- Start staged test modularization by splitting oversized integration test files into fixture-based domain test modules.

## Design Boundary

- Preserve test behavior and assertions; only reorganize structure and shared fixtures.
- Keep runtime/tool contracts unchanged.
- Limit this phase to integration test suite decomposition.

## Expected Design Outcome

- Oversized integration test file is decomposed into focused modules.
- Shared repository fixture setup is centralized and reusable.
- Test execution remains deterministic with no regression.
