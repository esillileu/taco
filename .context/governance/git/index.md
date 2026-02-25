---
id: GOV-GIT-INDEX
type: governance
title: Git Conventions
status: active
domain: git
scope: repo
must: []
must_not: []
links: []
---

# Git Rules Index

> Quick index of git convention files for agent task execution.

## References

- [Documentation Guide](./docs.md) - operational document rules
- [Todo](./todo.md) - active task tracking

## Files

- [01-principles.md](./git/01-principles.md)
- [02-branches.md](./git/02-branches.md)
- [03-commits.md](./git/03-commits.md)
- [04-pull-requests-and-merges.md](./git/04-pull-requests-and-merges.md)
- [05-ci-and-branch-protection.md](./git/05-ci-and-branch-protection.md)
- [06-issues-and-agent-decisions.md](./git/06-issues-and-agent-decisions.md)
- [07-change-size-and-forbidden.md](./git/07-change-size-and-forbidden.md)
- [08-versioning-and-workflow.md](./git/08-versioning-and-workflow.md)

## Action Map

- start a new task -> [06-issues-and-agent-decisions.md](./git/06-issues-and-agent-decisions.md), [02-branches.md](./git/02-branches.md)
- create commits -> [03-commits.md](./git/03-commits.md)
- open or merge a PR -> [04-pull-requests-and-merges.md](./git/04-pull-requests-and-merges.md), [05-ci-and-branch-protection.md](./git/05-ci-and-branch-protection.md)
- check safety guardrails -> [01-principles.md](./git/01-principles.md), [07-change-size-and-forbidden.md](./git/07-change-size-and-forbidden.md)
- check release flow -> [08-versioning-and-workflow.md](./git/08-versioning-and-workflow.md)

## When to Reference

- Starting work: read `06` then `02`.
- Preparing commits: read `03`.
- Opening or merging PRs: read `04` and `05`.
- Unsure about guardrails: read `01` and `07`.
