# AGENTS

## Loader-first behavior

- Always call `task.pack` before coding.
- Use `task.targets` before writing completion notes.
- Do not read large docs directly when a snippet is sufficient; call `doc.snippet`.

## Recording behavior

- Prefer dry-run record flow first.
- Record implementation and verification outcomes in task documents.

## Task branch workflow

- Execute one task per branch derived from `dev`.
- Use branch names that include task id when available (for example `feat/123-t-003-pack-budget`).
- Do not mix multiple task scopes in a single branch.
