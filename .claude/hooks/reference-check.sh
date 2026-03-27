#!/bin/bash
# PreToolUse hook (Edit): Advisory check for downstream references before renames.
#
# When an Edit replaces a string, grep evals/ and hooks/ for the old_string.
# If matches are found, WARN (do not block) so the agent knows to update consumers.
#
# Mining finding: rewrite-without-reading-evals was the #1 rework pattern
# across the v2.2→v3.0 sprint (sessions 337dd2da, b8458acc, f1e40ee5).

set -e

INPUT=$(cat)

# Parse tool input
PARSED=$(python3 -c "
import json, sys
try:
    d = json.loads(sys.stdin.read())
    tool = d.get('tool_name', '')
    old = d.get('tool_input', {}).get('old_string', '')
    new = d.get('tool_input', {}).get('new_string', '')
    fp = d.get('tool_input', {}).get('file_path', '')
    print(tool)
    print(old)
    print(new)
    print(fp)
except Exception:
    print('')
    print('')
    print('')
    print('')
" <<< "$INPUT" 2>/dev/null)

TOOL_NAME=$(echo "$PARSED" | sed -n '1p')
OLD_STRING=$(echo "$PARSED" | sed -n '2p')
NEW_STRING=$(echo "$PARSED" | sed -n '3p')
FILE_PATH=$(echo "$PARSED" | sed -n '4p')

# Only applies to Edit tool
if [ "$TOOL_NAME" != "Edit" ]; then
  exit 0
fi

# Skip if old_string is empty or very short (not a meaningful rename)
if [ -z "$OLD_STRING" ] || [ ${#OLD_STRING} -lt 5 ]; then
  exit 0
fi

# Skip if old and new are the same (no rename happening)
if [ "$OLD_STRING" = "$NEW_STRING" ]; then
  exit 0
fi

# Skip if editing an eval or test file (consumer, not producer)
if echo "$FILE_PATH" | grep -qE '(evals/|/tests/|test_|_test\.)'; then
  exit 0
fi

# Extract a short key phrase from old_string (first line, trimmed)
KEY=$(echo "$OLD_STRING" | head -1 | sed 's/^[[:space:]]*//' | cut -c1-60)

# Skip if key is just whitespace or code-like (not a nameable concept)
if [ -z "$KEY" ] || echo "$KEY" | grep -qE '^[[:space:]{}()\[\]<>]+$'; then
  exit 0
fi

# Search for references in evals/ and hooks/
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
REFS=""

if [ -d "$PROJECT_DIR/evals" ]; then
  EVAL_HITS=$(grep -rl "$KEY" "$PROJECT_DIR/evals/" 2>/dev/null | head -5)
  if [ -n "$EVAL_HITS" ]; then
    REFS="$REFS\n  Evals: $(echo "$EVAL_HITS" | xargs -I{} basename {} | tr '\n' ', ' | sed 's/,$//')"
  fi
fi

if [ -d "$PROJECT_DIR/.claude/hooks" ]; then
  HOOK_HITS=$(grep -rl "$KEY" "$PROJECT_DIR/.claude/hooks/" 2>/dev/null | head -5)
  if [ -n "$HOOK_HITS" ]; then
    REFS="$REFS\n  Hooks: $(echo "$HOOK_HITS" | xargs -I{} basename {} | tr '\n' ', ' | sed 's/,$//')"
  fi
fi

# If references found, warn (exit 0 = advisory, not blocking)
if [ -n "$REFS" ]; then
  echo "⚠ REFERENCE CHECK: The string being replaced appears in downstream consumers:" >&2
  echo -e "$REFS" >&2
  echo "" >&2
  echo "Consider updating these files to match the new content." >&2
  echo "This is advisory — the edit will proceed." >&2
fi

exit 0
