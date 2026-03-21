---
id: T-001
type: task
title: T-001-establish-deterministic-context-assembly-for-plan-and-build
status: active
plan_ref: PLAN-MAIN
scope:
  in:
  - src/taco
  - .context/project
  out:
  - Runtime migration from Python to Rust implementation
  - Introduction of new MCP/CLI tools outside existing pack flow
  - Team-specific policy hardcoding in command handlers
references:
  modules:
  - ARCH-INDEX
  flows:
  - PLAN-MAIN
  schemas:
  - GOV-CODE-PRINCIPLES
links:
- PLAN-MAIN
- I-002
- ARCH-INDEX
- GOV-CODE-PRINCIPLES
intent_ref: I-002
---

## Intent
Define the first implementation unit that recreates deterministic context assembly for TACO plan/build workflows using document SSOT. The task exists to make context pack generation reproducible, traceable, and execution-ready from project documents.

## Goal
Produce an implementation-ready specification and executable verification path for deterministic context assembly so later coding work can implement `plan.pack` and `task.pack` behavior without ambiguity.

## Scope
In scope:
- Define concrete document inputs and normalization order for context assembly from `.context/project/*` and governance references.
- Define traceability output requirements (selected references, rationale, and stable ordering) for pack outputs.
- Define failure behavior for missing required references and non-deterministic ordering risks.

Out of scope / non-goals:
- Implementing full end-to-end command runtime behavior in this task.
- Refactoring unrelated modules outside context assembly boundaries.
- Adding auto-remediation logic that mutates source documents during pack creation.

## Implementation Approach
1. Establish a hexagonal boundary contract for context assembly:
- Core (`src/taco/core/*`) owns deterministic selection, ordering, and validation rules for context assembly.
- Ports (`src/taco/ports/*`) define abstract interfaces for document loading, indexing, and trace output persistence.
- Adapters (`src/taco/adapters/*`) implement filesystem and transport concerns (file reads, MCP/CLI response formatting) without embedding domain rules.

2. Define deterministic assembly algorithm at the core boundary:
- Inputs: intent/task identifiers, plan references, and required governance links.
- Process: normalize references, resolve documents in fixed precedence, deduplicate by stable id/path key, and emit sorted bundle.
- Outputs: pack payload plus trace metadata (`selected_refs`, `reason_codes`, `omissions`) required for auditability.

3. Define boundary guardrails that prevent core bypass:
- `apps/*` entrypoints must call core use-cases through ports, not direct adapter logic.
- Adapter errors are mapped into domain-level error codes before surfacing to CLI/MCP.
- Contract changes to pack schema require explicit versioning notes in task results.

## Verification Approach
Run these commands from repository root:

1. `UV_CACHE_DIR=/tmp/uv-cache uv run taco plan intent view --intent-id I-002`
Pass condition: intent and linked references resolve without missing-document errors.
Fail condition: unresolved links, missing intent metadata, or non-zero exit.

2. `UV_CACHE_DIR=/tmp/uv-cache uv run taco plan task lint --intent-id I-002 --path .context/project/tasks/T-001-establish-deterministic-context-assembly-for-plan-and-build.md`
Pass condition: `valid=true` and no missing section/front matter diagnostics.
Fail condition: any lint violation, template-marker warning, or non-zero exit.

3. `UV_CACHE_DIR=/tmp/uv-cache uv run taco plan intent review-bundle --intent-id I-002`
Pass condition: bundle contains deterministic task references and no unresolved governance links.
Fail condition: mismatch between intent/task linkage, missing required refs, or unstable ordering diagnostics.

## Implementation Result
- Task document authored with executable scope for deterministic context assembly start.
- Hexagonal core/ports/adapters rationale is explicitly documented for future implementation boundaries.
- Contract and traceability expectations are fixed to reduce ambiguity for coding tasks.

## Verification Result
- Pending execution after task authoring and front matter synchronization.
- Expected artifact for completion: lint-valid task and review bundle output confirming reference integrity.
