---
id: I-043
type: intent
title: Enforce hexagonal boundaries and stable tool I/O contracts for src/taco
status: active
plan_ref: PLAN-MAIN
task_refs: []
links:
- PROJ-INTENT-INDEX
- PLAN-MAIN
- ARCH-INDEX
kind: general
design_impact: High impact on architecture governance and long-term replaceability/testability.
---

# Intent: i-043-enforce-hexagonal-boundaries-and-stable-tool-i-o-contracts-for-src-taco

## Intent

- Define and enforce ports/adapters boundaries so core use-cases remain independent from filesystem/git/mcp adapters while preserving stable CLI/MCP tool contracts.

## Scope

- In Scope:
  - Define architecture boundaries for core, ports, adapters, and app entrypoints.
  - Specify contract-compatibility requirements for tool names and I/O schemas.
  - Establish verification expectations for core tests without external I/O.
- Out of Scope:
  - Rewriting runtime language implementation choices.
  - Changing external tool contract semantics without compatibility strategy.

## Source

- input_type: agent_decomposed
