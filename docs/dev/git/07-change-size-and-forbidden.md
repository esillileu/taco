# Change Size and Forbidden Actions

> Recommended PR size and forbidden behaviors.

## References

- [Git Rules Index](../git.md) - entry point for git conventions
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
