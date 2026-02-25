---
id: FLOW-TOOL-DISPATCH
type: flow
title: Tool Dispatch Flow
status: active
purpose: Execute one canonical tool call from CLI input
path:
  - main
  - cli-mapper
  - tools-dispatch
touches_modules:
  - MOD-MAIN
  - MOD-CLI-MAPPER
  - MOD-TOOLS-DISPATCH
inputs:
  - SCH-TASK-NODE
outputs:
  - SCH-TOOL-ENVELOPE
state_owner: MOD-TOOLS-DISPATCH
branches:
  - invalid option branch
  - unknown tool branch
constraints:
  - output envelope must be stable
links: [MOD-MAIN, MOD-CLI-MAPPER, MOD-TOOLS-DISPATCH, SCH-TOOL-ENVELOPE]
---

# Tool Dispatch Flow

Main runtime flow from command input to tool envelope output.
