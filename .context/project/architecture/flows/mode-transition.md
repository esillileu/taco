---
id: FLOW-MODE-TRANSITION
type: flow
title: Plan-Build Mode Transition Flow
status: active
purpose: Split planning/writing from execution/coding and define deterministic mode
  switches
path:
- plan-mode
- build-mode
touches_modules:
- MOD-TOOLS-DISPATCH
- MOD-PACK
inputs:
- SCH-TASK-NODE
outputs:
- SCH-PACK-RESULT
state_owner: MOD-TOOLS-DISPATCH
branches:
- plan_to_build_ready branch
- build_to_plan_blocked branch
constraints:
- build mode must execute one task at a time
- plan mode must produce executable task nodes before handoff
- refactor intents must run code analysis before architecture/task finalization
intent_refs:
- I-001
- I-020
links:
- PLAN-MAIN
- ARCH-INDEX
- FLOW-TASK-PACK
---

# Plan-Build Mode Transition Flow

## Purpose

Define how TACO separates document planning from task execution and when the runtime must switch mode.

## Plan Mode

- Goal: update design/plan/task documents safely when decisions or scope changes are required.
- Entry surface:
  - `plan.intent.list` to discover active intents
  - `plan.intent.view` to inspect intent metadata and linked tasks
  - `plan.intent.index` to load plan-scoped index from intent linkage
- Output: executable task nodes with explicit references, scope boundaries, and verification criteria.
- Required checks:
  - front matter integrity and reference validity
  - impact visibility for linked architecture nodes
  - no unresolved blockers for active task handoff

## Build Mode

- Goal: execute one selected task with a minimal context bundle.
- Input contract:
  - single task node
  - referenced architecture/governance slices only
- Output:
  - implementation and verification results
  - task status update or explicit blocked signal

## Transition Rules

### Plan -> Build

Switch to build mode only when the selected task has:

- clear goal and scope
- explicit references (`modules`, `flows`, `schemas`)
- explicit verification criteria
- no critical validation errors

### Build -> Plan

Switch back to plan mode when execution discovers:

- required architecture boundary/contract changes
- scope expansion that needs task split or new tasks
- missing or ambiguous verification criteria
- dependency impact outside declared references

## Refactor Lane

- Trigger: intent front matter includes `kind: refactor`.
- Plan-mode precondition:
  - run code analysis first (file size, responsibility mixing, dependency and boundary impact)
  - use analysis output to decide whether design change is `none`, `minor`, or `major`
  - only then finalize architecture updates and generated tasks
- Build-mode closeout:
  - if analysis/implementation changed ownership or dependency boundaries, update architecture/flow docs in the same task closeout cycle
  - do not mark refactor task complete when required design sync is missing

## Operational Effect

- Writers operate in plan mode with view/locator/validator support.
- Builders operate in build mode with task bundle only.
- Mode separation prevents uncontrolled document drift during coding execution.
