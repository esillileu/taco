---
id: MOD-APPS
type: module
title: Apps Layer
status: active
role: Composition root and executable entrypoints
boundary: Wires adapters/core (and optional extension surface); no business decision logic
depends_on: [MOD-ADAPTERS, MOD-EXTENSIONS]
provides: [SCH-TOOL-ENVELOPE, SCH-TOOL-ERROR]
consumes: []
must_not:
  - Must not own domain validation or selection policy
invariants:
  - Entry layer remains thin and deterministic
related_flows: [FLOW-TOOL-DISPATCH]
links: [MOD-ADAPTERS, MOD-EXTENSIONS, MOD-MAIN]
---

# Apps Module

## Implementation Layout

- `src/taco/apps/main.py`: process entrypoint and composition root.
- `src/taco/apps/cli/`: app-facing CLI module surface.
- `src/taco/apps/mcp/main.py`: MCP entrypoint facade.
- `src/taco/apps/mcp/runtime.py`: stdio event loop and transport error boundaries.
- `src/taco/apps/mcp/handlers.py`: method dispatch and lifecycle/state handling.
- `src/taco/apps/mcp/protocol.py`: JSON-RPC request normalization helpers.
- `src/taco/apps/mcp/catalog.py`: tool registry metadata for `tools/list`.
