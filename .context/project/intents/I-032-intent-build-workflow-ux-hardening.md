---
id: I-032
type: intent
title: I-032-intent-build-workflow-ux-hardening
status: active
plan_ref: PLAN-MAIN
task_refs:
- T-025
links:
- PROJ-INTENT-INDEX
- PLAN-MAIN
- ARCH-INDEX
- T-025
---

# Intent: I-032-intent-build-workflow-ux-hardening

## Intent

- Remove recurring operator errors in build workflow commands and make pack/precheck/postcheck/record flows self-explanatory.

## Design Boundary

- Keep plan/build mode separation and existing task execution semantics unchanged.
- Improve CLI ergonomics, validation messages, and operator-facing guidance only.
- Do not change core task selection policy or tool contract naming.

## Expected Design Outcome

- `build precheck` input handling is explicit and hard to misuse.
- `build postcheck` changed-path/output-path expectations are validated with clear remediation messages.
- `task record` content handling avoids shell substitution surprises through safer UX and docs.
