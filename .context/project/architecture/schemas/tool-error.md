---
id: SCH-TOOL-ERROR
type: schema
title: Tool Error Envelope
status: active
purpose: Standard error envelope for all tool calls
used_by_modules:
  - MOD-MAIN
  - MOD-TOOLS-DISPATCH
used_in_flows:
  - FLOW-TOOL-DISPATCH
  - FLOW-TASK-RECORD
shape:
  ok: boolean
  error: { code: string, message: string, details: object }
rules:
  - ok must be false when error exists
compatibility:
  - stable keys across runtimes
links: [MOD-MAIN, MOD-TOOLS-DISPATCH]
---

# Tool Error Schema

Shared error response contract.

## Standard Planning Gate Codes

- `refactor_plan_missing`: returned when refactor-planning gate requires `## Refactor Plan` evidence and it is missing or non-actionable.
- `task_scope_policy_violation`: returned when generated task scope violates implementation-only constraint for gated workflows.
