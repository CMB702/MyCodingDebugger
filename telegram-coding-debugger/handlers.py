"""Telegram update handlers and safe message formatting."""

import html
import logging

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from ai_client import DebugResult, DebuggerAI
from database import Database

LOGGER = logging.getLogger(__name__)
MAX_SUBMISSION_LENGTH = 20_000

WELCOME = """Welcome to AI Coding Debugger.

Send me code or an error message and I'll help you find and fix the problem.

Available commands:
/start - Show this welcome message
/debug <code or error> - Debug a submission
/help - Learn how to use the bot"""


def _language_fence(language: str) -> str:
    aliases = {"c++": "cpp", "c#": "csharp", "typescript": "typescript", "javascript": "javascript"}
    return aliases.get(language.lower(), language.lower().replace(" ", ""))


def format_result(result: DebugResult) -> str:
    code = html.escape(result.fixed_code)
    return (
        f"<b>Language:</b>\n{html.escape(result.language)}\n\n"
        f"<b>Problem:</b>\n{html.escape(result.problem)}\n\n"
        f"<b>Why:</b>\n{html.escape(result.why)}\n\n"
        f"<b>Fixed code:</b>\n<pre><code class=\"language-{_language_fence(result.language)}\">{code}</code></pre>\n\n"
        f"<b>Explanation:</b>\n{html.escape(result.explanation)}\n\n"
        f"<b>Suggestions to improve the code:</b>\n{html.escape(result.suggestions)}"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text(WELCOME)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text(
            "Send code, an error message, or both. Use /debug followed by your submission "
            "when you want to explicitly start a debugging request."
        )


async def debug_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Split only once so pasted multiline code remains intact.
    submission = (update.message.text.partition(" ")[2] if update.message else "").strip()
    if not submission:
        if update.message:
            await update.message.reply_text("Usage: /debug <paste code or an error message>")
        return
    await process_debug(update, context, submission)


async def message_debug(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message and update.message.text:
        await process_debug(update, context, update.message.text)


async def process_debug(update: Update, context: ContextTypes.DEFAULT_TYPE, submission: str) -> None:
    message = update.message
    ai: DebuggerAI = context.application.bot_data["ai"]
    database: Database = context.application.bot_data["database"]
    if not message:
        return
    if len(submission) > MAX_SUBMISSION_LENGTH:
        await message.reply_text(f"Please keep submissions under {MAX_SUBMISSION_LENGTH:,} characters.")
        return

    try:
        await context.bot.send_chat_action(message.chat_id, ChatAction.TYPING)
        result = await ai.debug(submission)
        await database.save_request(message.from_user.id, result.language, submission)
        # Telegram's default message limit is 4096 characters.
        rendered = format_result(result)
        if len(rendered) <= 4096:
            await message.reply_text(rendered, parse_mode="HTML")
        else:
            await message.reply_text(rendered[:4000] + "\n\n[Response truncated due to Telegram length limit.]", parse_mode="HTML")
    except Exception:
        LOGGER.exception("Debug request failed")
        await message.reply_text("I couldn't analyze that submission right now. Please try again shortly.")
