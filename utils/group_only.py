"""
Group chat only decorator
"""

from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)


def group_only(func):
    """Decorator to restrict command to group chats only."""

    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_type = update.effective_chat.type

        if chat_type == "private":
            await update.message.reply_text(
                "This command only works in groups."
            )
            return

        return await func(update, context)

    return wrapper