---
id: T-005
type: task
title: T-005-mcp-tools
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

# Task: T-005-mcp-tools

> Define the MCP tool surface and CLI mapping contract before implementation.

## References

- [Overview](../overview.md)
- [Architecture Index](../architecture/index.md)
- [Plan](../plan.md)
- [Glossary](../architecture/schemas/glossary.md)

## Intent
<!-- taco:pack=task.core -->

- Fix one canonical tool naming model so Python-first and Rust-final implementations share the same contract.

## Goal
<!-- taco:pack=task.core -->

- Publish a decision-complete MCP/CLI interface specification for task-centric document orchestration.

## Scope
<!-- taco:pack=task.core,pack.next_actions -->

- Standardize naming to singular domain + concise action.
- Define MCP tool list and 1:1 CLI command mapping.
- Define request/response contract shape and shared error format.
- Define compatibility policy for pre-release rename stability.
- Exclude runtime implementation details and transport internals.

## Implementation Approach
<!-- taco:pack=task.plans,pack.next_actions -->

- Adopt canonical MCP tools:
  - `task.list`
  - `task.pack`
  - `task.targets`
  - `task.record`
  - `doc.snippet`
  - `issue.triage`
  - `convention.get`
- Adopt canonical CLI pattern: `taco <domain> <action> [options]`.
- Keep MCP and CLI in strict 1:1 mapping to minimize documentation and onboarding cost.
- Define common response envelope for all tools:
  - success: `{ "ok": true, "data": <payload> }`
  - failure: `{ "ok": false, "error": { "code": "<string>", "message": "<string>", "details": <object|null> } }`
- Define deterministic behavior requirements:
  - `task.pack` returns stable output for identical repository state and inputs.
  - `task.targets` returns stable write locations from identical repository state and task id.
- Pre-release compatibility policy:
  - No legacy alias is required.
  - Renames are allowed only before first external release tag.

## Verification Approach
<!-- taco:pack=task.plans,pack.acceptance_checks,pack.verification_commands -->

- Validate that SSOT docs and AGENTS instructions use canonical names consistently.
- Validate that examples in README follow the canonical CLI shape.
- Validate that no deprecated names remain (`tasks.*`, `docs.*`, `issues.*`, `conventions.*`).
- Add implementation-phase acceptance tests later:
  - MCP route resolution tests for each tool
  - CLI to MCP mapping parity tests
  - Schema validation tests for success and error envelopes

## Implementation Result

- Added tool-surface orchestration module at `src/taco/tools.py`.
- Implemented canonical MCP tool handlers:
  - `task.list`
  - `task.pack`
  - `task.targets`
  - `task.record`
  - `doc.snippet`
  - `issue.triage`
  - `convention.get`
- Implemented unified response envelope:
  - success: `{ "ok": true, "data": ... }`
  - failure: `{ "ok": false, "error": { "code", "message", "details" } }`
- Implemented repo-state loader:
  - `load_repo_state(root, config_path)` using `taco.yaml`
  - integrates `index`, `budget`, and `router` configs
- Implemented tool dispatcher:
  - `call_tool(state, name, args)` with consistent error mapping
- Implemented `task.record` dry-run and apply behavior:
  - dry-run preview output
  - append behavior under routed heading for non-dry-run mode
- Kept handler logic aligned with canonical naming and CLI parity assumptions.

## Verification Result

- Added tool-level behavior tests in `tests/test_tools.py` covering:
  - unknown tool error envelope
  - `task.list`/`task.pack`/`task.targets`
  - `doc.snippet`
  - `issue.triage`
  - `convention.get`
  - `task.record` dry-run
  - `load_repo_state` with config loading
- Verification commands:
  - `uv run --extra dev ruff check .` -> pass
  - `uv run --extra dev mypy .` -> pass
  - `uv run --extra dev pytest -q` -> pass
  - `uv run --extra dev python scripts/validate_docs.py` -> pass
