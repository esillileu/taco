---
id: I-030
type: intent
title: I-030-intent-codex-mcp-server
status: active
plan_ref: PLAN-MAIN
task_refs:
- T-021
links:
- PROJ-INTENT-INDEX
- PLAN-MAIN
- ARCH-INDEX
- T-021
---

# Intent: I-030-intent-codex-mcp-server

## Intent

- Define and execute a plan-mode workflow that produces authored, build-ready tasks for a Codex-compatible MCP server runtime.

## Design Boundary

- Reuse existing `core/usecases` tool contracts as the canonical execution surface.
- Implement MCP runtime concerns only in `apps/mcp` and `adapters/mcp`.
- Keep CLI and MCP parity on tool names, payload shape, and error envelope behavior.

## Expected Design Outcome

- Plan-mode flow produces authored tasks for MCP transport and runtime loop implementation.
- Review/apply gates pass only when authored tasks satisfy `task.pack` readiness.
- Build mode can start immediately with pack-ready MCP tasks and no additional planning assumptions.
