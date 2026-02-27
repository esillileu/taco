---
id: I-037
type: intent
title: I-037-intent-srp-refactor-over-200-lines-phase2
status: active
kind: refactor
design_impact: major
plan_ref: PLAN-MAIN
task_refs:
- T-030
links:
- PROJ-INTENT-INDEX
- PLAN-MAIN
- ARCH-INDEX
- T-030
---

# Intent: I-037-intent-srp-refactor-over-200-lines-phase2

## Intent

- Continue over-200-line refactor with structural, capability-based decomposition.

## Design Boundary

- Keep public CLI/MCP contracts stable.
- Split by responsibility boundaries (`policy`, `normalization`, `orchestration`, `io`), not by flat line windows.

## Expected Design Outcome

- Remaining oversized files are converted into thin-facade plus focused submodules.
- Related tests and architecture refs stay synchronized with each split.
