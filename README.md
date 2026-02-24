# TACO

TACO (Task Context Orchestrator) is a local MCP server that builds deterministic task-level context packs from repository documentation.

## Documentation System

- `docs/doc-map.md`: documentation SSOT and parsing contract
- `docs/intent.md`: project intent and success criteria
- `docs/architecture.md`: architecture and module boundaries
- `docs/principles.md`: engineering principles and constraints
- `docs/plan.md`: phased roadmap
- `docs/setup.md`: local development environment setup
- `docs/pre-implementation-checklist.md`: implementation readiness gate
- `docs/glossary.md`: glossary SSOT
- `docs/todo.md`: task index and status
- `docs/tasks/`: task execution SSOT documents
- `docs/adr/`: architecture decision records
- `docs/git.md`: git workflow convention

## Adding a New Task

1. Copy the task template structure from `docs/tasks/T-000-bootstrap.md`.
2. Create a new file under `docs/tasks/T-<id>.md`.
3. Add a row in `docs/todo.md` linking to the task file.

## Adding a New ADR

1. Copy the ADR structure from `docs/adr/ADR-000-foundations.md`.
2. Create a new file under `docs/adr/ADR-<id>.md`.
3. Link related tasks in the ADR `Links` section.


## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
make validate-docs
```
