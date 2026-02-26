---
id: T-025
type: task
title: T-025-i-032-intent-build-workflow-ux-hardening
status: done
plan_ref: PLAN-MAIN
scope:
  in:
  - src/taco
  - .context/project
  - tests
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
- I-032
- ARCH-INDEX
- GOV-CODE-PRINCIPLES
---

# Task: T-025-i-032-intent-build-workflow-ux-hardening

## Intent

- Remove avoidable build workflow operator mistakes by hardening command UX and guidance.

## Goal

- Make `task.pack` to `build.precheck` to `build.postcheck` to `task.record` paths deterministic and difficult to misuse.

## Scope

- Clarify and improve `build precheck --pack-json` input handling UX.
- Improve `build postcheck` diagnostics for changed paths vs produced outputs.
- Prevent shell substitution surprises in `task record --content` usage through safer interface/docs.

## Implementation Approach

1. Refine CLI option contracts for pack/precheck/postcheck with explicit accepted input forms and actionable errors.
2. Add integration tests for expected failure cases (invalid pack-json form, postcheck path misuse, record content shell-sensitive examples).
3. Update build-mode entrypoint docs with copy-paste-safe command patterns.

## Verification Approach

- Run targeted tests covering precheck/postcheck/record command error surfaces.
- Run `uv run pytest -q` to confirm no regression.
- Run documentation validation to confirm updated examples are structurally valid.

## Implementation Result

- No implementation changes applied yet in this task document.

- - Improved CLI pack-json UX: build precheck/postcheck now accept inline JSON or a JSON file path for --pack-json with actionable error messages.\n- Added safe recording path for shell-sensitive text via task record --content-file and wired CLI option parsing to read file content directly.\n- Hardened build postcheck diagnostics: strict input type checks, declared required outputs are excluded from boundary violations, and list-based check_results now reports failed checks deterministically.\n- Updated build-mode entrypoint guidance for file-based pack usage and content-file recording.
- Resolved build workflow UX gaps around pack-json input, postcheck diagnostics, and task record shell-sensitive content handling.
## Verification Result

- No verification results recorded yet for this task document.
- - uv run ruff check src/taco/apps/cli/options.py src/taco/apps/cli/parser.py src/taco/apps/cli/main.py src/taco/core/usecases/build/actions.py tests/test_cli_main.py tests/test_tools.py : pass\n- uv run pytest -q tests/test_cli_main.py tests/test_tools.py : pass\n- uv run python scripts/validate_docs.py : pass\n- uv run pytest -q : pass
- Targeted lint/tests, docs validation, and full pytest all passed.
