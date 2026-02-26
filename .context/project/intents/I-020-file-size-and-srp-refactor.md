---
id: I-020
type: intent
title: file-size-and-srp-refactor
status: active
kind: refactor
design_impact: tentative
plan_ref: PLAN-MAIN
task_refs:
- T-020
- T-021
- T-022
- T-023
- T-024
links:
- PROJ-INTENT-INDEX
- PLAN-MAIN
- ARCH-INDEX
- T-023
- T-024
---

# Intent: I-020-file-size-and-srp-refactor

## Intent

- Refactor the codebase so each file owns one responsibility.
- Keep source files at or below 250 lines where feasible.

## Scope

- Decompose oversized files into focused modules.
- Preserve behavior and interface contracts while splitting responsibilities.
- Run code analysis before design/task finalization to identify real boundary impacts.

## Refactor Workflow Constraints

- For `kind: refactor`, planner must run code analysis before confirming architecture and task breakdown.
- Build completion must update architecture/flow docs when design boundaries changed.
