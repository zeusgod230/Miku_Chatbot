from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_IDS, OWNER_ID
import logging

logger = logging.getLogger(__name__)

def admin_only(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id

        if user_id not in ADMIN_IDS and user_id != OWNER_ID:
            logger.warning(f"Unauthorized access attempt by user {user_id}")
            await update.message.reply_text(
                "...You don't have permission to use this command."
            )
            return
        return await func(update, context)

    return wrapper


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS or user_id == OWNER_ID

__all__ = ['admin_only', 'is_admin']