import asyncio
import random
import html
from aiogram import Router, F, Bot
from aiogram.types import Message, ChatPermissions
from datetime import datetime, timedelta
from utils.filters import contains_link, contains_bad_word, is_flood
from database.db import upsert_group, get_group, add_point
from core.cache import group_cache

router = Router()

# Cache for admin checks (30s)
_admin_cache: dict[tuple[int,int], tuple[bool, float]] = {}
import time

async def is_admin_cached(bot: Bot, chat_id: int, user_id: int) -> bool:
    key = (chat_id, user_id)
    cached = _admin_cache.get(key)
    if cached and time.time() - cached[1] < 30:
        return cached[0]
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        is_admin = member.status in ["administrator", "creator"]
        _admin_cache[key] = (is_admin, time.time())
        return is_admin
    except Exception:
        return False

@router.message(F.text | F.caption)
async def moderation_handler(message: Message, bot: Bot):
    if message.chat.type == "private":
        return

    if message.from_user and not message.from_user.is_bot:
        try:
            await add_point(message.from_user.id, message.from_user.username, message.from_user.first_name, 1)
        except Exception:
            pass

    text = message.text or message.caption or ""

    if await is_admin_cached(bot, message.chat.id, message.from_user.id):
        return

    await upsert_group(message.chat.id, message.chat.title or "")
    group = await get_group(message.chat.id)
    if not group:
        return

    strictness = group.get("strictness", 1)
    anti_link = group.get("anti_link", 0)
    anti_badword = group.get("anti_badword", 1)

    # Anti-link
    if anti_link and contains_link(text):
        try:
            await message.delete()
            name = html.escape(message.from_user.first_name)
            if strictness == 1:
                warn = await message.answer(f"🚫 {name} links not allowed")
            elif strictness == 2:
                warn = await message.answer(f"⚠️ {name} link warning")
            else:
                warn = await message.answer(f"🔨 {name} muted for link")
                until = datetime.now() + timedelta(minutes=5)
                await bot.restrict_chat_member(message.chat.id, message.from_user.id, permissions=ChatPermissions(can_send_messages=False), until_date=until)
            await asyncio.sleep(5)
            try:
                await warn.delete()
            except Exception:
                pass
        except Exception:
            pass
        return

    # Anti-forward: use forward_origin for aiogram 3 (forward_date is deprecated)
    if group.get("anti_forward", 0) and (getattr(message, "forward_origin", None) or getattr(message, "forward_from", None)):
        try:
            await message.delete()
            await message.answer(f"⛔ {html.escape(message.from_user.first_name)} forwarding not allowed")
        except Exception:
            pass
        return

    if anti_badword and contains_bad_word(text):
        try:
            await message.delete()
            await message.answer(random.choice([
                f"😠 {html.escape(message.from_user.first_name)} please watch your language",
                f"😅 {html.escape(message.from_user.first_name)} no bad words please",
            ]))
        except Exception:
            pass
        return

    if group.get("anti_spam", 1) and is_flood(message.from_user.id, message.chat.id):
        try:
            await message.delete()
            until = datetime.now() + timedelta(seconds=group.get("mute_duration", 300))
            await bot.restrict_chat_member(message.chat.id, message.from_user.id, permissions=ChatPermissions(can_send_messages=False), until_date=until)
            await message.answer(f"🤐 {html.escape(message.from_user.first_name)} slow down, muted briefly")
        except Exception:
            pass
