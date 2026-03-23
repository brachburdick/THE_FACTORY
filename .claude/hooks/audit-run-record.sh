#!/bin/bash
# Stop hook: Check if a run record was written this session.
# Warns (non-blocking) if task work happened but no run record was appended.
# No jq dependency — uses python3 for JSON parsing.

set -e

INPUT=$(cat)

# Parse CWD via python3 (no jq dependency)
CWD=$(python3 -c "
import json, sys
try:
    d = json.loads(sys.stdin.read())
    print(d.get('cwd', ''))
except Exception:
    print('')
" <<< "$INPUT" 2>/dev/null)

# Fallback if parsing failed
if [ -z "$CWD" ]; then
  CWD=$(pwd)
fi

# Find project root
PROJECT_ROOT="$CWD"
while [ "$PROJECT_ROOT" != "/" ]; do
  if [ -f "$PROJECT_ROOT/CLAUDE.md" ] || [ -d "$PROJECT_ROOT/.agent" ]; then
    break
  fi
  PROJECT_ROOT=$(dirname "$PROJECT_ROOT")
done

[ "$PROJECT_ROOT" = "/" ] && exit 0

RUNS_FILE="$PROJECT_ROOT/.agent/runs.jsonl"
TASKS_FILE="$PROJECT_ROOT/.agent/tasks.jsonl"

# If no tasks file, nothing to check
[ ! -f "$TASKS_FILE" ] && exit 0

# Check if runs.jsonl was modified in last 2 hours (proxy for "this session")
if [ -f "$RUNS_FILE" ] && [ -s "$RUNS_FILE" ]; then
  if find "$RUNS_FILE" -mmin -120 2>/dev/null | grep -q .; then
    exit 0
  fi
fi

# Non-blocking warning (exit 0, just print to stderr)
echo "NOTE: No run record written this session. If you completed a task, append to .agent/runs.jsonl" >&2
exit 0
