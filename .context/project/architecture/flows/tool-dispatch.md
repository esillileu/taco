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
intent_refs: [I-001]
links: [MOD-MAIN, MOD-CLI-MAPPER, MOD-TOOLS-DISPATCH, SCH-TOOL-ENVELOPE]
---

# Tool Dispatch Flow

Main runtime flow from command input to tool envelope output.

## Runtime Module Note

- `apps/main.py` composes runtime entry and delegates CLI mapping.
- `apps/cli/main.py` executes CLI runtime and delegates to core dispatcher.
- `core/usecases/dispatcher.py` dispatches to domain tool handlers.
- Repo state loading is delegated to `adapters/fs/repo_state.py`.
- Runtime no longer uses `exec`-based part loaders.

## Planning Gate Branch

- For gated refactor-planning intents, dispatch path must validate refactor-plan evidence before review/apply reports success.
- Dispatch path must return stable error envelope codes when planning evidence or generated task scope policy checks fail.
