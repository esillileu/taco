---
id: T-023
type: task
title: T-023-i-031-codex-e2e-validation
status: done
plan_ref: PLAN-MAIN
scope:
  in:
  - tests/test_integration_mcp_cli.py
  - README.md
  - .context/project/entrypoint-build.md
  out:
  - src/taco/core/*
references:
  modules:
  - MOD-APPS
  - MOD-ADAPTERS
  flows:
  - FLOW-TOOL-DISPATCH
  - FLOW-MODE-TRANSITION
  schemas:
  - SCH-TOOL-ENVELOPE
links:
- PLAN-MAIN
- I-031
- MOD-APPS
- MOD-ADAPTERS
- FLOW-TOOL-DISPATCH
- FLOW-MODE-TRANSITION
- SCH-TOOL-ENVELOPE
---

# Task: T-023-i-031-codex-e2e-validation

## Intent

- Validate Codex-facing MCP interactions end to end and ensure operator-facing instructions are executable.

## Goal

- Provide deterministic tests and runbook-level commands proving Codex-compatible MCP connectivity and tool invocation.

## Scope

- Add end-to-end validation scenarios that mirror Codex MCP request flow.
- Document executable setup and verification commands for MCP runtime usage.
- Keep validation focused on runtime boundary and tool invocation contracts.

## Implementation Approach

1. Add tests that perform representative initialize/tools/list/tools/call sequences with strict response assertions.
2. Add documentation snippets for starting MCP runtime and smoke-checking calls.
3. Cross-check documented commands against actual runtime behavior.

## Verification Approach

- Run `uv run pytest -q tests/test_integration_mcp_cli.py`.
- Run `uv run python scripts/validate_docs.py`.
- Run `uv run pytest -q` after documentation and tests are updated.

## Implementation Result

- Pending end-to-end validation and docs updates.

- - Added Codex-style MCP end-to-end integration test covering initialize, notifications/initialized, tools/list, tools/call, shutdown, and exit with strict response id assertions.\n- Updated README MCP runtime section with lifecycle method coverage and executable smoke-check command sequence.\n- Updated build entrypoint guide to show pack JSON extraction and MCP smoke validation steps.
- Codex E2E validation strengthened with lifecycle-inclusive integration test and executable MCP smoke/runbook docs in README and build entrypoint.
## Verification Result

- Pending verification results.
- - ..........                                                               [100%] pass\n- DOC VALIDATION OK pass\n- ........................................................................ [ 82%]
...............                                                          [100%] pass
- pytest(integration), docs validation, and full pytest passed.
