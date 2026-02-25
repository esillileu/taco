---
id: MOD-CLI-MAPPER
type: module
title: CLI Mapper
status: active
role: Map CLI domain/action options into canonical tool calls
boundary: Input option validation and payload shaping only
depends_on: []
provides: [SCH-TOOL-ENVELOPE]
consumes: []
must_not:
  - Must not load repository state
invariants:
  - Mapping parity between CLI and MCP tool surface
related_flows: [FLOW-TOOL-DISPATCH]
links: [MOD-MAIN, SCH-TOOL-ENVELOPE]
---

# CLI Mapper Module

Normalizes CLI commands into canonical MCP tool calls.
