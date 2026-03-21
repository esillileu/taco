#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
RESULT_MD="$ROOT_DIR/result-build.md"
RESULT_LOG="$ROOT_DIR/result-build.log"
ENTRYPOINT_BUILD="$SCRIPT_DIR/.context/project/entrypoint-build.md"
PROMPT_FILE="$ROOT_DIR/.tmp-build-prompt.md"

rm -f "$RESULT_MD"
echo "" > "$RESULT_LOG"

echo "[build 1/3] Rebind MCP server 'taco' to uroboros directory" | tee "$RESULT_LOG"
codex mcp remove taco || true
codex mcp add taco -- bash -lc "cd '$SCRIPT_DIR' && UV_CACHE_DIR=/tmp/uv-cache uv run python -m taco.apps.mcp.main"
codex mcp list | tee -a "$RESULT_LOG"

if [[ ! -f "$ENTRYPOINT_BUILD" ]]; then
  echo "[error] missing build entrypoint: $ENTRYPOINT_BUILD" | tee -a "$RESULT_LOG" >&2
  exit 1
fi

cat > "$PROMPT_FILE" <<'MD'
Execute build mode now. Do not stop at document existence checks.

Requirements:
1. Read the injected build entrypoint content below and execute its workflow in this repo.
2. Use Taco MCP tools as the primary execution path. Do NOT run `uv run taco ...` CLI commands except for diagnostics when MCP is unavailable.
3. If a required precondition is missing, report it explicitly and continue with best-effort checks.
4. End output with this strict contract:
   - First line: `BUILD_EXECUTED` or `BUILD_BLOCKED`
   - Then include:
     - selected `task_id`
     - tool calls made (ordered)
     - key outputs/errors per tool
     - final pass/fail verdict for build-mode execution

Required MCP tool-call sequence:
- `task.pack` (no args). If `no_task_available`, call `task.list`, choose first task, then call `task.pack` with `task_id`.
- `build.precheck` with `pack` object from `task.pack`.
- `build.postcheck` with:
  - same `pack`
  - `changed_paths` as array
  - `produced_outputs` as array; include `pack.required_outputs` when validating successful delivery
  - `check_results` as object
- If build is blocked, call `task.block` with supported reason code only:
  - `scope_split_required` or `verification_ambiguous`
- Before recording completion/block, call `task.targets` with a configured route type:
  - `implementation_result` or `verification_result`

Build entrypoint content:

MD
cat "$ENTRYPOINT_BUILD" >> "$PROMPT_FILE"

echo "[build 2/3] Run Codex headless in build mode" | tee -a "$RESULT_LOG"
set +e
cat "$PROMPT_FILE" | codex exec --full-auto -C "$SCRIPT_DIR" --output-last-message "$RESULT_MD" - 2>&1 | tee -a "$RESULT_LOG"
CODEX_RC=$?
set -e
rm -f "$PROMPT_FILE"

if [[ $CODEX_RC -ne 0 ]]; then
  echo "[error] codex exec failed with exit code $CODEX_RC" | tee -a "$RESULT_LOG"
  exit $CODEX_RC
fi

echo "[build 3/3] Done" | tee -a "$RESULT_LOG"
echo "- Result message: $RESULT_MD" | tee -a "$RESULT_LOG"
echo "- Full log: $RESULT_LOG" | tee -a "$RESULT_LOG"
