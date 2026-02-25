---
id: T-011
type: task
title: T-011-pack-precision
status: active
plan_ref: PLAN-MAIN
priority: p1
estimate: m
scope:
  in:
    - src/taco/pack.py
    - src/taco/tools.py
    - .context/project/architecture/index.md
  out:
    - major tool surface rename
references:
  modules: [MOD-PACK, MOD-TOOLS-DISPATCH]
  flows: [FLOW-TASK-PACK]
  schemas: [SCH-PACK-RESULT]
  governance: [GOV-CODE-PRINCIPLES]
deliverables: []
verification: []
links: [PLAN-MAIN]
---

# Task: T-011-pack-precision

## Intent

- Reduce pack payload noise while keeping one-call readiness.

## Goal

- Make `task.pack` include only action-ready context for the selected task and required refs.

## Scope

- tighten context extraction and filtering behavior
- remove residual legacy selector-path behavior where possible
- keep deterministic ordering and stable contract shape

## Context Requirements

- required: ARCH-INDEX, PLAN-MAIN

## Implementation Approach

- refine candidate building so task execution fields are extracted with less repetition
- ensure reference-derived snippets are prioritized and deduplicated
- keep required references strict and optional references budget-aware
- update architecture/plan docs when pack behavior changes

## Verification Approach

- verify deterministic output across repeated calls
- verify reduced token usage for same task without missing required checks
- run: `uv run --extra dev ruff check .`
- run: `uv run --extra dev mypy .`
- run: `uv run --extra dev pytest -q`
- run: `uv run --extra dev python scripts/validate_docs.py`

## Implementation Result

- Pending (do not fill until the task is completed)

## Verification Result

- Pending (do not fill until the task is completed)
