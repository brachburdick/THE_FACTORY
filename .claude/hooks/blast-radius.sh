#!/bin/bash
# PreToolUse hook (Edit, Write): Blast radius scope check (tf-025).
#
# Cross-references Edit/Write paths against the active task's section contract
# owned_paths. Blocks out-of-scope mutations when a section is assigned.
#
# Requirements:
#   - Active task in tasks.jsonl has 'section' field (e.g., "bridge")
#   - Active task has 'project' field (e.g., "DjTools/scue")
#   - Section contract exists at projects/{project}/sections/{section}.md
#   - Contract has an "Owned Paths" code block listing owned directories
#
# Behavior:
#   - No active task → allow (no enforcement possible)
#   - No section field → allow (pre-flight should have caught this)
#   - Section assigned + file in owned paths → allow
#   - Section assigned + file outside owned paths → block (exit 2)
#   - Section contract not found → warn to stderr, allow
#
# Exit codes:
#   0 — allow
#   2 — block (file outside section scope)

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

# Skip non-source files (config, docs within THE_FACTORY itself)
if echo "$FILE_PATH" | grep -qE '\.(md|json|jsonl|yaml|yml|toml|txt|sh|gitignore)$'; then
  exit 0
fi

# Skip test files
if echo "$FILE_PATH" | grep -qE '(test_|_test\.|/tests/|/evals/|\.test\.|spec\.)'; then
  exit 0
fi

HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"

# Get active task via canonical reader, then check blast radius
python3 -c "
import json, os, sys

hook_dir = sys.argv[1]
file_path = sys.argv[2]
project_dir = sys.argv[3]

# Import canonical reader
sys.path.insert(0, hook_dir)
from importlib.machinery import SourceFileLoader
reader = SourceFileLoader('task_reader', os.path.join(hook_dir, 'task-reader.py')).load_module()

tasks_path = reader.find_tasks_file()
if not tasks_path:
    sys.exit(0)

task = reader.get_active_task(tasks_path)
if not task:
    sys.exit(0)

section = task.get('section')
project = task.get('project')

if not section or not project:
    sys.exit(0)

# Find section contract
contract_path = os.path.join(project_dir, 'projects', project, 'sections', f'{section}.md')
if not os.path.exists(contract_path):
    print(f'WARNING: Section contract not found: {contract_path}', file=sys.stderr)
    sys.exit(0)

# Parse owned paths from contract
owned_paths = []
in_owned = False
with open(contract_path) as f:
    for line in f:
        if line.strip().startswith('## Owned Paths'):
            in_owned = True
            continue
        if in_owned and line.strip().startswith('## '):
            break
        if in_owned and line.strip().startswith('\`\`\`'):
            continue
        if in_owned and line.strip():
            owned_paths.append(line.strip())

if not owned_paths:
    sys.exit(0)

# Check if file_path falls within any owned path
project_root = os.path.join(project_dir, 'projects', project)
try:
    rel_path = os.path.relpath(file_path, project_root)
except ValueError:
    rel_path = file_path

for owned in owned_paths:
    owned = owned.rstrip('/')
    if rel_path.startswith(owned) or rel_path == owned:
        sys.exit(0)

# File is outside all owned paths — block
print(f'BLOCKED: File outside section scope.', file=sys.stderr)
print(f'', file=sys.stderr)
print(f'  File:    {rel_path}', file=sys.stderr)
print(f'  Section: {section}', file=sys.stderr)
print(f'  Owned:   {owned_paths}', file=sys.stderr)
print(f'', file=sys.stderr)
print(f'Either:', file=sys.stderr)
print(f'  1. Update the task\\'s section field to include this area', file=sys.stderr)
print(f'  2. File a separate task for out-of-scope changes', file=sys.stderr)
print(f'  3. Ask the operator to expand the scope', file=sys.stderr)
sys.exit(2)
" "$HOOK_DIR" "$FILE_PATH" "$PROJECT_DIR" || PYTHON_EXIT=$?
PYTHON_EXIT=${PYTHON_EXIT:-0}
if [ "$PYTHON_EXIT" -eq 2 ]; then
  python3 "$HOOK_DIR/log-incident.py" --category scope_creep --severity medium \
    --hook blast-radius --summary "Out-of-scope file edit blocked: $FILE_PATH" 2>/dev/null || true
  exit 2
fi
