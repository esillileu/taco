# Architecture

## System Boundaries

TACO is a local STDIO MCP server. Git-backed documents are SSOT, and SQLite is cache only.

## Core Modules

- parser: heading and anchor parsing with section slicing
- indexer: discovery, typing, id extraction, and link graph
- pack: task-centric context assembly
- budget: token estimation and section-level truncation
- router: write target and patch plan resolution
- server: MCP tool surface and orchestration

## Dependency Rules

- `server -> core -> storage`
- `core` must not import `server`
- `parser` must not import `storage`

## Data Model Notes

Responses should include `repo_revision` and `index_version` for reproducibility.
