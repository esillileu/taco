# Uroboros Headless Runbook

You are running in `/home/esillileu/taco/uroboros`.
Execution agent is **Codex in headless mode** (`codex exec`).

## Objective
Validate that TACO plan mode can ingest `taco.md` as planning input and produce a first task document that is authored, lint-valid, and sufficient to implement TACO (not only format-valid).

## Headless launch
Run Codex non-interactively and inject this file as the only brief:

```bash
cat /home/esillileu/taco/uroboros.md | codex exec --full-auto -C /home/esillileu/taco/uroboros -
```

Prerequisite:
- Codex MCP config must already include server `taco`.
- Execution must run with working directory fixed to `/home/esillileu/taco/uroboros`.

## MCP rebinding (required)
Before headless run, rebind MCP server `taco` so the server process starts from `/home/esillileu/taco/uroboros`:

```bash
codex mcp remove taco || true
codex mcp add taco -- bash -lc 'cd /home/esillileu/taco/uroboros && UV_CACHE_DIR=/tmp/uv-cache uv run python -m taco.apps.mcp.main'
codex mcp list
```

Expected result:
- `taco` is `enabled`
- command uses `bash -lc` with `cd /home/esillileu/taco/uroboros`

## Hard rules
- Use MCP server `taco` for plan workflow.
- You may run setup commands in this workspace if required.
- Do not ask user questions.
- Use this file as the only execution brief.
- Before plan workflow, reset files inside `/home/esillileu/taco/uroboros` so only `taco.md` and `run_headless_uroboros.sh` remain.
- Do not use MCP results unless the `taco` server has been rebound to the uroboros directory.

## Procedure
1. Confirm current working directory is exactly `/home/esillileu/taco/uroboros`.
2. Execute MCP rebinding steps in this document and confirm `codex mcp list` shows `taco` enabled.
3. Reset directory contents so only `taco.md` and `run_headless_uroboros.sh` remain:
   - `find . -mindepth 1 ! -name 'taco.md' ! -name 'run_headless_uroboros.sh' -exec rm -rf {} +`
4. Recreate baseline context by running `UV_CACHE_DIR=/tmp/uv-cache uv run taco init`.
5. Read full `./taco.md`.
6. Call `plan.intent.template` and follow its decomposition/mapping guidance.
7. Decompose `taco.md` into **multiple intents** (at least 2) and call `plan.intent.create_many`.
8. Select the highest-priority created intent and run:
   - `plan.intent.propose` (with `intent_id`)
   - `plan.intent.autodesign`
   - `plan.intent.generate_tasks`
9. For the first generated task:
   - Call `plan.task.template` for the selected `intent_id`.
   - Author the task markdown file at the generated `path` (do not leave blueprint-only).
   - The body must include concrete content for all required sections:
     - Intent, Goal, Scope, Implementation Approach, Verification Approach, Implementation Result, Verification Result
   - `Implementation Approach` must include explicit hexagonal boundary rationale (core/ports/adapters).
   - `Verification Approach` must include executable commands and pass/fail conditions.
   - `Scope` and front matter must include concrete out-of-scope/non-goals.
   - Run `plan.task.frontmatter.sync` with `intent_id` and `path`.
   - Run `plan.task.lint` with `intent_id` and `path` until `valid=true`.
10. Run:
   - `plan.intent.review_bundle`
   - `plan.intent.apply` with `dry_run=true` and explicit approval if required
11. Evaluate the first authored task against this sufficiency bar:
   - clear implementation scope for TACO recreation start
   - architecture boundary rationale (hexagonal/ports-adapters implications)
   - explicit verification criteria and commands/conditions
   - concrete non-goals and out-of-scope
12. If insufficient, output why it is insufficient with exact missing items.

## Output contract (strict)
- First line must be exactly one of:
  - `SUFFICIENT`
  - `INSUFFICIENT`
- Then include:
  - created intent ids/titles
  - selected intent id
  - proposal/design/taskset/decision fingerprints (if available)
  - generated task blueprint summary
  - task template/frontmatter sync/lint outputs
  - pass/fail for each sufficiency bar item
  - final reasoned verdict
