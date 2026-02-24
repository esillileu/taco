# ADR-000 Documentation Foundations

## Metadata

- **ADR ID:** ADR-000
- **Status:** Accepted
- **Date:** 2026-02-24
- **Decision Makers:** Repository maintainers

## Context

The project had no structured documentation system, making onboarding and validation inconsistent.

## Decision

Adopt a documentation system with:
- `docs/doc-map.md` as SSOT,
- required heading schemas for task and ADR docs,
- baseline top-level docs, and
- strict path and link conventions.

## Alternatives Considered

- **Unstructured markdown:** Rejected due to drift and discoverability issues.
- **External wiki:** Rejected to keep context in-repo and versioned.

## Consequences

- Better consistency and easier automation.
- Minor upfront overhead for contributors to follow templates.

## Links

- Task: [T-000-bootstrap](../tasks/T-000-bootstrap.md)
- Architecture: [docs/architecture.md](../architecture.md)
- Principles: [docs/principles.md](../principles.md)
- SSOT: [docs/doc-map.md](../doc-map.md)
