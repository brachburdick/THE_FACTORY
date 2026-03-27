#!/usr/bin/env bash
# Install a .skill archive into skills/custom/{name}/.
# Usage: scripts/install-skill.sh <archive.skill>
# Rebuilds skills/index.json after extraction.
set -euo pipefail

ARCHIVE="${1:?Usage: install-skill.sh <archive.skill>}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Derive skill name from archive filename
NAME="$(basename "$ARCHIVE" .skill)"
DEST="$REPO_ROOT/skills/custom/$NAME"

mkdir -p "$DEST"
unzip -o "$ARCHIVE" -d "$DEST"

# Validate SKILL.md was extracted
if [[ ! -f "$DEST/SKILL.md" ]]; then
  echo "ERROR: Archive did not contain SKILL.md" >&2
  rm -rf "$DEST"
  exit 1
fi

echo "Installed $NAME to $DEST"

# Rebuild skill index
python3 "$REPO_ROOT/scripts/build-skill-index.py"
