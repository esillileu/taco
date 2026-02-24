# Document Map (SSOT)

## Purpose

This file is the single source of truth (SSOT) for the documentation system. It defines document types, ownership, required headers, link rules, and default paths.

## Global Conventions

- All docs are Markdown files using ATX headings (`#`, `##`, `###`).
- Every document must start with a single H1 title.
- Relative links must be repository-relative from the current file location.
- Cross-references should use explicit markdown links, not plain text mentions.
- IDs in filenames are zero-padded to three digits for task and ADR docs.

## Document Types

### 1. Document Map
- **Path:** `docs/doc-map.md`
- **Owner:** Documentation Steward (default: repository maintainers)
- **Purpose:** Defines the entire documentation contract.
- **Mandatory H2 headings:**
  - `## Purpose`
  - `## Global Conventions`
  - `## Document Types`
  - `## Link Rules`
  - `## Validation Rules`

### 2. Intent
- **Path:** `docs/intent.md`
- **Owner:** Product/Project owner
- **Purpose:** Problem statement, outcomes, and scope boundaries.
- **Mandatory H2 headings:**
  - `## Problem`
  - `## Outcomes`
  - `## In Scope`
  - `## Out of Scope`

### 3. Architecture
- **Path:** `docs/architecture.md`
- **Owner:** Technical lead/architect
- **Purpose:** High-level system structure and decisions.
- **Mandatory H2 headings:**
  - `## Context`
  - `## Components`
  - `## Data Flows`
  - `## Constraints`

### 4. Principles
- **Path:** `docs/principles.md`
- **Owner:** Engineering team
- **Purpose:** Decision-making principles and quality bars.
- **Mandatory H2 headings:**
  - `## Engineering Principles`
  - `## Documentation Principles`
  - `## Delivery Principles`

### 5. Plan
- **Path:** `docs/plan.md`
- **Owner:** Delivery lead
- **Purpose:** Milestones and sequencing.
- **Mandatory H2 headings:**
  - `## Milestones`
  - `## Dependencies`
  - `## Risks`

### 6. Glossary
- **Path:** `docs/glossary.md`
- **Owner:** All contributors (maintained by docs steward)
- **Purpose:** Shared terms and canonical definitions.
- **Mandatory H2 headings:**
  - `## Terms`

### 7. Todo
- **Path:** `docs/todo.md`
- **Owner:** Delivery team
- **Purpose:** Actionable backlog and open work.
- **Mandatory H2 headings:**
  - `## Active`
  - `## Upcoming`
  - `## Done`

### 8. Task Documents
- **Path pattern:** `docs/tasks/T-XXX-<slug>.md`
- **Owner:** Assignee of the task
- **Purpose:** Implementation-level planning and tracking.
- **Mandatory H2 headings (exact text and order):**
  - `## Metadata`
  - `## Objective`
  - `## Scope`
  - `## Implementation Plan`
  - `## Validation`
  - `## Links`
  - `## Change Log`

### 9. ADR Documents
- **Path pattern:** `docs/adr/ADR-XXX-<slug>.md`
- **Owner:** Technical lead/decision maker
- **Purpose:** Record architectural decisions and rationale.
- **Mandatory H2 headings (exact text and order):**
  - `## Metadata`
  - `## Context`
  - `## Decision`
  - `## Alternatives Considered`
  - `## Consequences`
  - `## Links`

## Link Rules

1. `README.md` must link all top-level docs and both directories (`docs/tasks/`, `docs/adr/`).
2. `docs/plan.md` milestone entries should link to at least one task doc when implementation exists.
3. Each task doc should link to:
   - relevant plan milestone(s),
   - related ADR(s), and
   - affected architecture/intent sections where applicable.
4. Each ADR should link to impacted task(s) and architecture/principles sections.
5. Broken relative links are invalid.

## Validation Rules

- Required headings must match exactly (case, spacing, punctuation).
- For Task and ADR docs, required headings must appear once and in the listed order.
- Filename prefixes must match:
  - Task: `T-` followed by a 3-digit ID.
  - ADR: `ADR-` followed by a 3-digit ID.
- Top-level docs must exist at their default paths unless superseded by an explicit update to this SSOT.
