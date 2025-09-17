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

if [ ! -d "$PROJECT_DIR/.venv" ]; then
  echo "Backend virtual environment missing. Run scripts/install_backend.sh first." >&2
  exit 1
fi

if [ ! -f "$PROJECT_DIR/.venv/bin/activate" ]; then
  echo "Python virtual environment appears corrupted. Recreate it with scripts/install_backend.sh." >&2
  exit 1
fi

DEFAULT_BACKEND_HOST="$($PYTHON_BIN - <<'PY'
import json
from pathlib import Path
config = json.loads(Path("config/settings.json").read_text())
print(config.get("app", {}).get("host", "0.0.0.0"))
PY
)"
DEFAULT_BACKEND_PORT="$($PYTHON_BIN - <<'PY'
import json
from pathlib import Path
config = json.loads(Path("config/settings.json").read_text())
print(config.get("app", {}).get("port", 8000))
PY
)"
DEFAULT_FRONTEND_PORT="$($PYTHON_BIN - <<'PY'
import json
from pathlib import Path
config = json.loads(Path("config/settings.json").read_text())
print(config.get("frontend", {}).get("dev_server_port", 5173))
PY
)"

BACKEND_HOST="${1:-$DEFAULT_BACKEND_HOST}"
BACKEND_PORT="${2:-$DEFAULT_BACKEND_PORT}"
FRONTEND_HOST="${3:-localhost}"
FRONTEND_PORT="${4:-$DEFAULT_FRONTEND_PORT}"

BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
  if [[ -n "${BACKEND_PID:-}" ]]; then
    if kill -0 "$BACKEND_PID" 2>/dev/null; then
      echo "Stopping backend (PID $BACKEND_PID)..."
      kill "$BACKEND_PID" 2>/dev/null || true
      wait "$BACKEND_PID" 2>/dev/null || true
    fi
  fi
  if [[ -n "${FRONTEND_PID:-}" ]]; then
    if kill -0 "$FRONTEND_PID" 2>/dev/null; then
      echo "Stopping frontend (PID $FRONTEND_PID)..."
      kill "$FRONTEND_PID" 2>/dev/null || true
      wait "$FRONTEND_PID" 2>/dev/null || true
    fi
  fi
}
trap cleanup EXIT
trap 'cleanup; exit 130' INT TERM

cd "$PROJECT_DIR"
# shellcheck disable=SC1091
source ".venv/bin/activate"

uvicorn backend.main:app --host "$BACKEND_HOST" --port "$BACKEND_PORT" --reload &
BACKEND_PID=$!

echo "Backend running on http://${BACKEND_HOST}:${BACKEND_PORT} (PID $BACKEND_PID)"

cd "$FRONTEND_DIR"
npm run dev -- --host "$FRONTEND_HOST" --port "$FRONTEND_PORT" &
FRONTEND_PID=$!
cd "$PROJECT_DIR"

echo "Frontend running on http://${FRONTEND_HOST}:${FRONTEND_PORT} (PID $FRONTEND_PID)"
echo "Press Ctrl+C to stop both services."

set +e
EXIT_CODE=0
while true; do
  if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
    wait "$BACKEND_PID" 2>/dev/null
    EXIT_CODE=$?
    break
  fi
  if ! kill -0 "$FRONTEND_PID" 2>/dev/null; then
    wait "$FRONTEND_PID" 2>/dev/null
    EXIT_CODE=$?
    break
  fi
  sleep 1
done
exit $EXIT_CODE
