---
id: SCH-TOOL-ENVELOPE
type: schema
title: Tool Response Envelope
status: active
purpose: Standard success/error wrapper used by all tools
used_by_modules:
  - MOD-MAIN
  - MOD-TOOLS-DISPATCH
used_in_flows:
  - FLOW-TOOL-DISPATCH
shape:
  ok: boolean
  data: object
  error: object|null
rules:
  - success responses set ok=true and provide data
compatibility:
  - stable top-level keys required for CLI/MCP parity
links: [MOD-MAIN, MOD-TOOLS-DISPATCH]
---

# Tool Envelope Schema

Unified response wrapper for all tool handlers.
