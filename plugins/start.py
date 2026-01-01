from telegram import Update
from telegram.ext import ContextTypes
from db.database import Database
from config import DATABASE_PATH
from utils import check_blocked
import logging

logger = logging.getLogger(__name__)
db = Database(DATABASE_PATH)


@check_blocked
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    db.add_user(
        user_id=user.id,
        username=user.username or "",
        first_name=user.first_name,
        last_name=user.last_name or ""
    )

    welcome_message = (
        f"...Hello, {user.first_name}.\n\n"
        "I'm Miku Nakano. What do you want?\n\n"
        "You can talk to me normally, and I'll respond. "
        "If you need help, use /help."
    )

    await update.message.reply_text(welcome_message)
    logger.info(f"New user started bot: {user.id} (@{user.username})")