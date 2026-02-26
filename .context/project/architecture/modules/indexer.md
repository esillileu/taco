---
id: MOD-INDEXER
type: module
title: Indexer
status: active
role: Build graph index over context documents
boundary: Produces lookup tables for tasks, headings, links, and references
depends_on: [MOD-PARSER]
provides: [SCH-INDEX-GRAPH]
consumes: [SCH-SECTION-SLICE]
must_not:
  - Must not depend on transport layer
invariants:
  - Duplicate ids are rejected
decomposable: false
children: []
related_flows: [FLOW-TASK-PACK]
links: [MOD-PARSER, FLOW-TASK-PACK, SCH-INDEX-GRAPH]
---

# Indexer Module

## Role

Builds a deterministic context graph from `.context` documents.

## Boundary

- Input: parsed documents and config paths.
- Output: `node_index`, `task_index`, `heading_lookup`, `reference_lookup`.
- Enforces uniqueness for front matter ids and reference ids.

## Contracts

- Provides `SCH-INDEX-GRAPH` for pack/router/tool layers.
- Supports both node-level and heading-level lookup.

## Must Not

- Must not apply budget policy.
- Must not write repository files.

## Implementation Layout

- `src/taco/core/indexing/` owns indexing logic.
- No runtime `exec`-based part loading is used.
