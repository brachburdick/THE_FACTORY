#!/usr/bin/env python3
"""Index conversation transcripts for assess.py consumption.

Scans .agent/conversations/*.jsonl, extracts per-session metrics,
and writes index.jsonl sorted by recency (newest first).

Usage:
    python scripts/index-conversations.py
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONVOS = ROOT / ".agent" / "conversations"
INDEX = CONVOS / "index.jsonl"


def index_transcript(jsonl_path: Path) -> dict | None:
    """Extract metrics from a conversation JSONL file."""
    user_msgs = 0
    assistant_msgs = 0
    tool_calls = 0
    subagent_count = 0
    reads_before_edit = 0
    first_edit_seen = False
    project = "unknown"

    for line in jsonl_path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue

        role = entry.get("type") or entry.get("role")
        if role == "user":
            user_msgs += 1
        elif role == "assistant":
            assistant_msgs += 1
            # Tool calls can be in entry.tool_calls (Claude Code transcript format)
            # or in entry.content[].type=="tool_use" (API format)
            tc_list = entry.get("tool_calls", [])
            for tc in tc_list:
                tool_calls += 1
                tool_name = tc.get("tool", tc.get("name", ""))
                input_summary = tc.get("input_summary", "")

                if tool_name == "Agent":
                    subagent_count += 1

                if not first_edit_seen:
                    if tool_name in ("Edit", "Write", "NotebookEdit"):
                        first_edit_seen = True
                    elif tool_name in ("Read", "Glob", "Grep"):
                        reads_before_edit += 1

                # Try to detect project from file paths in input_summary
                if project == "unknown" and tool_name in ("Read", "Edit", "Write"):
                    if "/projects/" in input_summary:
                        parts = input_summary.split("/projects/")[1].split("/")
                        if parts:
                            project = parts[0]

            # Also handle API format (content array with tool_use blocks)
            content = entry.get("content", [])
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_use":
                        tool_calls += 1
                        tool_name = block.get("name", "")
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
    }


def main() -> None:
    if not CONVOS.exists():
        print("No conversations directory found.", file=sys.stderr)
        sys.exit(1)

    jsonl_files = sorted(CONVOS.glob("*.jsonl"))
    if not jsonl_files:
        print("No .jsonl transcript files found.", file=sys.stderr)
        sys.exit(1)

    entries = []
    skipped = 0
    for jsonl in jsonl_files:
        try:
            entry = index_transcript(jsonl)
            if entry:
                entries.append(entry)
            else:
                skipped += 1
        except Exception as e:
            print(f"  Skip {jsonl.name}: {e}", file=sys.stderr)
            skipped += 1

    # Sort by mtime descending (newest first)
    entries.sort(key=lambda e: e.get("mtime", 0), reverse=True)

    with open(INDEX, "w") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")

    print(f"Indexed {len(entries)} conversations → {INDEX.relative_to(ROOT)}")
    if skipped:
        print(f"  ({skipped} skipped — empty or unparseable)")


if __name__ == "__main__":
    main()
