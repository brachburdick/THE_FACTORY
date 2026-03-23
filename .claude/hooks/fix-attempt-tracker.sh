#!/bin/bash
# PreToolUse hook (Edit): Track sequential source file edits without test runs.
# After 3 edits to source files without an intervening test run, blocks with
# escalation message. Implements the debug-flow 3-attempt cap as enforcement.
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
    print(d.get('tool_name', ''))
    print(d.get('tool_input', {}).get('file_path', ''))
except Exception:
    print('')
    print('')
" <<< "$INPUT" 2>/dev/null)

TOOL_NAME=$(echo "$PARSED" | head -1)
FILE_PATH=$(echo "$PARSED" | tail -n +2)

# Only track Edit tool calls
if [ "$TOOL_NAME" != "Edit" ]; then
  exit 0
fi

# Skip test files — edits to tests don't count as fix attempts
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
if [ "$COUNT" -gt 3 ]; then
  echo "BLOCKED: $COUNT consecutive source edits without running tests." >&2
  echo "" >&2
  echo "The debug-flow caps fix attempts at 3 before escalation." >&2
  echo "Either:" >&2
  echo "  1. Run your test suite to verify progress (resets counter)" >&2
  echo "  2. Escalate to the operator with a diagnostic summary" >&2
  echo "" >&2
  echo "To reset: run tests via Bash (pytest, npm test, etc.)" >&2
  exit 2
fi

exit 0
