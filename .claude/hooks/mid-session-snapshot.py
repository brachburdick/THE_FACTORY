#!/usr/bin/env python3
"""PostToolUse hook: Lightweight mid-session state snapshot.

Fires after Edit/Write. Counts mutations via fix-attempt-tracker.state.
Every SNAPSHOT_INTERVAL mutations, writes a lightweight snapshot (no pytest,
no incident scan). Implements "Assume Interruption" — if the session dies,
the next session inherits recent state instead of starting from zero.
"""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SNAPSHOT_INTERVAL = 15  # Write snapshot every N mutations


def git(args: list[str], cwd: str) -> str:
    try:
        result = subprocess.run(
            ["git"] + args, cwd=cwd, capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except Exception:
        return ""


def main() -> None:
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except Exception:
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
    hooks_dir = project_root / ".claude" / "hooks"

    # Check mutation count from fix-attempt-tracker state
    tracker_state = hooks_dir / "fix-attempt-tracker.state"
    if not tracker_state.exists():
        sys.exit(0)

    try:
        lines = tracker_state.read_text().splitlines()
        total_mutations = int(lines[1]) if len(lines) > 1 else 0
    except (ValueError, IndexError):
        sys.exit(0)

    # Only snapshot at intervals (and not at 0)
    if total_mutations == 0 or total_mutations % SNAPSHOT_INTERVAL != 0:
        sys.exit(0)

    # --- Lightweight snapshot (no pytest, no incident scan) ---

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
        canonical: dict[str, dict] = {}
        for line in tasks_file.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                task = json.loads(line)
                tid = task.get("id", "")
                if tid:
                    canonical[tid] = task
            except json.JSONDecodeError:
                continue
        for task in canonical.values():
            status = task.get("status", "")
            if status in ("in_progress", "blocked"):
                active_tasks.append({
                    "id": task.get("id", ""),
                    "status": status,
                    "taskType": task.get("taskType", ""),
                    "summary": task.get("summary", ""),
                })

    # Preserve session knowledge
    session_knowledge = {}
    knowledge_file = agent_dir / "session-knowledge.json"
    if knowledge_file.exists():
        try:
            session_knowledge = json.loads(knowledge_file.read_text())
        except (json.JSONDecodeError, OSError):
            pass

    # Friction from tracker
    friction: dict[str, int] = {}
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

    # Atomic write
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
        "mid_session": True,
    }

    snapshot_path = agent_dir / "state-snapshot.json"
    tmp_path = snapshot_path.with_suffix(".tmp")
    tmp_path.write_text(json.dumps(snapshot, indent=2) + "\n")
    tmp_path.rename(snapshot_path)


if __name__ == "__main__":
    main()
