---
id: MOD-ADAPTERS
type: module
title: Adapters Layer
status: active
role: Infrastructure implementation for runtime, CLI, filesystem, and git
boundary: Converts external I/O and environment concerns for core use
depends_on: [MOD-PORTS]
provides: [SCH-INDEX-GRAPH, SCH-TOOL-ENVELOPE]
consumes: []
must_not:
  - Must not contain core policy decisions
invariants:
  - Adapter behavior is replaceable behind ports
related_flows: [FLOW-TOOL-DISPATCH, FLOW-TASK-PACK]
links: [MOD-PORTS, MOD-TOOLS-DISPATCH]
---

# Adapters Module

## Implementation Layout

- `src/taco/adapters/mcp/`: MCP transport adapter.
- `src/taco/adapters/fs/repo_state.py`: repo/config/index load adapter.
- `src/taco/adapters/fs/storage.py`: `StoragePort` implementation.
- `src/taco/adapters/git/repository.py`: `RepositoryPort` implementation.
