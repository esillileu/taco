# Task: T-006-integration-tests

> Define end-to-end and cross-runtime behavior tests for MCP and CLI.

## References

- [Intent](../../intent.md)
- [Architecture](../../architecture.md)
- [Plan](../../plan.md)
- [Glossary](../../glossary.md)

## Intent

- Lock external behavior so Python implementation can be safely ported to Rust.

## Goal

- Provide behavior-based acceptance tests for all canonical tools and CLI mappings.

## Scope

- Cover MCP tools:
  - `task.list`
  - `task.pack`
  - `task.targets`
  - `task.record`
  - `doc.snippet`
  - `issue.triage`
  - `convention.get`
- Cover CLI mapping parity (`taco <domain> <action>` -> MCP tool).
- Cover success and standardized error envelope behavior.
- Exclude micro-benchmarking and load tests from this task.

## Implementation Approach

- Build reusable fixture repositories and expected outputs (golden files).
- Write behavior assertions against public I/O only (no internal function coupling).
- Separate test layers:
  - contract tests (DTO schema)
  - e2e tests (CLI/MCP behavior)
  - parity tests (Python vs Rust same fixture, same expected output)
- Keep test data language-neutral (JSON/YAML fixtures) to reuse in Rust test harness.

## Verification Approach

- Required scenarios:
  - happy path for each tool
  - invalid input schema per tool
  - missing docs/task id/heading conditions
  - deterministic repeatability checks
- Add parity gate definition:
  - Rust migration cannot switch default runtime until golden parity is complete.
- Capture test execution instructions in task completion notes for repeatability.

## Implementation Result

- Pending (do not fill until the task is completed)

## Verification Result

- Pending (do not fill until the task is completed)
