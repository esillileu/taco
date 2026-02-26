---
id: FLOW-TASK-PACK
type: flow
title: Task Pack Assembly Flow
status: active
purpose: Build a minimal, deterministic context bundle for one task
path:
  - parser
  - indexer
  - pack
touches_modules:
  - MOD-PARSER
  - MOD-INDEXER
  - MOD-PACK
inputs:
  - SCH-TASK-NODE
outputs:
  - SCH-PACK-RESULT
state_owner: MOD-PACK
branches:
  - fail when required references are unresolved
constraints:
  - include only task-scoped context and required governance
intent_refs: [I-001]
links: [MOD-PARSER, MOD-INDEXER, MOD-PACK, SCH-PACK-RESULT]
---

# Task Pack Flow

## Purpose

Prepare agent-ready context from one task node without loading unrelated global content.

## Steps

1. Parse and index `.context` docs.
2. Resolve task node by id.
3. Collect required references from task front matter and common policy.
4. Resolve reference nodes/slices and merge task execution sections.
5. Apply budget and deterministic ordering.
6. Return pack payload.

## Branches

- If required references are unresolved, stop with `pack_not_ready`.
- If optional context exceeds budget, drop with explicit reason.
