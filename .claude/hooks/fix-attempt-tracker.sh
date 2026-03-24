#!/bin/bash
# PreToolUse hook (Edit, Write, Bash): Track source mutations without test runs.
# After 2 source mutations without an intervening test run, blocks with
# escalation message. Implements the debug-flow 2-attempt cap as enforcement.
#
# Behavior:
#   Edit/Write to source file → increment counter
#   Edit/Write to test/doc/config file → ignore
#   Bash running tests (pytest, npm test, etc.) → reset counter
#   Counter > 2 → block with exit 2
#
# No jq dependency — uses python3 for JSON parsing.
# State is tracked in a .state file (gitignored).

set -e

HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
STATE_FILE="$HOOK_DIR/fix-attempt-tracker.state"

INPUT=$(cat)

# Parse tool input via python3 (no jq dependency)
PARSED=$(python3 -c "
import json, sys
try:
    d = json.loads(sys.stdin.read())
    tool = d.get('tool_name', '')
    fp = d.get('tool_input', {}).get('file_path', '')
    cmd = d.get('tool_input', {}).get('command', '')
    print(tool)
    print(fp)
    print(cmd)
except Exception:
    print('')
    print('')
    print('')
" <<< "$INPUT" 2>/dev/null)

TOOL_NAME=$(echo "$PARSED" | sed -n '1p')
FILE_PATH=$(echo "$PARSED" | sed -n '2p')
COMMAND=$(echo "$PARSED" | sed -n '3p')

# ── Bash: reset counter on test runs ──
if [ "$TOOL_NAME" = "Bash" ]; then
  if echo "$COMMAND" | grep -qE '(pytest|py\.test|npm test|npm run test|npx jest|npx vitest|cargo test|go test|\.venv/bin/python -m pytest)'; then
    echo "0" > "$STATE_FILE"
  fi
  exit 0
fi

# ── Edit/Write: track source mutations ──
if [ "$TOOL_NAME" != "Edit" ] && [ "$TOOL_NAME" != "Write" ]; then
  exit 0
fi

# Skip test files — mutations to tests don't count as fix attempts
if echo "$FILE_PATH" | grep -qE '(test_|_test\.|/tests/|/evals/|\.test\.|spec\.)'; then
  exit 0
fi

# Skip non-source files (config, docs, etc.)
if echo "$FILE_PATH" | grep -qE '\.(md|json|jsonl|yaml|yml|toml|txt|sh|gitignore)$'; then
  exit 0
fi

# Initialize state file if missing
if [ ! -f "$STATE_FILE" ]; then
  echo "0" > "$STATE_FILE"
fi

# Read current count
COUNT=$(head -1 "$STATE_FILE" 2>/dev/null || echo "0")
COUNT=${COUNT:-0}

# Increment
COUNT=$((COUNT + 1))

# Write updated state
echo "$COUNT" > "$STATE_FILE"

# Check threshold
if [ "$COUNT" -gt 2 ]; then
  echo "BLOCKED: $COUNT consecutive source mutations without running tests." >&2
  echo "" >&2
  echo "The debug-flow caps fix attempts at 2 before requiring verification." >&2
  echo "Either:" >&2
  echo "  1. Run your test suite to verify progress (resets counter)" >&2
  echo "  2. Escalate to the operator with a diagnostic summary" >&2
  echo "" >&2
  echo "To reset: run tests via Bash (pytest, npm test, etc.)" >&2
  exit 2
fi

exit 0
