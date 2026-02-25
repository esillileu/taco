---
id: SCH-SECTION-SLICE
type: schema
title: Section Slice
status: active
purpose: Parsed markdown section boundaries
used_by_modules:
  - MOD-PARSER
  - MOD-INDEXER
used_in_flows:
  - FLOW-TASK-PACK
shape:
  heading: string
  anchor_id: string
  start_line: integer
  end_line: integer
rules: []
compatibility: []
links: [MOD-PARSER, MOD-INDEXER]
---

# Section Slice

## Purpose

Represents one heading-bounded slice in a markdown document.

## Fields

- `heading`: visible heading text.
- `anchor_id`: normalized anchor key.
- `start_line` / `end_line`: inclusive source boundaries.
