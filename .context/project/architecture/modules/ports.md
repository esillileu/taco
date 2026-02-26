---
id: MOD-PORTS
type: module
title: Ports Layer
status: active
role: Core-facing interfaces for external dependencies
boundary: Defines abstractions only; no concrete implementation
depends_on: []
provides: [SCH-TOOL-ENVELOPE]
consumes: []
must_not:
  - Must not import adapters
invariants:
  - Ports are stable contracts used by core/adapters/extensions
related_flows: [FLOW-TOOL-DISPATCH]
links: [MOD-ADAPTERS, MOD-TOOLS-DISPATCH]
---

# Ports Module

## Interfaces

- `src/taco/ports/storage.py`: storage port contract.
- `src/taco/ports/repository.py`: repository port contract.
