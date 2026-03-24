#!/bin/bash
# Stop hook: Check that every completed task has a matching run record.
# Warns (non-blocking) if a completed task in tasks.jsonl lacks a corresponding
# entry in runs.jsonl. No jq dependency — uses python3 for JSON parsing.

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

# Use python3 to cross-reference completed tasks against run records
python3 -c "
import json, sys

tasks_file = '$TASKS_FILE'
runs_file = '$RUNS_FILE'

# Load completed task IDs
completed = set()
try:
    with open(tasks_file) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                task = json.loads(line)
                if task.get('status') == 'complete':
                    tid = task.get('id', '')
                    if tid:
                        completed.add(tid)
            except json.JSONDecodeError:
                continue
except FileNotFoundError:
    sys.exit(0)

if not completed:
    sys.exit(0)

# Load run record task IDs and check for summary field
run_task_ids = set()
runs_missing_summary = []
try:
    with open(runs_file) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                run = json.loads(line)
                tid = run.get('task_id', '')
                if tid:
                    run_task_ids.add(tid)
                if not run.get('summary'):
                    runs_missing_summary.append(run.get('run_id', '?'))
            except json.JSONDecodeError:
                continue
except FileNotFoundError:
    pass

# Find completed tasks without run records
orphans = sorted(completed - run_task_ids)
if orphans:
    print(f'WARNING: {len(orphans)} completed task(s) have no run record in runs.jsonl:', file=sys.stderr)
    for tid in orphans:
        print(f'  - {tid}', file=sys.stderr)
    print('Append a run record for each before closing the session.', file=sys.stderr)

if runs_missing_summary:
    print(f'WARNING: {len(runs_missing_summary)} run record(s) missing summary field:', file=sys.stderr)
    for rid in runs_missing_summary:
        print(f'  - {rid}', file=sys.stderr)
" 2>&1 >&2

# Non-blocking (exit 0) — warnings only
exit 0
