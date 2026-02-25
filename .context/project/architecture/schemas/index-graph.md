---
id: SCH-INDEX-GRAPH
type: schema
title: Index Graph
status: active
purpose: Indexed document graph for orchestration
used_by_modules:
  - MOD-INDEXER
  - MOD-PACK
  - MOD-ROUTER
used_in_flows:
  - FLOW-TASK-PACK
shape:
  documents: array
  task_index: map
  node_index: map
rules: []
compatibility: []
links: [MOD-INDEXER, MOD-PACK, MOD-ROUTER]
---

# Index Graph

## Purpose

Primary lookup structure for task, node, heading, and reference resolution.

## Core Maps

- `task_index`: task id -> document path.
- `node_index`: front matter id -> document path.
- `heading_lookup`: `path#anchor` -> heading metadata.
- `reference_lookup`: reference id -> `path#anchor`.
