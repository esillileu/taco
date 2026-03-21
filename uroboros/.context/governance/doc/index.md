---
id: GOV-DOC-INDEX
type: governance
title: Documentation Conventions
status: active
domain: doc
scope: repo
must: []
must_not: []
links: [ARCH-INDEX, PLAN-MAIN]
---

# Documentation Guide

## Structure

- Canonical knowledge root is `.context/`.
- Project design and execution docs live in `.context/project/`.
- Governance rules live in `.context/governance/`.

## Project Documents

- `.context/project/overview.md`: project objective anchor.
- `.context/project/entrypoint-plan.md`: plan-mode entry and operating sequence.
- `.context/project/entrypoint-build.md`: build-mode entry and operating sequence.
- `.context/project/intents/index.md`: intent registry anchor.
- `.context/project/intents/I-*.md`: plan intents linked to executable tasks.
- `.context/project/plan.md`: thin execution map and active task links.
- `.context/project/architecture/index.md`: architecture anchor.
- `.context/project/architecture/modules/*`: module leaves.
- `.context/project/architecture/flows/*`: flow leaves.
- `.context/project/architecture/schemas/*`: schema leaves.
- `.context/project/tasks/*`: executable task nodes.

## Writing Rules

- Every document must include valid front matter.
- `id` is global and stable; references are `id-only`.
- `plan.md` stores task management only (queue, status, sequencing, handoff state).
- `architecture/*` stores project design only (boundaries, dependencies, public contracts, structural flow).
- `intents/I-*.md` stores design intent only (why/change intent, boundary, expected design outcome).
- Flow documents should declare intent linkage via `intent_refs: [I-xxx]` when applicable.
- Task documents must keep scope/verification explicit.
- Avoid copying architecture definitions into tasks.
- Update links and references together when splitting documents.
- Plan-mode agents should start from `.context/project/entrypoint-plan.md`.
- Build-mode agents should start from `.context/project/entrypoint-build.md`.
