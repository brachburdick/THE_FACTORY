#!/bin/bash
# PreToolUse hook (Edit, Write, Bash): Track source mutations with two caps.
#
# Cap 1 — Fix-attempt cap (inner loop):
#   2 consecutive source mutations without a test run → block.
#   Resets when tests are run.
#
# Cap 2 — Compound error budget (middle loop, tf-026):
#   Total source mutations this phase, regardless of test resets.
#   Budget depends on task risk level (reads from tasks.jsonl):
#     low    → 15 mutations
#     medium → 7 mutations
#     high   → 4 mutations
#   When budget is exhausted → block with checkpoint message.
#   Resets on: budget-reset Bash command, or state file deletion.
#
# Behavior:
#   Edit/Write to source file → increment both counters
#   Edit/Write to test/doc/config file → ignore
#   Bash running tests → reset fix-attempt counter (not budget)
#   Bash with "budget-reset" → reset budget counter
#   Fix-attempt > 2 → block (exit 2)
#   Budget > threshold → block (exit 2)
#
# State file format (2 lines):
#   Line 1: mutations_since_test (fix-attempt counter)
#   Line 2: total_mutations (compound budget counter)
#
# No jq dependency — uses python3 for JSON parsing.

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

# ── Helper: read state file (2 lines) ──
read_state() {
  if [ -f "$STATE_FILE" ]; then
    FIX_COUNT=$(sed -n '1p' "$STATE_FILE" 2>/dev/null || echo "0")
    TOTAL_COUNT=$(sed -n '2p' "$STATE_FILE" 2>/dev/null || echo "0")
  else
    FIX_COUNT=0
    TOTAL_COUNT=0
  fi
  FIX_COUNT=${FIX_COUNT:-0}
  TOTAL_COUNT=${TOTAL_COUNT:-0}
}

# ── Helper: write state file ──
write_state() {
  printf '%s\n%s\n' "$FIX_COUNT" "$TOTAL_COUNT" > "$STATE_FILE"
}

# ── Helper: get risk level from tasks.jsonl ──
get_risk() {
  local tasks_file=""
  local project_dir="${CLAUDE_PROJECT_DIR:-.}"
  if [ -f ".agent/tasks.jsonl" ]; then
    tasks_file=".agent/tasks.jsonl"
  elif [ -f "$project_dir/.agent/tasks.jsonl" ]; then
    tasks_file="$project_dir/.agent/tasks.jsonl"
  fi
  if [ -z "$tasks_file" ] || [ ! -f "$tasks_file" ]; then
    echo "medium"
    return
  fi
  python3 -c "
import json, re, sys

HIGH_KW = re.compile(r'(security|migration|schema|auth|credentials|cross-section|destructive|irreversible)', re.I)
LOW_KW = re.compile(r'^(test|doc|config|lint|typo|frontmatter|license|readme)', re.I)

with open(sys.argv[1]) as f:
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
        risk = task.get('risk')
        if risk in ('low', 'medium', 'high'):
            print(risk)
            sys.exit(0)
        text = task.get('summary', '') + ' ' + task.get('description', '')
        task_type = task.get('taskType', '')
        if HIGH_KW.search(text):
            print('high')
            sys.exit(0)
        if LOW_KW.match(task_type) or LOW_KW.match(text.strip()):
            print('low')
            sys.exit(0)
        print('medium')
        sys.exit(0)
print('medium')
" "$tasks_file" 2>/dev/null
}

# ── Helper: budget threshold for risk level ──
get_budget() {
  case "$1" in
    low)    echo 15 ;;
    high)   echo 4 ;;
    *)      echo 7 ;;
  esac
}

# ── Bash: handle resets ──
if [ "$TOOL_NAME" = "Bash" ]; then
  # Budget reset: explicit operator checkpoint
  if echo "$COMMAND" | grep -qE 'budget-reset'; then
    read_state
    TOTAL_COUNT=0
    FIX_COUNT=0
    write_state
    exit 0
  fi
  # Test run: reset fix-attempt counter only (not budget)
  if echo "$COMMAND" | grep -qE '(pytest|py\.test|npm test|npm run test|npx jest|npx vitest|cargo test|go test|\.venv/bin/python -m pytest)'; then
    read_state
    FIX_COUNT=0
    write_state
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

# Read and increment both counters
read_state
FIX_COUNT=$((FIX_COUNT + 1))
TOTAL_COUNT=$((TOTAL_COUNT + 1))
write_state

# ── Check fix-attempt cap (inner loop: 2 consecutive without tests) ──
if [ "$FIX_COUNT" -gt 2 ]; then
  echo "BLOCKED: $FIX_COUNT consecutive source mutations without running tests." >&2
  echo "" >&2
  echo "The debug-flow caps fix attempts at 2 before requiring verification." >&2
  echo "Either:" >&2
  echo "  1. Run your test suite to verify progress (resets counter)" >&2
  echo "  2. Escalate to the operator with a diagnostic summary" >&2
  echo "" >&2
  echo "To reset: run tests via Bash (pytest, npm test, etc.)" >&2
  exit 2
fi

# ── Check compound error budget (middle loop: total mutations this phase) ──
RISK=$(get_risk)
BUDGET=$(get_budget "$RISK")

if [ "$TOTAL_COUNT" -gt "$BUDGET" ]; then
  echo "BUDGET EXHAUSTED: $TOTAL_COUNT total source mutations (budget: $BUDGET for $RISK-risk task)." >&2
  echo "" >&2
  echo "The compound error budget tracks all source mutations this phase," >&2
  echo "including those between test runs. This prevents edit-test spirals" >&2
  echo "that pass individual gates but accumulate drift." >&2
  echo "" >&2
  echo "Either:" >&2
  echo "  1. Checkpoint with the operator: explain progress and get approval to continue" >&2
  echo "  2. Re-evaluate approach: if you've exceeded budget, the approach may need rethinking" >&2
  echo "" >&2
  echo "To reset after operator approval: run 'echo budget-reset' via Bash" >&2
  exit 2
fi

exit 0
