import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import BOT_TOKEN, LOG_LEVEL
from plugins import start, chat, help_command, stats
from utils.logger_chat import setup_logging

logger = logging.getLogger(__name__)


def main():

    setup_logging(LOG_LEVEL)
    logger.info("Starting Miku Nakano Bot...")

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start.start_command))
    application.add_handler(CommandHandler("help", help_command.help_command))
    application.add_handler(CommandHandler("stats", stats.stats_command))

    from plugins.admin import register_admin_handlers
    register_admin_handlers(application)

    from plugins.sticker_setup import register_sticker_handlers
    register_sticker_handlers(application)

    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        chat.handle_message
    ))
    application.add_error_handler(error_handler)

    logger.info("Bot started successfully! Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

async def error_handler(update: Update, context):
    logger.error(f"Exception while handling an update: {context.error}")

if __name__ == "__main__":
    main()