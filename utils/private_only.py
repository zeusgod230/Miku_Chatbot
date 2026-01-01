"""
Private chat only decorator
"""

from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)


def private_only(func):
    """Decorator to restrict command to private chats only."""

    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_type = update.effective_chat.type

        if chat_type != "private":
            await update.message.reply_text(
                "This command only works in private chat. Message me directly."
            )
            return

        return await func(update, context)

    return wrapper