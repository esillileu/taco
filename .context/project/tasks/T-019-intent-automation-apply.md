---
id: T-019
type: task
title: T-019-intent-automation-apply
status: active
plan_ref: PLAN-MAIN
priority: p0
estimate: l
scope:
  in:
    - src/taco/main.py
    - src/taco/cli.py
    - src/taco/tools.py
    - scripts/validate_docs.py
    - README.md
    - .context/project/architecture/index.md
    - .context/project/architecture/modules/tools-dispatch.md
    - tests/test_cli_main.py
    - tests/test_tools.py
    - tests/test_integration_mcp_cli.py
  out:
    - build mode execution semantics change
    - legacy task/doc tool behavior changes
references:
  modules: [MOD-MAIN, MOD-CLI-MAPPER, MOD-TOOLS-DISPATCH, MOD-PACK]
  flows: [FLOW-MODE-TRANSITION, FLOW-TOOL-DISPATCH]
  schemas: [SCH-TOOL-ENVELOPE, SCH-TOOL-ERROR, SCH-INDEX-GRAPH]
  governance: [GOV-CODE-PRINCIPLES, GOV-DOC-INDEX]
deliverables:
  - plan intent automation tools (`propose`, `autodesign`, `generate_tasks`, `review_bundle`)
  - one-shot retry on fail for review bundle (`retry_on_fail=1`)
  - approval-gated apply flow with fingerprint check (`plan.intent.apply`)
verification:
  - uv run --extra dev ruff check .
  - uv run --extra dev mypy .
  - uv run --extra dev pytest -q
  - uv run --extra dev python scripts/validate_docs.py
links: [PLAN-MAIN, ARCH-INDEX, I-001]
---

# Task: T-019-intent-automation-apply

## Intent
<!-- taco:pack=task.core -->

- Automate plan-mode intent workflow through proposal, design derivation, task derivation, review, and approval-gated apply.

## Goal
<!-- taco:pack=task.core -->

- Make intent-first planning executable end-to-end in plan mode without leaking build-mode context.

## Scope
<!-- taco:pack=task.core,pack.next_actions -->

- Add `plan.intent.propose` to normalize incoming intent payload.
- Add `plan.intent.autodesign` to derive architecture/plan update proposals from indexed gaps.
- Add `plan.intent.generate_tasks` with deterministic risk-priority ordering.
- Add `plan.intent.review_bundle` with optional one-shot retry (`retry_on_fail=1`).
- Add `plan.intent.apply` with fingerprint gate and dry-run/apply paths.

## Context Requirements

- required: ARCH-INDEX, PLAN-MAIN, GOV-DOC-INDEX

## Implementation Approach
<!-- taco:pack=task.plans,pack.next_actions -->

- Extend CLI parser and mapper for the new plan intent actions and options.
- Implement deterministic helper utilities for task derivation and gap handling.
- Keep apply behavior section-oriented (front matter/targeted patches) instead of whole-doc regeneration.
- Ensure stale fingerprint or failed quality gate blocks apply.

## Verification Approach
<!-- taco:pack=task.plans,pack.acceptance_checks,pack.verification_commands -->

- Verify each new tool path returns stable envelopes.
- Verify `retry_on_fail=1` reports retry metadata.
- Verify `plan.intent.apply` succeeds in dry-run with valid fingerprint and blocks invalid fingerprint.
- Run:
  - `uv run --extra dev ruff check .`
  - `uv run --extra dev mypy .`
  - `uv run --extra dev pytest -q`
  - `uv run --extra dev python scripts/validate_docs.py`

## Implementation Result

- Pending (do not fill until the task is completed)

## Verification Result

- Pending (do not fill until the task is completed)
