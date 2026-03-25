#!/bin/bash
# PreToolUse hook (Edit, Write): Blocks source mutations when the active task
# references a plan file that was never read (i.e. doesn't exist).
#
# How it works:
#   1. Reads .agent/tasks.jsonl for the current in_progress task
#   2. If the task description contains a .claude/plans/*.md path, extracts it
#   3. Checks if that file exists on disk
#   4. If missing → blocks the Edit/Write with an actionable message
#
# This prevents the known failure mode where an agent is handed a task that
# references a plan doc, the plan doesn't exist, and the agent proceeds to
# write code without stopping to ask.
#
# Only fires on source file edits (same skip rules as fix-attempt-tracker).

set -e

INPUT=$(cat)

# Parse tool input
PARSED=$(python3 -c "
import json, sys
try:
    d = json.loads(sys.stdin.read())
    tool = d.get('tool_name', '')
    fp = d.get('tool_input', {}).get('file_path', '')
    print(tool)
    print(fp)
except Exception:
    print('')
    print('')
" <<< "$INPUT" 2>/dev/null)

TOOL_NAME=$(echo "$PARSED" | sed -n '1p')
FILE_PATH=$(echo "$PARSED" | sed -n '2p')

# Only gate Edit/Write
if [ "$TOOL_NAME" != "Edit" ] && [ "$TOOL_NAME" != "Write" ]; then
  exit 0
fi

# Skip non-source files (config, docs, incidents, tasks, etc.)
if echo "$FILE_PATH" | grep -qE '\.(md|json|jsonl|yaml|yml|toml|txt|sh|gitignore)$'; then
  exit 0
fi

# Skip test files
if echo "$FILE_PATH" | grep -qE '(test_|_test\.|/tests/|/evals/|\.test\.|spec\.)'; then
  exit 0
fi

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"

# Tasks file lives in the working directory (project root), not necessarily
# CLAUDE_PROJECT_DIR (which is the factory root for portfolio-level hooks).
# Search CWD first, then PROJECT_DIR.
TASKS_FILE=""
if [ -f ".agent/tasks.jsonl" ]; then
  TASKS_FILE=".agent/tasks.jsonl"
elif [ -f "$PROJECT_DIR/.agent/tasks.jsonl" ]; then
  TASKS_FILE="$PROJECT_DIR/.agent/tasks.jsonl"
fi

# No tasks file → nothing to gate
if [ -z "$TASKS_FILE" ] || [ ! -f "$TASKS_FILE" ]; then
  exit 0
fi

# Find in_progress task and extract any plan file reference
PLAN_PATH=$(python3 -c "
import json, re, sys

tasks_file = sys.argv[1]
plan_pattern = re.compile(r'\.claude/plans/[A-Za-z0-9_-]+\.md')

with open(tasks_file) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            task = json.loads(line)
        except json.JSONDecodeError:
            continue
        if task.get('status') != 'in_progress':
            continue
        # Search all text fields for plan file references
        text = ' '.join([
            task.get('summary', ''),
            task.get('description', ''),
            task.get('context', ''),
            task.get('prompt', ''),
        ])
        match = plan_pattern.search(text)
        if match:
            print(match.group(0))
            sys.exit(0)

# No in_progress task with a plan reference
print('')
" "$TASKS_FILE" 2>/dev/null)

# No plan reference in active task → allow
if [ -z "$PLAN_PATH" ]; then
  exit 0
fi

FULL_PLAN_PATH="$PROJECT_DIR/$PLAN_PATH"

# Plan file exists → allow
if [ -f "$FULL_PLAN_PATH" ]; then
  exit 0
fi

# Plan file missing → block
echo "BLOCKED: Active task references plan file that does not exist." >&2
echo "" >&2
echo "  Referenced: $PLAN_PATH" >&2
echo "  Full path:  $FULL_PLAN_PATH" >&2
echo "" >&2
echo "The task was dispatched with a plan file reference, but the plan" >&2
echo "was never created. Do NOT proceed without the plan." >&2
echo "" >&2
echo "Either:" >&2
echo "  1. Ask the operator to create the plan first" >&2
echo "  2. Use EnterPlanMode to draft a plan at that path" >&2
echo "  3. Ask the operator to update the task to remove the plan reference" >&2
exit 2
