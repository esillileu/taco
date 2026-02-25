---
id: GOV-GIT-03-COMMITS
type: governance
title: Git 03-commits
status: active
domain: git
scope: repo
must: []
must_not: []
links: []
---

# Commit Rules

> Commit message format and granularity policy.

## References

- [Git Rules Index](../git.md) - entry point for git conventions
- [Branch Rules](./02-branches.md) - branch prerequisites
- [PR and Merge Rules](./04-pull-requests-and-merges.md) - next step after commit

## Commit Message

- format: `<type>: <summary>`
- english, lowercase, single line, no trailing period
- allowed types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ops`

## Granularity

- one logical change per commit
- split commits when purpose/module/responsibility differs
- keep one commit when all edits belong to one logical unit
