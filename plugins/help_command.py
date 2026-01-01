"""
Help command handler
"""

from telegram import Update
from telegram.ext import ContextTypes
from utils import check_blocked
from utils.admin import is_admin
import logging

logger = logging.getLogger(__name__)


@check_blocked
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    user_id = update.effective_user.id

    help_text = """
🎧 **Miku Nakano Bot - Help**

Just talk to me normally and I'll respond in Hinglish. I remember our recent conversations.

**Commands:**
/start - Start the bot
/help - Show this help message
"""

    # Add admin commands if user is admin
    if is_admin(user_id):
        help_text += """/stats - View bot statistics

**Admin Commands:**
/astats - Detailed bot statistics
/broadcast <message> - Broadcast to all users
/confirm_broadcast - Confirm pending broadcast
/block <user_id> - Block a user
/unblock <user_id> - Unblock a user
/sticker_guide - Guide to setup stickers
/reload_stickers - Reload stickers.json

**Sticker Setup:**
Just send any sticker to get its file_id!
"""

    help_text += """
**About Me:**
I'm Miku Nakano from The Quintessential Quintuplets. I love history, especially the Sengoku period, and I'm always listening to music through my headphones.

...That's all you need to know yaar.
    """

    await update.message.reply_text(help_text, parse_mode="Markdown")