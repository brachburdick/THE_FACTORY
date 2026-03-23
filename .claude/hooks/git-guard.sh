#!/bin/bash
# PreToolUse hook (Bash matcher): Enforce git branch rules.
# Blocks: commits/pushes to main, force-push, reset --hard.
# Allows: everything else passes through.

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name')
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Only check Bash commands
if [ "$TOOL_NAME" != "Bash" ]; then
  exit 0
fi

# Skip if not a git command
if ! echo "$COMMAND" | grep -q "git "; then
  exit 0
fi

# Block: direct commits to main
if echo "$COMMAND" | grep -qE "git (commit|merge)"; then
  BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
  if [ "$BRANCH" = "main" ] || [ "$BRANCH" = "master" ]; then
    echo "BLOCKED: Cannot commit/merge directly to $BRANCH. Create a branch first: git checkout -b {type}/{task-id}-{slug}" >&2
    exit 2
  fi
fi

# Block: push to main
if echo "$COMMAND" | grep -qE "git push.*(main|master)"; then
  echo "BLOCKED: Cannot push directly to main/master. Push your feature branch instead." >&2
  exit 2
fi

# Block: force-push
if echo "$COMMAND" | grep -qE "git push.*(-f|--force)"; then
  echo "BLOCKED: Force-push is not allowed. Make a new commit to fix issues." >&2
  exit 2
fi

# Block: destructive operations
if echo "$COMMAND" | grep -qE "git reset --hard"; then
  echo "BLOCKED: git reset --hard is destructive. Use git stash or git revert instead." >&2
  exit 2
fi

exit 0
