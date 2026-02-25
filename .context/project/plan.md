---
id: PLAN-MAIN
type: plan
title: Execution Plan
status: active
phase: phase-feature-precision
focus: Close feature gaps while enforcing plan/build mode separation and deterministic closeout
active_tasks:
- T-011
blocked_tasks: []
next_tasks:
- T-012
- T-013
- T-014
- T-015
milestones:
- M1-front-matter-migration
- M2-architecture-alignment
- M3-feature-precision
- M4-cli-ergonomics
- M5-mode-transition-contract
links:
- ARCH-INDEX
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

### Phase 5 Task Breakdown

- `T-012`: Plan->Build readiness gate enforcement
- `T-013`: Build->Plan fallback state and blocked sync
- `T-014`: Planner tool surface (view/locator/validator)

## Phase 6: CLI Ergonomics and Human Workflow

- Add human-readable context output mode for CLI.
- Keep machine envelope as default.
- Ensure parity between CLI behavior and MCP contract.

## Phase 7: Rust Migration Readiness

- Freeze DTO/error envelope contracts at tool boundary.
- Ensure core logic remains language-portable and side-effect bounded.
- Build behavior-first parity tests to support Python-to-Rust transition.

## Operational Loop

1. Select active task from plan.
2. Validate plan->build readiness for selected task.
3. Call `task.pack`.
4. Implement and verify against task verification criteria.
5. Call `task.targets` / `task.record` (or `task.complete`) to record outcomes.
6. If boundary or scope changes are required, switch back to plan mode.
7. Update plan status and next tasks.

## Exit Criteria

- All active tasks have deterministic pack output.
- No unresolved references in `.context`.
- Architecture index fully covers runtime module map.
- Pack/record/snippet flows pass integration and regression checks.

## Active Tasks

- [T-011](./tasks/T-011-feature-precision.md)

## Next Tasks

- [T-012](./tasks/T-012-plan-build-readiness-gate.md)
- [T-013](./tasks/T-013-build-plan-fallback-state.md)
- [T-014](./tasks/T-014-planner-view-locator-validator.md)
- [T-015](./tasks/T-015-cli-human-context-view.md)
- [T-000](./tasks/T-000-bootstrap.md)
- [T-001](./tasks/T-001-parser-foundation.md)
- [T-002](./tasks/T-002-indexer-foundation.md)
- [T-003](./tasks/T-003-pack-budget.md)
- [T-004](./tasks/T-004-write-target-router.md)
- [T-005](./tasks/T-005-mcp-tools.md)
- [T-006](./tasks/T-006-integration-tests.md)
- [T-007](./tasks/T-007-pre-implementation-readiness.md)
- [T-008](./tasks/T-008-cli-entrypoint.md)
