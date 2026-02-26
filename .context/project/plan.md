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
active_tasks:
- T-011
blocked_tasks: []
next_tasks:
- T-016
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

## Planning Boundary

- This plan is an execution map for priority and sequencing.
- Design definitions stay in architecture documents.
- Task body content is not duplicated in plan.

## Phase 0: Readiness Baseline (Current)

- Lock `.context` as canonical knowledge root.
- Enforce front matter and id/reference validation as hard failure.
- Keep task execution deterministic and traceable to referenced nodes.
- Keep legacy docs removed to avoid dual-SSOT drift.

## Phase 1: Scope and Interface Definition
<!-- taco:ref=PLAN-PHASE1-001 -->

- Define tool input/output contracts from front matter-driven model.
- Keep MCP and CLI naming parity (`taco <domain> <action>`).
- Stabilize DTO/error contract for Python-first and Rust-final migration.
- Define reference policy as `id-only` and heading-slice extraction.
- Define module/flow/schema ownership boundaries from source mapping.

## Phase 2: Approach and Verification Design
<!-- taco:ref=PLAN-PHASE2-001 -->

- Standardize task metadata (`plan_ref`, `scope`, `references`, `verification`).
- Standardize architecture node metadata (`module/flow/schema/anchor`).
- Define deterministic pack ordering and budget/drop behavior.
- Define validation gates for duplicate id, invalid type, unresolved references.
- Define regression matrix for task pack, task record, and doc snippet behavior.

## Phase 3: Architecture and Contract Alignment

- Reflect all runtime modules in architecture index and leaf docs.
- Reflect transport and error contracts as explicit schemas.
- Ensure architecture docs remain ahead of implementation scope.

## Phase 4: Feature Precision and Completeness

- Remove missing workflow gaps across task tools and closeout flows.
- Promote front matter references to primary selection mechanism.
- Add deterministic behavior checks for each tool path.
- Keep one-call pack readiness and end-to-end task completion viability.

## Phase 5: Mode Separation and Transition Safety

- Keep plan mode and build mode responsibilities explicitly separated.
- Require explicit transition checks before entering build mode.
- Require build-to-plan fallback on boundary/scope/verification ambiguity.
- Keep mode transition policy consistent with architecture flow docs.
- Split pack defaults by mode intent:
  - `plan.pack` defaults: `ARCH-INDEX`, `PLAN-MAIN`, `GOV-DOC-INDEX`
  - `task.pack` defaults: `GOV-CODE-PRINCIPLES`
- Keep config migration backward compatible:
  - prefer `pack.required_refs_by_tool`
  - fallback to legacy `pack.common_required_refs`
- Keep build git rules on-demand by behavior (`convention.get` -> optional `doc.snippet`).
- Add intent-first planning surface:
  - `plan.intent.list`
  - `plan.intent.view`
  - `plan.intent.index`
  - intent links to executable tasks via `task_refs`.

### Phase 5 Task Breakdown

- `T-012`: Plan->Build readiness gate enforcement
- `T-013`: Build->Plan fallback state and blocked sync
- `T-014`: Planner tool surface (view/locator/validator)

## Phase 6: CLI Ergonomics and Human Workflow

- Add human-readable context output mode for CLI.
- Keep machine envelope as default.
- Ensure parity between CLI behavior and MCP contract.

### Phase 6 Task Breakdown

- `T-015`: Init/bootstrap command for context scaffolding
- `T-016`: Human-readable CLI context output mode

## Phase 7: Rust Migration Readiness

- Freeze DTO/error envelope contracts at tool boundary.
- Ensure core logic remains language-portable and side-effect bounded.
- Build behavior-first parity tests to support Python-to-Rust transition.

## Operational Loop

1. Select active intent from plan and inspect with `plan.intent.view`.
2. Call `plan.intent.index` to gather planning index tied to executable tasks.
3. Refine architecture/plan/task docs in plan mode.
4. Switch to build mode and call `task.pack` for the selected task.
5. Implement and verify against task verification criteria.
6. Call `task.targets` / `task.record` (or `task.complete`) to record outcomes.
7. Update plan status, active/next tasks, and intent linkage.

## Exit Criteria

- All active tasks have deterministic pack output.
- No unresolved references in `.context`.
- Architecture index fully covers runtime module map.
- Pack/record/snippet flows pass integration and regression checks.

## Active Tasks

- [T-011](./tasks/T-011-feature-precision.md)

## Active Intents

- [I-001](./intents/I-001-intent-plan-mode.md)

## Next Tasks

- [T-016](./tasks/T-016-cli-human-context-view.md)
