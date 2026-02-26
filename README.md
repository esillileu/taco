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
| `task.complete` | `taco task complete --task-id T-003 --implementation "done" --verification "passed"` |
| `task.block` | `taco task block --task-id T-003 --reason-code scope_split_required --reason "needs split"` |
| `plan.pack` | `taco plan pack --task-id T-003 --budget-tokens 1800` |
| `plan.intent.list` | `taco plan intent list` |
| `plan.intent.view` | `taco plan intent view --intent-id I-001` |
| `plan.intent.index` | `taco plan intent index --intent-id I-001 --budget-tokens 1800` |
| `doc.snippet` | `taco doc snippet --path .context/project/architecture/index.md --anchor-id architecture-index` |
| `issue.triage` | `taco issue triage --title "fix broken parser"` |
| `convention.get` | `taco convention get --topic git` |
| `plan.view` | `taco plan view` |
| `plan.locate` | `taco plan locate --change-type task --target T-014` |
| `plan.validate` | `taco plan validate` |

## Mode-Aware Pack Policy

- Use `plan.intent.index` for intent-first plan-mode context indexing.
- Use `plan.pack` when planning from a specific task id directly.
- Build mode continues to use `task.pack`.
- Default required refs by mode intent:
  - plan mode: `ARCH-INDEX`, `PLAN-MAIN`, `GOV-DOC-INDEX`
  - build mode: `GOV-CODE-PRINCIPLES`
- Config compatibility policy:
  - prefer `pack.required_refs_by_tool` for mode-aware defaults
  - fallback to legacy `pack.common_required_refs` for backward compatibility
- Build git rule policy:
  - do not always include git conventions in build packs
  - before branch/commit/merge actions, call `convention.get --topic git`
  - optionally call `doc.snippet` for specific git rule anchors

## Delivery Strategy

- Near term: ship Python implementation first for rapid iteration.
- Long term: replace runtime with a pure Rust binary.
- Constraint: keep MCP/CLI contracts stable across both runtimes.
- Dogfooding: use `taco` on this repository as soon as each tool becomes available.

## Python Tooling

- Use `uv` as the standard Python package and command manager.
- Run project checks via `make` (which delegates to `uv`) or directly with `uv run --extra dev ...`.

## Documentation Structure

### Canonical Root

- `.context/project/overview.md`
- `.context/project/intents/index.md`
- `.context/project/intents/`
- `.context/project/plan.md`
- `.context/project/architecture/index.md`
- `.context/project/architecture/modules/`
- `.context/project/architecture/flows/`
- `.context/project/architecture/schemas/`
- `.context/project/tasks/`
- `.context/governance/code-principles.md`
- `.context/governance/git/`
- `.context/governance/doc/`

## Current Project Phase

The repository is in a pre-implementation design phase.
Current work is focused on documentation structure alignment and scope tracking.
