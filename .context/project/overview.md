---
id: PROJ-OVERVIEW
type: anchor
title: Project Overview
status: active
links: [ARCH-INDEX, PLAN-MAIN, FLOW-TASK-PACK]
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

## Task-First Model

- Unit of execution is exactly one task node.
- Task node must include execution intent, scope boundary, references, and verification criteria.
- Pack builder resolves references to architecture/governance nodes and extracts heading slices.

## Quality Bar

- Deterministic output for identical input state.
- Stable public error shape: `code`, `message`, `details`.
- Stable CLI/MCP command parity.
- Strict validation failure for broken front matter or unresolved references.

## Expected Outcome

- An agent can start implementation from one `task.pack` call.
- Task execution and document updates remain traceable through IDs and links.
- Architecture scale-up is handled by node splitting, not by copying definitions into tasks.
