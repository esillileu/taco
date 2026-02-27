---
id: ARCH-INDEX
type: anchor
title: Architecture Index
status: active
modules_dir: .context/project/architecture/modules
flows_dir: .context/project/architecture/flows
schemas_dir: .context/project/architecture/schemas
modules:
  - MOD-APPS
  - MOD-ADAPTERS
  - MOD-PORTS
  - MOD-EXTENSIONS
  - MOD-MAIN
  - MOD-CLI-MAPPER
  - MOD-TOOLS-DISPATCH
  - MOD-PARSER
  - MOD-INDEXER
  - MOD-PACK
  - MOD-ROUTER
flows:
  - FLOW-TASK-PACK
  - FLOW-TOOL-DISPATCH
  - FLOW-TASK-RECORD
  - FLOW-MODE-TRANSITION
schemas:
  - SCH-PACK-RESULT
  - SCH-WRITE-TARGET
  - SCH-GLOSSARY
  - SCH-SECTION-SLICE
  - SCH-INDEX-GRAPH
  - SCH-TASK-NODE
  - SCH-TOOL-ERROR
  - SCH-TOOL-ENVELOPE
dependency_rules:
  - apps -> adapters -> ports -> core
  - apps -> extensions -> core
  - extensions -> ports -> core
  - core must not depend on adapters or extensions
links:
  - PROJ-INTENT-INDEX
  - MOD-MAIN
  - MOD-APPS
  - MOD-ADAPTERS
  - MOD-PORTS
  - MOD-EXTENSIONS
  - MOD-CLI-MAPPER
  - MOD-TOOLS-DISPATCH
  - MOD-PARSER
  - MOD-INDEXER
  - MOD-PACK
  - MOD-ROUTER
  - FLOW-TASK-PACK
  - FLOW-TOOL-DISPATCH
  - FLOW-TASK-RECORD
  - FLOW-MODE-TRANSITION
  - SCH-PACK-RESULT
  - SCH-SECTION-SLICE
  - SCH-INDEX-GRAPH
  - SCH-TASK-NODE
  - SCH-TOOL-ERROR
  - SCH-TOOL-ENVELOPE
  - PLAN-MAIN
---

# Architecture Index

<!-- taco:ref=ARCH-REFMODEL-001 -->
Architecture anchor for modules, flows, and schemas. This document is global SSOT for boundaries and dependency direction.

- Runtime strategy: Python-first delivery with Rust-final runtime target.
- design-sync: I-038 test-suite srp refactor phase2 synchronized via FLOW-MODE-TRANSITION updates.

## System Boundary
<!-- taco:ref=ARCH-BOUNDARY-001 -->

- TACO operates as a local STDIO MCP server and CLI.
- Git-backed markdown is the primary source of truth.
- Index/cache is auxiliary and must not override source docs.
- Context assembly is deterministic extraction, not free-form summarization.
- Architecture docs define structure only; they do not manage task queue state.

## Reference Model

- Architecture stays global and stable; task-specific variants are not created.
- Tasks declare required references; pack resolves those references only.
- Node identity is front matter `id`; references are `id-only`.
- Front matter metadata and heading-level content are both first-class in assembly.

## Processing Pipeline

1. App entry (`apps/main.py`): parse command and compose runtime.
2. CLI map (`apps/cli`): map command to canonical tool call.
3. State load (`adapters/fs/repo_state.py`): load config, scan docs, build index.
4. Core parse/index (`core/parsing`, `core/indexing`): build heading/node lookups.
5. Core tool dispatch (`core/usecases/dispatcher.py`): route to task/doc/issue/convention handlers.
6. Core pack/router (`core/packing`, `core/routing`): build bundle or write target.
7. Envelope emit (`apps/main.py`): return JSON response envelope.

## Mode Architecture

- Plan mode responsibilities:
  - refine design boundaries, contracts, and structural data/event flow.
  - decide design-level impact classification for intent changes.
- Build mode responsibilities:
  - execute scoped code changes from task pack.
  - produce implementation/verification evidence without redefining architecture.
- Mode switch contract is defined by `FLOW-MODE-TRANSITION`.
- Queue sequencing and active/blocked task management are owned by `PLAN-MAIN` (not this document).

