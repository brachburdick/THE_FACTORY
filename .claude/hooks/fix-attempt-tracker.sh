#!/bin/bash
# PreToolUse hook (Edit, Write, Bash): Track source mutations with three safety layers.
#
# Layer 1 — Fix-attempt cap (inner loop):
#   2 consecutive source mutations without a test run → block.
#   Resets when tests are run.
#
# Layer 2 — Compound error budget (middle loop, tf-026):
#   Total source mutations this phase, regardless of test resets.
#   Universal budget: 10 mutations (simplified from per-risk tiers).
#   When budget is exhausted → block with checkpoint message.
#   Resets on: budget-reset Bash command, or state file deletion.
#
# Layer 3 — Circuit breaker (tf-050):
#   Regression/spiral signal: test_cycles tracks edit-test cycles.
#     Universal threshold: 4 cycles → halt.
#   Drift signal: tracks unique files modified.
#     Universal threshold: 10 files → halt.
#
# State file format (4 lines):
#   Line 1: mutations_since_test (fix-attempt counter)
#   Line 2: total_mutations (compound budget counter)
#   Line 3: test_cycles (number of test-reset cycles)
#   Line 4: modified_files (comma-separated unique file paths)
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

# ── Helper: read state file (4 lines) ──
read_state() {
  if [ -f "$STATE_FILE" ]; then
    FIX_COUNT=$(sed -n '1p' "$STATE_FILE" 2>/dev/null || echo "0")
    TOTAL_COUNT=$(sed -n '2p' "$STATE_FILE" 2>/dev/null || echo "0")
    TEST_CYCLES=$(sed -n '3p' "$STATE_FILE" 2>/dev/null || echo "0")
    MODIFIED_FILES=$(sed -n '4p' "$STATE_FILE" 2>/dev/null || echo "")
  else
    FIX_COUNT=0
    TOTAL_COUNT=0
    TEST_CYCLES=0
    MODIFIED_FILES=""
  fi
  FIX_COUNT=${FIX_COUNT:-0}
  TOTAL_COUNT=${TOTAL_COUNT:-0}
  TEST_CYCLES=${TEST_CYCLES:-0}
  MODIFIED_FILES=${MODIFIED_FILES:-}
}

# ── Helper: write state file ──
write_state() {
  printf '%s\n%s\n%s\n%s\n' "$FIX_COUNT" "$TOTAL_COUNT" "$TEST_CYCLES" "$MODIFIED_FILES" > "$STATE_FILE"
}

# ── Helper: count unique files ──
count_files() {
  if [ -z "$MODIFIED_FILES" ]; then
    echo 0
  else
    echo "$MODIFIED_FILES" | tr ',' '\n' | sort -u | wc -l | tr -d ' '
  fi
}

