---
id: I-044
type: intent
title: Guarantee taco init canonical governance/template parity across local and packaged
  runs
status: active
plan_ref: PLAN-MAIN
task_refs: []
links:
- PROJ-INTENT-INDEX
- PLAN-MAIN
- ARCH-INDEX
kind: general
design_impact: High impact on initialization reliability and deployment consistency.
---

# Intent: i-044-guarantee-taco-init-canonical-governance-template-parity-across-local-and-packaged-runs

## Intent

- Ensure taco init always produces the same baseline documents and canonical governance templates in both local development and packaged distribution contexts.

## Scope

- In Scope:
  - Define canonical template source and packaging requirements.
  - Define init output parity checks for local vs packaged execution.
  - Define regression tests verifying generated files equal canonical template content.
- Out of Scope:
  - Adding unrelated init scaffolding beyond minimum operational baseline.
  - Team-specific policy customization hardcoded into init.

## Source

- input_type: agent_decomposed
