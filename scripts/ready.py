#!/usr/bin/env python3
"""Dependency-resolved task selector for THE_FACTORY.

Reads .agent/tasks.jsonl, resolves blocked_by dependencies,
and outputs the next claimable task(s).

Usage:
    python scripts/ready.py              # Print next ready task (human-readable)
    python scripts/ready.py --json       # Print next ready task as JSON
    python scripts/ready.py --all        # Print all ready tasks
    python scripts/ready.py --all --json # All ready tasks as JSON array
"""

import json
import sys
from pathlib import Path

TASKS_FILE = Path(__file__).parent.parent / ".agent" / "tasks.jsonl"
QUESTIONS_FILE = Path(__file__).parent.parent / ".agent" / "questions.jsonl"

PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def load_tasks() -> list[dict]:
    if not TASKS_FILE.exists():
        return []
    tasks = []
    for line in TASKS_FILE.read_text().splitlines():
        line = line.strip()
        if line:
            tasks.append(json.loads(line))
    return tasks


def load_pending_questions() -> set[str]:
    """Return task IDs that have unanswered questions."""
    if not QUESTIONS_FILE.exists():
        return set()
    blocked = set()
    for line in QUESTIONS_FILE.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        q = json.loads(line)
        if q.get("status") == "pending":
            blocked.add(q.get("task", ""))
    return blocked


def find_ready(tasks: list[dict]) -> list[dict]:
    """Return pending tasks whose blocked_by deps are all complete."""
    complete_ids = {t["id"] for t in tasks if t.get("status") == "complete"}
    question_blocked = load_pending_questions()

    ready = []
    for t in tasks:
        if t.get("status") != "pending":
            continue

        # Check blocked_by (formal dependency field)
        blocked_by = t.get("blocked_by", [])
        if any(dep not in complete_ids for dep in blocked_by):
            continue

        # Check legacy blockers field for task ID patterns
        blockers = t.get("blockers", [])
        if any(b in _all_task_ids(tasks) and b not in complete_ids for b in blockers):
            continue

        # Check unanswered questions
        if t["id"] in question_blocked:
            continue

        ready.append(t)

    # Sort: critical > high > medium > low, then by ID for stability
    ready.sort(key=lambda t: (
        PRIORITY_ORDER.get(t.get("priority", "medium"), 2),
        t["id"],
    ))
    return ready


def _all_task_ids(tasks: list[dict]) -> set[str]:
    return {t["id"] for t in tasks}


def main():
    args = set(sys.argv[1:])
    as_json = "--json" in args
    show_all = "--all" in args

    tasks = load_tasks()
    ready = find_ready(tasks)

    if not ready:
        if as_json:
            print("null" if not show_all else "[]")
        else:
            print("No ready tasks. All pending tasks are blocked or have unanswered questions.")
        sys.exit(1)

    if show_all:
        if as_json:
            print(json.dumps(ready, indent=2))
        else:
            for t in ready:
                blocked_by = t.get("blocked_by", [])
                pri = t.get("priority", "medium")
                print(f"  [{pri:>8}] {t['id']}: {t.get('title', t.get('summary', ''))}")
    else:
        task = ready[0]
        if as_json:
            print(json.dumps(task, indent=2))
        else:
            print(f"Next ready: {task['id']} — {task.get('title', task.get('summary', ''))}")
            if task.get("description"):
                print(f"  {task['description'][:120]}")

    sys.exit(0)


if __name__ == "__main__":
    main()
