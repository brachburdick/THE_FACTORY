#!/usr/bin/env python3
"""Build skills/index.json from SKILL.md frontmatter.

Globs skills/**/SKILL.md and .claude/skills/**/SKILL.md,
parses YAML frontmatter, extracts trigger words from description,
and writes a sorted index to skills/index.json.

Usage: python scripts/build-skill-index.py
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def parse_frontmatter(path: Path) -> dict:
    """Extract YAML frontmatter fields from a SKILL.md file."""
    text = path.read_text()
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    fm = {}
    # Simple YAML parser for flat key: value (handles multi-line >)
    current_key = None
    current_val_lines = []
    for line in parts[1].strip().splitlines():
        m = re.match(r"^(\w[\w_-]*):\s*(.*)", line)
        if m:
            if current_key:
                fm[current_key] = " ".join(current_val_lines).strip()
            current_key = m.group(1)
            val = m.group(2).strip()
            if val == ">":
                current_val_lines = []
            else:
                current_val_lines = [val]
        elif current_key:
            current_val_lines.append(line.strip())
    if current_key:
        fm[current_key] = " ".join(current_val_lines).strip()
    return fm


def extract_triggers(description: str) -> list[str]:
    """Extract quoted trigger words from description, or split on commas."""
    # Look for quoted words first
    quoted = re.findall(r'"([^"]+)"', description)
    if quoted:
        return quoted
    # Fall back: extract words after "Signals:" if present
    signals_match = re.search(r"Signals?:\s*(.+)", description)
    if signals_match:
        return [w.strip().strip('"').strip("'") for w in signals_match.group(1).split(",")]
    return []


def build_index() -> list[dict]:
    """Build the skill index from all SKILL.md files."""
    entries = []
    for pattern in ["skills/**/SKILL.md", ".claude/skills/**/SKILL.md"]:
        for path in sorted(ROOT.glob(pattern)):
            fm = parse_frontmatter(path)
            if not fm.get("name"):
                continue
            rel_path = str(path.relative_to(ROOT))
            scope = "flow" if ".claude/skills" in rel_path else "pipeline"
            entry = {
                "name": fm["name"],
                "path": rel_path,
                "description": fm.get("description", ""),
                "triggers": extract_triggers(fm.get("description", "")),
                "scope": scope,
            }
            entries.append(entry)
    return sorted(entries, key=lambda e: e["name"])


def main():
    index = build_index()
    out = ROOT / "skills" / "index.json"
    out.write_text(json.dumps(index, indent=2) + "\n")
    print(f"Wrote {len(index)} skills to {out}")


if __name__ == "__main__":
    main()
