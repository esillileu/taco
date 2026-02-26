---
id: GOV-GIT-08-VERSIONING-AND-WORKFLOW
type: governance
title: Git 08-versioning-and-workflow
status: active
domain: git
scope: repo
must: []
must_not: []
links: []
---

# Versioning and Workflow

> Optional versioning policy and minimal end-to-end git workflow.

## References

- [Git Rules Index](./index.md) - entry point for git conventions
- [PR and Merge Rules](./04-pull-requests-and-merges.md) - integration rules
- [Issues and Agent Decisions](./06-issues-and-agent-decisions.md) - start rules

## Optional Versioning

- use `vX.Y.Z` tags when release tagging is enabled
- release boundary is `dev -> main`

## Minimal Workflow

- `Issue -> Branch -> Commit -> PR -> CI -> Review -> Merge -> Sync`
