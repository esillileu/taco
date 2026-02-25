---
id: MOD-ROUTER
type: module
title: Write Target Router
status: active
role: Resolve where task results are written
boundary: Maps route types to headings in task documents
depends_on: [MOD-INDEXER]
provides: [SCH-WRITE-TARGET]
consumes: [SCH-INDEX-GRAPH]
must_not:
  - Must not write files directly
invariants:
  - Route resolution fails on ambiguity
decomposable: false
children: []
related_flows: [FLOW-TASK-PACK]
links: [MOD-INDEXER, SCH-WRITE-TARGET]
---

# Router Module

## Role

Computes deterministic write targets for `task.record` operations.

## Boundary

- Input: task id, route type, index graph.
- Output: one `SCH-WRITE-TARGET`.
- Uses heading identity in task documents.

## Contracts

- `implementation` / `implementation_result` -> `Implementation Result`.
- `verification` / `verification_result` / `issue_record` -> `Verification Result`.
- Ambiguous/missing target heading returns stable error codes.

## Must Not

- Must not modify markdown content.
- Must not depend on CLI/MCP transport details.
