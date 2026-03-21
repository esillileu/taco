---
id: I-046
type: intent
title: Define Hexagonal Architecture Boundaries for src/taco
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

# Intent: i-046-define-hexagonal-architecture-boundaries-for-src-taco

## Intent

- Fix ports-and-adapters boundaries for core, ports, adapters, and app entrypoints so implementations remain testable and replaceable without contract drift.

## Scope

- In Scope:
  - Domain use-case ownership in core layer
  - Port contract definitions for persistence and external interactions
  - Adapter responsibilities for filesystem/git/mcp transport
  - Boundary rules preventing app entrypoints from bypassing core policies
- Out of Scope:
  - Concrete runtime migration to Rust
  - Feature expansion beyond current tool contracts

## Source

- input_type: agent_decomposed
