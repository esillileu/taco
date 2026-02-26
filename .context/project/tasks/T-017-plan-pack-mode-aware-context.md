---
id: T-017
type: task
title: T-017-plan-pack-mode-aware-context
status: active
plan_ref: PLAN-MAIN
priority: p1
estimate: m
scope:
  in:
    - src/taco/main.py
    - src/taco/cli.py
    - src/taco/tools.py
    - src/taco/pack.py
    - taco.yaml
    - tests/test_cli_main.py
    - tests/test_tools.py
    - tests/test_integration_mcp_cli.py
    - README.md
    - .context/project/overview.md
    - .context/project/plan.md
    - .context/project/architecture/index.md
  out:
    - build-mode execution semantics change
    - git automation implementation
references:
  modules: [MOD-MAIN, MOD-CLI-MAPPER, MOD-TOOLS-DISPATCH, MOD-PACK]
  flows: [FLOW-MODE-TRANSITION, FLOW-TASK-PACK, FLOW-TOOL-DISPATCH]
  schemas: [SCH-PACK-RESULT, SCH-TOOL-ENVELOPE, SCH-TOOL-ERROR]
  governance: [GOV-CODE-PRINCIPLES, GOV-DOC-INDEX, GOV-GIT-INDEX]
deliverables:
  - "`plan.pack` tool surface and CLI mapping"
  - "mode-intent-based required refs policy in config/runtime"
  - "build git convention on-demand workflow documentation"
verification:
  - uv run --extra dev ruff check .
  - uv run --extra dev mypy .
  - uv run --extra dev pytest -q
  - uv run --extra dev python scripts/validate_docs.py
links: [PLAN-MAIN, ARCH-INDEX, FLOW-MODE-TRANSITION]
---

# Task: T-017-plan-pack-mode-aware-context

## Intent
<!-- taco:pack=task.core -->

- Separate plan/build context defaults by intent so pack behavior matches mode responsibilities.

## Goal
<!-- taco:pack=task.core -->

- Introduce plan-specific pack loading while keeping build execution deterministic and minimal.

## Scope
<!-- taco:pack=task.core,pack.next_actions -->

- Add `plan.pack` as a first-class tool and CLI command.
- Replace single `pack.common_required_refs` policy with mode-intent-aware required refs:
  - plan defaults: `ARCH-INDEX`, `PLAN-MAIN`, `GOV-DOC-INDEX`
  - build defaults: `GOV-CODE-PRINCIPLES`
- Keep `task.pack` as build workflow entrypoint.
- Keep git conventions out of always-on build pack and define on-demand lookup flow:
  - `convention.get(topic=git)` before git actions
  - optional `doc.snippet` for specific rule anchors

## Context Requirements

- required: ARCH-INDEX, PLAN-MAIN, FLOW-MODE-TRANSITION

## Implementation Approach
<!-- taco:pack=task.plans,pack.next_actions -->

- Add `plan pack` parser/action and CLI-to-tool mapping.
- Add `plan.pack` handler in tools dispatcher and route required refs by tool.
- Add config compatibility strategy:
  - prefer `pack.required_refs_by_tool`
  - fallback to `pack.common_required_refs` for backward compatibility
- Update architecture/overview/plan/readme to reflect tool surface and mode policy.

## Verification Approach
<!-- taco:pack=task.plans,pack.acceptance_checks,pack.verification_commands -->

- `plan.pack` returns stable pack envelope for valid task inputs.
- `task.pack` continues build-mode behavior with no regressions.
- Required refs differ by tool as configured.
- Git behavior flow is documented and traceable through conventions tools.
- Run:
  - `uv run --extra dev ruff check .`
  - `uv run --extra dev mypy .`
  - `uv run --extra dev pytest -q`
  - `uv run --extra dev python scripts/validate_docs.py`

## Implementation Result

- Pending (do not fill until the task is completed)

## Verification Result

- Pending (do not fill until the task is completed)
