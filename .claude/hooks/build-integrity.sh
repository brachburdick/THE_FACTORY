#!/bin/bash
# PreToolUse hook (Edit, Write): Warn on high-risk infrastructure file mutations.
#
# Detects edits to: hooks, CI/CD, packaging, release scripts, settings.
# Does NOT block — issues a warning so the operator is aware.
# The risk-classifier hook handles actual blocking for high-risk tasks.
#
# Exit codes:
#   0 — allow (with optional warning on stderr)

set -e

INPUT=$(cat)

# Parse file path from tool input
FILE_PATH=$(python3 -c "
import json, sys
try:
    d = json.loads(sys.stdin.read())
    print(d.get('tool_input', {}).get('file_path', ''))
except Exception:
    print('')
" <<< "$INPUT" 2>/dev/null)

# No file path → skip
if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# Normalize to relative path
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
REL_PATH="${FILE_PATH#$PROJECT_DIR/}"

# High-risk infrastructure patterns
IS_HIGH_RISK=false
RISK_CATEGORY=""

# Hook scripts
if echo "$REL_PATH" | grep -qE '^\.claude/hooks/'; then
  IS_HIGH_RISK=true
  RISK_CATEGORY="hook script"
fi

# Settings files
if echo "$REL_PATH" | grep -qE '^\.claude/settings(\.local)?\.json$'; then
  IS_HIGH_RISK=true
  RISK_CATEGORY="Claude Code settings"
fi

# CI/CD workflows
if echo "$REL_PATH" | grep -qE '^\.github/(workflows|actions)/'; then
  IS_HIGH_RISK=true
  RISK_CATEGORY="CI/CD workflow"
fi

# Package manifests
if echo "$REL_PATH" | grep -qE '(^|/)((pyproject\.toml|setup\.py|setup\.cfg|Pipfile|requirements.*\.txt)|(package\.json|package-lock\.json|yarn\.lock|pnpm-lock\.yaml))$'; then
  IS_HIGH_RISK=true
  RISK_CATEGORY="package manifest"
fi

# Dockerfiles and compose
if echo "$REL_PATH" | grep -qiE '(^|/)(Dockerfile|docker-compose|\.dockerignore)'; then
  IS_HIGH_RISK=true
  RISK_CATEGORY="container config"
fi

# Release/deploy scripts
if echo "$REL_PATH" | grep -qE '(^|/)(release|deploy|publish|Makefile|Justfile)'; then
  IS_HIGH_RISK=true
  RISK_CATEGORY="build/release script"
fi

# Gitignore (can expose secrets if weakened)
if echo "$REL_PATH" | grep -qE '\.gitignore$'; then
  IS_HIGH_RISK=true
  RISK_CATEGORY="gitignore"
fi

if [ "$IS_HIGH_RISK" = "true" ]; then
  echo "WARNING: Editing $RISK_CATEGORY file: $REL_PATH" >&2
  echo "  Infrastructure files affect the build/deploy pipeline." >&2
  echo "  Verify this change is intentional and test thoroughly." >&2
fi

# Always allow — this is a warning, not a block
exit 0
