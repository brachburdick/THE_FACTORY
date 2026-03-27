#!/usr/bin/env python3
"""Write an incident record to .agent/incidents.jsonl.

Called by hooks when they block an action (exit 2). Keeps incidents.jsonl
from being permanently empty — the most obvious gap in THE_FACTORY's
feedback loop.

Usage:
  python3 log-incident.py --category blocked --severity medium \
    --summary "Budget exhausted: 8 mutations (limit 7 for medium-risk)"

Automatically fills: incident_id, date, task_id (from canonical reader).
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Log an incident")
    parser.add_argument("--category", required=True,
                        choices=["hook_failure", "test_regression", "scope_creep",
                                 "blocked", "flaky_test", "other"])
    parser.add_argument("--severity", required=True,
                        choices=["low", "medium", "high", "critical"])
    parser.add_argument("--summary", required=True)
    parser.add_argument("--hook", type=str, default="", help="Which hook triggered this")
    args = parser.parse_args()

    # Find .agent directory
    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
    agent_dir = project_dir / ".agent"
    if not agent_dir.exists():
        agent_dir = Path(".agent")
    if not agent_dir.exists():
        sys.exit(0)

    # Get active task ID via canonical reader
    hook_dir = Path(__file__).parent
    task_id = "unknown"
    try:
        reader_path = hook_dir / "task-reader.py"
        if reader_path.exists():
            from importlib.machinery import SourceFileLoader
            reader = SourceFileLoader("task_reader", str(reader_path)).load_module()
            tasks_path = reader.find_tasks_file()
            if tasks_path:
                task = reader.get_active_task(tasks_path)
                if task:
                    task_id = task.get("id", "unknown")
    except Exception:
        pass

    now = datetime.now(timezone.utc)
    incident = {
        "incident_id": f"inc-{task_id}-{now.strftime('%Y%m%d-%H%M%S%f')[:22]}",
        "date": now.strftime("%Y-%m-%d"),
        "task_id": task_id,
        "severity": args.severity,
        "category": args.category,
        "summary": args.summary,
    }
    if args.hook:
        incident["hook"] = args.hook

    incidents_file = agent_dir / "incidents.jsonl"
    with open(incidents_file, "a") as f:
        f.write(json.dumps(incident) + "\n")


if __name__ == "__main__":
    main()
