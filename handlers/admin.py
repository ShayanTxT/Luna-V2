import asyncio
import html
from aiogram import Router, F, Bot
from aiogram.types import Message, ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from datetime import timedelta, datetime
from database.db import upsert_group, update_group, add_warn, reset_warn, get_group
from config import PERSONALITIES
from core.security import sanitize

router = Router()

async def is_admin(bot: Bot, chat_id: int, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in ["administrator", "creator"]
    except Exception:
        return False

@router.message(Command("ban"))
async def ban_user(message: Message, bot: Bot):
    if not await is_admin(bot, message.chat.id, message.from_user.id):
        return await message.reply("⛔ Admins only")
    if not message.reply_to_message:
        return await message.reply("Reply to a user to ban")
    target = message.reply_to_message.from_user
    # Prevent banning admins or bots
    try:
        target_member = await bot.get_chat_member(message.chat.id, target.id)
        if target_member.status in ["administrator", "creator"]:
            return await message.reply("Cannot ban an admin")
    except Exception:
        pass
    try:
        await bot.ban_chat_member(message.chat.id, target.id)
        await message.reply(f"🔨 {html.escape(target.first_name)} banned")
    except Exception as e:
        await message.reply(f"Failed: {html.escape(str(e))}")

@router.message(Command("unban"))
async def unban_user(message: Message, bot: Bot):
    if not await is_admin(bot, message.chat.id, message.from_user.id):
        return
    if not message.reply_to_message:
        return await message.reply("Reply to a user")
    target = message.reply_to_message.from_user
    await bot.unban_chat_member(message.chat.id, target.id)
    await message.reply(f"✅ {html.escape(target.first_name)} unbanned")

@router.message(Command("kick"))
async def kick_user(message: Message, bot: Bot):
    if not await is_admin(bot, message.chat.id, message.from_user.id):
        return
    if not message.reply_to_message:
        return await message.reply("Reply to a user")
    target = message.reply_to_message.from_user
    try:
        m = await bot.get_chat_member(message.chat.id, target.id)
        if m.status in ["administrator", "creator"]:
            return await message.reply("Cannot kick admin")
    except Exception:
        pass
    await bot.ban_chat_member(message.chat.id, target.id)
    await bot.unban_chat_member(message.chat.id, target.id)
    await message.reply(f"👢 {html.escape(target.first_name)} kicked")

@router.message(Command("mute"))
async def mute_user(message: Message, bot: Bot):
    if not await is_admin(bot, message.chat.id, message.from_user.id):
        return
    if not message.reply_to_message:
        return await message.reply("Reply to a user")
    target = message.reply_to_message.from_user
    group = await get_group(message.chat.id)
    duration = group["mute_duration"] if group and group.get("mute_duration") else 300
    # Clamp duration
    duration = max(60, min(duration, 86400))
    until = datetime.now() + timedelta(seconds=duration)
    await bot.restrict_chat_member(message.chat.id, target.id, permissions=ChatPermissions(can_send_messages=False), until_date=until)
    await message.reply(f"🔇 {html.escape(target.first_name)} muted for {duration // 60} min")

@router.message(Command("unmute"))
async def unmute_user(message: Message, bot: Bot):
    if not await is_admin(bot, message.chat.id, message.from_user.id):
        return
    if not message.reply_to_message:
        return
    target = message.reply_to_message.from_user
    await bot.restrict_chat_member(message.chat.id, target.id, permissions=ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True))
    await message.reply(f"🔊 {html.escape(target.first_name)} unmuted")

@router.message(Command("warn"))
async def warn_user(message: Message, bot: Bot):
    if not await is_admin(bot, message.chat.id, message.from_user.id):
        return
    if not message.reply_to_message:
        return await message.reply("Reply to a user")
    target = message.reply_to_message.from_user
    group = await get_group(message.chat.id)
    limit = group["warn_limit"] if group else 3
    count = await add_warn(message.chat.id, target.id)
    await message.reply(f"⚠️ {html.escape(target.first_name)} warned {count}/{limit}")
    if count >= limit:
        await bot.ban_chat_member(message.chat.id, target.id)
        await message.reply(f"🚫 {html.escape(target.first_name)} banned after {limit} warns")
        await reset_warn(message.chat.id, target.id)

