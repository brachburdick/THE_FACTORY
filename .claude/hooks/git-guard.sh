#!/bin/bash
# PreToolUse hook (Bash matcher): Enforce git branch rules + reset fix-attempt counter.
# Blocks: commits/pushes to main, force-push, reset --hard.
# Resets: fix-attempt counter when a test command is detected.
# Allows: everything else passes through.
#
# FAIL-CLOSED: If input parsing fails, blocks the command (exit 2).
# No jq dependency — uses python3 for JSON parsing.

INPUT=$(cat)

# Parse JSON fields via python3 (no jq dependency).
# Fail closed: if parsing fails, block the command.
PARSED=$(python3 -c "
import json, sys
try:
    d = json.loads(sys.stdin.read())
    print(d.get('tool_name', ''))
    print(d.get('tool_input', {}).get('command', ''))
except Exception:
    print('__PARSE_ERROR__')
    print('')
" <<< "$INPUT" 2>/dev/null)

TOOL_NAME=$(echo "$PARSED" | head -1)
COMMAND=$(echo "$PARSED" | tail -n +2)

# Fail closed on parse error
if [ "$TOOL_NAME" = "__PARSE_ERROR__" ]; then
  echo "BLOCKED: git-guard could not parse hook input. Failing closed for safety." >&2
  exit 2
fi

# Only check Bash commands
if [ "$TOOL_NAME" != "Bash" ]; then
  exit 0
fi

# Reset fix-attempt counter if running tests
HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
FIX_STATE="$HOOK_DIR/fix-attempt-tracker.state"
if echo "$COMMAND" | grep -qEi '(pytest|npm test|npm run test|cargo test|go test|\.venv/bin/python -m pytest)'; then
  if [ -f "$FIX_STATE" ]; then
    echo "0" > "$FIX_STATE"
  fi
fi

# Skip if not a git command
if ! echo "$COMMAND" | grep -q "git "; then
  exit 0
fi

# Block: direct commits to main
if echo "$COMMAND" | grep -qE "git (commit|merge)"; then
  BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
  if [ "$BRANCH" = "main" ] || [ "$BRANCH" = "master" ]; then
    echo "BLOCKED: Cannot commit/merge directly to $BRANCH. Create a branch first: git checkout -b {type}/{task-id}-{slug}" >&2
    exit 2
  fi
fi

# Block: push to main
if echo "$COMMAND" | grep -qE "git push.*(main|master)"; then
  echo "BLOCKED: Cannot push directly to main/master. Push your feature branch instead." >&2
  exit 2
fi

# Block: force-push
if echo "$COMMAND" | grep -qE "git push.*(-f|--force)"; then
  echo "BLOCKED: Force-push is not allowed. Make a new commit to fix issues." >&2
  exit 2
fi

# Block: destructive operations
if echo "$COMMAND" | grep -qE "git reset --hard"; then
  echo "BLOCKED: git reset --hard is destructive. Use git stash or git revert instead." >&2
  exit 2
fi

exit 0
