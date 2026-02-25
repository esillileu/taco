---
id: SCH-TASK-NODE
type: schema
title: Task Node
status: active
purpose: Front matter contract for executable task documents
used_by_modules:
  - MOD-PACK
used_in_flows:
  - FLOW-TASK-PACK
shape:
  id: string
  references: object
rules:
  - references must contain id-only values
compatibility: []
links: [MOD-PACK]
---

# Task Node

## Purpose

Defines task metadata needed for deterministic context assembly.

## Required Metadata

- `id`, `type`, `title`, `status`
- `plan_ref`
- `scope.in`, `scope.out`
- `references.modules|flows|schemas|governance`
