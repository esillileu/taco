---
id: PROJ-ENTRYPOINT-PLAN
type: anchor
title: Plan Mode Entrypoint
status: active
links: [PROJ-OVERVIEW, PROJ-INTENT-INDEX, ARCH-INDEX, PLAN-MAIN, GOV-DOC-INDEX]
---

# Plan Mode Entrypoint

## Purpose

- Provide a deterministic starting guide for plan-mode agents.
- Keep intent, architecture, and plan updates consistent with SSOT boundaries.

## When to Use

- Start of every planning session before editing intent/architecture/plan/task docs.
- Any time build results are blocked and design decisions must be revisited.

## Required Inputs

- User intent and objective.
- Current SSOT state (`overview`, `intents`, `architecture`, `plan`).

## Preload Order

1. `.context/project/overview.md`
2. `.context/project/intents/index.md`
3. `.context/project/architecture/index.md`
4. `.context/project/plan.md`
5. `.context/governance/doc/index.md`

## Command Sequence

1. `uv run taco plan intent list`
2. `uv run taco plan intent view --intent-id <INTENT_ID>`
3. `uv run taco plan intent propose --intent-id <INTENT_ID>`
4. `uv run taco plan intent autodesign --intent-id <INTENT_ID> --proposal-fingerprint <PROPOSAL_FP>`
5. `uv run taco plan intent generate-tasks --intent-id <INTENT_ID> --design-fingerprint <DESIGN_FP>`
6. `uv run taco plan intent review-bundle --intent-id <INTENT_ID> --proposal-fingerprint <PROPOSAL_FP> --design-fingerprint <DESIGN_FP> --taskset-fingerprint <TASKSET_FP> [--retry-on-fail 1]`
7. `uv run taco plan intent apply --intent-id <INTENT_ID> --decision-fingerprint <DECISION_FP> --approve --apply`
8. `uv run taco plan validate`

## Review Gate Notes

- `review-bundle` requires authored task documents for generated blueprints.
- Missing task files or pack-readiness failures keep status at `fail`.
- `apply` is blocked until review issues are empty.

## Plan Responsibilities

- Convert user intent into explicit design intent records.
- Update intent/plan metadata and queue state through gated apply operations.
- Produce task blueprints (path/front matter/required sections/readiness rules), not task body text.
- Require agents to author actual task section content before build handoff.
- Keep links and references synchronized when splitting or moving docs.

## Handoff to Build

- Build handoff is allowed only when:
  - task scope and verification are explicit
  - references are resolvable
  - review bundle status is `pass`
  - apply fingerprint gate succeeded with explicit approval
  - validation passes without critical errors

## Do / Do Not

- Do: make design decisions and document them explicitly.
- Do: keep architecture/plan/intents as SSOT for reasoning.
- Do not: execute implementation changes in plan mode.
- Do not: treat historical notes as mandatory execution context.
