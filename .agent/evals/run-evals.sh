#!/usr/bin/env bash
# Eval runner for meta-infrastructure convention checks.
# Usage: .agent/evals/run-evals.sh [category]
# Categories: conventions, handoffs, skills, all (default)
#
# This script lists all eval cases and their status.
# Eval cases are .eval.md files describing expected agent behavior.
# Automated execution requires integration with an LLM testing framework.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CATEGORY="${1:-all}"

echo "=== Meta-Infrastructure Eval Suite ==="
echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""

list_evals() {
  local dir="$1"
  local category="$2"

  if [ ! -d "$dir" ]; then
    return
  fi

  echo "## $category"
  local count=0
  for eval_file in "$dir"/*.eval.md; do
    [ -f "$eval_file" ] || continue
    count=$((count + 1))
    name=$(basename "$eval_file" .eval.md)
    # Extract first "## Should:" line as description
    desc=$(grep -m1 "^## Should:" "$eval_file" 2>/dev/null | sed 's/^## Should: //' || echo "No description")
    echo "  [$count] $name — $desc"
  done
  echo "  Total: $count eval(s)"
  echo ""
}

case "$CATEGORY" in
  conventions)
    list_evals "$SCRIPT_DIR/conventions" "Conventions"
    ;;
  handoffs)
    list_evals "$SCRIPT_DIR/handoffs" "Handoffs"
    ;;
  skills)
    list_evals "$SCRIPT_DIR/skills" "Skills"
    ;;
  all)
    list_evals "$SCRIPT_DIR/conventions" "Conventions"
    list_evals "$SCRIPT_DIR/handoffs" "Handoffs"
    list_evals "$SCRIPT_DIR/skills" "Skills"
    ;;
  *)
    echo "Usage: $0 [conventions|handoffs|skills|all]" >&2
    exit 1
    ;;
esac

echo "---"
echo "To run evals against an agent, integrate with your LLM testing framework."
echo "Each .eval.md contains input/expected/fail-if criteria for automated testing."
