# shayan.txt
from aiogram import Router, F, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart, Command
from core.config import settings

router = Router()

WELCOME_TEXT = """
🌙 **سلام! من لونا هستم**

مدیر باهوش + دوست صمیمی گروهت

✨ **چیکار می‌کنم؟**
• مدیریت گروه (ضد لینک/اسپم/فحش)
• کپچا برای تازه‌واردها
• ۴ شخصیت (شوخ، ناز، لات، رُک)
• جوک، فال، بازی کلمه + امتیاز
• هوش مصنوعی با حافظه گروه

👇 منو به گروهت اضافه کن و ادمین کن
"""

def get_start_keyboard(is_private: bool = False):
    if is_private:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ افزودن به گروه", url=f"https://t.me/{settings.BOT_USERNAME}?startgroup=true")],
            [InlineKeyboardButton(text="🎛️ پنل مدیریت", callback_data="panel_help")],
            [InlineKeyboardButton(text="🎭 شخصیت‌ها", callback_data="show_personalities")],
        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📖 راهنما", callback_data="help")],
            [InlineKeyboardButton(text="🎛️ پنل", callback_data="panel_help")],
        ])

@router.message(CommandStart())
async def start_handler(message: Message, bot: Bot):
    # Different behavior for private vs group
    if message.chat.type == "private":
        await message.answer(WELCOME_TEXT, reply_markup=get_start_keyboard(True))
    else:
        await message.answer(
            f"سلام {message.from_user.first_name}! 👋\nمن لونا‌م، آماده‌ام گروه رو مدیریت کنم.\nبرای دیدن دستورات /help بزن",
            reply_markup=get_start_keyboard(False)
        )

@router.message(Command("help"))
async def help_handler(message: Message):
    text = """
🤖 **راهنمای لونا**

🛡️ **مدیریت (فقط ادمین):**
/ban - بن (ریپلای)
/kick - کیک
/mute /unmute - سکوت
/warn - اخطار (۳ = بن)
/purge - پاکسازی
/pin - سنجاق
/personality - تغییر شخصیت
/setwelcome متن - خوش‌آمد

💬 **هوش:**
لونا رو تگ کن یا ریپلای کن
/ai سوال - سوال مستقیم
/ask سوال - از دانش گروه
/summarize - خلاصه چت

🎮 **فان:**
/jok - جوک
/fal - فال
/word - حدس کلمه
/quiz - کوییز
/top - برترین‌ها

📚 **دانش:**
/learn سوال | جواب - آموزش
/knowledge - لیست دانش
"""
    await message.answer(text)

@router.callback_query(F.data == "help")
async def help_cb(call: CallbackQuery):
    await help_handler(call.message)
    await call.answer()

@router.callback_query(F.data == "panel_help")
async def panel_cb(call: CallbackQuery):
    await call.message.answer(
        f"🎛️ **پنل مدیریت:**\nhttp://localhost:{settings.PORT}/admin\n\n"
        f"روی هاست: https://your-domain.com/admin\n"
        f"از اونجا ضد لینک، کپچا، شخصیت و API رو تنظیم کن"
    )
    await call.answer()

@router.callback_query(F.data == "show_personalities")
async def personalities_cb(call: CallbackQuery):
    from config import PERSONALITIES
    text = "🎭 **شخصیت‌های لونا:**\n\n"
    for k, v in PERSONALITIES.items():
        text += f"{v['emoji']} **{v['name']}** - {v['desc']}\n"
    text += "\nبرای تغییر: /personality"
    await call.message.answer(text)
    await call.answer()

@router.message(Command("ping"))
async def ping_handler(message: Message):
    await message.reply("🏓 پونگ! آنلاینم ✅")
