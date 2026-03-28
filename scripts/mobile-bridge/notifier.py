"""Notification engine — watches filesystem for events and pushes to Telegram."""

import asyncio
import json
import logging
import time
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger("notifier")


class JsonlWatcher(FileSystemEventHandler):
    """Watch a JSONL file for new lines appended."""

    def __init__(self, filepath: Path, callback, debounce_seconds: float = 2.0):
        self.filepath = filepath
        self.callback = callback
        self.debounce = debounce_seconds
        self._last_size = filepath.stat().st_size if filepath.exists() else 0
        self._last_fire = 0.0

    def on_modified(self, event):
        if Path(event.src_path).resolve() != self.filepath.resolve():
            return

        now = time.time()
        if now - self._last_fire < self.debounce:
            return

        if not self.filepath.exists():
            return

        current_size = self.filepath.stat().st_size
        if current_size <= self._last_size:
            self._last_size = current_size
            return

        # Read new content
        try:
            with open(self.filepath) as f:
                f.seek(self._last_size)
                new_data = f.read()
        except OSError:
            return

        self._last_size = current_size
        self._last_fire = now

        # Parse new JSONL lines
        new_records = []
        for line in new_data.splitlines():
            line = line.strip()
            if line:
                try:
                    new_records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        if new_records:
            self.callback(new_records)


def format_run_notification(run: dict) -> str:
    result = run.get("result", "?")
    icon = "✅" if result == "success" else "❌"
    task = run.get("task_id", "?")
    project = run.get("project_id", "?")
    summary = run.get("summary", "")[:150]
    return f"🏁 *Run complete*\n{icon} `{task}` ({project})\n_{summary}_"


def format_question_notification(q: dict) -> str:
    lines = [f"❓ *New question: {q['id']}*", f"Task: `{q.get('task', '?')}`\n"]
    lines.append(q.get("question", ""))
    if options := q.get("options"):
        for i, opt in enumerate(options):
            label = chr(65 + i)
            lines.append(f"  *{label}.* {opt}")
        lines.append(f"\n_Reply: /answer {q['id']} A_")
    return "\n".join(lines)


def start_notifier(app, factory_root: Path, config: dict):
    """Start filesystem watchers in background threads."""
    chat_id = config.get("telegram_chat_id")
    if not chat_id:
        logger.warning("No chat_id configured — notifications disabled.")
        return

    notif_config = config.get("notifications", {})
    observer = Observer()
    agent_dir = factory_root / ".agent"

    def send_message(text: str):
        """Queue a message to be sent via the bot."""
        loop = app._loop if hasattr(app, '_loop') else asyncio.get_event_loop()
        asyncio.run_coroutine_threadsafe(
            app.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown"),
            loop,
        )

    # Watch runs.jsonl
    if notif_config.get("watch_runs"):
        runs_file = agent_dir / "runs.jsonl"
        if runs_file.exists():
            def on_new_runs(records):
                for r in records:
                    if not r.get("backfilled"):
                        try:
                            send_message(format_run_notification(r))
                        except Exception as e:
                            logger.error(f"Failed to send run notification: {e}")

            runs_watcher = JsonlWatcher(runs_file, on_new_runs)
            observer.schedule(runs_watcher, str(agent_dir), recursive=False)
            logger.info("Watching runs.jsonl for new records")

    # Watch questions.jsonl
    if notif_config.get("watch_questions"):
        qfile = agent_dir / "questions.jsonl"
        if qfile.exists():
            def on_new_questions(records):
                for q in records:
                    if q.get("status") == "pending":
                        try:
                            send_message(format_question_notification(q))
                        except Exception as e:
                            logger.error(f"Failed to send question notification: {e}")

            q_watcher = JsonlWatcher(qfile, on_new_questions)
            observer.schedule(q_watcher, str(agent_dir), recursive=False)
            logger.info("Watching questions.jsonl for new questions")

    observer.daemon = True
    observer.start()
    logger.info("Notifier started")
