#!/usr/bin/env bash
# Pack a skill directory into a .skill archive (ZIP).
# Usage: scripts/pack-skill.sh <skill-directory>
# Output: {name}.skill in the current directory.
set -euo pipefail

SKILL_DIR="${1:?Usage: pack-skill.sh <skill-directory>}"

# Resolve to absolute path
SKILL_DIR="$(cd "$SKILL_DIR" && pwd)"

# Validate SKILL.md exists
if [[ ! -f "$SKILL_DIR/SKILL.md" ]]; then
  echo "ERROR: $SKILL_DIR/SKILL.md not found" >&2
  exit 1
fi

# Derive name from directory basename
NAME="$(basename "$SKILL_DIR")"
OUTPUT="${NAME}.skill"

# Create ZIP archive from the skill directory contents
(cd "$SKILL_DIR" && zip -r - .) > "$OUTPUT"

echo "Packed $OUTPUT ($(du -h "$OUTPUT" | cut -f1) from $SKILL_DIR)"
