---
id: GOV-GIT-07-CHANGE-SIZE-AND-FORBIDDEN
type: governance
title: Git 07-change-size-and-forbidden
status: active
domain: git
scope: repo
must: []
must_not: []
links: []
---

# Change Size and Forbidden Actions

> Recommended PR size and forbidden behaviors.

## References

- [Git Rules Index](./index.md) - entry point for git conventions
- [CI and Branch Protection](./05-ci-and-branch-protection.md) - shared branch safety
- [Versioning and Workflow](./08-versioning-and-workflow.md) - full workflow baseline

## Change Size

- target PR size under ~300 LOC
- keep single-purpose PRs
- split large work into multiple PRs

## Forbidden

- bypassing PR process
- merging without review
- rewriting shared history
- combining unrelated changes
- committing secrets
- ignoring CI failures
