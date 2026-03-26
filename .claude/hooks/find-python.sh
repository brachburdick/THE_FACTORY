#!/bin/bash
# Portable Python resolver for hook scripts.
#
# Tries, in order:
#   1. .venv/bin/python (project venv — preferred)
#   2. python3 (system Python)
#   3. python (fallback)
#
# Usage from settings.json:
#   "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/find-python.sh \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/some-hook.py"
#
# Or source it to get PYTHON_CMD:
#   source "$(dirname "$0")/find-python.sh" --resolve-only
#   "$PYTHON_CMD" my-script.py

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"

# Resolve mode: just export PYTHON_CMD, don't run anything
if [ "${1:-}" = "--resolve-only" ]; then
  if [ -x "$PROJECT_DIR/.venv/bin/python" ]; then
    PYTHON_CMD="$PROJECT_DIR/.venv/bin/python"
  elif command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
  elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
  else
    echo "ERROR: No Python interpreter found. Install Python 3.11+ or create .venv." >&2
    exit 1
  fi
  export PYTHON_CMD
  return 0 2>/dev/null || exit 0
fi

# Execution mode: find Python and run the provided script
SCRIPT="$1"
shift

if [ -z "$SCRIPT" ]; then
  echo "Usage: find-python.sh <script.py> [args...]" >&2
  exit 1
fi

if [ -x "$PROJECT_DIR/.venv/bin/python" ]; then
  exec "$PROJECT_DIR/.venv/bin/python" "$SCRIPT" "$@"
elif command -v python3 >/dev/null 2>&1; then
  exec python3 "$SCRIPT" "$@"
elif command -v python >/dev/null 2>&1; then
  exec python "$SCRIPT" "$@"
else
  echo "ERROR: No Python interpreter found. Install Python 3.11+ or create .venv." >&2
  echo "Hook script '$SCRIPT' could not run." >&2
  exit 1
fi
