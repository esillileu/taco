# Taco Documentation System

This repository uses a documentation-first workflow with a single source of truth for structure and validation rules.

## Documentation Index

- [Document Map (SSOT)](docs/doc-map.md)
- [Intent](docs/intent.md)
- [Architecture](docs/architecture.md)
- [Principles](docs/principles.md)
- [Plan](docs/plan.md)
- [Glossary](docs/glossary.md)
- [Todo](docs/todo.md)
- [Tasks Directory](docs/tasks/)
- [ADR Directory](docs/adr/)

## How to add a new Task

1. Copy `docs/tasks/T-000-bootstrap.md` to a new file named `T-XXX-short-title.md`.
2. Keep the required headings exactly as listed in [`docs/doc-map.md`](docs/doc-map.md).
3. Set status, owner, and links to relevant plan items/ADRs.

## How to add a new ADR

1. Copy `docs/adr/ADR-000-foundations.md` to a new file named `ADR-XXX-short-title.md`.
2. Keep the required headings exactly as listed in [`docs/doc-map.md`](docs/doc-map.md).
3. Link impacted tasks and update architecture/principles references if needed.