## Layer Layout

- `apps/`: composition root and executable entrypoints only.
- `adapters/`: runtime/fs/git implementations.
- `ports/`: storage/repository abstractions.
- `core/`: deterministic domain logic (parsing/indexing/packing/routing/task/plan).
- `extensions/`: optional extension surface (resource-backed by `resources/templates`).

## Source Mapping

- `src/taco/apps/main.py`: CLI entrypoint and composition root.
- `src/taco/apps/cli/`: app-facing CLI surface, mapping, and validation.
- `src/taco/adapters/mcp/`: MCP transport adapter surface.
- `src/taco/adapters/fs/repo_state.py`: config/index loading adapter.
- `src/taco/apps/composition.py`: shared composition/wiring for tool runtime.
- `src/taco/apps/cli/main.py`: CLI runtime entry implementation.
- `src/taco/core/parsing/`: markdown heading and marker slicing.
- `src/taco/core/indexing/`: index graph and front matter metadata indexing.
- `src/taco/core/packing/`: task bundle assembly with budget/ref resolution.
- `src/taco/core/routing/`: write-target resolution and route policy (`policy.py`).
- `src/taco/core/task/`: task readiness/design-sync/plan-sync decision logic.
- `src/taco/core/plan/`: planning domain rules (`config_policy.py`, `text_ops.py`, `markdown_ops.py`, `plan_policy.py`, `types.py`).
- `src/taco/core/usecases/dispatcher.py`: tool dispatch facade.
- `src/taco/core/usecases/{bootstrap,build,doc,plan,task}/`: domain-specific usecase handlers.
- `src/taco/resources/templates/`: externalized scaffolding templates.
- `src/taco/ports/`: storage/repository port interfaces.
- `src/taco/adapters/fs/storage.py`: `StoragePort` implementation.
- `src/taco/adapters/git/repository.py`: `RepositoryPort` implementation.

## Module Responsibilities

- `MOD-MAIN`: process entrypoint and transport-neutral output envelope.
- `MOD-APPS`: executable composition root and entry surfaces.
- `MOD-ADAPTERS`: infrastructure adapters for CLI/runtime/fs/git.
- `MOD-PORTS`: core-facing external dependency interfaces.
- `MOD-EXTENSIONS`: optional plugin/template surface.
- `MOD-CLI-MAPPER`: validates CLI options and canonical tool mapping.
- `MOD-TOOLS-DISPATCH`: core usecase dispatcher and envelope orchestration.
- `MOD-PARSER`: deterministic heading and marker extraction.
- `MOD-INDEXER`: typed document graph and id/reference lookup.
- `MOD-PACK`: task-centered context bundle assembly.
- `MOD-ROUTER`: route-type to heading target resolution.

## Dependency Rules

- `apps/*` may depend on `adapters/*` and `core/*` (and optional extension surface).
- `adapters/*` may depend on `ports/*` and `core/*`.
- `extensions/*` is optional and may depend on `ports/*` and `core/*`.
- `core/*` may depend only on `ports/*` and `core/*`.
- `core` must not import `adapters` or `extensions`.
- `pack` and `routing` consume index graph but do not write source docs directly.
- concurrency/cache policy is an optional layer, separated from correctness logic.

## Portability Principles

- Tool DTOs are language-agnostic and stable across runtime migration.
- I/O is isolated in adapters; core logic remains side-effect free where possible.
- Public errors follow one structure: `code`, `message`, `details`.
- Rules/policy are configured, not hardcoded.

## Documentation Boundary

- Architecture documents must not include task queue directives or sprint-like status tracking.
- Architecture documents define only:
  - module responsibility boundaries
  - dependency direction
  - public contract and schema
  - structural processing flow

## Architectural Risks to Track

- Incomplete migration from legacy marker groups to front matter-only semantics.
- Oversized pack payload when heading slices are too broad.
- Drift between schema docs and actual response shape.
- Confusion between node-id references and heading marker references.
- Mode drift where plan-level decisions leak into build execution without task updates.

## Dogfooding Rule

- As soon as a tool is available, use it to run this repository workflow.
- Defects found via dogfooding are prioritized over adding new scope.
