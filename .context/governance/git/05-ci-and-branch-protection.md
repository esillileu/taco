---
id: GOV-GIT-05-CI-AND-BRANCH-PROTECTION
type: governance
title: Git 05-ci-and-branch-protection
status: active
domain: git
scope: repo
must: []
must_not: []
links: []
---

# CI and Branch Protection

> Required CI behavior and shared branch safety rules.

## References

- [Git Rules Index](../git.md) - entry point for git conventions
- [PR and Merge Rules](./04-pull-requests-and-merges.md) - merge policy
- [Change Size and Forbidden Actions](./07-change-size-and-forbidden.md) - guardrail set

## CI Gate

- do not merge when CI fails
- merge only after CI passes
- pipeline expectation: `local -> dev -> main`

## Shared Branch Protection

- no direct push to `main`
- no force-push to `dev`
- no rebase of shared `dev` history
- history rewrite allowed only on personal working branches
