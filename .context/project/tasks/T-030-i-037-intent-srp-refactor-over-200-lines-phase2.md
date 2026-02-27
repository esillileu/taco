---
id: T-030
type: task
title: T-030-i-037-intent-srp-refactor-over-200-lines-phase2
status: blocked
plan_ref: PLAN-MAIN
scope:
  in:
  - src/taco
  - .context/project
  out: []
references:
  modules:
  - ARCH-INDEX
  flows:
  - PLAN-MAIN
  schemas:
  - GOV-CODE-PRINCIPLES
links:
- PLAN-MAIN
- I-037
- ARCH-INDEX
- GOV-CODE-PRINCIPLES
---

# Task: T-030-i-037-intent-srp-refactor-over-200-lines-phase2

## Intent

- Decompose the remaining oversized production file into capability modules with explicit boundaries and a stable facade.

## Goal

- Refactor `src/taco/core/usecases/plan/intent_helpers.py` (over line budget) into structured, functional modules without changing public CLI/MCP behavior.

## Scope

- Code:
  - `src/taco/core/usecases/plan/intent_helpers.py`
  - new modules under `src/taco/core/usecases/plan/` for helper capabilities
- Docs:
  - `.context/project/architecture/modules/tools-dispatch.md`
  - `.context/project/architecture/flows/mode-transition.md` (if intent refs/boundaries change)

## Implementation Approach

1. Split helper responsibilities into capability units:
   - path/config lookup
   - task-blueprint derivation
   - plan queue mutation support
   - intent/task link merge helpers
2. Keep a thin facade file that preserves existing call surface.
3. Enforce dependency direction: helper utilities must not introduce cross-layer coupling.
4. Sync architecture docs when module boundaries or flow references are affected.

## Verification Approach

- `uvx ruff check src/taco/core/usecases/plan`
- `uv run pytest -q tests/cli/test_plan_intent_flow.py tests/tools/test_dispatch_and_pack.py`
- `uv run pytest -q`
- `uv run taco plan validate`
- `uv run python scripts/validate_docs.py`

## Implementation Result

- Pending implementation updates.

- blocked: [scope_split_required] Prioritize I-038 test-suite refactor lane before continuing T-030
## Verification Result

- Pending verification results.
