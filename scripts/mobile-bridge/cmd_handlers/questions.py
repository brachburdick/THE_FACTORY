"""Questions command — view and answer agent questions from Telegram."""

import json
from datetime import datetime, timezone
from pathlib import Path

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


def load_questions(factory_root: Path) -> list[dict]:
    qfile = factory_root / ".agent" / "questions.jsonl"
    if not qfile.exists():
        return []
    questions = []
    for line in qfile.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            questions.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return questions


def format_question(q: dict) -> str:
    """Format a single question for display."""
    lines = [f"❓ *{q['id']}* (task: `{q.get('task', '?')}`)\n"]
    lines.append(q["question"])

    if options := q.get("options"):
        lines.append("")
        for i, opt in enumerate(options):
            label = chr(65 + i)  # A, B, C...
            default = " _(default)_" if opt == q.get("default") else ""
            lines.append(f"  *{label}.* {opt}{default}")

    if impact := q.get("impact"):
        lines.append(f"\n_Impact: {impact}_")

    return "\n".join(lines)


def build_answer_keyboard(q: dict) -> InlineKeyboardMarkup | None:
    """Build inline keyboard buttons for question options."""
    options = q.get("options")
    if not options:
        return None

    buttons = []
    for i, opt in enumerate(options):
        label = chr(65 + i)
        # callback_data format: answer:q-001:A
        callback = f"answer:{q['id']}:{label}"
        display = f"{label}. {opt[:30]}"
        buttons.append(InlineKeyboardButton(display, callback_data=callback))

    # Arrange in rows of 2
    rows = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(rows)


def write_answer(factory_root: Path, question_id: str, answer: str) -> bool:
    """Write answer to questions.jsonl by updating the matching line."""
    qfile = factory_root / ".agent" / "questions.jsonl"
    if not qfile.exists():
        return False

    lines = qfile.read_text().splitlines()
    updated = False
    new_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            new_lines.append(line)
            continue
        try:
            q = json.loads(stripped)
        except json.JSONDecodeError:
            new_lines.append(line)
            continue

        if q.get("id") == question_id and q.get("status") == "pending":
            q["status"] = "answered"
            q["answer"] = answer
            q["answered"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            new_lines.append(json.dumps(q, ensure_ascii=False))
            updated = True
        else:
            new_lines.append(line)

    if updated:
        qfile.write_text("\n".join(new_lines) + "\n")

    return updated


async def questions_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /questions — show pending questions."""
    factory_root = context.bot_data["factory_root"]
    questions = load_questions(factory_root)
    pending = [q for q in questions if q.get("status") == "pending"]

    if not pending:
        await update.message.reply_text("No pending questions. 🎯")
        return

    for q in pending[:5]:
        text = format_question(q)
        keyboard = build_answer_keyboard(q)
        await update.message.reply_text(
            text, parse_mode="Markdown", reply_markup=keyboard
        )

    if len(pending) > 5:
        await update.message.reply_text(f"_{len(pending) - 5} more pending…_", parse_mode="Markdown")


async def answer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /answer q-001 B — answer a question by ID and option letter."""
    factory_root = context.bot_data["factory_root"]
    args = context.args

    if not args or len(args) < 2:
        await update.message.reply_text(
            "Usage: `/answer q-001 B` or `/answer q-001 your free text answer`",
            parse_mode="Markdown",
        )
        return

    question_id = args[0]
    answer_text = " ".join(args[1:])

    # If single letter, resolve to option text
    questions = load_questions(factory_root)
    matching = [q for q in questions if q.get("id") == question_id]

    if not matching:
        await update.message.reply_text(f"Question `{question_id}` not found.", parse_mode="Markdown")
        return

    q = matching[0]
    if q.get("status") != "pending":
        await update.message.reply_text(f"Question `{question_id}` already answered.", parse_mode="Markdown")
        return

    # Resolve letter to option
    if len(answer_text) == 1 and answer_text.upper() in "ABCDEFGH":
        options = q.get("options", [])
        idx = ord(answer_text.upper()) - 65
        if idx < len(options):
            answer_text = options[idx]

    if write_answer(factory_root, question_id, answer_text):
        await update.message.reply_text(
            f"✅ Answered `{question_id}`: _{answer_text}_", parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(f"Failed to write answer for `{question_id}`.", parse_mode="Markdown")


async def question_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard button presses for question answers."""
    query = update.callback_query
    await query.answer()

    data = query.data  # format: answer:q-001:A
    if not data or not data.startswith("answer:"):
        return

    parts = data.split(":")
    if len(parts) != 3:
        return

    _, question_id, letter = parts
    factory_root = context.bot_data["factory_root"]

    # Resolve letter to option text
    questions = load_questions(factory_root)
    matching = [q for q in questions if q.get("id") == question_id]

    if not matching:
        await query.edit_message_text(f"Question `{question_id}` not found.", parse_mode="Markdown")
        return

    q = matching[0]
    options = q.get("options", [])
    idx = ord(letter.upper()) - 65
    answer_text = options[idx] if idx < len(options) else letter

    if write_answer(factory_root, question_id, answer_text):
        # Update the message to show it's been answered
        await query.edit_message_text(
            f"✅ *{question_id}* answered: _{answer_text}_\n\n"
            f"_{q['question']}_",
            parse_mode="Markdown",
        )
    else:
        await query.edit_message_text(
            f"Failed to answer `{question_id}`.", parse_mode="Markdown"
        )
