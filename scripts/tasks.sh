#!/usr/bin/env bash
# Query the structured task tracker (.agent/tasks.jsonl)
# Usage: scripts/tasks.sh [ready|blocked|in-progress|all] [project-path]
# If project-path is omitted, uses current directory.

set -euo pipefail

FILTER="${1:-all}"
PROJECT="${2:-.}"
TASKS_FILE="$PROJECT/.agent/tasks.jsonl"

if [ ! -f "$TASKS_FILE" ]; then
  echo "No task tracker found at $TASKS_FILE" >&2
  echo "Create one with: echo '{}' >> $TASKS_FILE" >&2
  exit 1
fi

case "$FILTER" in
  ready|pending)
    python3 -c "
import json, sys
for line in open('$TASKS_FILE'):
    line = line.strip()
    if not line: continue
    t = json.loads(line)
    if t.get('status') == 'pending' and not t.get('blockers'):
        print(json.dumps(t))
"
    ;;
  blocked)
    python3 -c "
import json, sys
for line in open('$TASKS_FILE'):
    line = line.strip()
    if not line: continue
    t = json.loads(line)
    if t.get('blockers'):
        print(json.dumps(t))
"
    ;;
  in-progress)
    python3 -c "
import json, sys
for line in open('$TASKS_FILE'):
    line = line.strip()
    if not line: continue
    t = json.loads(line)
    if t.get('status') == 'in-progress':
        print(json.dumps(t))
"
    ;;
  all)
    python3 -c "
import json, sys
for line in open('$TASKS_FILE'):
    line = line.strip()
    if not line: continue
    t = json.loads(line)
    print(f\"{t.get('id','?'):12s} {t.get('status','?'):12s} {t.get('summary','')}\")
"
    ;;
  *)
    echo "Usage: $0 [ready|blocked|in-progress|all] [project-path]" >&2
    exit 1
    ;;
esac
