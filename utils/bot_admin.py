from functools import wraps
from telegram import Update, ChatMember
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

def bot_admin_only(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat = update.effective_chat

        if chat.type == "private":
            return await func(update, context)

        bot_member = await chat.get_member(context.bot.id)

        if bot_member.status not in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
            await update.message.reply_text(
                "I need to be an admin to use this feature..."
            )
            return

        return await func(update, context)

    return wrapper

async def is_bot_admin(chat, bot_id: int) -> bool:
    try:
        bot_member = await chat.get_member(bot_id)
        return bot_member.status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]
    except Exception as e:
        logger.error(f"Error checking bot admin status: {e}")
        return False