from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters, CommandHandler
from utils.admin import admin_only
from utils.sticker_helper import get_sticker_setup_guide, reload_stickers
import logging

logger = logging.getLogger(__name__)


@admin_only
async def sticker_guide_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    guide = get_sticker_setup_guide()
    await update.message.reply_text(guide, parse_mode="Markdown")


@admin_only
async def reload_stickers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        count = reload_stickers()
        await update.message.reply_text(
            f"✅ Stickers reloaded successfully!\n"
            f"Loaded {count} categories from stickers.json"
        )
        logger.info(f"Admin {update.effective_user.id} reloaded stickers")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to reload stickers: {e}")
        logger.error(f"Failed to reload stickers: {e}")


async def handle_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sticker = update.message.sticker

    response = (
        f"**Sticker Info:**\n"
        f"File ID: `{sticker.file_id}`\n"
        f"Emoji: {sticker.emoji if sticker.emoji else 'None'}\n"
        f"Set: {sticker.set_name if sticker.set_name else 'None'}\n\n"
        f"Copy the File ID and add it to `stickers.json`\n\n"
        f"**Example format:**\n"
        f"```json\n"
        f'{{\n'
        f'  "greeting": ["{sticker.file_id}"],\n'
        f'  "happy": ["{sticker.file_id}"]\n'
        f'}}\n'
        f"```"
    )

    await update.message.reply_text(response, parse_mode="Markdown")
    logger.info(f"User {update.effective_user.id} queried sticker: {sticker.file_id}")


def register_sticker_handlers(application):
    application.add_handler(CommandHandler("sticker_guide", sticker_guide_command))

    application.add_handler(CommandHandler("reload_stickers", reload_stickers_command))

    application.add_handler(MessageHandler(filters.Sticker.ALL, handle_sticker))