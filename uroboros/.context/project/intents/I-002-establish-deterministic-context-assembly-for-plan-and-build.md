---
id: I-002
type: intent
title: Establish Deterministic Context Assembly for Plan and Build
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

# Intent: i-002-establish-deterministic-context-assembly-for-plan-and-build

## Intent

- Ensure TACO deterministically assembles task and plan context packs from document SSOT so identical inputs produce identical packs with traceability.

## Scope

- In Scope:
  - Define decomposition from project documents into stable context-pack inputs for plan/build commands.
  - Specify traceability expectations for references, path selection, and rationale capture in intent/task flow.
  - Constrain loading strategy to minimal required snippets rather than whole-repo scans.
- Out of Scope:
  - Implementing runtime-specific optimizations.
  - Adding new unrelated tool commands beyond context assembly flow.

## Source

- input_type: agent_decomposed
