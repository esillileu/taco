---
id: I-041
type: intent
title: Guarantee taco init canonical governance/template parity across local and packaged
  runs
status: active
plan_ref: PLAN-MAIN
task_refs: []
links:
- PLAN-MAIN
- ARCH-INDEX
- PROJ-INTENT-INDEX
kind: general
---

# Intent: i-041-guarantee-taco-init-canonical-governance-template-parity-across-local-and-packaged-runs

## Intent

- Ensure `taco init` always emits executable baseline docs and governance templates identical to canonical sources in both local and distributed package execution.

## Scope

- In Scope:
  - Init template resource packaging and canonical source mapping
  - Regression checks that generated governance files match canonical templates byte-for-byte
  - Parity verification between local source run and packaged distribution run
- Out of Scope:
  - Team-specific policy customization in init output
  - Non-init workflow behavior changes

## Source

- input_type: agent_decomposed
