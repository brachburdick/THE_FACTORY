#!/bin/bash
# PreToolUse hook (Edit, Write): Enforces risk-tiered autonomy controls.
#
# Reads the active task's risk level from tasks.jsonl. For high-risk tasks,
# blocks source mutations unless a plan file exists (approved plan = go-ahead).
# For low-risk tasks, skips plan-gate entirely.
#
# Risk levels:
#   low    — auto-approve, post-hoc review only (tests, docs, config, lint)
#   medium — default behavior (plan-gate, 2-attempt cap)
#   high   — require approved plan for ANY source mutation
#
# Risk is set explicitly on the task, or inferred from signals:
#   - "security", "migration", "schema", "auth", "credentials" → high
#   - cross-section (multiple section paths in summary) → high
#   - "test", "doc", "config", "lint", "typo" → low
#   - everything else → medium
#
# Exit codes:
#   0 — allow
#   2 — block (high-risk without approved plan)

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

# Skip non-source files (config, docs, etc.)
if echo "$FILE_PATH" | grep -qE '\.(md|json|jsonl|yaml|yml|toml|txt|sh|gitignore)$'; then
  exit 0
fi

# Skip test files
if echo "$FILE_PATH" | grep -qE '(test_|_test\.|/tests/|/evals/|\.test\.|spec\.)'; then
  exit 0
fi

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"

# Find tasks file
TASKS_FILE=""
if [ -f ".agent/tasks.jsonl" ]; then
  TASKS_FILE=".agent/tasks.jsonl"
elif [ -f "$PROJECT_DIR/.agent/tasks.jsonl" ]; then
  TASKS_FILE="$PROJECT_DIR/.agent/tasks.jsonl"
fi

# No tasks file → default to medium (allow)
if [ -z "$TASKS_FILE" ] || [ ! -f "$TASKS_FILE" ]; then
  exit 0
fi

# Determine risk level of active task
RISK=$(python3 -c "
import json, re, sys

HIGH_KEYWORDS = re.compile(r'(security|migration|schema|auth|credentials|cross-section|destructive|irreversible)', re.I)
LOW_KEYWORDS = re.compile(r'^(test|doc|config|lint|typo|frontmatter|license|readme)', re.I)

tasks_file = sys.argv[1]

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

        # Explicit risk field takes precedence
        risk = task.get('risk')
        if risk in ('low', 'medium', 'high'):
            print(risk)
            sys.exit(0)

        # Infer from task content
        text = task.get('summary', '') + ' ' + task.get('description', '')
        task_type = task.get('taskType', '')

        if HIGH_KEYWORDS.search(text):
            print('high')
            sys.exit(0)
        if LOW_KEYWORDS.match(task_type) or LOW_KEYWORDS.match(text.strip()):
            print('low')
            sys.exit(0)

        print('medium')
        sys.exit(0)

# No in_progress task → medium
print('medium')
" "$TASKS_FILE" 2>/dev/null)

# Low risk → always allow (skip plan-gate too)
if [ "$RISK" = "low" ]; then
  exit 0
fi

# Medium risk → allow (plan-gate and fix-attempt-tracker handle enforcement)
if [ "$RISK" = "medium" ]; then
  exit 0
fi

# High risk → require approved plan
# Check if any .claude/plans/*.md exists for the active task
HAS_PLAN=$(python3 -c "
import json, re, sys, os

tasks_file = sys.argv[1]
project_dir = sys.argv[2]
plan_pattern = re.compile(r'\.claude/plans/[A-Za-z0-9_/-]+\.md')

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
        text = ' '.join([
            task.get('summary', ''),
            task.get('description', ''),
            task.get('context', ''),
        ])
        match = plan_pattern.search(text)
        if match:
            plan_path = os.path.join(project_dir, match.group(0))
            if os.path.exists(plan_path):
                print('yes')
                sys.exit(0)
        # Also check if a plan with the task ID exists
        task_id = task.get('id', '')
        if task_id:
            for name in os.listdir(os.path.join(project_dir, '.claude', 'plans')):
                if task_id in name and name.endswith('.md'):
                    print('yes')
                    sys.exit(0)
        break

print('no')
" "$TASKS_FILE" "$PROJECT_DIR" 2>/dev/null)

if [ "$HAS_PLAN" = "yes" ]; then
  exit 0
fi

echo "BLOCKED: High-risk task requires an approved plan before source mutations." >&2
echo "" >&2
echo "  Risk level: HIGH (inferred or explicit)" >&2
echo "  High-risk tasks (security, migrations, cross-section changes)" >&2
echo "  require an approved plan file in .claude/plans/ before editing source code." >&2
echo "" >&2
echo "Either:" >&2
echo "  1. Use EnterPlanMode to draft and get approval for a plan" >&2
echo "  2. Ask the operator to set risk: medium on the task if risk was misjudged" >&2
echo "  3. Create a plan file manually at .claude/plans/{task-id}.md" >&2
exit 2
