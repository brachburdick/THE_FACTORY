#!/usr/bin/env python3
"""PostToolUse hook (Read): Log file reads to .agent/read-state.jsonl.

Tracks file path, content hash, and timestamp. On session resume, agents
check hashes against current files — skip unchanged, re-read only stale.
Eliminates ~20-30% redundant token spend on cross-session re-reads.

Filters out noise: only logs reads within the project root, skips
.agent/state-snapshot.json and other meta-files the agent reads every session.
"""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Files read every session — don't log these
SKIP_PATTERNS = {
    "state-snapshot.json",
    "session-knowledge.json",
    "MEMORY.md",
    "fix-attempt-tracker.state",
}


def main() -> None:
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except Exception:
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    tool_response = data.get("tool_response", {})
    cwd = data.get("cwd", "")
    session_id = data.get("session_id", "unknown")

    file_path = tool_input.get("file_path", "")
    if not file_path:
        sys.exit(0)

    # Skip files outside project root
    project_root = Path(cwd)
    while project_root != project_root.parent:
        if (project_root / "CLAUDE.md").exists() or (project_root / ".agent").exists():
            break
        project_root = project_root.parent
    else:
        sys.exit(0)

    if project_root == project_root.parent:
        sys.exit(0)

    # Skip meta-files
    basename = Path(file_path).name
    if basename in SKIP_PATTERNS:
        sys.exit(0)

    # Skip files outside project
    try:
        Path(file_path).resolve().relative_to(project_root.resolve())
    except ValueError:
        sys.exit(0)

    # Get content for hashing
    content = tool_response.get("content", "")
    if not content or not tool_response.get("success", True):
        sys.exit(0)

    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]

    # Make path relative to project root
    try:
        rel_path = str(Path(file_path).resolve().relative_to(project_root.resolve()))
    except ValueError:
        rel_path = file_path

    entry = {
        "path": rel_path,
        "hash": content_hash,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "session": session_id,
    }

    # Append atomically
    read_state = project_root / ".agent" / "read-state.jsonl"
    with open(read_state, "a") as f:
        f.write(json.dumps(entry, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
