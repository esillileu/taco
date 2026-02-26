---
id: MOD-TOOLS-DISPATCH
type: module
title: Tool Dispatcher
status: active
role: Load repo state and dispatch canonical tool handlers
boundary: Orchestrates parser/indexer/pack/router usage
depends_on: [MOD-PARSER, MOD-INDEXER, MOD-PACK, MOD-ROUTER]
provides: [SCH-TOOL-ENVELOPE, SCH-TOOL-ERROR]
consumes: [SCH-INDEX-GRAPH]
must_not:
  - Must not implement CLI argument parsing
invariants:
  - Unknown tools return deterministic error envelope
related_flows: [FLOW-TOOL-DISPATCH, FLOW-TASK-PACK, FLOW-TASK-RECORD]
links: [MOD-PARSER, MOD-INDEXER, MOD-PACK, MOD-ROUTER, SCH-TOOL-ERROR]
---

# Tools Dispatch Module

Central runtime orchestrator for supported tool handlers, including plan-intent handlers
(`plan.intent.list`, `plan.intent.view`, `plan.intent.index`, `plan.intent.propose`,
`plan.intent.autodesign`, `plan.intent.generate_tasks`, `plan.intent.review_bundle`,
`plan.intent.apply`).
