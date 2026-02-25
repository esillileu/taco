# Task: T-005-mcp-tools

> Define the MCP tool surface and CLI mapping contract before implementation.

## References

- [Intent](../../intent.md)
- [Architecture](../../architecture.md)
- [Plan](../../plan.md)
- [Glossary](../../glossary.md)

## Intent

- Fix one canonical tool naming model so Python-first and Rust-final implementations share the same contract.

## Goal

- Publish a decision-complete MCP/CLI interface specification for task-centric document orchestration.

## Scope

- Standardize naming to singular domain + concise action.
- Define MCP tool list and 1:1 CLI command mapping.
- Define request/response contract shape and shared error format.
- Define compatibility policy for pre-release rename stability.
- Exclude runtime implementation details and transport internals.

## Implementation Approach

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

- Validate that SSOT docs and AGENTS instructions use canonical names consistently.
- Validate that examples in README follow the canonical CLI shape.
- Validate that no deprecated names remain (`tasks.*`, `docs.*`, `issues.*`, `conventions.*`).
- Add implementation-phase acceptance tests later:
  - MCP route resolution tests for each tool
  - CLI to MCP mapping parity tests
  - Schema validation tests for success and error envelopes

## Implementation Result

- Pending (do not fill until the task is completed)

## Verification Result

- Pending (do not fill until the task is completed)
