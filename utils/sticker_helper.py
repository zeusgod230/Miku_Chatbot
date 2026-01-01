"""
Sticker helper for sending contextual stickers with messages
"""

import random
import re
import json
import os
from config import STICKERS_JSON_PATH, STICKER_CHANCE
from telegram import Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

# Load stickers from JSON file
MIKU_STICKERS = {}


def load_stickers():
    """Load stickers from stickers.json file."""
    global MIKU_STICKERS
    try:
        if os.path.exists(STICKERS_JSON_PATH):
            with open(STICKERS_JSON_PATH, 'r', encoding='utf-8') as f:
                MIKU_STICKERS = json.load(f)
            logger.info(f"Loaded {len(MIKU_STICKERS)} sticker categories from {STICKERS_JSON_PATH}")
        else:
            logger.warning(f"Stickers file not found: {STICKERS_JSON_PATH}")
            MIKU_STICKERS = {}
    except Exception as e:
        logger.error(f"Failed to load stickers: {e}")
        MIKU_STICKERS = {}


# Load stickers on module import
load_stickers()


def should_send_sticker() -> bool:
    """Determine if a sticker should be sent based on chance."""
    return random.random() < STICKER_CHANCE


def detect_emotion(message: str, response: str) -> str:
    """Detect emotion from message and response context."""
    message_lower = message.lower()
    response_lower = response.lower()

    # Greeting
    if re.search(r'\b(hi|hello|hey|namaste)\b', message_lower):
        return "greeting"

    # Happy/positive
    if re.search(r'\b(happy|excited|great|good|nice|khush|mast|acha)\b', message_lower):
        return "happy"

    # Annoyed/negative
    if re.search(r'\b(annoying|irritating|stop|bakwas|chup)\b', message_lower):
        return "annoyed"

    # Shy/compliments
    if re.search(r'\b(cute|beautiful|pretty|love|pyar)\b', message_lower):
        return "shy"

    # Study/serious
    if re.search(r'\b(study|exam|test|history|padhai)\b', message_lower):
        return "studying"

    # Music
    if re.search(r'\b(music|song|listen|gaana)\b', message_lower):
        return "music"

    # Thinking/questions
    if message.endswith('?'):
        return "thinking"

    # Default cool/neutral
    return "cool"


def get_random_sticker_from_category(category: str) -> str:
    """Get a random sticker from a category."""
    if category in MIKU_STICKERS:
        stickers = MIKU_STICKERS[category]
        if isinstance(stickers, list) and stickers:
            return random.choice(stickers)
        elif isinstance(stickers, str):
            return stickers
    return ""


async def send_sticker_with_message(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        text: str,
        message: str
) -> None:
    """Send a sticker with the response if appropriate."""

    # Check if stickers are configured
    if not MIKU_STICKERS:
        # No stickers configured, just send text
        await update.message.reply_text(text)
        return

    # Decide whether to send sticker
    if not should_send_sticker():
        await update.message.reply_text(text)
        return

    # Detect emotion and get appropriate sticker
    emotion = detect_emotion(message, text)
    sticker_id = get_random_sticker_from_category(emotion)

    # If no sticker for this emotion, try default "cool"
    if not sticker_id:
        sticker_id = get_random_sticker_from_category("cool")

    # Send sticker if available
    if sticker_id:
        try:
            await update.message.reply_sticker(sticker=sticker_id)
            # Small delay before text
            import asyncio
            await asyncio.sleep(0.3)
        except Exception as e:
            logger.error(f"Failed to send sticker: {e}")

    # Always send the text
    await update.message.reply_text(text)


def reload_stickers():
    """Reload stickers from JSON file."""
    load_stickers()
    return len(MIKU_STICKERS)


def get_sticker_setup_guide() -> str:
    """Return guide for setting up stickers."""
    return f"""
🎨 **How to Setup Miku Stickers:**

Your bot uses `{STICKERS_JSON_PATH}` for stickers.

**JSON Format:**
```json
{{
  "greeting": ["CAACAgIAAxkBAAIC...", "CAACAgIAAxkBAAID..."],
  "happy": ["CAACAgIAAxkBAAIE..."],
  "thinking": "CAACAgIAAxkBAAIF...",
  "annoyed": ["CAACAgIAAxkBAAIG..."],
  "shy": ["CAACAgIAAxkBAAIH..."],
  "cool": ["CAACAgIAAxkBAAII..."],
  "studying": ["CAACAgIAAxkBAAIJ..."],
  "music": ["CAACAgIAAxkBAAIK..."]
}}
```

**How to add stickers:**
1. Send any sticker to the bot
2. Copy the file_id from the response
3. Add it to your `{STICKERS_JSON_PATH}` file
4. Use `/reload_stickers` to reload without restart

**Notes:**
- You can use arrays for multiple stickers per emotion (bot picks randomly)
- Or use a single string for one sticker per emotion
- Currently loaded: {len(MIKU_STICKERS)} categories

**Available emotions:**
- greeting (for hi/hello)
- thinking (for questions)
- happy (positive messages)
- annoyed (negative/irritating)
- shy (compliments/love)
- cool (default/neutral)
- studying (study/exam topics)
- music (music related)
"""