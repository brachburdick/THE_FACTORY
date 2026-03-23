#!/bin/bash
# Stop hook: Write session state snapshot for cross-session continuity.
# Addresses mining finding #1: 10% ramp-up tax + 1500 wasted tool calls.
# The snapshot is read at next session start to skip re-exploration.

set -e

INPUT=$(cat)
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id')
CWD=$(echo "$INPUT" | jq -r '.cwd')

# Determine project root (look for CLAUDE.md or .agent/)
PROJECT_ROOT="$CWD"
while [ "$PROJECT_ROOT" != "/" ]; do
  if [ -f "$PROJECT_ROOT/CLAUDE.md" ] || [ -d "$PROJECT_ROOT/.agent" ]; then
    break
  fi
  PROJECT_ROOT=$(dirname "$PROJECT_ROOT")
done

if [ "$PROJECT_ROOT" = "/" ]; then
  exit 0  # Not in a project, skip
fi

SNAPSHOT_FILE="$PROJECT_ROOT/.agent/state-snapshot.json"
mkdir -p "$(dirname "$SNAPSHOT_FILE")"

# Gather state
BRANCH=$(git -C "$PROJECT_ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
LAST_COMMIT=$(git -C "$PROJECT_ROOT" log -1 --format='%H %s' 2>/dev/null || echo "unknown")
MODIFIED_FILES=$(git -C "$PROJECT_ROOT" diff --name-only HEAD 2>/dev/null | head -20 | jq -R . | jq -s .)
STAGED_FILES=$(git -C "$PROJECT_ROOT" diff --cached --name-only 2>/dev/null | head -20 | jq -R . | jq -s .)

# Read active tasks from tasks.jsonl if it exists
ACTIVE_TASKS="[]"
if [ -f "$PROJECT_ROOT/.agent/tasks.jsonl" ]; then
  ACTIVE_TASKS=$(grep -v '"status":"complete"' "$PROJECT_ROOT/.agent/tasks.jsonl" 2>/dev/null | jq -s '[.[] | {id, status, taskType, summary}]' 2>/dev/null || echo "[]")
fi

# Write snapshot
cat > "$SNAPSHOT_FILE" << SNAPSHOT
{
  "session_id": "$SESSION_ID",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "project_root": "$PROJECT_ROOT",
  "branch": "$BRANCH",
  "last_commit": $(echo "$LAST_COMMIT" | jq -R .),
  "modified_files": $MODIFIED_FILES,
  "staged_files": $STAGED_FILES,
  "active_tasks": $ACTIVE_TASKS,
  "working_directory": "$CWD"
}
SNAPSHOT

exit 0
