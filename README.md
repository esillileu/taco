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
| `plan.intent.propose` | `taco plan intent propose --intent-id I-010 --intent-text "..." --title "..."` |
| `plan.intent.autodesign` | `taco plan intent autodesign --intent-id I-001` |
| `plan.intent.generate_tasks` | `taco plan intent generate-tasks --intent-id I-001` |
| `plan.intent.review_bundle` | `taco plan intent review-bundle --intent-id I-001 --retry-on-fail 1` |
| `plan.intent.apply` | `taco plan intent apply --intent-id I-001 --fingerprenroint <fp> --retry-on-fail 1 --apply` |
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

## MCP Runtime (STDIO)

- Start MCP runtime:
  - `uv run python -m taco.apps.mcp.main`
- Supported core methods:
  - `initialize`
  - `notifications/initialized` (notification, no response)
  - `ping`
  - `tools/list`
  - `tools/call`
  - `shutdown`
  - `exit` (notification, no response)
- Tool execution path reuses canonical dispatcher (`call_tool`) so CLI and MCP stay contract-compatible.
- Codex-style smoke check:

```bash
cat <<'JSON' | uv run python -m taco.apps.mcp.main
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}
{"jsonrpc":"2.0","method":"notifications/initialized","params":{}}
{"jsonrpc":"2.0","id":2,"method":"tools/list"}
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"task.list","arguments":{}}}
{"jsonrpc":"2.0","id":4,"method":"shutdown"}
{"jsonrpc":"2.0","method":"exit"}
JSON
```

### MCP Runtime Notes

- `tools/list` and `tools/call` require successful `initialize` first.
- After `shutdown`, requests other than `exit` are rejected with MCP error `-32000`.
- Use `notifications/initialized` and `exit` as notifications (no response expected).

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
