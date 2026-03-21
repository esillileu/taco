---
id: I-040
type: intent
title: Enforce hexagonal boundaries and stable tool I/O contracts for src/taco
status: active
plan_ref: PLAN-MAIN
task_refs: []
links:
- ARCH-INDEX
- PLAN-MAIN
- PROJ-INTENT-INDEX
kind: general
---

# Intent: i-040-enforce-hexagonal-boundaries-and-stable-tool-i-o-contracts-for-src-taco

## Intent

- Preserve ports-and-adapters architecture so core use cases remain I/O-agnostic while CLI/MCP adapters honor stable tool contracts.

## Scope

- In Scope:
  - Domain/core use cases independent from filesystem/git/MCP implementation
  - Port definitions for repositories and external interactions
  - Adapter conformance for CLI/MCP entrypoints without bypassing core
- Out of Scope:
  - Runtime rewrite to a new language in this phase
  - Feature expansion unrelated to architecture boundary compliance

## Source

- input_type: agent_decomposed
