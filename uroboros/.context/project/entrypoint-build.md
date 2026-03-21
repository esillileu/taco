---
id: PROJ-ENTRYPOINT-BUILD
type: anchor
title: Build Mode Entrypoint
status: active
links: [PROJ-OVERVIEW, PLAN-MAIN, FLOW-MODE-TRANSITION, GOV-CODE-PRINCIPLES]
---

# Build Mode Entrypoint

## Purpose

- Provide a deterministic execution guide for build-mode agents.
- Minimize implementation-time judgment by enforcing pack-first execution.

## Context Policy

- Build mode is `pack-only` by default.
- Global design docs are not loaded as default execution context.
- Primary input is the result of `task.pack`.

## Command Sequence

1. `uv run taco task pack` (or `uv run taco task pack --task-id <TASK_ID>`)
2. Serialize pack payload once and reuse it:
   - `PACK_JSON=$(uv run python - <<'PY'\nimport json, subprocess\nraw = subprocess.check_output(['uv', 'run', 'taco', 'task', 'pack'], text=True)\nprint(json.dumps(json.loads(raw)['data'], ensure_ascii=False))\nPY\n)`
   - Alternative: save pack to file and pass the file path (`--pack-json /path/to/pack.json`).
3. `uv run taco build precheck --pack-json "$PACK_JSON"`
4. Implement and verify only within pack scope.
5. `uv run taco build postcheck --pack-json "$PACK_JSON" --changed-paths-json '<CHANGED_PATHS_JSON>' --produced-outputs-json '<PRODUCED_OUTPUTS_JSON>' --check-results-json '<CHECK_RESULTS_JSON>'`
6. Record outcome:
  - success: `uv run taco task complete --task-id <TASK_ID> --implementation "<TEXT>" --verification "<TEXT>" --apply`
  - blocked: `uv run taco task block --task-id <TASK_ID> --reason-code <CODE> --reason "<TEXT>" --apply`
  - when content includes shell-sensitive text, prefer `task record --content-file <PATH>` over inline `--content`.

## MCP Smoke Flow (Build Validation)

Use this when build scope includes MCP runtime compatibility checks.

```bash
cat <<'JSON' | uv run python -m taco.apps.mcp.main
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}
{"jsonrpc":"2.0","method":"notifications/initialized","params":{}}
{"jsonrpc":"2.0","id":2,"method":"tools/list"}
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"task.list","arguments":{}}}
{"jsonrpc":"2.0","id":4,"method":"shutdown"}
{"jsonrpc":"2.0","method":"exit"}
JSON
```

## Auto Task Selection

- If `task_id` is omitted in `task.pack`:
  - select first `active_tasks` item
  - else select first `next_tasks` item
  - if no candidate, fail with `no_task_available`
  - if multiple active tasks, fail with `ambiguous_active_tasks`

## Drift Policy

- `build.postcheck` failures are hard failures.
- `changed_paths_json` is for implementation-changed paths.
- `produced_outputs_json` is for required output artifacts.
- If a required output also appears in changed paths, postcheck treats it as declared output and excludes it from scope-violation checks.
- Drift details must be reported through error details:
  - `task_id`
  - `failed_rule`
  - `changed_paths_snapshot`
  - `suggested_plan_actions`
- Failed build loops return control to plan mode for design/task adjustment.

## Do / Do Not

- Do: execute only the packed task scope.
- Do: report drift or blocked states explicitly.
- Do not: reinterpret architecture intent during build execution.
- Do not: broaden scope without plan-mode updates.
