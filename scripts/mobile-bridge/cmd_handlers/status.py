"""Status command — task queue summary for Telegram."""

import json
from pathlib import Path

from telegram import Update
from telegram.ext import ContextTypes

PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def load_tasks(factory_root: Path) -> list[dict]:
    tasks_file = factory_root / ".agent" / "tasks.jsonl"
    if not tasks_file.exists():
        return []
    tasks = []
    for line in tasks_file.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                tasks.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return tasks


def load_pending_questions(factory_root: Path) -> set[str]:
    qfile = factory_root / ".agent" / "questions.jsonl"
    if not qfile.exists():
        return set()
    blocked = set()
    for line in qfile.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            q = json.loads(line)
            if q.get("status") == "pending":
                blocked.add(q.get("task", ""))
        except json.JSONDecodeError:
            continue
    return blocked


def find_ready(tasks: list[dict], factory_root: Path) -> list[dict]:
    complete_ids = {t["id"] for t in tasks if t.get("status") == "complete"}
    question_blocked = load_pending_questions(factory_root)
    all_ids = {t["id"] for t in tasks}

    ready = []
    for t in tasks:
        if t.get("status") != "pending":
            continue
        blocked_by = t.get("blocked_by", [])
        if any(dep not in complete_ids for dep in blocked_by):
            continue
        blockers = t.get("blockers", [])
        if any(b in all_ids and b not in complete_ids for b in blockers):
            continue
        if t["id"] in question_blocked:
            continue
        ready.append(t)

    ready.sort(
        key=lambda t: (PRIORITY_ORDER.get(t.get("priority", "medium"), 2), t["id"])
    )
    return ready


def format_status(tasks: list[dict], ready: list[dict]) -> str:
    """Format task queue status for Telegram."""
    complete = sum(1 for t in tasks if t.get("status") == "complete")
    pending = sum(1 for t in tasks if t.get("status") == "pending")
    in_progress = sum(1 for t in tasks if t.get("status") == "in_progress")

    lines = [f"📋 *Queue:* {complete}✅  {in_progress}🔄  {pending}⏳\n"]

    # In-progress tasks
    wip = [t for t in tasks if t.get("status") == "in_progress"]
    if wip:
        lines.append("*In progress:*")
        for t in wip:
            title = t.get("title", t.get("summary", "untitled"))[:60]
            lines.append(f"  🔄 `{t['id']}` {title}")
        lines.append("")

    # Ready tasks
    if ready:
        lines.append(f"*Ready ({len(ready)}):*")
        for t in ready[:8]:
            pri = t.get("priority", "medium")
            icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "⚪"}.get(
                pri, "🟡"
            )
            title = t.get("title", t.get("summary", "untitled"))[:55]
            lines.append(f"  {icon} `{t['id']}` {title}")
        if len(ready) > 8:
            lines.append(f"  _…and {len(ready) - 8} more_")
    else:
        lines.append("_No tasks ready — all blocked or have pending questions._")

    return "\n".join(lines)


async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command."""
    factory_root = context.bot_data["factory_root"]
    tasks = load_tasks(factory_root)
    ready = find_ready(tasks, factory_root)
    text = format_status(tasks, ready)
    await update.message.reply_text(text, parse_mode="Markdown")
