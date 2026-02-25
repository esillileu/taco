---
id: ARCH-INDEX
type: anchor
title: Architecture Index
status: active
modules_dir: .context/project/architecture/modules
flows_dir: .context/project/architecture/flows
schemas_dir: .context/project/architecture/schemas
modules:
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
  - main -> cli -> tools -> core
  - main -> tools -> core
  - core modules must not depend on CLI transport
links:
  - MOD-MAIN
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

## System Boundary
<!-- taco:ref=ARCH-BOUNDARY-001 -->

- TACO operates as a local STDIO MCP server and CLI.
- Git-backed markdown is the primary source of truth.
- Index/cache is auxiliary and must not override source docs.
- Context assembly is deterministic extraction, not free-form summarization.

## Reference Model

- Architecture stays global and stable; task-specific variants are not created.
- Tasks declare required references; pack resolves those references only.
- Node identity is front matter `id`; references are `id-only`.
- Front matter metadata and heading-level content are both first-class in assembly.

## Processing Pipeline

1. CLI parse (`main.py`): parse command and options.
2. CLI map (`cli.py`): map command to canonical tool call.
3. State load (`tools.py`): load config, scan docs, build index.
4. Core parse/index (`parser.py`, `indexer.py`): build heading/node lookups.
5. Tool dispatch (`tools.py`): route to task/doc/issue/convention handlers.
6. Pack/Router (`pack.py`, `router.py`): build bundle or write target.
7. Envelope emit (`main.py`): return JSON response envelope.

## Operating Modes

- Plan mode: update architecture/plan/task nodes with validation and impact awareness.
- Build mode: execute exactly one task using `task.pack` output and record results.
- Mode switches follow `FLOW-MODE-TRANSITION` and must be explicit.

## Interface Surface

- `task.list`
- `task.pack`
- `task.targets`
- `task.record`
- `doc.snippet`
- `issue.triage`
- `convention.get`

## Source Mapping

- `src/taco/main.py`: CLI entrypoint, argparse, response printing.
- `src/taco/cli.py`: CLI-to-tool mapping and option validation.
- `src/taco/tools.py`: repo state loading, tool dispatch handlers.
- `src/taco/parser.py`: markdown heading and marker slicing.
- `src/taco/indexer.py`: index graph and front matter metadata indexing.
- `src/taco/pack.py`: task bundle assembly with budget and ref resolution.
- `src/taco/router.py`: write-target resolution for record flows.

## Module Responsibilities

- `MOD-MAIN`: process entrypoint and transport-neutral output envelope.
- `MOD-CLI-MAPPER`: validates CLI options and canonical tool mapping.
- `MOD-TOOLS-DISPATCH`: central dispatch and repo state orchestration.
- `MOD-PARSER`: deterministic heading and marker extraction.
- `MOD-INDEXER`: typed document graph and id/reference lookup.
- `MOD-PACK`: task-centered context bundle assembly.
- `MOD-ROUTER`: route-type to heading target resolution.

## Dependency Rules

- `main.py` may depend on `cli.py` and `tools.py`.
- `tools.py` may depend on core modules (`indexer`, `pack`, `router`).
- `parser/indexer/pack/router` must not depend on CLI concerns.
- `pack` and `router` consume index graph but do not write source docs directly.
- concurrency/cache policy is an optional layer, separated from correctness logic.

## Portability Principles

- Tool DTOs are language-agnostic and stable across runtime migration.
- I/O is isolated in adapters; core logic remains side-effect free where possible.
- Public errors follow one structure: `code`, `message`, `details`.
- Rules/policy are configured, not hardcoded.

## Architectural Risks to Track

- Incomplete migration from legacy marker groups to front matter-only semantics.
- Oversized pack payload when heading slices are too broad.
- Drift between schema docs and actual response shape.
- Confusion between node-id references and heading marker references.
- Mode drift where plan-level decisions leak into build execution without task updates.

## Dogfooding Rule

- As soon as a tool is available, use it to run this repository workflow.
- Defects found via dogfooding are prioritized over adding new scope.
