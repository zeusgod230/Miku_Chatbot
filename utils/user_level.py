from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from db.database import Database
from config import DATABASE_PATH
import logging

logger = logging.getLogger(__name__)
db = Database(DATABASE_PATH)


class UserLevel:

    NORMAL = 0
    TRUSTED = 1
    MODERATOR = 2
    ADMIN = 3


def check_user_level(required_level: int):
    def decorator(func):
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            user_id = update.effective_user.id
            user = db.get_user(user_id)

            if not user or user.get("user_level", 0) < required_level:
                await update.message.reply_text(
                    "You don't have the required permission level for this."
                )
                return

            return await func(update, context)

        return wrapper

    return decorator


def get_user_level(user_id: int) -> int:
    user = db.get_user(user_id)
    return user.get("user_level", 0) if user else 0


def set_user_level(user_id: int, level: int):
    import sqlite3
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET user_level = ? WHERE user_id = ?",
            (level, user_id)
        )
        conn.commit()