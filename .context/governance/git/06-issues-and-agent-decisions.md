---
id: GOV-GIT-06-ISSUES-AND-AGENT-DECISIONS
type: governance
title: Git 06-issues-and-agent-decisions
status: active
domain: git
scope: repo
must: []
must_not: []
links: []
---

# Issues and Agent Decisions

> Issue-first workflow and default agent decisions.

## References

- [Git Rules Index](../git.md) - entry point for git conventions
- [Branch Rules](./02-branches.md) - branch creation after issue
- [PR and Merge Rules](./04-pull-requests-and-merges.md) - integration path

## Issue Requirement

- every task starts from an issue
- issue title format: `[Type] Summary`
- allowed types: `Feat`, `Fix`, `Docs`, `Refactor`, `Test`, `Chore`, `Ops`

## Agent Defaults

- if no issue exists, request issue creation first
- if commit type is unclear, default to `chore`
- if CI fails, do not merge
