#!/usr/bin/env python3
"""Index conversation transcripts for assess.py consumption.

Scans all conversation sources:
1. ~/.claude/projects/<project-slug>/*.jsonl (Claude Code's native storage)
2. .agent/conversations/*.jsonl (legacy local copies, if any)

Deduplicates by session_id, preferring the newer mtime.
Writes index.jsonl sorted by recency (newest first).

Usage:
    python scripts/index-conversations.py [--rebuild]
"""

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / ".agent" / "conversations" / "index.jsonl"

# Claude Code stores transcripts here, with project path encoded as slug
CLAUDE_PROJECTS_DIR = Path.home() / ".claude" / "projects"

# Known project slugs for this workspace
PROJECT_SLUGS = {
    "-Users-brach-Documents-THE-FACTORY": "THE_FACTORY",
    "-Users-brach-Documents-THE-FACTORY-projects-DjTools-scue": "SCUE",
    "-Users-brach-Documents-THE-FACTORY-projects-CRUCIBLE": "CRUCIBLE",
    "-Users-brach-Documents-THE-FACTORY-projects-tinyshop": "Tinyshop",
    "-Users-brach-Documents-THE-FACTORY-projects-enable": "enable",
}

# Legacy local copies
LOCAL_CONVOS = ROOT / ".agent" / "conversations"


def find_all_transcripts() -> list[tuple[Path, str]]:
    """Find all transcript JSONL files across all sources.

    Returns list of (path, project_name) tuples.
    """
    transcripts: list[tuple[Path, str]] = []

    # 1. Scan Claude Code's native storage
    if CLAUDE_PROJECTS_DIR.exists():
        for slug, project_name in PROJECT_SLUGS.items():
            project_dir = CLAUDE_PROJECTS_DIR / slug
            if project_dir.exists():
                for jsonl in project_dir.glob("*.jsonl"):
                    # Skip subagent transcripts (in subdirs)
                    if jsonl.parent == project_dir:
                        transcripts.append((jsonl, project_name))

    # 2. Scan legacy local copies
    if LOCAL_CONVOS.exists():
        for jsonl in LOCAL_CONVOS.glob("*.jsonl"):
            if jsonl.name == "index.jsonl":
                continue
            transcripts.append((jsonl, "unknown"))

    return transcripts


def index_transcript(jsonl_path: Path, project_hint: str = "unknown") -> dict | None:
    """Extract metrics from a conversation JSONL file."""
    user_msgs = 0
    assistant_msgs = 0
    tool_calls = 0
    subagent_count = 0
    reads_before_edit = 0
    first_edit_seen = False
    project = project_hint
    tool_frequency: dict[str, int] = {}

    try:
        text = jsonl_path.read_text()
    except (PermissionError, OSError):
        return None

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue

        # Handle both transcript formats
        msg = entry.get("message", entry)
        role = msg.get("role", entry.get("type", ""))

        if role == "user":
            user_msgs += 1
        elif role == "assistant":
            assistant_msgs += 1

            # Format 1: entry.tool_calls (Claude Code transcript format)
            for tc in entry.get("tool_calls", []):
                tool_calls += 1
                tool_name = tc.get("tool", tc.get("name", "unknown"))
                tool_frequency[tool_name] = tool_frequency.get(tool_name, 0) + 1

                if tool_name == "Agent":
                    subagent_count += 1
                if not first_edit_seen:
                    if tool_name in ("Edit", "Write", "NotebookEdit"):
                        first_edit_seen = True
                    elif tool_name in ("Read", "Glob", "Grep"):
                        reads_before_edit += 1

            # Format 2: content array with tool_use blocks (API format)
            content = msg.get("content", [])
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_use":
                        tool_calls += 1
                        tool_name = block.get("name", "unknown")
                        tool_frequency[tool_name] = tool_frequency.get(tool_name, 0) + 1

                        if tool_name == "Agent":
                            subagent_count += 1
                        if not first_edit_seen:
                            if tool_name in ("Edit", "Write", "NotebookEdit"):
                                first_edit_seen = True
                            elif tool_name in ("Read", "Glob", "Grep"):
                                reads_before_edit += 1

    if user_msgs == 0 and assistant_msgs == 0:
        return None

    return {
        "session_id": jsonl_path.stem,
        "mtime": jsonl_path.stat().st_mtime,
        "project": project,
        "user_messages": user_msgs,
        "assistant_messages": assistant_msgs,
        "tool_calls": tool_calls,
        "total_tool_calls": tool_calls,
        "subagent_count": subagent_count,
        "reads_before_edit": reads_before_edit,
        "tool_frequency": tool_frequency,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Index conversation transcripts")
    parser.add_argument("--rebuild", action="store_true", help="Force full rebuild")
    args = parser.parse_args()

    INDEX.parent.mkdir(parents=True, exist_ok=True)

    # Find all transcripts
    all_transcripts = find_all_transcripts()
    if not all_transcripts:
        print("No conversation transcripts found.", file=sys.stderr)
        sys.exit(1)

    # Deduplicate by session_id (prefer newer mtime)
    best: dict[str, tuple[Path, str]] = {}
    for path, project in all_transcripts:
        sid = path.stem
        if sid not in best or path.stat().st_mtime > best[sid][0].stat().st_mtime:
            best[sid] = (path, project)

    # Index each transcript
    entries = []
    skipped = 0
    for sid, (path, project) in best.items():
        try:
            entry = index_transcript(path, project)
            if entry:
                entries.append(entry)
            else:
                skipped += 1
        except Exception as e:
            print(f"  Skip {path.name}: {e}", file=sys.stderr)
            skipped += 1

    # Sort by mtime descending (newest first)
    entries.sort(key=lambda e: e.get("mtime", 0), reverse=True)

    with open(INDEX, "w") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")

    # Summary
    projects = {}
    for e in entries:
        p = e.get("project", "unknown")
        projects[p] = projects.get(p, 0) + 1

    print(f"Indexed {len(entries)} conversations → {INDEX.relative_to(ROOT)}")
    for p, count in sorted(projects.items()):
        print(f"  {p}: {count}")
    if skipped:
        print(f"  ({skipped} skipped — empty or unparseable)")


if __name__ == "__main__":
    main()
