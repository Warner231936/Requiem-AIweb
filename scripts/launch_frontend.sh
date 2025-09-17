#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$PROJECT_DIR/frontend"

PYTHON_BIN="${PYTHON_BIN:-python3}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN="python"
fi
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python 3 is required to read config/settings.json." >&2
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is required but was not found on PATH." >&2
  exit 1
fi

DEFAULT_PORT="$($PYTHON_BIN - <<'PY'
import json
from pathlib import Path
config = json.loads(Path("config/settings.json").read_text())
print(config.get("frontend", {}).get("dev_server_port", 5173))
PY
)"

HOST="${1:-localhost}"
PORT="${2:-$DEFAULT_PORT}"

cd "$FRONTEND_DIR"

echo "Starting Requiem frontend on http://${HOST}:${PORT}"
npm run dev -- --host "$HOST" --port "$PORT"
