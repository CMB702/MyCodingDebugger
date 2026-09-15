"""Entrypoint for the AI Coding Debugger Telegram bot."""

import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from ai_client import DebuggerAI
from config import get_settings
from database import Database
from handlers import debug_command, help_command, message_debug, start


async def post_init(application: Application) -> None:
    await application.bot_data["database"].initialize()


async def error_handler(update: object, context: object) -> None:
    """Record framework failures without writing message or credential content to logs."""
    logging.getLogger(__name__).exception("Unhandled Telegram update error")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    settings = get_settings()
    application = Application.builder().token(settings.telegram_bot_token).post_init(post_init).build()
    application.bot_data["ai"] = DebuggerAI(settings)
    application.bot_data["database"] = Database(settings.database_path)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("debug", debug_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_debug))
    application.add_error_handler(error_handler)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
