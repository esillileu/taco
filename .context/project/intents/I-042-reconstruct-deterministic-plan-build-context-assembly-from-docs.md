---
id: I-042
type: intent
title: Reconstruct deterministic Plan/Build context assembly from docs
status: active
plan_ref: PLAN-MAIN
task_refs: []
links:
- PROJ-INTENT-INDEX
- PLAN-MAIN
- ARCH-INDEX
kind: general
design_impact: High impact on core planning/build orchestration contracts and task
  decomposition boundaries.
---

# Intent: i-042-reconstruct-deterministic-plan-build-context-assembly-from-docs

## Intent

- Recreate TACO so plan/build context packs are assembled deterministically from .context documents with traceable references and stable outputs across operator changes.

## Scope

- In Scope:
  - Define plan.pack/task.pack/plan.intent.index behavior against document SSOT and minimal-loading rules.
  - Specify traceability payload requirements (references, paths, reason codes) for pack outputs.
  - Decompose plan-to-build flow into executable tasks with validation gates.
- Out of Scope:
  - Implementing broad autonomous coding behavior.
  - Full-text search engine behavior across arbitrary repositories.

## Source

- input_type: agent_decomposed
