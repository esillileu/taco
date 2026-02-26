---
id: GOV-CODE-PRINCIPLES
type: governance
title: Code Principles
status: active
domain: doc
scope: repo
must: []
must_not: []
links: []
---

# Principles

> Execution constraints for consistent planning before implementation.

## References

- [Documentation Guide](./doc/index.md) - structure and writing rules
- [Intent Index](../project/intents/index.md) - planning objective baseline
- [Architecture Index](../project/architecture/index.md) - boundary baseline
- [Plan](../project/plan.md) - phase baseline

## Principles

- Use MCP-first workflow over direct document exploration when operating as an agent.
- Keep planning deterministic and traceable to SSOT documents.
- Keep each task focused on one scope unit.
- Record decisions, assumptions, and unresolved points in task scope/approach sections.
- Record implementation and verification outcomes only after task completion.
- Keep architecture/plan documents global and stable; do not reshape SSOT by task.
- Resolve task context through declared references, not broad whole-document loading.

## Design and Implementation Principles
<!-- taco:ref=PRINCIPLES-DESIGN-001 -->

- Python-first delivery, Rust-final architecture:
  - Deliver the first usable version in Python.
  - Keep contracts and behavior stable so the runtime can be replaced with a pure Rust binary later.
- Dogfooding by default:
  - Use `taco` itself to run planning and execution workflows in this repository as soon as each tool is available.
  - Prefer fixing gaps discovered during dogfooding over adding new scope.
- DTO and schema stability:
  - Define request/response DTOs once and keep them language-agnostic.
  - Validate DTO shape at boundaries only; internal logic receives typed DTO values.
- I/O separation:
  - Keep filesystem, process, and network access in adapter layers.
  - Keep domain logic independent from I/O implementation details.
- Pure core functions:
  - Core modules (`parser`, `indexer`, `pack`, `budget`, `router`) should be deterministic and side-effect free.
  - Pass required inputs explicitly; avoid hidden global state.
- Standardized error model:
  - Use one shared error structure: `code`, `message`, `details`.
  - Map internal errors to stable public error codes at tool boundaries.
- Rules in configuration:
  - Keep policy and selection rules (`headings`, `priority`, paths, budgets) in config (`taco.yaml`) instead of hardcoding.
  - Keep code generic; change behavior through config updates.
- Reference-addressable documentation:
  - Assign stable reference ids to retrievable sections in SSOT and operational docs.
  - Task docs must declare required references explicitly so pack assembly is deterministic.
- Simple data types:
  - Prefer plain records/lists/maps over deep inheritance or framework-specific types.
  - Avoid Python-only magic patterns that complicate Rust parity.
- Concurrency and cache policy separation:
  - Keep correctness logic independent from concurrency/caching.
  - Treat concurrency/caching as replaceable performance layers with explicit policy.
- Behavior-first testing:
  - Test observable behavior and contracts, not implementation internals.
  - Build shared fixture and golden-output tests to enforce Python/Rust parity.

## Runtime Operation Principles
<!-- taco:ref=PRINCIPLES-OPS-001 -->

- MCP lifecycle determinism:
  - Require `initialize` before tool listing/calls.
  - Treat `notifications/initialized` and `exit` as notification-only paths.
  - After `shutdown`, reject non-exit requests with a stable runtime error.
- Error boundary clarity:
  - Map parse/validation/runtime failures to stable JSON-RPC error envelopes.
  - Avoid silent failures; return explicit error code and message at runtime boundaries.
