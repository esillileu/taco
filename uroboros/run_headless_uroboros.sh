#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SCRIPT_NAME="$(basename "$0")"
RESULT_MD="$ROOT_DIR/result.md"
RESULT_LOG="$ROOT_DIR/result.log"

if [[ ! -f "$SCRIPT_DIR/taco.md" ]]; then
  echo "[error] taco.md not found in $SCRIPT_DIR" >&2
  exit 1
fi
if [[ ! -f "$ROOT_DIR/uroboros.md" ]]; then
  echo "[error] uroboros.md not found in $ROOT_DIR" >&2
  exit 1
fi

echo "[1/5] Rebind MCP server 'taco' to uroboros directory" | tee "$RESULT_LOG"
codex mcp remove taco || true
codex mcp add taco -- bash -lc "cd '$SCRIPT_DIR' && UV_CACHE_DIR=/tmp/uv-cache uv run python -m taco.apps.mcp.main"
codex mcp list | tee -a "$RESULT_LOG"

echo "[2/5] Reset uroboros directory (keep taco.md + $SCRIPT_NAME only)" | tee -a "$RESULT_LOG"
find "$SCRIPT_DIR" -mindepth 1 \
  ! -name 'taco.md' \
  ! -name "$SCRIPT_NAME" \
  -exec rm -rf {} +

echo "[3/5] Recreate baseline with taco init" | tee -a "$RESULT_LOG"
(
  cd "$SCRIPT_DIR"
  UV_CACHE_DIR=/tmp/uv-cache uv run taco init | tee -a "$RESULT_LOG"
)

echo "[4/5] Run Codex headless (save last message to result.md)" | tee -a "$RESULT_LOG"
cat "$ROOT_DIR/uroboros.md" | codex exec --full-auto -C "$SCRIPT_DIR" --output-last-message "$RESULT_MD" - | tee -a "$RESULT_LOG"

echo "[5/5] Done" | tee -a "$RESULT_LOG"
echo "- Result message: $RESULT_MD" | tee -a "$RESULT_LOG"
echo "- Full log: $RESULT_LOG" | tee -a "$RESULT_LOG"
