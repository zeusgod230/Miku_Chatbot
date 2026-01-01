from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from db.database import Database
from config import DATABASE_PATH
import logging

logger = logging.getLogger(__name__)
db = Database(DATABASE_PATH)

def check_blocked(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id

        if db.is_user_blocked(user_id):
            logger.info(f"Blocked user {user_id} attempted to interact")
            await update.message.reply_text(
                "...I'm not talking to you right now."
            )
            return

        return await func(update, context)

    return wrapper