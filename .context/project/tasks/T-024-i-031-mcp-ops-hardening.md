---
id: T-024
type: task
title: T-024-i-031-mcp-ops-hardening
status: done
plan_ref: PLAN-MAIN
scope:
  in:
  - src/taco/apps/mcp/main.py
  - README.md
  - .context/governance/code-principles.md
  out:
  - src/taco/core/*
references:
  modules:
  - MOD-APPS
  - MOD-ADAPTERS
  flows:
  - FLOW-MODE-TRANSITION
  - FLOW-TOOL-DISPATCH
  schemas:
  - SCH-TOOL-ERROR
links:
- PLAN-MAIN
- I-031
- MOD-APPS
- MOD-ADAPTERS
- FLOW-MODE-TRANSITION
- FLOW-TOOL-DISPATCH
- SCH-TOOL-ERROR
---

# Task: T-024-i-031-mcp-ops-hardening

## Intent

- Improve operational robustness for MCP runtime execution, failure visibility, and controlled shutdown semantics.

## Goal

- Reduce runtime ambiguity during failures by tightening runtime guards, predictable shutdown behavior, and operator guidance.

## Scope

- Define and enforce runtime error handling boundaries in MCP loop.
- Improve runtime control behavior for stop and shutdown paths.
- Document operating conventions needed for reliable local use.

## Implementation Approach

1. Add explicit runtime error handling branches for invalid inputs and unsupported methods.
2. Ensure shutdown and exit handling remains deterministic under repeated or unexpected sequences.
3. Document operator notes for runtime lifecycle and troubleshooting.

## Verification Approach

- Run `uv run pytest -q tests/test_integration_mcp_cli.py`.
- Run `uv run ruff check src/taco/apps/mcp/main.py`.
- Run `uv run pytest -q` and confirm no regression.

## Implementation Result

- Pending operations hardening updates.

- - Added MCP runtime session guards for initialize/shutdown lifecycle: tools/list and tools/call now require initialize, shutdown state blocks non-exit requests with a stable error.\n- Added defensive runtime error boundary in MCP main loop to return JSON-RPC internal error envelope on unexpected exceptions.\n- Documented MCP lifecycle operation notes in README and governance runtime-operation principles.
- MCP ops hardening implemented: lifecycle-state guards, deterministic shutdown behavior, and runtime error boundary; operator guidance updated.
## Verification Result

- Pending verification results.
- - ..........                                                               [100%] pass\n- All checks passed! pass\n- ........................................................................ [ 82%]
...............                                                          [100%] pass
- pytest(integration), ruff(main), pytest(full) all passed.
