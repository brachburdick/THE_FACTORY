"""Last run command — show recent run records."""

import json
from pathlib import Path

from telegram import Update
from telegram.ext import ContextTypes


def load_runs(factory_root: Path, count: int = 5) -> list[dict]:
    """Load last N run records from runs.jsonl."""
    runs_file = factory_root / ".agent" / "runs.jsonl"
    if not runs_file.exists():
        return []

    runs = []
    for line in runs_file.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            runs.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    return runs[-count:]


def format_run(run: dict) -> str:
    """Format a single run record."""
    result = run.get("result", "?")
    icon = "✅" if result == "success" else "❌" if result == "failure" else "⚠️"

    lines = [
        f"{icon} *{run.get('task_id', '?')}* — {result}",
        f"📅 {run.get('date', '?')} | 📦 {run.get('project_id', '?')}",
    ]

    if summary := run.get("summary"):
        # Truncate long summaries
        if len(summary) > 200:
            summary = summary[:197] + "..."
        lines.append(f"_{summary}_")

    if evals_passed := run.get("evals_passed"):
        eval_str = f"Evals: {evals_passed}✅"
        if failed := run.get("evals_failed"):
            eval_str += f" {failed}❌"
        lines.append(eval_str)

    return "\n".join(lines)


async def lastrun_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /lastrun and /runs N."""
    factory_root = context.bot_data["factory_root"]

    # Parse count from args
    count = 1
    if update.message.text.startswith("/runs"):
        if context.args:
            try:
                count = min(int(context.args[0]), 10)
            except ValueError:
                count = 5
        else:
            count = 5

    runs = load_runs(factory_root, count)

    if not runs:
        await update.message.reply_text("No run records found.")
        return

    texts = [format_run(r) for r in reversed(runs)]
    await update.message.reply_text(
        "\n\n".join(texts), parse_mode="Markdown"
    )
