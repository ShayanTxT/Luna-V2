import re
import asyncio
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import Command
from utils.ai import get_ai_response
from database.db import upsert_group
from core.rate_limiter import limiter

router = Router()

TRIGGER_WORDS = ["luna", "لونا"]

# Use word boundaries to avoid false positives like "bottom" -> "bot"
TRIGGER_PATTERN = re.compile(r"\b(luna|لونا)\b", re.IGNORECASE)

async def should_respond(message: Message, bot: Bot) -> bool:
    if not message.text:
        return False
    text = message.text.lower()
    # Reply to bot
    if message.reply_to_message and message.reply_to_message.from_user.id == bot.id:
        return True
    # Mention
    if bot.username and f"@{bot.username.lower()}" in text:
        return True
    # Word boundary check for trigger words
    if TRIGGER_PATTERN.search(text):
        return True
    return False

@router.message(F.text)
async def ai_handler(message: Message, bot: Bot):
    # Rate limit per user
    if limiter.is_limited(message.chat.id, message.from_user.id):
        return

    if message.chat.type == "private":
        await bot.send_chat_action(message.chat.id, "typing")
        await asyncio.sleep(0.8)
        reply_text = message.reply_to_message.text if message.reply_to_message and message.reply_to_message.text else None
        # Escape HTML in reply
        answer = await get_ai_response(message.chat.id, message.from_user.first_name, message.text, reply_text)
        return await message.reply(answer)

    if not await should_respond(message, bot):
        return

    await upsert_group(message.chat.id, message.chat.title or "")
    await bot.send_chat_action(message.chat.id, "typing")
    await asyncio.sleep(1.0)
    reply_to_text = message.reply_to_message.text if message.reply_to_message and message.reply_to_message.text else None
    answer = await get_ai_response(message.chat.id, message.from_user.first_name, message.text, reply_to_text)
    await message.reply(answer)

@router.message(Command("ai"))
async def ai_command(message: Message):
    if limiter.is_limited(message.chat.id, message.from_user.id):
        return await message.reply("⏳ Slow down, try again in a few seconds")
    prompt = message.text.replace("/ai", "").strip()[:1000]
    if not prompt:
        return await message.reply("Ask something:\n/ai tell a joke")
    await message.bot.send_chat_action(message.chat.id, "typing")
    answer = await get_ai_response(message.chat.id, message.from_user.first_name, prompt)
    await message.reply(answer)
