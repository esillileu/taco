---
id: PLAN-MAIN
type: plan
title: Execution Plan
status: active
phase: phase-feature-precision
focus: Close feature gaps while enforcing plan/build mode separation and deterministic
  closeout
active_intents:
- I-001
- I-020
- I-030
- I-031
- I-032
- I-033
- I-034
- I-035
- I-036
active_tasks: []
blocked_tasks:
- T-026
next_tasks: []
milestones:
- M1-front-matter-migration
- M2-architecture-alignment
- M3-feature-precision
- M4-cli-ergonomics
- M5-mode-transition-contract
links:
- ARCH-INDEX
- PROJ-INTENT-INDEX
- PROJ-OVERVIEW
- FLOW-MODE-TRANSITION
---

# Plan

## Scope

- This document manages task queue and execution state only.
- Project design definitions are managed in architecture documents.
- Intent rationale and design direction are managed in intent documents.

## Task Queue Policy

- `active_tasks`: tasks currently executing in build mode.
- `blocked_tasks`: tasks paused with explicit blocking reason.
- `next_tasks`: ordered backlog candidates for activation.
- One task is activated at a time unless an explicit parallel execution decision is recorded.

## Intent Queue Policy

- `active_intents` tracks intents currently in plan-mode refinement.
- Intent activation does not imply immediate build execution.
- Task generation and queue updates are recorded as plan state transitions, not design content.

## Mode Handoff Policy

- Plan mode updates queue state and handoff readiness.
- Build mode executes one active task and records implementation/verification outputs.
- If build reveals boundary ambiguity, dependency spillover, or missing verification criteria, the task is blocked and returned to plan queue management.

## Refactor Intake Policy

- Refactor intents require explicit readiness evidence before build activation.
- Design-change review outcomes are tracked as task state decisions in this plan.
- Detailed boundary/contract/flow definitions remain in architecture docs.

## Operational Loop (Task Management)

1. Select active intent and choose executable task candidates.
2. Move one task into `active_tasks` when readiness requirements are satisfied.
3. Execute in build mode and record results or block reason.
4. On completion or block, update `active_tasks`, `blocked_tasks`, and `next_tasks`.
5. Keep `active_intents` synchronized with current planning focus.

## Exit Criteria (Management)

- Queue state is consistent (`active/blocked/next`).
- Every blocked task has explicit reason and follow-up path.
- Every completed task has recorded implementation and verification outcomes.
- Build handoff decisions are traceable from this plan to task records.

## Active Tasks


## Active Intents

- [I-001](./intents/I-001-intent-plan-mode.md)
- [I-020](./intents/I-020-intent-blueprint-handoff.md)
- [I-030](./intents/I-030-intent-codex-mcp-server.md)
- [I-031](./intents/I-031-intent-codex-mcp-hardening.md)

## Next Tasks
