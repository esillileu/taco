---
id: PROJ-OVERVIEW
type: anchor
title: Project Overview
status: active
links: [PROJ-INTENT-INDEX, ARCH-INDEX, PLAN-MAIN, FLOW-TASK-PACK, FLOW-MODE-TRANSITION]
---

# Project Overview

## Purpose

TACO orchestrates task-first execution by delivering one executable task with only the minimum required context bundle.

## Core Objective

- Reduce both context overflow and context omission.
- Keep agent execution deterministic and repeatable.
- Keep architectural SSOT global while letting tasks consume scoped slices.
- Preserve runtime contract across Python-first to Rust-final migration.

## Non-Goals

- TACO does not optimize for full-repository summarization.
- TACO does not decide product priority by itself.
- TACO does not treat historical narrative as required execution context.

## Intent-to-Task Model

- Planning starts from intent nodes, then maps to executable task nodes.
- Unit of build execution is exactly one task node.
- Task node must include execution intent, scope boundary, references, and verification criteria.
- Pack builder resolves references to architecture/governance nodes and extracts heading slices.

## Mode Model

- Plan mode:
  - updates architecture/plan/task documents
  - validates references and transition readiness
  - uses `plan.intent.*` for intent-first planning (`list`, `view`, `pack`)
  - uses `plan.pack` when a specific task-level plan pack is needed
- Build mode:
  - executes one task with bundle-only context
  - records implementation/verification outcomes
  - uses `task.pack` to load build-scoped default context
- Mode switching policy is defined in `FLOW-MODE-TRANSITION`.

## Intent Policy

- Plan intent:
  - optimize for design safety and document consistency
  - default pack references must include `ARCH-INDEX`, `PLAN-MAIN`, `GOV-DOC-INDEX`
- Build intent:
  - optimize for implementation determinism and minimal execution context
  - default pack references must include `GOV-CODE-PRINCIPLES`
- Git intent in build:
  - git conventions are not always-included pack context
  - before branch/commit/merge actions, agent must call `convention.get(topic=git)`
  - when needed, agent should follow with `doc.snippet` on the returned git rule path

## Quality Bar

- Deterministic output for identical input state.
- Stable public error shape: `code`, `message`, `details`.
- Stable CLI/MCP command parity.
- Strict validation failure for broken front matter or unresolved references.

## Expected Outcome

- An agent can start planning from one `plan.intent.index` call, then move to `task.pack` for build execution.
- Task execution and document updates remain traceable through IDs and links.
- Architecture scale-up is handled by node splitting, not by copying definitions into tasks.
