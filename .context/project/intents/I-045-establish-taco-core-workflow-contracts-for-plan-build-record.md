---
id: I-045
type: intent
title: Establish TACO Core Workflow Contracts for Plan-Build-Record
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

# Intent: i-045-establish-taco-core-workflow-contracts-for-plan-build-record

## Intent

- Define and formalize deterministic Plan->Build->Record workflow contracts so task execution packs and lifecycle transitions are reproducible and traceable.

## Scope

- In Scope:
  - Define task/plan pack behavior and selection rules
  - Define lifecycle state handling for task.record, task.complete, task.block
  - Define traceability requirements for implementation and verification records
- Out of Scope:
  - Implementing generic coding-agent capabilities
  - Adding broad full-text search features

## Source

- input_type: agent_decomposed
