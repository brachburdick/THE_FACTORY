#!/usr/bin/env bash
# LEGACY — .eval.md spec runner (listing only).
#
# This script lists eval cases from .eval.md spec files. It does NOT execute tests.
# For executable tests, use the pytest suite:
#
#   .venv/bin/python -m pytest evals/ -v
#
# The .eval.md files are reference specs. The executable implementations
# are in evals/test_*.py (migrated during v2.0).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CATEGORY="${1:-all}"

echo "=== .eval.md Spec Inventory (reference only) ==="
echo "NOTE: For executable tests, run: .venv/bin/python -m pytest evals/ -v"
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
    desc=$(grep -m1 "^## Should:" "$eval_file" 2>/dev/null | sed 's/^## Should: //' || echo "No description")
    echo "  [$count] $name — $desc"
  done
  echo "  Total: $count spec(s)"
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
  flows)
    list_evals "$SCRIPT_DIR/flows" "Flows"
    ;;
  all)
    list_evals "$SCRIPT_DIR/conventions" "Conventions"
    list_evals "$SCRIPT_DIR/flows" "Flows"
    list_evals "$SCRIPT_DIR/handoffs" "Handoffs"
    list_evals "$SCRIPT_DIR/skills" "Skills"
    ;;
  *)
    echo "Usage: $0 [conventions|flows|handoffs|skills|all]" >&2
    exit 1
    ;;
esac
