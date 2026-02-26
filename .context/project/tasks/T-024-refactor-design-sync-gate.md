---
id: T-024
type: task
title: T-024-refactor-design-sync-gate
status: done
plan_ref: PLAN-MAIN
priority: p0
estimate: m
scope:
  in:
  - src/taco/tools.py
  - src/taco/router.py
  - .context/project/architecture/index.md
  - .context/project/architecture/flows/mode-transition.md
  - .context/project/plan.md
  - tests/test_tools.py
  - tests/test_task_complete.py
  out:
  - unrelated feature planning behavior changes
references:
  modules:
  - MOD-TOOLS-DISPATCH
  - MOD-ROUTER
  flows:
  - FLOW-MODE-TRANSITION
  - FLOW-TASK-RECORD
  schemas:
  - SCH-WRITE-TARGET
  - SCH-TOOL-ERROR
  - SCH-TOOL-ENVELOPE
  governance:
  - GOV-CODE-PRINCIPLES
  - GOV-DOC-INDEX
deliverables:
- refactor closeout gate for required architecture/flow sync
- clear failure reason when design-impact exists but docs were not updated
verification:
- uv run --extra dev pytest -q
- uv run --extra dev python scripts/validate_docs.py
links:
- PLAN-MAIN
- ARCH-INDEX
- I-020
---

# Task: T-024-refactor-design-sync-gate

## Intent
<!-- taco:pack=task.core -->

- Prevent refactor completion drift by forcing design docs to match boundary-impacting code changes.

## Goal
<!-- taco:pack=task.core -->

- Require architecture/flow document sync when refactor impact is `minor` or `major`.

## Scope
<!-- taco:pack=task.core,pack.next_actions -->

- Add closeout validation for refactor tasks with non-none design impact.
- Define and return explicit error details when design sync evidence is missing.
- Keep validation deterministic and auditable from task records.

## Context Requirements

- required: ARCH-INDEX, PLAN-MAIN, GOV-DOC-INDEX

## Implementation Approach
<!-- taco:pack=task.plans,pack.next_actions -->

- Extend task closeout validation to inspect declared refactor impact and required doc updates.
- Reuse task targets/record path metadata for traceability of design-sync evidence.
- Add tests for pass/fail branches of the new closeout gate.

## Verification Approach
<!-- taco:pack=task.plans,pack.acceptance_checks,pack.verification_commands -->

- Verify refactor task completion fails when required architecture/flow updates are missing.
- Verify completion passes when required design sync is recorded.
- Run:
  - `uv run --extra dev pytest -q`
  - `uv run --extra dev python scripts/validate_docs.py`

## Implementation Result

- Pending

- Implemented refactor closeout design-sync gate in task.complete: resolves linked intents, enforces design-sync evidence when refactor design_impact is minor/major, and returns deterministic error details for missing sync evidence.
## Verification Result

- Pending
- Validated fail/pass branches through new tests and full suite: task.complete rejects missing design-sync for refactor-major and accepts explicit design-sync evidence; uv run --extra dev pytest -q and uv run --extra dev python scripts/validate_docs.py passed.
