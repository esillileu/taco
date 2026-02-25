# Documentation Guide

> Agent-facing operating guide for the implementation-readiness phase.

## References

- [Intent](../intent.md) - SSOT objective and flow
- [Architecture](../architecture.md) - SSOT boundaries and tool surface
- [Plan](../plan.md) - current phase and next steps
- [Glossary](../glossary.md) - shared terms

## Document Structure

- Human-facing SSOT lives in `docs/`.
- Agent-facing operational docs live in `docs/dev/`.

## SSOT in docs/

- `intent.md`: purpose, objective, success criteria, core flow
- `architecture.md`: system boundary, pipeline, modules, tool surface
- `plan.md`: phase progression from readiness to kickoff prep
- `glossary.md`: project terminology

## Operational Docs in docs/dev/

- `docs.md`: writing policy, structure, and navigation
- `git.md`: which git rule file to use for each action
- `todo.md`: task tracking board for `docs/dev/tasks/`
- `principles.md`: execution constraints for pre-implementation planning
- `tasks/`: one-task-per-file planning docs
- `git/`: detailed git conventions

## Functional Definition Location

- Scenario and command-level functional definition is tracked in:
- SSOT summary: `docs/architecture.md` (tool surface + pipeline)
- task-level planning: `docs/dev/tasks/` (scope and approach per work unit)
- workflow conventions: `docs/dev/git.md` + `docs/dev/git/*`

## Recommended Read Order

- Session start: `intent -> architecture -> plan -> docs/dev/docs.md -> docs/dev/todo.md`
- Before task editing: `docs/dev/principles.md -> target task file`
- Before git operations: `docs/dev/git.md -> relevant file in docs/dev/git/`

## Writing Rules

- Write all `docs/dev/*` content in English.
- Keep one explicit scope per task file.
- Keep repository state in pre-implementation planning mode unless explicitly moved forward.
- Keep `Implementation Result` and `Verification Result` pending until completion.
- Use canonical tool naming: singular domain + concise action (`task.pack`, `doc.snippet`).
- Keep CLI command shape aligned with MCP naming: `taco <domain> <action> [options]`.

## Task File Contract

Every file in `docs/dev/tasks/` must include:

- `Intent`
- `Goal`
- `Scope`
- `Implementation Approach`
- `Verification Approach`
- `Implementation Result`
- `Verification Result`
