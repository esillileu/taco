# TACO

TACO (Task Context Orchestrator) is a local MCP server that builds deterministic task-level context packs from repository documentation.

## Tool Surface and CLI

- Naming standard: singular domain + concise action
- MCP and CLI use a 1:1 mapping

| MCP Tool | CLI Command |
| --- | --- |
| `task.list` | `taco task list` |
| `task.pack` | `taco task pack --id T-003 --budget 1800` |
| `task.targets` | `taco task targets --id T-003 --mode done` |
| `task.record` | `taco task record --id T-003 --type implementation --from result.md` |
| `doc.snippet` | `taco doc snippet --path docs/architecture.md --anchor "핵심 모듈"` |
| `issue.triage` | `taco issue triage --id 123` |
| `convention.get` | `taco convention get git` |

## Delivery Strategy

- Near term: ship Python implementation first for rapid iteration.
- Long term: replace runtime with a pure Rust binary.
- Constraint: keep MCP/CLI contracts stable across both runtimes.
- Dogfooding: use `taco` on this repository as soon as each tool becomes available.

## Documentation Structure

### SSOT (Human-facing)

- `docs/intent.md`
- `docs/architecture.md`
- `docs/plan.md`
- `docs/glossary.md`

### Operational (Agent-facing)

- `docs/dev/docs.md`
- `docs/dev/git.md`
- `docs/dev/todo.md`
- `docs/dev/principles.md`
- `docs/dev/tasks/`
- `docs/dev/git/`

## Current Project Phase

The repository is in a pre-implementation design phase.
Current work is focused on documentation structure alignment and scope tracking.
