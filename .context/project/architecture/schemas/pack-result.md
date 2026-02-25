---
id: SCH-PACK-RESULT
type: schema
title: Pack Result Schema
status: active
purpose: Define the response contract of task.pack
used_by_modules:
  - MOD-PACK
used_in_flows:
  - FLOW-TASK-PACK
shape:
  pack_version: string
  task_id: string
  context_snippets: array
rules:
  - task_id must match requested task
compatibility:
  - evolve via pack_version
links: [MOD-PACK, FLOW-TASK-PACK]
---

# Pack Result Schema

## Purpose

Stable contract returned by `task.pack` for agent execution.

## Required Fields

- `task_id`, `pack_version`, `budget_tokens`, `used_tokens`
- `context_snippets`, `write_targets`
- `coverage`, `dropped`

## Compatibility

Contract evolution is versioned by `pack_version`.
