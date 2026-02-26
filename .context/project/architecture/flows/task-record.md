---
id: FLOW-TASK-RECORD
type: flow
title: Task Record Flow
status: active
purpose: Resolve write target and append task outcome records
path:
  - tools-dispatch
  - router
touches_modules:
  - MOD-TOOLS-DISPATCH
  - MOD-ROUTER
inputs:
  - SCH-TASK-NODE
  - SCH-WRITE-TARGET
outputs:
  - SCH-TOOL-ENVELOPE
state_owner: MOD-TOOLS-DISPATCH
branches:
  - dry-run preview branch
  - apply write branch
constraints:
  - write only under configured target heading
intent_refs: [I-001]
links: [MOD-TOOLS-DISPATCH, MOD-ROUTER, SCH-WRITE-TARGET, SCH-TOOL-ENVELOPE]
---

# Task Record Flow

Flow for target resolution and task result recording behavior.
