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

## Implementation Layout

- `src/taco/apps/cli/mapper.py` is the stable facade for CLI-to-tool mapping.
- `src/taco/apps/cli/map/` provides responsibility-based mapping modules:
  - `dispatch.py`: top-level domain routing
  - `task.py`: task command mapping
  - `plan.py`: plan/intent command mapping
  - `doc.py`: doc command mapping
  - `build.py`: build precheck/postcheck payload mapping
  - `common.py`: shared option coercion/validation helpers
- No runtime `exec`-based part loading is used.
