#!/usr/bin/env python3
"""Canonical task state reader for THE_FACTORY hooks and scripts.

Solves the "multiple consumers, multiple semantics" problem:
- tasks.jsonl uses JSONL append semantics (same ID can appear multiple times)
- The LAST entry for a given ID is the canonical state
- All hooks and scripts must use this reader for consistent task resolution

Usage from bash hooks:
  TASK_JSON=$(python3 "$HOOK_DIR/task-reader.py" --active)
  RISK=$(python3 "$HOOK_DIR/task-reader.py" --active --field risk)
  SECTION=$(python3 "$HOOK_DIR/task-reader.py" --active --field section)

Usage from Python scripts:
  from task_reader import get_active_task, get_all_tasks, get_task_by_id
"""

import json
import os
import re
import sys
from pathlib import Path

HIGH_KEYWORDS = re.compile(
    r"(security|migration|schema|auth|credentials|cross-section|destructive|irreversible)",
    re.I,
)
LOW_KEYWORDS = re.compile(
    r"^(test|doc|config|lint|typo|frontmatter|license|readme)", re.I
)


def find_tasks_file() -> Path | None:
    """Locate tasks.jsonl, checking cwd and CLAUDE_PROJECT_DIR."""
    candidates = [
        Path(".agent/tasks.jsonl"),
        Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")) / ".agent" / "tasks.jsonl",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def load_tasks_canonical(tasks_path: Path) -> dict[str, dict]:
    """Load tasks.jsonl with JSONL append dedup: last entry per ID wins."""
    tasks: dict[str, dict] = {}
    for line in tasks_path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            task = json.loads(line)
            task_id = task.get("id", "")
            if task_id:
                tasks[task_id] = task
        except json.JSONDecodeError:
            continue
    return tasks


def get_active_task(tasks_path: Path) -> dict | None:
    """Return the single in_progress task (canonical: last entry per ID wins).

    If multiple tasks are in_progress after dedup, returns the one with the
    most recent 'updated' timestamp. If no timestamp, returns the last one
    encountered in file order.
    """
    canonical = load_tasks_canonical(tasks_path)
    active = [t for t in canonical.values() if t.get("status") == "in_progress"]
    if not active:
        return None
    if len(active) == 1:
        return active[0]
    # Multiple in_progress: prefer most recently updated
    return max(active, key=lambda t: t.get("updated", ""))


def infer_risk(task: dict) -> str:
    """Infer risk level from task fields when not explicitly set."""
    risk = task.get("risk")
    if risk in ("low", "medium", "high"):
        return risk

    text = task.get("summary", "") + " " + task.get("description", "")
    task_type = task.get("taskType", "")

    if HIGH_KEYWORDS.search(text):
        return "high"
    if LOW_KEYWORDS.match(task_type) or LOW_KEYWORDS.match(text.strip()):
        return "low"
    return "medium"


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Canonical task state reader")
    parser.add_argument(
        "--active", action="store_true", help="Return the active (in_progress) task"
    )
    parser.add_argument(
        "--field",
        type=str,
        help="Return a specific field value (e.g., risk, section, project, id)",
    )
    parser.add_argument(
        "--infer-risk",
        action="store_true",
        help="If --field=risk and no explicit risk, infer from keywords",
    )
    parser.add_argument(
        "--all-active",
        action="store_true",
        help="Return all non-complete tasks (for state snapshot)",
    )
    parser.add_argument(
        "--tasks-file", type=str, help="Explicit path to tasks.jsonl"
    )

    args = parser.parse_args()

    tasks_path = Path(args.tasks_file) if args.tasks_file else find_tasks_file()
    if not tasks_path or not tasks_path.exists():
        if args.field:
            # Return empty for field queries (hooks need a default)
            print("")
        elif args.all_active:
            print("[]")
        else:
            print("{}")
        sys.exit(0)

    if args.all_active:
        canonical = load_tasks_canonical(tasks_path)
        active = [
            {
                "id": t.get("id", ""),
                "status": t.get("status", ""),
                "taskType": t.get("taskType", ""),
                "summary": t.get("summary", ""),
            }
            for t in canonical.values()
            if t.get("status") != "complete"
        ]
        print(json.dumps(active))
        sys.exit(0)

    if args.active:
        task = get_active_task(tasks_path)
        if not task:
            if args.field:
                print("")
            else:
                print("{}")
            sys.exit(0)

        if args.field:
            if args.field == "risk" and args.infer_risk:
                print(infer_risk(task))
            else:
                print(task.get(args.field, ""))
        else:
            print(json.dumps(task))
        sys.exit(0)

    # Default: dump all canonical tasks
    canonical = load_tasks_canonical(tasks_path)
    print(json.dumps(list(canonical.values())))


if __name__ == "__main__":
    main()
