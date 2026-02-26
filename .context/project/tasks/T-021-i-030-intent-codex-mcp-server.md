---
id: T-021
type: task
title: T-021-i-030-intent-codex-mcp-server
status: done
plan_ref: PLAN-MAIN
scope:
  in:
  - src/taco/apps/mcp/main.py
  - src/taco/adapters/mcp/transport.py
  - src/taco/apps/composition.py
  - tests/test_integration_mcp_cli.py
  - README.md
  out:
  - src/taco/core/usecases/*
  - src/taco/core/task/*
references:
  modules:
  - MOD-ADAPTERS
  - MOD-APPS
  - MOD-TOOLS-DISPATCH
  flows:
  - FLOW-TOOL-DISPATCH
  - FLOW-MODE-TRANSITION
  schemas:
  - SCH-TOOL-ENVELOPE
  - SCH-TOOL-ERROR
links:
- PLAN-MAIN
- I-030
- MOD-ADAPTERS
- MOD-APPS
- MOD-TOOLS-DISPATCH
- FLOW-TOOL-DISPATCH
- FLOW-MODE-TRANSITION
- SCH-TOOL-ENVELOPE
- SCH-TOOL-ERROR
---

# Task: T-021-i-030-intent-codex-mcp-server

## Intent

- Build a Codex-compatible MCP runtime entry that reuses canonical TACO tool dispatch behavior.

## Goal

- Define and implement a concrete MCP server runtime path so Codex can call TACO tools through MCP without CLI mediation.

## Scope

- Implement MCP app runtime loop and transport encode/decode.
- Keep tool invocation path anchored to `call_tool`.
- Add integration checks that confirm MCP request handling and error mapping.

## Implementation Approach

1. Implement request parsing and response encoding in `adapters/mcp/transport.py` for canonical MCP method handling.
2. Implement runtime flow in `apps/mcp/main.py` that reads messages, dispatches tools, and writes deterministic envelopes.
3. Add tests that validate CLI/MCP parity and MCP error behavior while preserving existing tool contracts.

## Verification Approach

- Run `uv run pytest -q tests/test_integration_mcp_cli.py` and verify MCP-adjacent parity scenarios pass.
- Run `uv run pytest -q` and confirm no regressions in plan/task/build flows.
- Run `uv run ruff check .` and verify new MCP runtime modules satisfy lint rules.

## Implementation Result

- Implementation changes are tracked during build-mode execution.

- Implemented Codex-compatible MCP stdio runtime by replacing the MCP stubs with JSON-RPC request handling in apps/mcp and adapters/mcp, reusing call_tool for canonical tool execution parity, and documenting the runtime entry in README.
## Verification Result

- Verification outputs are recorded after build-mode checks complete.
- Verified via uv run ruff check .; uv run pytest -q tests/test_integration_mcp_cli.py; uv run pytest -q; uv run python scripts/validate_docs.py; uv run taco plan validate; uv run taco build postcheck with T-021 scope and outputs.
