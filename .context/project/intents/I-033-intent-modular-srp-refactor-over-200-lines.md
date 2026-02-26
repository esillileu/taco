---
id: I-033
type: intent
title: I-033-intent-modular-srp-refactor-over-200-lines
status: active
kind: refactor
design_impact: major
plan_ref: PLAN-MAIN
task_refs:
- T-026
links:
- PROJ-INTENT-INDEX
- PLAN-MAIN
- ARCH-INDEX
- T-026
---

# Intent: I-033-intent-modular-srp-refactor-over-200-lines

## Intent

- Refactor files over 200 lines into purpose-driven modules with explicit boundaries and single responsibility.

## Design Boundary

- Keep external CLI/MCP contracts stable while reorganizing internal module boundaries.
- Separate orchestration, validation, transformation, and I/O concerns into focused modules.
- Prioritize extensibility and testability over flat file splitting.

## Expected Design Outcome

- High-churn files are split into cohesive submodules with clear naming and dependency direction.
- Test suites are reorganized by behavior domain to reduce oversized mixed-purpose test files.
- Architectural docs and flow references are updated to reflect new module boundaries.
