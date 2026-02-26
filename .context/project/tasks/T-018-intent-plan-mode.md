---
id: T-018
type: task
title: T-018-intent-plan-mode
status: done
plan_ref: PLAN-MAIN
priority: p1
estimate: m
scope:
  in:
    - src/taco/main.py
    - src/taco/cli.py
    - src/taco/tools.py
    - scripts/validate_docs.py
    - taco.yaml
    - README.md
    - .context/project/overview.md
    - .context/project/plan.md
    - .context/project/architecture/index.md
    - .context/project/intents/index.md
    - .context/project/intents/I-001-intent-plan-mode.md
    - .context/governance/doc/index.md
    - tests/test_cli_main.py
    - tests/test_tools.py
    - tests/test_integration_mcp_cli.py
    - tests/test_task_complete.py
  out:
    - build-mode task execution semantics change
    - git convention rules content change
references:
  modules: [MOD-MAIN, MOD-CLI-MAPPER, MOD-TOOLS-DISPATCH, MOD-INDEXER, MOD-PACK]
  flows: [FLOW-MODE-TRANSITION, FLOW-TASK-PACK, FLOW-TOOL-DISPATCH]
  schemas: [SCH-PACK-RESULT, SCH-TOOL-ENVELOPE, SCH-TOOL-ERROR, SCH-INDEX-GRAPH]
  governance: [GOV-CODE-PRINCIPLES, GOV-DOC-INDEX]
deliverables:
  - plan intent tool surface and CLI mapping (`plan.intent.list/view/index`)
  - intent document model and validation rules (`type: intent`, `plan_ref`, `task_refs`)
  - intent-first planning workflow reflected in overview/plan/architecture/readme
verification:
  - uv run --extra dev ruff check .
  - uv run --extra dev mypy .
  - uv run --extra dev pytest -q
  - uv run --extra dev python scripts/validate_docs.py
links: [PLAN-MAIN, ARCH-INDEX, PROJ-INTENT-INDEX, I-001]
---

# Task: T-018-intent-plan-mode

## Intent
<!-- taco:pack=task.core -->

- Keep plan mode aligned with intent-first philosophy and make it executable via TACO tool flow.

## Goal
<!-- taco:pack=task.core -->

- Provide deterministic plan-intent tools and keep plan/design/intent documentation fully consistent with runtime behavior.

## Scope
<!-- taco:pack=task.core,pack.next_actions -->

- Add CLI and tool dispatch support for `plan intent list/view/index`.
- Ensure `plan.intent.index` resolves executable-task coverage through intent `task_refs`.
- Extend doc validation for `type: intent` with required `plan_ref` and `task_refs`.
- Update SSOT docs (overview/plan/architecture/README/governance doc index) to reflect intent-first planning.

## Context Requirements

- required: ARCH-INDEX, PLAN-MAIN, GOV-DOC-INDEX

## Implementation Approach
<!-- taco:pack=task.plans,pack.next_actions -->

- Wire argparse and CLI mapper to normalized MCP tool names.
- Implement intent list/view/index handlers in tools dispatch with stable error envelopes.
- Keep required refs mode-aware using `pack.required_refs_by_tool` and add `plan.intent.index` defaults.
- Introduce `.context/project/intents/` as canonical intent registry and keep references id-only.

## Verification Approach
<!-- taco:pack=task.plans,pack.acceptance_checks,pack.verification_commands -->

- Confirm `plan.intent.list/view/index` works from both CLI mapping and direct tool calls.
- Confirm `plan.locate --change-type intent` and `plan.view` include intent nodes.
- Confirm validation accepts intent docs and rejects missing required intent fields.
- Run:
  - `uv run --extra dev ruff check .`
  - `uv run --extra dev mypy .`
  - `uv run --extra dev pytest -q`
  - `uv run --extra dev python scripts/validate_docs.py`

## Implementation Result

- Added `plan intent` CLI surface in `main.py` and mapped actions in `cli.py`:
  - `plan.intent.list`
  - `plan.intent.view`
  - `plan.intent.index`
- Implemented plan-intent handlers in `tools.py` with deterministic error envelopes:
  - intent discovery/view
  - intent index generation via `task_refs` coverage
  - plan view and locator coverage for `intent` nodes
- Migrated default policy to tool-specific refs in `taco.yaml` with `plan_intent_index`.
- Added intent SSOT docs:
  - `.context/project/intents/index.md`
  - `.context/project/intents/I-001-intent-plan-mode.md`
- Updated overview/plan/architecture/README/governance docs to reflect intent-first plan workflow.
- Extended doc validation to accept and validate `type: intent` with required `plan_ref` and `task_refs`.
- Added/updated tests for CLI, tool, integration, bootstrap, and docs presence.

## Verification Result

- `uv run --extra dev ruff check .` passed.
- `uv run --extra dev mypy .` passed.
- `uv run --extra dev pytest -q` passed (`63 passed`).
- `uv run --extra dev python scripts/validate_docs.py` passed.
