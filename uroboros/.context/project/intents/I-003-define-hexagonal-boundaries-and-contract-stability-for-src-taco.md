---
id: I-003
type: intent
title: Define Hexagonal Boundaries and Contract Stability for src/taco
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

# Intent: i-003-define-hexagonal-boundaries-and-contract-stability-for-src-taco

## Intent

- Formalize ports-and-adapters boundaries so core rules remain isolated from transport/storage implementations while preserving command I/O compatibility.

## Scope

- In Scope:
  - Document core/ports/adapters responsibilities and allowed dependency directions.
  - Define constraints for CLI/MCP entrypoints to use core use-cases without bypass.
  - Specify compatibility expectations for tool contract changes and migration scenarios.
- Out of Scope:
  - Replacing Python runtime with Rust in this phase.
  - Refactoring all existing modules immediately.

## Source

- input_type: agent_decomposed
