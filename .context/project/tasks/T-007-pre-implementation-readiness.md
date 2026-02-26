---
id: T-007
type: task
title: T-007-pre-implementation-readiness
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

# Task: T-007-pre-implementation-readiness

> Final readiness gate before implementation kickoff and dogfooding start.

## References

- [Overview](../overview.md)
- [Architecture Index](../architecture/index.md)
- [Plan](../plan.md)
- [Glossary](../architecture/schemas/glossary.md)

## Intent
<!-- taco:pack=task.core -->

- Verify that design, task plans, and operating principles are decision-complete and internally consistent.

## Goal
<!-- taco:pack=task.core -->

- Approve implementation kickoff with explicit Python-first and Rust-porting constraints.

## Scope
<!-- taco:pack=task.core,pack.next_actions -->

- Validate consistency across SSOT and `.context/governance/*`.
- Validate canonical tool naming and CLI mapping consistency.
- Validate design principles presence:
  - DTO fixed contracts
  - I/O separation
  - pure core functions
  - standardized errors
  - config-driven rules
  - simplified data types
  - separated cache/concurrency policy
  - behavior-based testing
- Validate dogfooding policy and migration gate criteria.

## Implementation Approach
<!-- taco:pack=task.plans,pack.next_actions -->

- Run documentation conformance checks (`scripts/validate_docs.py`).
- Run targeted content checks for stale names and outdated assumptions.
- Build a readiness checklist based on this task and mark status per criterion.
- Keep any unresolved decisions explicitly listed as blockers.

## Verification Approach
<!-- taco:pack=task.plans,pack.acceptance_checks,pack.verification_commands -->

- Acceptance criteria:
  - no stale tool names remain in active docs
  - no unresolved draft markers remain in active phase task plans (`T-001` to `T-007`)
  - architecture and principles reflect Python-first/Rust-final strategy
  - dogfooding policy is explicitly documented
- Verification evidence should include command outputs and referenced file lines.

## Implementation Result

- Added readiness-gate test suite at `tests/test_preimplementation_readiness.py`.
- Encoded acceptance criteria as executable checks:
  - stale legacy tool names are absent in active docs
  - active task plans (`T-001`..`T-007`) have no unresolved draft markers
  - architecture/principles include Python-first and Rust-final strategy
  - dogfooding policy is explicitly documented
- Readiness checks now run alongside existing lint/type/test/doc validation workflow.

## Verification Result

- Verification commands:
  - `uv run --extra dev ruff check .` -> pass
  - `uv run --extra dev mypy .` -> pass
  - `uv run --extra dev pytest -q` -> pass
  - `uv run --extra dev python scripts/validate_docs.py` -> pass
- Readiness gate tests passed as part of the same test run.
