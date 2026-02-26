---
id: MOD-TOOLS-DISPATCH
type: module
title: Tool Dispatcher
status: active
role: Load repo state and dispatch canonical tool handlers
boundary: Orchestrates parser/indexer/pack/router usage
depends_on: [MOD-PARSER, MOD-INDEXER, MOD-PACK, MOD-ROUTER]
provides: [SCH-TOOL-ENVELOPE, SCH-TOOL-ERROR]
consumes: [SCH-INDEX-GRAPH]
must_not:
  - Must not implement CLI argument parsing
invariants:
  - Unknown tools return deterministic error envelope
related_flows: [FLOW-TOOL-DISPATCH, FLOW-TASK-PACK, FLOW-TASK-RECORD]
links: [MOD-PARSER, MOD-INDEXER, MOD-PACK, MOD-ROUTER, SCH-TOOL-ERROR]
---

# Tools Dispatch Module

Central runtime orchestrator for supported tool handlers, including plan-intent handlers
(`plan.intent.list`, `plan.intent.view`, `plan.intent.index`, `plan.intent.propose`,
`plan.intent.autodesign`, `plan.intent.generate_tasks`, `plan.intent.review_bundle`,
`plan.intent.apply`, `plan.intent.validate`).

## Planning Gate Responsibilities

- Enforce refactor-planning gate checks before review/apply passes.
- Return deterministic tool error codes for missing plan evidence and invalid generated task scope.
- Keep generation output as blueprint metadata only (no task body text generation).

## Implementation Layout

- `src/taco/core/usecases/dispatcher.py` is the dispatch facade.
- Implementation is grouped in `src/taco/core/usecases/` by responsibility:
  - `task/` for task/record/complete/block handlers
  - `plan/` for plan/intent read, automation, review, and apply handlers
  - `doc/` for doc section handlers
  - `build/` for precheck/postcheck, diagnostics, convention, and issue helpers
  - `bootstrap/` for init scaffolding
- State loading is handled by `src/taco/adapters/fs/repo_state.py`.
- Shared decision/helper contracts are in `src/taco/core/plan/`:
  - `config_policy.py`
  - `text_ops.py`
  - `markdown_ops.py`
  - `plan_policy.py`
  - `types.py`
- Port usage:
  - `StoragePort` is injected into `RepoState` and used by task write paths.
  - `RepositoryPort` is injected into `RepoState` and used by build postcheck fallback.
- Build submodule split:
  - `build/precheck.py`: pack contract preflight checks
  - `build/postcheck.py`: changed-path/output/check result validation
  - `build/diagnostics.py`: standardized drift detail payloads
  - `build/misc.py`: convention/issue helper tools
