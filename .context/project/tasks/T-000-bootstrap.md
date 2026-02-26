---
id: T-000
type: task
title: T-000-bootstrap
status: done
plan_ref: PLAN-MAIN
priority: p1
estimate: m
scope:
  in: []
  out: []
references:
  modules: [MOD-PACK, MOD-INDEXER]
  flows: [FLOW-TASK-PACK]
  schemas: [SCH-PACK-RESULT]
  governance: [GOV-CODE-PRINCIPLES, GOV-GIT-INDEX]
deliverables: []
verification: []
links: []
---

# Task: T-000-bootstrap

> Align documentation purpose, structure, and operational flow for implementation readiness.

## References

- [Overview](../overview.md)
- [Architecture Index](../architecture/index.md)
- [Plan](../plan.md)
- [Glossary](../architecture/schemas/glossary.md)
- [Documentation Guide](../docs.md)

## Intent
<!-- taco:pack=task.core -->

- Make documentation alone sufficient to track project intent, scope, and readiness status.

## Goal
<!-- taco:pack=task.core -->

- Stabilize the SSOT + operational documentation model before implementation starts.

## Scope
<!-- taco:pack=task.core,pack.next_actions -->

- Enforce the boundary: `.context/project/` for SSOT, `.context/project/dev/` for agent operations.
- Ensure functional-definition ownership is explicit across SSOT and task docs.
- Ensure downstream task documents are detailed enough for implementation kickoff.

## Implementation Approach
<!-- taco:pack=task.plans,pack.next_actions -->

- Reflect legacy design intent (MCP-first, deterministic extraction, task-centric routing) into SSOT docs.
- Maintain concise operational guidance in `.context/governance/doc/index.md`, `.context/governance/git/index.md`, and `.context/project/plan.md`.
- Keep required task headings consistent with `taco.yaml` and validation logic.

## Verification Approach
<!-- taco:pack=task.plans,pack.acceptance_checks,pack.verification_commands -->

- Confirm links resolve across `.context/project/` and `.context/project/dev/`.
- Confirm todo tracking points to `.context/project/tasks/*`.
- Confirm task heading contract is validated by `scripts/validate_docs.py`.

## Implementation Result

- Established SSOT + operational documentation boundary:
  - SSOT: `.context/project/overview.md`, `.context/project/architecture/index.md`, `.context/project/plan.md`, `.context/project/architecture/schemas/glossary.md`
  - Operational: `.context/governance/*`
- Added detailed operational docs:
  - documentation guide, principles, todo board, git convention index and detailed files
- Added task contract-aligned files for `T-001`..`T-007` and completed them with implementation/verification outcomes.
- Aligned canonical tool naming and CLI mapping across active docs:
  - `task.*`, `doc.*`, `issue.*`, `convention.*`
  - `taco <domain> <action>` shape.
- Added config and validation scaffolding:
  - `taco.yaml`
  - `scripts/validate_docs.py`
  - readiness/document existence tests.

## Verification Result

- Confirmed cross-document link and structure consistency through:
  - `python scripts/validate_docs.py` during initial setup
  - `uv run --extra dev python scripts/validate_docs.py` after uv standardization
- Confirmed todo/task tracking points to `.context/project/tasks/*` and headings comply with `taco.yaml` contract.
- Confirmed readiness guard tests and full test suite pass in current state.
