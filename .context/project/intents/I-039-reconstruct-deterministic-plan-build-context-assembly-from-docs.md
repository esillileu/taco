---
id: I-039
type: intent
title: Reconstruct deterministic Plan/Build context assembly from docs
status: active
plan_ref: PLAN-MAIN
task_refs: []
links:
- PLAN-MAIN
- ARCH-INDEX
- PROJ-INTENT-INDEX
kind: general
---

# Intent: i-039-reconstruct-deterministic-plan-build-context-assembly-from-docs

## Intent

- Define and implement deterministic context pack assembly so identical document state yields identical plan/build packs with traceable references and reason codes.

## Scope

- In Scope:
  - Deterministic selection and ordering rules for plan/task pack construction
  - Traceability metadata in pack outputs (document ids/paths and rationale codes)
  - Minimal-load policy that avoids full repository scans in normal flow
- Out of Scope:
  - Automated code generation outside task execution context
  - General-purpose semantic search across all documents

## Source

- input_type: agent_decomposed
