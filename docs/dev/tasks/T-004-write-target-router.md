# Task: T-004-write-target-router

> Define deterministic write target routing for task completion and issue records.

## References

- [Intent](../../intent.md)
- [Architecture](../../architecture.md)
- [Plan](../../plan.md)
- [Glossary](../../glossary.md)

## Intent

- Standardize where `task.record` writes across task lifecycle states.

## Goal

- Return precise file/section targets through `task.targets` without manual document lookup.

## Scope

- Route targets for:
  - implementation completion notes
  - verification results
  - issue/decision records
- Support configured task file contract headings.
- Exclude actual write execution semantics (handled by `task.record`).

## Implementation Approach

- Keep routing core pure:
  - input: task id + route type + index/task DTOs
  - output: target DTOs (`path`, `heading`, `line_hint`, `mode`)
- Resolve headings by parser/index data, not raw string scan in tool handler.
- Keep route policy configurable for future section naming evolution.
- Normalize not-found and ambiguous-target cases to standard error types.

## Verification Approach

- Add behavior tests for:
  - valid routing to `Implementation Result` and `Verification Result`
  - missing heading/malformed task contract detection
  - multiple matching headings disambiguation behavior
- Add golden tests for target DTO output stability.
- Add integration check with `task.record` contract expectations.

## Implementation Result

- Pending (do not fill until the task is completed)

## Verification Result

- Pending (do not fill until the task is completed)
