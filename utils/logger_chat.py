"""
Logging configuration and chat logger
"""

import logging
from pathlib import Path
from telegram import Bot
from config import LOG_CHAT_ID


def setup_logging(level: str = "INFO"):
    """Setup logging configuration."""
    # Create logs directory if it doesn't exist
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=getattr(logging, level.upper()),
        handlers=[
            logging.FileHandler('logs/miku_bot.log'),
            logging.StreamHandler()
        ]
    )

    # Reduce telegram library logging
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('telegram').setLevel(logging.WARNING)


async def log_to_chat(bot: Bot, message: str):
    """Send log message to log chat if configured."""
    if LOG_CHAT_ID:
        try:
            await bot.send_message(chat_id=LOG_CHAT_ID, text=message)
        except Exception as e:
            logging.error(f"Failed to send log to chat: {e}")