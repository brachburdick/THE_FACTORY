#!/usr/bin/env python3
"""THE_FACTORY Mobile Bridge — Telegram bot for phone-based operator access.

Lets you check task status, answer agent questions, view run records,
and get push notifications — all from Telegram on your phone.

Usage:
    python scripts/mobile-bridge/bridge.py
    # Or with env var: TF_TELEGRAM_TOKEN=xxx python scripts/mobile-bridge/bridge.py
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

import yaml
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from cmd_handlers.status import status_handler
from cmd_handlers.questions import questions_handler, answer_handler, question_callback_handler
from cmd_handlers.lastrun import lastrun_handler
from notifier import start_notifier

logging.basicConfig(
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("bridge")

BRIDGE_DIR = Path(__file__).parent
CONFIG_PATH = BRIDGE_DIR / "config.yaml"


def load_config() -> dict:
    """Load config from config.yaml, with env var overrides."""
    config = {}
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            config = yaml.safe_load(f) or {}

    # Env var overrides
    if tok := os.environ.get("TF_TELEGRAM_TOKEN"):
        config["telegram_bot_token"] = tok
    if cid := os.environ.get("TF_TELEGRAM_CHAT_ID"):
        config["telegram_chat_id"] = int(cid)
    if root := os.environ.get("TF_FACTORY_ROOT"):
        config["factory_root"] = root

    # Defaults
    config.setdefault("factory_root", str(BRIDGE_DIR.parent.parent))
    config.setdefault("notifications", {})
    config["notifications"].setdefault("watch_runs", True)
    config["notifications"].setdefault("watch_questions", True)
    config["notifications"].setdefault("watch_plans", True)
    config["notifications"].setdefault("ci_poll_minutes", 5)

    return config


def authorized(config: dict):
    """Decorator: only respond to the configured chat ID."""
    chat_id = config.get("telegram_chat_id")

    def decorator(func):
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            if chat_id and update.effective_chat.id != chat_id:
                logger.warning(
                    f"Unauthorized access attempt from chat_id={update.effective_chat.id}"
                )
                return
            return await func(update, context)

        return wrapper

    return decorator


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show available commands."""
    text = (
        "*THE\\_FACTORY Mobile Bridge*\n\n"
        "/status — Next ready tasks \\+ queue summary\n"
        "/questions — Pending agent questions\n"
        "/answer `q\\-001 B` — Answer a question\n"
        "/lastrun — Most recent run record\n"
        "/runs `N` — Last N run records \\(default 5\\)\n"
        "/help — This message\n\n"
        "_Notifications are automatic for new runs, questions, and plans\\._"
    )
    await update.message.reply_text(text, parse_mode="MarkdownV2")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start — show chat ID for config setup."""
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        f"Your chat ID: `{chat_id}`\n\n"
        f"Add this to config.yaml as `telegram_chat_id`.\n\n"
        f"Then restart the bridge and send /help.",
        parse_mode="Markdown",
    )


async def post_init(application: Application):
    """Set bot commands for Telegram's command menu."""
    commands = [
        BotCommand("status", "Task queue status"),
        BotCommand("questions", "Pending agent questions"),
        BotCommand("answer", "Answer a question (e.g. /answer q-001 B)"),
        BotCommand("lastrun", "Most recent run record"),
        BotCommand("runs", "Last N run records"),
        BotCommand("help", "Show all commands"),
    ]
    await application.bot.set_my_commands(commands)


def main():
    config = load_config()

    token = config.get("telegram_bot_token")
    if not token or token == "YOUR_BOT_TOKEN_HERE":
        logger.error(
            "No bot token configured. Set telegram_bot_token in config.yaml "
            "or TF_TELEGRAM_TOKEN env var.\n"
            "Create a bot: https://t.me/BotFather"
        )
        sys.exit(1)

    factory_root = Path(config["factory_root"])
    if not (factory_root / ".agent" / "tasks.jsonl").exists():
        logger.error(f"Can't find .agent/tasks.jsonl in {factory_root}")
        sys.exit(1)

    logger.info(f"Factory root: {factory_root}")
    logger.info(f"Chat ID filter: {config.get('telegram_chat_id', 'NONE (open)')}")

    # Build application
    app = Application.builder().token(token).post_init(post_init).build()

    # Store config in bot_data for handlers to access
    app.bot_data["config"] = config
    app.bot_data["factory_root"] = factory_root

    # Auth wrapper
    auth = authorized(config)

    # Register handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", auth(help_command)))
    app.add_handler(CommandHandler("status", auth(status_handler)))
    app.add_handler(CommandHandler("questions", auth(questions_handler)))
    app.add_handler(CommandHandler("answer", auth(answer_handler)))
    app.add_handler(CommandHandler("lastrun", auth(lastrun_handler)))
    app.add_handler(CommandHandler("runs", auth(lastrun_handler)))
    app.add_handler(CallbackQueryHandler(auth(question_callback_handler)))

    # Start file watchers for notifications
    notifier_config = config["notifications"]
    if any(
        notifier_config.get(k)
        for k in ("watch_runs", "watch_questions", "watch_plans")
    ):
        start_notifier(app, factory_root, config)

    logger.info("Bridge is running. Ctrl+C to stop.")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
