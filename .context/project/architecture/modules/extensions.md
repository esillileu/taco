---
id: MOD-EXTENSIONS
type: module
title: Extensions Layer
status: active
role: Optional tool/template extension surface
boundary: Orchestrates use cases without changing core policy
depends_on: [MOD-PORTS, MOD-PACK, MOD-ROUTER]
provides: [SCH-TOOL-ENVELOPE, SCH-TOOL-ERROR]
consumes: [SCH-INDEX-GRAPH]
must_not:
  - Must not force core changes for extension additions
invariants:
  - Extensions can be removed without breaking core libraries
related_flows: [FLOW-TOOL-DISPATCH]
links: [MOD-TOOLS-DISPATCH, MOD-PORTS]
---

# Extensions Module

## Implementation Layout

- `src/taco/resources/templates/`: externalized templates used by bootstrap usecases.
- `src/taco/extensions/` remains optional; plugin paths are reserved and not required for core CLI/MCP operation.
