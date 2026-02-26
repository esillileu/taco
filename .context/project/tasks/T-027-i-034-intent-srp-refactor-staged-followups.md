---
id: T-027
type: task
title: T-027-i-034-intent-srp-refactor-staged-followups
status: done
plan_ref: PLAN-MAIN
scope:
  in:
  - src/taco/core/usecases/plan
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
- I-034
- ARCH-INDEX
- GOV-CODE-PRINCIPLES
---

# Task: T-027-i-034-intent-srp-refactor-staged-followups

## Intent

- Split `core/usecases/plan/intent.py` into cohesive modules while preserving plan-intent tool behavior.

## Goal

- Replace monolithic intent orchestration file with query/pipeline/review/apply/helper modules.
- Keep dispatcher contracts and CLI/MCP behavior unchanged.

## Scope

- Refactor `src/taco/core/usecases/plan/intent.py` into modular files:
  - `intent_query.py`
  - `intent_pipeline.py`
  - `intent_review.py`
  - `intent_apply.py`
  - `intent_helpers.py`
- Keep `intent.py` as a thin facade exposing existing handler symbols.
- Do not change user-facing tool names or payload schemas.

## Implementation Approach

1. Move index/list/view/validate concerns into query module.
2. Move bundle/fingerprint/task-blueprint derivation into pipeline+helpers.
3. Move review gate logic and apply gate logic into dedicated modules.
4. Leave facade wrappers in `intent.py` to preserve import compatibility.
5. Run focused tests and full regression before task closeout.

## Verification Approach

- `uv run ruff check src/taco/core/usecases/plan/intent*.py src/taco/core/usecases/plan/__init__.py`
- `uv run pytest -q tests/test_cli_main.py tests/test_tools.py tests/test_integration_mcp_cli.py`
- `uv run pytest -q`
- `uv run taco plan validate`

## Implementation Result

- Pending implementation updates.

- - Refactored monolithic plan intent usecase into responsibility-based modules: intent_query.py, intent_pipeline.py, intent_review.py, intent_apply.py, and intent_helpers.py.\n- Reduced intent.py to thin facade wrappers preserving existing handler symbols and input contracts.\n- Kept plan/intent tool behavior and dispatcher-facing API stable while isolating query, fingerprint pipeline, review gate, and apply mutation paths.\n- Synced mode-transition flow intent refs for I-034 to keep plan validation consistent.
- Intent usecase modular decomposition completed with stable external contracts and reduced file responsibility overlap. design-sync: FLOW-MODE-TRANSITION intent_refs updated to include I-034 and validation rechecked.
## Verification Result

- Pending verification results.
- - uv run ruff check src/taco/core/usecases/plan/intent*.py src/taco/core/usecases/plan/__init__.py : pass\n- uv run pytest -q tests/test_cli_main.py tests/test_tools.py tests/test_integration_mcp_cli.py : pass\n- uv run pytest -q : pass\n- uv run taco plan validate : pass
- ruff targeted, focused pytest, full pytest, and plan validate passed.
