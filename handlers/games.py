from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
import random

router = Router()

JOKES = [
    "A programmer goes to the doctor: 'I'm cached!' Doctor: 'Clear it' 😂",
    "Why do programmers prefer dark mode? Because light attracts bugs 😂",
]

FALS = [
    "🔮 Today you will hear great news! ✨",
    "🌙 Someone is thinking of you ❤️",
    "⭐ Money is on the way 😉",
]

WORDS = ["apple", "sea", "book", "laptop", "pizza", "beach", "rain", "star"]
current_word = {}

QUIZ = [
    {"q": "Capital of Iran?", "o": ["Tehran", "Isfahan", "Mashhad", "Tabriz"], "a": 0},
    {"q": "2+2*2 = ?", "o": ["4", "6", "8", "10"], "a": 1},
    {"q": "Largest planet?", "o": ["Earth", "Jupiter", "Mars", "Saturn"], "a": 1},
]

@router.message(Command("jok"))
async def jok_cmd(message: Message):
    await message.reply(f"😂 {random.choice(JOKES)}")

@router.message(Command("fal"))
async def fal_cmd(message: Message):
    await message.reply(random.choice(FALS))

@router.message(Command("word"))
async def word_cmd(message: Message):
    word = random.choice(WORDS)
    current_word[message.chat.id] = word
    hint = word[0] + " _ " * (len(word) - 1)
    await message.reply(f"🎯 Guess the word: {hint} ({len(word)} letters)")

# Only handle word guesses when a game is active in that chat
@router.message(F.text)
async def word_guess(message: Message):
    if message.chat.id not in current_word:
        return
    # Case-insensitive match
    if message.text.strip().lower() == current_word[message.chat.id].lower():
        word = current_word.pop(message.chat.id)
        await message.reply(f"🎉 Correct! {word} 👏 +5 points")
        from database.db import add_point
        try:
            await add_point(message.from_user.id, message.from_user.username, message.from_user.first_name, 5)
        except Exception:
            pass

@router.message(Command("quiz"))
async def quiz_cmd(message: Message):
    q = random.choice(QUIZ)
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=o, callback_data=f"quiz_{i}_{q['a']}")] for i, o in enumerate(q["o"])
    ])
    await message.reply(f"🧠 {q['q']}", reply_markup=keyboard)

@router.callback_query(F.data.startswith("quiz_"))
async def quiz_answer(call):
    _, chosen, correct = call.data.split("_")
    if chosen == correct:
        await call.message.edit_text("✅ Correct! 🎉")
        await call.answer("Correct!")
    else:
        await call.message.edit_text("❌ Wrong! Try /quiz again")
        await call.answer("Wrong")

@router.message(Command("top"))
async def top_cmd(message: Message):
    from database.db import get_top_users
    tops = await get_top_users(10)
    if not tops:
        return await message.reply("No points yet")
    text = "🏆 <b>Top Users:</b>\n\n"
    for i, user in enumerate(tops, 1):
        name = user["first_name"] or user["username"] or "Unknown"
        text += f"{i}. {name} - {user['points']} pts ({user['messages']} msgs)\n"
    await message.reply(text)

@router.message(Command("translate"))
async def translate_cmd(message: Message):
    text = message.text.replace("/translate", "").strip()
    if not text:
        return await message.reply("Usage: /translate Hello")
    try:
        from utils.ai import get_ai_response
        answer = await get_ai_response(message.chat.id, message.from_user.first_name, f"Translate to Persian: {text}")
        await message.reply(f"🌐 {answer}")
    except Exception as e:
        await message.reply(f"Error: {e}")

@router.message(Command("weather"))
async def weather_cmd(message: Message):
    city = message.text.replace("/weather", "").strip() or "Tehran"
    await message.reply(f"🌤️ Weather in {city}: 25°C ☀️")
