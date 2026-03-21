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
- I-030
- I-031
- I-032
- I-033
- I-034
- I-035
- I-036
- I-037
- I-038
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
  - `plan.intent.template` to load intent format and decomposition rules
  - `plan.intent.create_many` to create decomposed intents authored by the agent
  - `plan.intent.list` to discover active intents
  - `plan.intent.view` to inspect intent metadata and linked tasks
  - `plan.intent.index` to load plan-scoped index from intent linkage
  - `plan.intent.propose` to normalize planning proposal from an existing intent id
  - `plan.intent.autodesign` to derive design/document updates
  - `plan.intent.generate_tasks` to emit executable tasks
  - `plan.intent.review_bundle` to gate proposal/design/task consistency
  - `plan.intent.apply` to apply with explicit approval and fingerprint gate
- Output: executable task nodes with explicit references, scope boundaries, and verification criteria.
- Plan automation output is blueprint-level metadata; section body authoring is agent-owned.
- Legacy `plan.intent.propose(intent_text=...)` path remains for backward compatibility and is deprecated.
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

## Refactor Planning Gate Lane

- Trigger: intent metadata marks refactor-planning gate policy.
- Plan-mode precondition:
  - require `## Refactor Plan` section with actionable steps before gated review/apply checks can pass quality gate.
  - fail with deterministic reason (`refactor_plan_missing`) when section is absent or empty.
- Task generation rule:
  - generated task scope must describe executable code-change work only.
  - design-level updates stay in intent/architecture/plan docs and are not emitted as task goals.
- Runtime status:
  - planning automation uses `plan.intent.propose -> autodesign -> generate_tasks -> review_bundle -> apply`.
  - `plan.intent.apply` requires explicit approval and matching decision fingerprint.
  - `plan.intent.apply` updates metadata/queue only; it does not author task body content.
  - `plan.intent.review_bundle` fails when generated task blueprints are not yet authored or fail `task.pack` readiness checks.

## Operational Effect

- Writers operate in plan mode with view/locator/validator support.
- Builders operate in build mode with task bundle only.
- Mode separation prevents uncontrolled document drift during coding execution.
- design-sync: FLOW-MODE-TRANSITION intent_refs includes I-038 for test-suite srp refactor phase2 closeout.
