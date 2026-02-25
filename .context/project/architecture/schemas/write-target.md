---
id: SCH-WRITE-TARGET
type: schema
title: Write Target Schema
status: active
purpose: Describe write location for task.record
used_by_modules:
  - MOD-ROUTER
used_in_flows: []
shape:
  path: string
  heading: string
  line_hint: integer
  mode: string
rules:
  - heading must exist exactly once in task document
compatibility:
  - stable keys required by CLI/MCP
links: [MOD-ROUTER]
---

# Write Target Schema

## Purpose

Specify deterministic destination for result recording.

## Fields

- `path`: task document path.
- `heading`: target section heading.
- `line_hint`: append hint near heading block.
- `mode`: append strategy.
