#!/usr/bin/env python3
"""Stop hook: Write session state snapshot for cross-session continuity.

Addresses mining finding #1: 10% ramp-up tax + 1500 wasted tool calls.
The snapshot is read at next session start to skip re-exploration.

No jq dependency. Produces guaranteed-valid JSON.
"""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def git(args: list[str], cwd: str) -> str:
    """Run a git command, return stdout or empty string on failure."""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except Exception:
        return ""


def main() -> None:
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except Exception:
        # Can't parse input — skip silently (non-critical hook)
        sys.exit(0)

    session_id = data.get("session_id", "unknown")
    cwd = data.get("cwd", "")
    if not cwd:
        sys.exit(0)

    # Find project root
    project_root = Path(cwd)
    while project_root != project_root.parent:
        if (project_root / "CLAUDE.md").exists() or (project_root / ".agent").exists():
            break
        project_root = project_root.parent
    else:
        sys.exit(0)

    if project_root == project_root.parent:
        sys.exit(0)

    root = str(project_root)
    agent_dir = project_root / ".agent"
    agent_dir.mkdir(parents=True, exist_ok=True)

    # Gather state
    branch = git(["rev-parse", "--abbrev-ref", "HEAD"], root) or "unknown"
    last_commit = git(["log", "-1", "--format=%H %s"], root) or "unknown"

    modified_raw = git(["diff", "--name-only", "HEAD"], root)
    modified_files = [f for f in modified_raw.splitlines() if f][:20]

    staged_raw = git(["diff", "--cached", "--name-only"], root)
    staged_files = [f for f in staged_raw.splitlines() if f][:20]

    # Read active tasks
    active_tasks = []
    tasks_file = agent_dir / "tasks.jsonl"
    if tasks_file.exists():
        for line in tasks_file.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                task = json.loads(line)
                if task.get("status") != "complete":
                    active_tasks.append({
                        "id": task.get("id", ""),
                        "status": task.get("status", ""),
                        "taskType": task.get("taskType", ""),
                        "summary": task.get("summary", ""),
                    })
            except json.JSONDecodeError:
                continue

    # Write snapshot — guaranteed valid JSON via json.dumps
    snapshot = {
        "session_id": session_id,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "project_root": root,
        "branch": branch,
        "last_commit": last_commit,
        "modified_files": modified_files,
        "staged_files": staged_files,
        "active_tasks": active_tasks,
        "working_directory": cwd,
    }

    snapshot_path = agent_dir / "state-snapshot.json"
    snapshot_path.write_text(json.dumps(snapshot, indent=2) + "\n")


if __name__ == "__main__":
    main()
