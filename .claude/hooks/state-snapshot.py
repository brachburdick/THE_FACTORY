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

    # Read active tasks with canonical dedup (last entry per ID wins)
    active_tasks = []
    tasks_file = agent_dir / "tasks.jsonl"
    if tasks_file.exists():
        canonical: dict[str, dict] = {}
        for line in tasks_file.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                task = json.loads(line)
                task_id = task.get("id", "")
                if task_id:
                    canonical[task_id] = task
            except json.JSONDecodeError:
                continue

        # Include in_progress and blocked tasks (pending omitted — in tasks.jsonl if needed)
        for task in canonical.values():
            status = task.get("status", "")
            if status in ("in_progress", "blocked"):
                active_tasks.append({
                    "id": task.get("id", ""),
                    "status": status,
                    "taskType": task.get("taskType", ""),
                    "summary": task.get("summary", ""),
                })

    # Read prior session knowledge (preserve across sessions if exists)
    session_knowledge = {}
    knowledge_file = agent_dir / "session-knowledge.json"
    if knowledge_file.exists():
        try:
            session_knowledge = json.loads(knowledge_file.read_text())
        except (json.JSONDecodeError, OSError):
            pass

    # Read session friction from fix-attempt-tracker state
    friction: dict[str, int] = {}
    hooks_dir = project_root / ".claude" / "hooks"
    tracker_state = hooks_dir / "fix-attempt-tracker.state"
    if tracker_state.exists():
        try:
            lines = tracker_state.read_text().splitlines()
            friction = {
                "mutations_since_test": int(lines[0]) if len(lines) > 0 else 0,
                "total_mutations": int(lines[1]) if len(lines) > 1 else 0,
                "test_cycles": int(lines[2]) if len(lines) > 2 else 0,
                "unique_files_modified": len(lines[3].split(",")) if len(lines) > 3 and lines[3] else 0,
            }
        except (ValueError, IndexError):
            pass

    # Count incidents logged this session
    incidents_file = agent_dir / "incidents.jsonl"
    incident_count = 0
    if incidents_file.exists():
        for line in incidents_file.read_text().splitlines():
            if line.strip():
                incident_count += 1
    friction["incidents_logged"] = incident_count

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
        "session_friction": friction,
        "session_knowledge": session_knowledge,
        "working_directory": cwd,
    }

    snapshot_path = agent_dir / "state-snapshot.json"
    snapshot_path.write_text(json.dumps(snapshot, indent=2) + "\n")


if __name__ == "__main__":
    main()
