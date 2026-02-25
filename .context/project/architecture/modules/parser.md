---
id: MOD-PARSER
type: module
title: Parser
status: active
role: Parse markdown headings and metadata markers
boundary: Converts markdown text into deterministic section slices
depends_on: []
provides: [SCH-SECTION-SLICE]
consumes: []
must_not:
  - Must not access filesystem directly
invariants:
  - Deterministic parsing for identical input
decomposable: false
children: []
related_flows: [FLOW-TASK-PACK]
links: [FLOW-TASK-PACK, SCH-SECTION-SLICE]
---

# Parser Module

## Role

Parses markdown into reusable section slices and extracts front matter metadata.

## Boundary

- Input: document path and markdown text.
- Output: section slices with heading/anchor line boundaries.
- No filesystem access. No runtime policy decision.

## Contracts

- Provides `SCH-SECTION-SLICE` to indexer.
- Keeps parsing deterministic for repeatable pack output.

## Must Not

- Must not infer task priority or context relevance.
- Must not mutate source text.
