# PR and Merge Rules

> Rules for pull request targets and merge strategy.

## References

- [Git Rules Index](../git.md) - entry point for git conventions
- [CI and Branch Protection](./05-ci-and-branch-protection.md) - merge prerequisites
- [Commit Rules](./03-commits.md) - commit quality baseline

## Pull Request

- title format: `<type>: <summary>`
- target branches:
- `working` -> `dev`
- `hotfix` -> `main`
- `dev` -> `main`
- link issues with keywords like `Closes #123` or `Fixes #45`

## Merge Strategy

- into `dev`: merge commit (`--no-ff`)
- into `main`: squash merge
