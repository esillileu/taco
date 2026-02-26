---
id: T-022
type: task
title: T-022-i-031-intent-codex-mcp-hardening
status: done
plan_ref: PLAN-MAIN
scope:
  in:
  - src/taco/apps/mcp/main.py
  - src/taco/adapters/mcp/transport.py
  - tests/test_integration_mcp_cli.py
  out:
  - src/taco/core/usecases/*
  - src/taco/core/task/*
references:
  modules:
  - MOD-ADAPTERS
  - MOD-APPS
  flows:
  - FLOW-TOOL-DISPATCH
  - FLOW-MODE-TRANSITION
  schemas:
  - SCH-TOOL-ENVELOPE
  - SCH-TOOL-ERROR
links:
- PLAN-MAIN
- I-031
- MOD-ADAPTERS
- MOD-APPS
- FLOW-TOOL-DISPATCH
- FLOW-MODE-TRANSITION
- SCH-TOOL-ENVELOPE
- SCH-TOOL-ERROR
---

# Task: T-022-i-031-intent-codex-mcp-hardening

## Intent

- Tighten MCP protocol compatibility and lifecycle handling for Codex-facing runtime behavior.

## Goal

- Make MCP request parsing, response encoding, and lifecycle methods deterministic and spec-aligned for expected Codex calls.

## Scope

- Harden JSON-RPC request validation and error mapping behavior.
- Confirm initialize/ping/tools/list/tools/call/shutdown/exit flow consistency.
- Keep tool execution path anchored to canonical `call_tool`.

## Implementation Approach

1. Refine MCP transport parsing/serialization edge cases and error envelopes for malformed payloads.
2. Refine MCP runtime lifecycle method handling and response shape consistency.
3. Extend integration tests for lifecycle and protocol error cases.

## Verification Approach

- Run `uv run pytest -q tests/test_integration_mcp_cli.py`.
- Run `uv run ruff check src/taco/apps/mcp/main.py src/taco/adapters/mcp/transport.py tests/test_integration_mcp_cli.py`.
- Run `uv run pytest -q` for regression safety.

## Implementation Result

- Pending implementation updates for MCP protocol hardening.

- - Hardened MCP request handling: notifications (including notifications/initialized) now return no response; invalid id types are rejected with -32600; non-object decoded payloads map to invalid request.\n- Transport encoding now uses stable key ordering and compact separators for deterministic wire output.\n- Added lifecycle/validation integration tests for notification behavior and invalid request/id handling.
- MCP request/lifecycle hardening applied in main+transport with notification/no-response behavior and invalid request/id validation; integration tests expanded.
## Verification Result

- Pending verification results.
- - .........                                                                [100%] pass\n- All checks passed! pass\n- ........................................................................ [ 83%]
..............                                                           [100%] pass
- pytest(mcp integration), ruff(target files), pytest(full) all passed.
