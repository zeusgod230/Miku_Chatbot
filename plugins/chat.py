"""
Chat message handler with multiple AI provider support and sticker support
"""

from telegram import Update
from telegram.ext import ContextTypes
from db.database import Database
from config import (DATABASE_PATH, AI_PROVIDER, GROQ_API_KEY,
                    COHERE_API_KEY, MIKU_SYSTEM_PROMPT)
from utils import check_blocked, rate_limit
from utils.chat_engine import MikuChatEngine
from utils.sticker_helper import send_sticker_with_message
import httpx
import logging

logger = logging.getLogger(__name__)
db = Database(DATABASE_PATH)
rule_based_chat = MikuChatEngine()


@check_blocked
@rate_limit
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular chat messages."""
    user = update.effective_user
    message_text = update.message.text

    # Add/update user
    db.add_user(
        user_id=user.id,
        username=user.username or "",
        first_name=user.first_name,
        last_name=user.last_name or ""
    )

    # Increment message count
    db.increment_message_count(user.id)

    # Show typing indicator
    await update.message.chat.send_action("typing")

    try:
        # Get response based on provider
        if AI_PROVIDER == "groq" and GROQ_API_KEY:
            response = await get_groq_response(user.id, message_text)
        elif AI_PROVIDER == "cohere" and COHERE_API_KEY:
            response = await get_cohere_response(user.id, message_text)
        else:
            # Default to rule-based (100% free)
            response = rule_based_chat.get_response(message_text, user.first_name)

        # Save to database
        db.save_chat(user.id, message_text, response)

        # Send response with sticker (if configured)
        await send_sticker_with_message(update, context, response, message_text)

    except Exception as e:
        logger.error(f"Error generating response: {e}")
        await update.message.reply_text(
            "...Sorry, I'm having trouble thinking right now. Try again later."
        )


async def get_groq_response(user_id: int, message: str) -> str:
    """Get response from Groq AI with best model (Llama 3.3 70B Versatile)."""
    history = db.get_chat_history(user_id, limit=6)  # Increased for better context

    # Get total message count for warmth tracking
    user_data = db.get_user(user_id)
    message_count = user_data.get("message_count", 0) if user_data else 0

    messages = []
    if history:
        for chat in reversed(history):
            messages.append({"role": "user", "content": chat["message"]})
            messages.append({"role": "assistant", "content": chat["response"]})

    # Add warmth context to system prompt
    warmth_context = f"\n\n[Internal Note: User has sent {message_count} messages. Adjust warmth accordingly based on the Progressive Warmth System.]"

    messages.append({"role": "user", "content": message})

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GROQ_API_KEY}"
            },
            json={
                "model": "llama-3.3-70b-versatile",  # Best free model - world-class performance
                "messages": [
                    {"role": "system", "content": MIKU_SYSTEM_PROMPT + warmth_context},
                    *messages
                ],
                "max_tokens": 200,  # Reduced for more concise Miku-style responses
                "temperature": 0.85,  # Slightly higher for personality variation
                "top_p": 0.95,
                "frequency_penalty": 0.3,  # Reduce repetition
                "presence_penalty": 0.2  # Encourage topic diversity
            }
        )

        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


async def get_cohere_response(user_id: int, message: str) -> str:
    """Get response from Cohere AI with best model (Command R+ 08-2024)."""
    history = db.get_chat_history(user_id, limit=5)

    # Get total message count for warmth tracking
    user_data = db.get_user(user_id)
    message_count = user_data.get("message_count", 0) if user_data else 0

    chat_history = []
    if history:
        for chat in reversed(history):
            chat_history.append({"role": "USER", "message": chat["message"]})
            chat_history.append({"role": "CHATBOT", "message": chat["response"]})

    # Add warmth context to system prompt
    warmth_context = f"\n\n[Internal Note: User has sent {message_count} messages. Adjust warmth accordingly based on the Progressive Warmth System.]"

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://api.cohere.com/v2/chat",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {COHERE_API_KEY}"
            },
            json={
                "model": "command-r-plus-08-2024",  # Best available Cohere model
                "messages": [
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                "chat_history": chat_history,
                "preamble": MIKU_SYSTEM_PROMPT + warmth_context,
                "temperature": 0.85,
                "max_tokens": 200,
                "frequency_penalty": 0.3,
                "presence_penalty": 0.2
            }
        )

        response.raise_for_status()
        data = response.json()

        # Extract text from the new response format
        if "message" in data and "content" in data["message"]:
            for content in data["message"]["content"]:
                if content.get("type") == "text":
                    return content.get("text", "...I don't know what to say.")

        return "...Something went wrong."