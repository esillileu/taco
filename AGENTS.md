# AGENTS

## Loader-first behavior

- Always call `uv run taco task pack --task-id <TASK_ID>` before coding.
- Use `uv run taco task targets --task-id <TASK_ID> --route-type <ROUTE_TYPE>` before writing completion notes.
- Do not read large docs directly when a snippet is sufficient; call `uv run taco doc snippet --path <PATH> --anchor-id <ANCHOR_ID>`.

## Recording behavior

- Prefer dry-run record flow first.
- Record implementation and verification outcomes in task documents.
- Before branch/commit/merge actions in build work, call `uv run taco convention get --topic git` and use `uv run taco doc snippet ...` as needed for rule details.

## Task branch workflow

- Execute one task per branch derived from `dev`.
- Use branch names that include task id when available (for example `feat/t-003-pack-budget`).
- Do not mix multiple task scopes in a single branch.
