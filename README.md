# TACO

TACO (Task Context Orchestrator) is a local MCP server that builds deterministic task-level context packs from repository documentation.

## Tool Surface and CLI

- Naming standard: singular domain + concise action
- MCP and CLI use a 1:1 mapping

| MCP Tool | CLI Command |
| --- | --- |
| `task.list` | `taco task list` |
| `task.pack` | `taco task pack --task-id T-003 --budget-tokens 1800` |
| `task.targets` | `taco task targets --task-id T-003 --route-type implementation_result` |
| `task.record` | `taco task record --task-id T-003 --route-type implementation_result --content "done"` |
| `doc.snippet` | `taco doc snippet --path docs/architecture.md --anchor-id system` |
| `issue.triage` | `taco issue triage --title "fix broken parser"` |
| `convention.get` | `taco convention get --topic git` |

## Delivery Strategy

- Near term: ship Python implementation first for rapid iteration.
- Long term: replace runtime with a pure Rust binary.
- Constraint: keep MCP/CLI contracts stable across both runtimes.
- Dogfooding: use `taco` on this repository as soon as each tool becomes available.

## Python Tooling

- Use `uv` as the standard Python package and command manager.
- Run project checks via `make` (which delegates to `uv`) or directly with `uv run --extra dev ...`.

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