@router.message(Command("purge"))
async def purge(message: Message, bot: Bot):
    if not await is_admin(bot, message.chat.id, message.from_user.id):
        return
    if not message.reply_to_message:
        return await message.reply("Reply to the first message to delete from")
    start_id = message.reply_to_message.message_id
    end_id = message.message_id
    if end_id - start_id > 100:
        return await message.reply("Cannot purge more than 100 messages at once")
    deleted = 0
    for msg_id in range(start_id, end_id + 1):
        try:
            await bot.delete_message(message.chat.id, msg_id)
            deleted += 1
            if deleted % 20 == 0:
                await asyncio.sleep(0.5)  # Avoid rate limit
        except Exception:
            pass
    await message.reply(f"🧹 {deleted} messages deleted")

@router.message(Command("pin"))
async def pin_msg(message: Message, bot: Bot):
    if not await is_admin(bot, message.chat.id, message.from_user.id):
        return
    if not message.reply_to_message:
        return await message.reply("Reply to a message to pin")
    await bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id)
    await message.reply("📌 Pinned")

@router.message(Command("personality"))
async def personality_cmd(message: Message, bot: Bot):
    if message.chat.type != "private" and not await is_admin(bot, message.chat.id, message.from_user.id):
        return await message.reply("Only admins can change personality")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{v['emoji']} {v['name']}", callback_data=f"pers_{k}")]
        for k, v in PERSONALITIES.items()
    ])
    await message.reply("🎭 Choose Luna's personality:", reply_markup=keyboard)

@router.callback_query(F.data.startswith("pers_"))
async def pers_callback(call: CallbackQuery, bot: Bot):
    if call.message.chat.type != "private":
        if not await is_admin(bot, call.message.chat.id, call.from_user.id):
            return await call.answer("Admins only", show_alert=True)
    key = call.data.replace("pers_", "")
    if key not in PERSONALITIES:
        return await call.answer("Invalid", show_alert=True)
    await upsert_group(call.message.chat.id, call.message.chat.title or "")
    await update_group(call.message.chat.id, personality=key)
    info = PERSONALITIES[key]
    await call.message.edit_text(f"✅ Personality changed to {info['name']}\n{info['desc']}")
    await call.answer("Done")

@router.message(Command("panel"))
async def panel_cmd(message: Message):
    await message.reply(
        f"🎛️ <b>Admin Panel</b>\n\n"
        f"Manage your group at:\n"
        f"http://localhost:8000/admin?chat_id={message.chat.id}\n\n"
        f"On your host: https://your-domain.com/admin"
    )

@router.message(Command("help"))
async def help_cmd(message: Message):
    await message.reply(
        "🤖 <b>Luna Help</b>\n\n"
        "🛡️ <b>Admin:</b>\n"
        "/ban /unban /kick /mute /unmute\n"
        "/warn - warn user\n"
        "/purge - delete messages\n"
        "/pin - pin message\n"
        "/personality - change personality\n"
        "/panel - admin panel\n\n"
        "💬 <b>Chat:</b>\n"
        "Mention Luna or reply to chat\n"
        "/ai <question> - ask Luna\n\n"
        "🎮 <b>Games:</b>\n"
        "/jok /fal /word /quiz /top\n"
    )

@router.message(Command("setwelcome"))
async def set_welcome(message: Message, bot: Bot):
    if not await is_admin(bot, message.chat.id, message.from_user.id):
        return
    text = message.text.replace("/setwelcome", "").strip()
    if not text:
        return await message.reply("Usage: /setwelcome Hello {name} welcome to {title}")
    text = sanitize(text, max_len=1000)
    await upsert_group(message.chat.id, message.chat.title or "")
    await update_group(message.chat.id, welcome_text=text)
    await message.reply(f"✅ Welcome message updated:\n{text}")
