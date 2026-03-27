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

HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"

# Determine risk level of active task via canonical reader
RISK=$(python3 "$HOOK_DIR/task-reader.py" --active --field risk --infer-risk 2>/dev/null)
RISK="${RISK:-medium}"

# Low risk → always allow (skip plan-gate too)
if [ "$RISK" = "low" ]; then
  exit 0
fi

# Medium risk → allow (plan-gate and fix-attempt-tracker handle enforcement)
if [ "$RISK" = "medium" ]; then
  exit 0
fi

# High risk → require approved plan
# Use canonical reader to get active task ID, then check for plan file
TASK_ID=$(python3 "$HOOK_DIR/task-reader.py" --active --field id 2>/dev/null)
HAS_PLAN="no"
if [ -n "$TASK_ID" ]; then
  # Check if a plan file with the task ID exists in .claude/plans/
  PLANS_DIR="${PROJECT_DIR}/.claude/plans"
  if [ -d "$PLANS_DIR" ]; then
    for plan_file in "$PLANS_DIR"/*.md; do
      [ -f "$plan_file" ] || continue
      case "$(basename "$plan_file")" in
        *"$TASK_ID"*) HAS_PLAN="yes"; break ;;
      esac
    done
  fi
fi

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
python3 "$HOOK_DIR/log-incident.py" --category blocked --severity high \
  --hook risk-classifier --summary "High-risk mutation blocked: no approved plan for task $TASK_ID" 2>/dev/null || true
exit 2
