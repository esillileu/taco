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

- [Documentation Guide](../doc/index.md) - operational document rules

## Files

- [01-principles.md](./01-principles.md)
- [02-branches.md](./02-branches.md)
- [03-commits.md](./03-commits.md)
- [04-pull-requests-and-merges.md](./04-pull-requests-and-merges.md)
- [05-ci-and-branch-protection.md](./05-ci-and-branch-protection.md)
- [06-issues-and-agent-decisions.md](./06-issues-and-agent-decisions.md)
- [07-change-size-and-forbidden.md](./07-change-size-and-forbidden.md)
- [08-versioning-and-workflow.md](./08-versioning-and-workflow.md)

## Action Map

- start a new task -> [06-issues-and-agent-decisions.md](./06-issues-and-agent-decisions.md), [02-branches.md](./02-branches.md)
- create commits -> [03-commits.md](./03-commits.md)
- open or merge a PR -> [04-pull-requests-and-merges.md](./04-pull-requests-and-merges.md), [05-ci-and-branch-protection.md](./05-ci-and-branch-protection.md)
- check safety guardrails -> [01-principles.md](./01-principles.md), [07-change-size-and-forbidden.md](./07-change-size-and-forbidden.md)
- check release flow -> [08-versioning-and-workflow.md](./08-versioning-and-workflow.md)

## When to Reference

- Starting work: read `06` then `02`.
- Preparing commits: read `03`.
- Opening or merging PRs: read `04` and `05`.
- Unsure about guardrails: read `01` and `07`.
