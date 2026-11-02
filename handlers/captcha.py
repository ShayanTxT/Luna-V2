import asyncio
import random
import uuid
from aiogram import Router, F, Bot
from aiogram.types import ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER
from aiogram.types import ChatPermissions
from database.db import upsert_group, get_group, set_captcha_state, get_captcha_state, clear_captcha_state
import html

router = Router()

# Background tasks store to avoid blocking handler
_pending_tasks = set()

@router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def on_new_member(event: ChatMemberUpdated, bot: Bot):
    chat_id = event.chat.id
    user = event.new_chat_member.user
    if user.is_bot:
        return

    await upsert_group(chat_id, event.chat.title or "")
    group = await get_group(chat_id)
    if not group:
        return

    if not group.get("captcha_enabled", 1):
        if group.get("welcome_enabled", 1):
            welcome = group.get("welcome_text") or "Hi {name} welcome to {title} 🎉"
            text = welcome.replace("{name}", html.escape(user.first_name)).replace("{title}", html.escape(event.chat.title or "group"))
            try:
                await bot.send_message(chat_id, text)
            except Exception:
                pass
        return

    try:
        await bot.restrict_chat_member(
            chat_id, user.id,
            permissions=ChatPermissions(can_send_messages=False, can_send_media_messages=False, can_send_other_messages=False)
        )
    except Exception:
        pass

    a, b = random.randint(1, 9), random.randint(1, 9)
    ans = a + b
    fake1, fake2 = ans + 2, ans - 1 if ans > 1 else ans + 3
    # Shuffle options and store correct server-side (not in callback_data)
    options = [ans, fake1, fake2]
    random.shuffle(options)
    token = str(uuid.uuid4())[:8]
    await set_captcha_state(chat_id, user.id, ans, expire_seconds=120)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=str(opt), callback_data=f"verify_{user.id}_{opt}_{token}")]
        for opt in options
    ])

    welcome = group.get("welcome_text") or "Hi {name} welcome to {title} 🎉"
    text = welcome.replace("{name}", html.escape(user.first_name)).replace("{title}", html.escape(event.chat.title or "group"))
    text += f"\n\n🧩 Verify you're human: {a} + {b} = ?"

    try:
        msg = await bot.send_message(chat_id, text, reply_markup=keyboard)
        # Run verification timeout as background task
        task = asyncio.create_task(verification_timeout(bot, chat_id, user.id, msg.message_id))
        _pending_tasks.add(task)
        task.add_done_callback(_pending_tasks.discard)
    except Exception:
        pass

async def verification_timeout(bot: Bot, chat_id: int, user_id: int, msg_id: int):
    await asyncio.sleep(120)
    correct = await get_captcha_state(chat_id, user_id)
    if correct is None:
        return  # Already verified or expired
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        if member.status == "restricted":
            await bot.ban_chat_member(chat_id, user_id)
            await bot.unban_chat_member(chat_id, user_id)
            try:
                await bot.delete_message(chat_id, msg_id)
            except Exception:
                pass
    except Exception:
        pass
    finally:
        await clear_captcha_state(chat_id, user_id)

@router.callback_query(F.data.startswith("verify_"))
async def verify_callback(call: CallbackQuery, bot: Bot):
    try:
        _, uid, chosen, _token = call.data.split("_", 3)
        uid = int(uid)
        chosen = int(chosen)
        if call.from_user.id != uid:
            return await call.answer("Not for you", show_alert=True)

        correct = await get_captcha_state(call.message.chat.id, uid)
        if correct is None:
            return await call.answer("Expired, please rejoin", show_alert=True)

        if chosen == correct:
            await bot.restrict_chat_member(
                call.message.chat.id, uid,
                permissions=ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True)
            )
            await clear_captcha_state(call.message.chat.id, uid)
            await call.message.edit_text(f"✅ {html.escape(call.from_user.first_name)} verified, welcome!")
            await call.answer("Welcome!")
        else:
            await call.answer("Wrong, try again", show_alert=True)
    except Exception:
        await call.answer("Error", show_alert=True)
