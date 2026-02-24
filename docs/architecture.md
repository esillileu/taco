# Architecture

## Context

Documentation is modeled as a lightweight information architecture with one SSOT and multiple specialized documents.

## Components

- `docs/doc-map.md` as schema and policy contract.
- Top-level thematic docs (intent, principles, plan, glossary, todo).
- Operational docs (`docs/tasks/*`) for execution details.
- Decision logs (`docs/adr/*`) for architecture records.

## Data Flows

1. Intent and principles inform plan and task creation.
2. Tasks reference ADRs for decision alignment.
3. ADRs feed back into architecture constraints and principles.

## Constraints

- Required headings must remain deterministic.
- File naming must support simple automated parsing.
