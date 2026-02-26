---
id: MOD-PACK
type: module
title: Pack Assembler
status: active
role: Build task execution context bundles
boundary: Selects required snippets by task and references
depends_on: [MOD-INDEXER]
provides: [SCH-PACK-RESULT]
consumes: [SCH-INDEX-GRAPH, SCH-TASK-NODE]
must_not:
  - Must not mutate source documents
invariants:
  - Deterministic output order
decomposable: false
children: []
related_flows: [FLOW-TASK-PACK]
links: [MOD-INDEXER, FLOW-TASK-PACK, SCH-PACK-RESULT]
---

# Pack Module

## Role

Assembles one-task execution context using required references and minimal governance rules.

## Boundary

- Input: task id, index graph, budget config.
- Output: `SCH-PACK-RESULT` payload.
- Selection unit: heading section slices.

## Contracts

- Required references: `required_refs_by_tool[tool] + task.references + task.plan_ref`.
- Compatibility fallback: when tool-specific refs are absent, runtime may fallback to legacy `common_required_refs`.
- Missing required context fails with `pack_not_ready`.
- Optional context can be dropped by budget with explicit reason.

## Must Not

- Must not rank snippets probabilistically.
- Must not include unrelated task documents.
