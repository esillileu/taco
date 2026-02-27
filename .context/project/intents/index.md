---
id: PROJ-INTENT-INDEX
type: anchor
title: Intent Index
status: active
links: [PLAN-MAIN, ARCH-INDEX, I-001, I-020, I-030, I-031, I-032, I-033, I-034, I-035, I-036, I-037, I-038]
---

# Intent Index

## Scope

- This index is a registry of design intents only.
- Task queue ordering and execution state are managed by `PLAN-MAIN`.
- Architecture boundary and contract details are managed by `ARCH-INDEX`.

## Active Intents

- [I-001](./I-001-intent-plan-mode.md): intent-first planning mode and tool flow.
- [I-020](./I-020-intent-blueprint-handoff.md): blueprint-only intent-to-task handoff validation.
- [I-030](./I-030-intent-codex-mcp-server.md): codex-compatible MCP server planning and task handoff.
- [I-031](./I-031-intent-codex-mcp-hardening.md): MCP hardening for Codex end-to-end compatibility and operations.
- [I-032](./I-032-intent-build-workflow-ux-hardening.md): build workflow UX hardening for pack/precheck/postcheck/record loops.
- [I-033](./I-033-intent-modular-srp-refactor-over-200-lines.md): modular SRP refactor plan for files over 200 lines.
- [I-034](./I-034-intent-srp-refactor-staged-followups.md): staged follow-up refactor execution for remaining oversized modules.
- [I-035](./I-035-intent-task-pack-srp-split.md): SRP decomposition for task pack orchestration/readiness modules.
- [I-036](./I-036-intent-test-suite-modularization-phase1.md): staged modularization for oversized integration tests and fixture reuse.
- [I-037](./I-037-intent-srp-refactor-over-200-lines-phase2.md): follow-up structural modularization lane for remaining oversized files.
- [I-038](./I-038-intent-test-suite-srp-refactor-over-200-lines-phase2.md): follow-up test-suite structural modularization for oversized test files.
