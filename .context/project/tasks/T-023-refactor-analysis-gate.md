---
id: T-023
type: task
title: T-023-refactor-analysis-gate
status: done
plan_ref: PLAN-MAIN
priority: p0
estimate: m
scope:
  in:
  - src/taco/tools.py
  - src/taco/main.py
  - src/taco/cli.py
  - .context/project/architecture/flows/mode-transition.md
  - .context/project/overview.md
  - .context/project/plan.md
  - tests/test_tools.py
  - tests/test_cli_main.py
  out:
  - build-mode task execution semantics change
references:
  modules:
  - MOD-TOOLS-DISPATCH
  - MOD-CLI-MAPPER
  - MOD-MAIN
  flows:
  - FLOW-MODE-TRANSITION
  - FLOW-TOOL-DISPATCH
  schemas:
  - SCH-TOOL-ENVELOPE
  - SCH-TOOL-ERROR
  governance:
  - GOV-CODE-PRINCIPLES
  - GOV-DOC-INDEX
deliverables:
- refactor intent precondition gate (`code-analysis` before design/task finalization)
- deterministic analysis result shape for planner consumption
verification:
- uv run --extra dev pytest -q
- uv run --extra dev python scripts/validate_docs.py
links:
- PLAN-MAIN
- ARCH-INDEX
- I-020
---

# Task: T-023-refactor-analysis-gate

## Intent
<!-- taco:pack=task.core -->

- Ensure refactor planning decisions are based on real code analysis rather than keyword-only assumptions.

## Goal
<!-- taco:pack=task.core -->

- Add a deterministic pre-design analysis gate for `intent.kind == refactor`.

## Scope
<!-- taco:pack=task.core,pack.next_actions -->

- Add planner rule: refactor intent must run code analysis before architecture/task finalization.
- Define analysis outputs that can drive design impact classification.
- Keep behavior backward compatible for non-refactor intents.

## Context Requirements

- required: ARCH-INDEX, PLAN-MAIN, GOV-DOC-INDEX

## Implementation Approach
<!-- taco:pack=task.plans,pack.next_actions -->

- Extend plan intent workflow to include a required analysis phase for refactor kind.
- Reuse existing oversized-file/dependency heuristics and publish stable output fields.
- Add tests for gate enforcement and deterministic output.

## Verification Approach
<!-- taco:pack=task.plans,pack.acceptance_checks,pack.verification_commands -->

- Verify refactor intent cannot proceed to finalized generation without analysis result.
- Verify non-refactor intents keep current behavior.
- Run:
  - `uv run --extra dev pytest -q`
  - `uv run --extra dev python scripts/validate_docs.py`

## Implementation Result

- Pending

- Added refactor analysis-first lane in plan intent workflow: intent kind/design_impact parsing, analysis payload generation in plan.intent.index, quality gate enforcement for refactor analysis, and deterministic surfaced findings for task generation/review bundle.
## Verification Result

- Pending
- Validated via automated tests and docs checks: uv run --extra dev pytest -q; uv run --extra dev python scripts/validate_docs.py; plus plan.intent.index/review-bundle output confirms analysis fields and refactor gating behavior.