# ── Helper: add file to modified set (repo-relative paths for accurate drift) ──
add_file() {
  local fp="$1"
  # Use repo-relative path for accurate drift tracking (basename collisions are real)
  local rel_path
  local project_dir="${CLAUDE_PROJECT_DIR:-.}"
  rel_path=$(python3 -c "
import os, sys
fp = sys.argv[1]
root = sys.argv[2]
try:
    print(os.path.relpath(fp, root))
except ValueError:
    print(os.path.basename(fp))
" "$fp" "$project_dir" 2>/dev/null)
  rel_path="${rel_path:-$(basename "$fp")}"
  if [ -z "$MODIFIED_FILES" ]; then
    MODIFIED_FILES="$rel_path"
  elif ! echo ",$MODIFIED_FILES," | grep -qF ",$rel_path,"; then
    MODIFIED_FILES="$MODIFIED_FILES,$rel_path"
  fi
}

# ── Universal thresholds (simplified from per-risk tiers) ──
BUDGET_LIMIT=10
CYCLE_LIMIT=4
DRIFT_LIMIT=10

# ── Bash: handle resets ──
if [ "$TOOL_NAME" = "Bash" ]; then
  # Budget reset: explicit operator checkpoint (resets everything)
  if echo "$COMMAND" | grep -qE 'budget-reset'; then
    read_state
    TOTAL_COUNT=0
    FIX_COUNT=0
    TEST_CYCLES=0
    MODIFIED_FILES=""
    write_state
    exit 0
  fi
  # Test run: reset fix-attempt counter, increment test cycle
  if echo "$COMMAND" | grep -qE '(pytest|py\.test|npm test|npm run test|npx jest|npx vitest|cargo test|go test|\.venv/bin/python -m pytest)'; then
    read_state
    # Only count as a cycle if there were mutations since last test
    if [ "$FIX_COUNT" -gt 0 ]; then
      TEST_CYCLES=$((TEST_CYCLES + 1))
    fi
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

# Read and increment counters, track file
read_state
FIX_COUNT=$((FIX_COUNT + 1))
TOTAL_COUNT=$((TOTAL_COUNT + 1))
add_file "$FILE_PATH"
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
  python3 "$HOOK_DIR/log-incident.py" --category blocked --severity medium \
    --hook fix-attempt-tracker --summary "Fix-attempt cap: $FIX_COUNT consecutive mutations without tests" 2>/dev/null || true
  exit 2
fi

# ── Check compound error budget (middle loop: total mutations this phase) ──
if [ "$TOTAL_COUNT" -gt "$BUDGET_LIMIT" ]; then
  echo "BUDGET EXHAUSTED: $TOTAL_COUNT total source mutations (budget: $BUDGET_LIMIT)." >&2
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
  python3 "$HOOK_DIR/log-incident.py" --category blocked --severity medium \
    --hook fix-attempt-tracker --summary "Budget exhausted: $TOTAL_COUNT mutations (limit $BUDGET_LIMIT)" 2>/dev/null || true
  exit 2
fi

# ── Circuit breaker: regression/spiral signal ──
if [ "$TEST_CYCLES" -ge "$CYCLE_LIMIT" ]; then
  echo "CIRCUIT BREAKER: Edit-test spiral detected ($TEST_CYCLES cycles, limit: $CYCLE_LIMIT)." >&2
  echo "" >&2
  echo "You have gone through $TEST_CYCLES edit→test cycles without completing the task." >&2
  echo "This pattern indicates the current approach may not be converging." >&2
  echo "" >&2
  echo "STOP and:" >&2
  echo "  1. Re-read the failing test output carefully" >&2
  echo "  2. Re-diagnose the root cause — the fix may be targeting the wrong layer" >&2
  echo "  3. Escalate to the operator if the root cause is unclear" >&2
  echo "" >&2
  echo "To reset after re-evaluation: run 'echo budget-reset' via Bash" >&2
  python3 "$HOOK_DIR/log-incident.py" --category blocked --severity high \
    --hook fix-attempt-tracker --summary "Circuit breaker: edit-test spiral ($TEST_CYCLES cycles, limit $CYCLE_LIMIT)" 2>/dev/null || true
  exit 2
fi

# ── Circuit breaker: drift signal (too many files modified) ──
FILE_COUNT=$(count_files)
if [ "$FILE_COUNT" -gt "$DRIFT_LIMIT" ]; then
  echo "CIRCUIT BREAKER: Scope drift detected ($FILE_COUNT unique files modified, limit: $DRIFT_LIMIT)." >&2
  echo "" >&2
  echo "Modified files: $MODIFIED_FILES" >&2
  echo "" >&2
  echo "Modifying this many files suggests the task scope has expanded beyond" >&2
  echo "the original plan. Either the plan was underspecified or the approach" >&2
  echo "has drifted." >&2
  echo "" >&2
  echo "STOP and:" >&2
  echo "  1. Compare modified files to the original plan" >&2
  echo "  2. Split remaining work into separate tasks if scope has grown" >&2
  echo "  3. Get operator approval to continue at expanded scope" >&2
  echo "" >&2
  echo "To reset after operator approval: run 'echo budget-reset' via Bash" >&2
  python3 "$HOOK_DIR/log-incident.py" --category scope_creep --severity medium \
    --hook fix-attempt-tracker --summary "Drift: $FILE_COUNT files modified (limit $DRIFT_LIMIT)" 2>/dev/null || true
  exit 2
fi

exit 0
