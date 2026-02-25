# Branch Rules

> Branch model, naming rules, and branch creation policy.

## References

- [Git Rules Index](../git.md) - related git guidance
- [Commit Rules](./03-commits.md) - next step after branching
- [Issues and Agent Decisions](./06-issues-and-agent-decisions.md) - start requirements

## Branch Model

- `main`: production-ready branch
- `dev`: integration branch
- `working`: task execution branches
- default flow: `working -> dev -> main`
- hotfix flow: `hotfix -> main -> dev`

## Allowed Branch Types

- `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ops`, `hotfix`

## Naming

- format: `<type>/<issue-number>-<slug>`
- use lowercase kebab-case slug
- always include issue number

## Creation Base

- start `hotfix` from `main`
- start all other types from `dev`
