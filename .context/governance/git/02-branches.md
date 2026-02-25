---
id: GOV-GIT-02-BRANCHES
type: governance
title: Git 02-branches
status: active
domain: git
scope: repo
must: []
must_not: []
links: []
---

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

- format: `<type>/<slug>`
- use lowercase kebab-case slug
- include task id in slug when available (example: `feat/t-003-pack-budget`)
- issue number in branch name is optional

## Creation Base

- start `hotfix` from `main`
- start all other types from `dev`
