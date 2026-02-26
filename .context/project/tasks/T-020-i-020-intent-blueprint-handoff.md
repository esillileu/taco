---
id: T-020
type: task
title: T-020-i-020-intent-blueprint-handoff
status: active
plan_ref: PLAN-MAIN
scope:
  in: ["src/taco/core/usecases/plan/intent.py", "src/taco/core/task/pack.py", ".context/project/entrypoint-plan.md"]
  out: ["src/taco/adapters/mcp/*", "build mode execution semantics"]
references:
  modules: [MOD-TOOLS-DISPATCH, MOD-PACK]
  flows: [FLOW-MODE-TRANSITION, FLOW-TASK-PACK]
  schemas: [SCH-TASK-NODE, SCH-PACK-RESULT]
links: [PLAN-MAIN, I-020, MOD-TOOLS-DISPATCH, MOD-PACK, FLOW-MODE-TRANSITION, FLOW-TASK-PACK, SCH-TASK-NODE, SCH-PACK-RESULT]
---

# Task: T-020-i-020-intent-blueprint-handoff

## Intent

- Complete a full intent-to-task handoff where TACO controls metadata and the agent authors executable task content.

## Goal

- Ensure generated task blueprint is converted into a pack-ready task document without relying on template-written body text.

## Scope

- Validate plan intent chain outputs for I-020.
- Author task sections required by pack readiness.
- Confirm pack entry can load task context for T-020.

## Implementation Approach

1. Use `plan.intent.propose/autodesign/generate_tasks/review_bundle/apply` for I-020 and record returned fingerprints.
2. Author `T-020` task markdown with required front matter and section content from blueprint requirements.
3. Run `task.pack` to confirm task is now discoverable and ready for build-mode handoff.

## Verification Approach

- Run `uv run taco plan validate` to confirm plan and intent references remain valid after apply.
- Run `uv run taco task pack --task-id T-020` and verify `ok: true` with `task_id: T-020`.
- Run `uv run taco task pack` and verify auto-selection can use active task `T-020`.

## Implementation Result

- Added agent-authored task content for T-020 based on TACO blueprint output.
- Kept write scope inside plan/task context without additional architecture body generation.

## Verification Result

- Pending verification command execution for final handoff.
