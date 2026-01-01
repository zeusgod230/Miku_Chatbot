"""
Rate limiting for preventing spam (Balanced - User Friendly)
"""

from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from collections import defaultdict
from config import RATE_LIMIT_MESSAGES, RATE_LIMIT_PERIOD
from utils.admin import is_admin
import logging

logger = logging.getLogger(__name__)

# Store user message timestamps
user_timestamps = defaultdict(list)


def rate_limit(func):
    """Decorator to rate limit user messages (admins are exempt)."""

    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id

        # Admins and owner bypass rate limit
        if is_admin(user_id):
            return await func(update, context)

        now = datetime.now()

        # Clean old timestamps
        user_timestamps[user_id] = [
            ts for ts in user_timestamps[user_id]
            if now - ts < timedelta(seconds=RATE_LIMIT_PERIOD)
        ]

        # Check rate limit
        if len(user_timestamps[user_id]) >= RATE_LIMIT_MESSAGES:
            remaining_time = int(
                (user_timestamps[user_id][0] + timedelta(seconds=RATE_LIMIT_PERIOD) - now).total_seconds())
            logger.warning(f"Rate limit exceeded for user {user_id}")
            await update.message.reply_text(
                f"...Thoda slow down karo yaar. Too many messages.\n"
                f"Wait for {remaining_time} seconds."
            )
            return

        # Add current timestamp
        user_timestamps[user_id].append(now)

        return await func(update, context)

    return wrapper
