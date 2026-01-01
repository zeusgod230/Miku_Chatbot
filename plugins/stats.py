"""
Statistics command handler (Admin Only)
"""

from telegram import Update
from telegram.ext import ContextTypes
from db.database import Database
from config import DATABASE_PATH
from utils.block_list import check_blocked
from utils.admin import admin_only
import logging

logger = logging.getLogger(__name__)
db = Database(DATABASE_PATH)


@admin_only
@check_blocked
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command (Admin/Owner only)."""
    user_id = update.effective_user.id

    # Get user stats
    user = db.get_user(user_id)
    total_users = db.get_total_users()
    total_messages = db.get_total_messages()

    if user:
        user_message_count = user.get("message_count", 0)
        first_seen = user.get("first_seen", "Unknown")

        stats_text = f"""
📊 **Bot Statistics**

**Your Stats:**
Messages sent: {user_message_count}
Member since: {first_seen[:10]}

**Global Stats:**
Total users: {total_users}
Total messages: {total_messages}

...I guess you talk to me quite a bit yaar.

💡 *Tip: Use /astats for detailed admin statistics*
        """
    else:
        stats_text = "...I don't have any data on you yet."

    await update.message.reply_text(stats_text, parse_mode="Markdown")