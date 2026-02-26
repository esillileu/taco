---
id: T-022
type: task
title: T-022-sync-plan-active-intents
status: done
plan_ref: PLAN-MAIN
priority: p1
estimate: m
scope:
  in: []
  out: []
references:
  modules:
  - ARCH-INDEX
  flows:
  - FLOW-MODE-TRANSITION
  schemas:
  - SCH-TOOL-ENVELOPE
  governance:
  - GOV-CODE-PRINCIPLES
links:
- PLAN-MAIN
- ARCH-INDEX
- I-020
---

# Task: T-022-sync-plan-active-intents

## Intent

- Auto-generated from intent `I-020`.

## Goal

- align plan active_intents queue

## Scope

- Fill generated scope from review bundle.

## Implementation Approach

- Define implementation details before build mode handoff.

## Verification Approach

- Define deterministic verification checklist.

## Implementation Result

- Pending

- Confirmed active_intents synchronization is stable: plan keeps I-020 active and flow intent_refs includes I-020; no queue mismatch gap remains for the refactor lane.
## Verification Result

- Pending
- Verified with plan.intent.index(I-020) reporting no plan_queue_mismatch gap and plan.view showing active_intents includes I-020; docs validation also passes.
