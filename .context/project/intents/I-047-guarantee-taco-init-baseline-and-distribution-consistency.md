---
id: I-047
type: intent
title: Guarantee taco init Baseline and Distribution Consistency
status: active
plan_ref: PLAN-MAIN
task_refs: []
links:
- PLAN-MAIN
- ARCH-INDEX
- PROJ-INTENT-INDEX
kind: general
design_impact: high
---

# Intent: i-047-guarantee-taco-init-baseline-and-distribution-consistency

## Intent

- Ensure taco init deterministically generates the required governance and project baseline documents and that local and packaged executions produce identical outputs.

## Scope

- In Scope:
  - Define canonical template source for governance docs
  - Specify packaging/resource inclusion requirements for templates
  - Define regression checks that compare generated outputs against canonical templates
- Out of Scope:
  - New documentation taxonomy redesign
  - Non-init command behavior changes

## Source

- input_type: agent_decomposed
