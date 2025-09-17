#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN="python"
fi
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python 3 is required but was not found on PATH." >&2
  exit 1
fi

DEFAULT_HOST="$($PYTHON_BIN - <<'PY'
import json
from pathlib import Path
config = json.loads(Path("config/settings.json").read_text())
print(config.get("app", {}).get("host", "0.0.0.0"))
PY
)"
DEFAULT_PORT="$($PYTHON_BIN - <<'PY'
import json
from pathlib import Path
config = json.loads(Path("config/settings.json").read_text())
print(config.get("app", {}).get("port", 8000))
PY
)"

HOST="${1:-$DEFAULT_HOST}"
PORT="${2:-$DEFAULT_PORT}"

if [ ! -d ".venv" ]; then
  echo "Virtual environment missing. Run scripts/install_backend.sh first." >&2
  exit 1
fi

if [ ! -f ".venv/bin/activate" ]; then
  echo "Python virtual environment appears corrupted. Recreate it with scripts/install_backend.sh." >&2
  exit 1
fi

# shellcheck disable=SC1091
source ".venv/bin/activate"

uvicorn backend.main:app --host "$HOST" --port "$PORT" --reload
