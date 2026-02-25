---
id: T-010
type: task
title: T-010-task-closeout-automation
status: done
plan_ref: PLAN-MAIN
priority: p0
estimate: m
scope:
  in:
  - src/taco/tools.py
  - src/taco/router.py
  - src/taco/pack.py
  - .context/project/plan.md
  out:
  - large CLI redesign
  - non-task workflow automation
references:
  modules:
  - MOD-TOOLS-DISPATCH
  - MOD-ROUTER
  - MOD-PACK
  flows:
  - FLOW-TASK-RECORD
  - FLOW-TASK-PACK
  schemas:
  - SCH-TOOL-ENVELOPE
  - SCH-WRITE-TARGET
  - SCH-TASK-NODE
  governance:
  - GOV-CODE-PRINCIPLES
  - GOV-GIT-INDEX
deliverables: []
verification: []
links:
- PLAN-MAIN
---

# Task: T-010-task-closeout-automation

## Intent

- Automate post-implementation closeout so agents can finish tasks without manual plan/status bookkeeping.

## Goal

- Add one-command closeout flow that records results, marks task done, and advances plan active/next pointers.

## Scope

- add closeout automation entrypoint in tool layer
- keep existing `task.record` behavior intact
- update task front matter `status` from `active` to `done` automatically
- update plan front matter `active_tasks`/`next_tasks` automatically for completed task
- include dry-run preview mode before apply

## Context Requirements

- required: ARCH-INDEX, PLAN-MAIN

## Implementation Approach

- introduce a new tool operation (e.g. `task.complete`) with:
  - task id
  - implementation summary
  - verification summary
  - dry-run/apply mode
- internally sequence:
  1. resolve write targets
  2. append implementation/verification records
  3. patch task front matter status
  4. patch plan front matter queues
- keep atomicity semantics explicit:
  - if any step fails, return error and do not partially apply in `apply` mode
- add deterministic update rules for plan queue transitions:
  - remove completed task from `active_tasks`
  - promote first eligible entry from `next_tasks` to `active_tasks`

## Verification Approach

- dry-run closeout returns full preview and target summary
- apply closeout updates all expected sections and front matter fields
- repeated closeout on already done task returns stable error code
- run:
  - `uv run --extra dev ruff check .`
  - `uv run --extra dev mypy .`
  - `uv run --extra dev pytest -q`
  - `uv run --extra dev python scripts/validate_docs.py`

## Implementation Result

- Pending (do not fill until the task is completed)

- closeout automation implemented
## Verification Result

- Pending (do not fill until the task is completed)
- automated checks passed
