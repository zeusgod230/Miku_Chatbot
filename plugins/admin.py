"""
Admin command handlers - Stats and Broadcast
"""

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from db.database import Database
from config import DATABASE_PATH
from utils.admin import admin_only
import logging
import asyncio

logger = logging.getLogger(__name__)
db = Database(DATABASE_PATH)


@admin_only
async def stats_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show detailed bot statistics (Admin only)."""
    total_users = db.get_total_users()
    total_messages = db.get_total_messages()

    # Get recent active users (last 24 hours)
    import sqlite3
    from datetime import datetime, timedelta

    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()

        # Active users in last 24 hours
        yesterday = datetime.now() - timedelta(days=1)
        cursor.execute("""
            SELECT COUNT(*) FROM users 
            WHERE last_seen > ?
        """, (yesterday,))
        active_24h = cursor.fetchone()[0]

        # Active users in last 7 days
        week_ago = datetime.now() - timedelta(days=7)
        cursor.execute("""
            SELECT COUNT(*) FROM users 
            WHERE last_seen > ?
        """, (week_ago,))
        active_7d = cursor.fetchone()[0]

        # Blocked users count
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_blocked = 1")
        blocked_count = cursor.fetchone()[0]

        # Top 5 active users
        cursor.execute("""
            SELECT first_name, username, message_count 
            FROM users 
            ORDER BY message_count DESC 
            LIMIT 5
        """)
        top_users = cursor.fetchall()

    stats_text = f"""📊 **Bot Statistics (Admin Panel)**

**User Statistics:**
👥 Total Users: {total_users}
📈 Active (24h): {active_24h}
📊 Active (7d): {active_7d}
🚫 Blocked: {blocked_count}

**Message Statistics:**
💬 Total Messages: {total_messages}
📨 Avg per User: {total_messages // total_users if total_users > 0 else 0}

**Top 5 Active Users:**
"""

    for i, (name, username, msg_count) in enumerate(top_users, 1):
        username_str = f"@{username}" if username else "No username"
        stats_text += f"{i}. {name} ({username_str}): {msg_count} msgs\n"

    await update.message.reply_text(stats_text, parse_mode="Markdown")


@admin_only
async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast a message to all users (Admin only)."""
    if not context.args:
        await update.message.reply_text(
            "**Broadcast Usage:**\n"
            "`/broadcast <message>`\n\n"
            "Example:\n"
            "`/broadcast Hello everyone! Bot update coming soon.`",
            parse_mode="Markdown"
        )
        return

    message = " ".join(context.args)

    # Get all users
    import sqlite3
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE is_blocked = 0")
        users = cursor.fetchall()

    total_users = len(users)

    # Confirm broadcast
    confirm_text = (
        f"📢 **Broadcast Confirmation**\n\n"
        f"Message: {message}\n\n"
        f"Will be sent to: {total_users} users\n\n"
        f"Reply with `/confirm_broadcast` to proceed."
    )

    # Store broadcast data in context
    context.user_data['pending_broadcast'] = {
        'message': message,
        'users': users,
        'total': total_users
    }

    await update.message.reply_text(confirm_text, parse_mode="Markdown")


@admin_only
async def confirm_broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm and execute broadcast."""
    if 'pending_broadcast' not in context.user_data:
        await update.message.reply_text("No pending broadcast found. Use `/broadcast` first.")
        return

    broadcast_data = context.user_data['pending_broadcast']
    message = broadcast_data['message']
    users = broadcast_data['users']
    total_users = broadcast_data['total']

    # Start broadcasting
    status_msg = await update.message.reply_text(
        f"📤 Broadcasting to {total_users} users...\n"
        f"Progress: 0/{total_users}"
    )

    success_count = 0
    failed_count = 0

    for i, (user_id,) in enumerate(users, 1):
        try:
            await context.bot.send_message(chat_id=user_id, text=message)
            success_count += 1

            # Update progress every 10 users
            if i % 10 == 0 or i == total_users:
                await status_msg.edit_text(
                    f"📤 Broadcasting...\n"
                    f"Progress: {i}/{total_users}\n"
                    f"✅ Success: {success_count}\n"
                    f"❌ Failed: {failed_count}"
                )

            # Rate limiting to avoid Telegram limits
            await asyncio.sleep(0.05)  # 50ms delay between messages

        except Exception as e:
            failed_count += 1
            logger.error(f"Failed to send broadcast to {user_id}: {e}")

    # Final report
    await status_msg.edit_text(
        f"✅ **Broadcast Complete!**\n\n"
        f"📊 Total: {total_users}\n"
        f"✅ Success: {success_count}\n"
        f"❌ Failed: {failed_count}"
    )

    # Clear pending broadcast
    del context.user_data['pending_broadcast']

    logger.info(f"Broadcast completed by {update.effective_user.id}: {success_count}/{total_users} successful")


@admin_only
async def block_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Block a user from using the bot."""
    if not context.args:
        await update.message.reply_text("Usage: `/block <user_id>`", parse_mode="Markdown")
        return

    try:
        user_id = int(context.args[0])
        db.block_user(user_id)
        await update.message.reply_text(f"✅ User `{user_id}` has been blocked.", parse_mode="Markdown")
        logger.info(f"Admin {update.effective_user.id} blocked user {user_id}")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID. Must be a number.")


@admin_only
async def unblock_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unblock a user."""
    if not context.args:
        await update.message.reply_text("Usage: `/unblock <user_id>`", parse_mode="Markdown")
        return

    try:
        user_id = int(context.args[0])
        db.unblock_user(user_id)
        await update.message.reply_text(f"✅ User `{user_id}` has been unblocked.", parse_mode="Markdown")
        logger.info(f"Admin {update.effective_user.id} unblocked user {user_id}")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID. Must be a number.")


# Register admin handlers
def register_admin_handlers(application):
    """Register all admin command handlers."""
    application.add_handler(CommandHandler("astats", stats_admin_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("confirm_broadcast", confirm_broadcast_command))
    application.add_handler(CommandHandler("block", block_user_command))
    application.add_handler(CommandHandler("unblock", unblock_user_command))