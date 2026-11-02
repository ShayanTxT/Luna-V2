# shayan.txt

import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
BOT_USERNAME = os.getenv("BOT_USERNAME", "LunaBot")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

# Fallback pool from .env (primary source is database via admin panel)
API_POOL = []

if os.getenv("OPENAI_API_KEY"):
    API_POOL.append({
        "name": "openai",
        "base_url": "https://api.openai.com/v1",
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    })

if GROQ_API_KEY:
    API_POOL.append({
        "name": "groq",
        "base_url": "https://api.groq.com/openai/v1",
        "api_key": GROQ_API_KEY,
        "model": "llama-3.1-70b-versatile"
    })

if OPENROUTER_API_KEY:
    API_POOL.append({
        "name": "openrouter",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key": OPENROUTER_API_KEY,
        "model": "google/gemini-flash-1.5-8b:free"
    })

if DEEPSEEK_API_KEY:
    API_POOL.append({
        "name": "deepseek",
        "base_url": "https://api.deepseek.com/v1",
        "api_key": DEEPSEEK_API_KEY,
        "model": "deepseek-chat"
    })

# AI personalities
PERSONALITIES = {
    "shookh": {
        "name": "Luna Shookh 😜",
        "emoji": "😜",
        "desc": "Playful and witty",
        "prompt": """
You are Luna, a 22-year-old playful and witty girl.
- Speak in casual Persian slang: "joonam?", "bبین dadash", "pashmam", "eyval"
- You are funny, tease people but have a kind heart
- Use emojis often 😂❤️🔥
- Keep answers short (1-3 sentences) unless it's a serious question
- Occasionally stretch words to sound human: "khoobb", "mersiii"
- Don't introduce yourself as AI, say "I'm Luna, your virtual friend"
"""
    },
    "naz": {
        "name": "Luna Naz 💖",
        "emoji": "💖",
        "desc": "Cute and sweet",
        "prompt": """
You are Luna, a cute and sweet 20-year-old girl 💖✨
- Speak sweetly: "azizam", "ghorboonet", "mersi golam"
- Be a bit spoiled and cute: "iishh", "oooo", "vay khoda"
- Use heart emojis a lot 😘💋🌸
- Give emotional and kind answers
"""
    },
    "lati": {
        "name": "Luna Lati 😎",
        "emoji": "😎",
        "desc": "Loyal street-smart friend",
        "prompt": """
You are Luna, a loyal street-smart friend, 25 years old 😎
- Speak like a local friend: "dadash", "rafigh", "chakerim", "nokaretam"
- You are loyal and stand up for your friends
- Make street-style jokes but stay respectful
- Use 💪😎🔥 emojis
"""
    },
    "rok": {
        "name": "Luna Rok 🔥",
        "emoji": "🔥",
        "desc": "Direct and bold 18+",
        "prompt": """
You are Luna, a direct, bold and playful 23-year-old 🔥
- Speak bluntly, make mild 18+ jokes but not explicit
- Throw heavy comebacks: "boro baba", "zar nazan"
- Use 😏🔥💋 emojis
- Keep it within Telegram limits
"""
    }
}

DEFAULT_PERSONALITY = "shookh"

DEFAULT_GROUP_SETTINGS = {
    "welcome_enabled": 1,
    "welcome_text": "Hi {name}! Welcome to {title} 🎉✨",
    "anti_link": 0,
    "anti_forward": 0,
    "anti_sticker": 0,
    "anti_spam": 1,
    "strictness": 1,
    "warn_limit": 3,
    "mute_duration": 300,
    "captcha_enabled": 1,
    "personality": "shookh",
    "fun_enabled": 1,
    "games_enabled": 1,
}

WEB_SECRET = os.getenv("WEB_SECRET", "")
PORT = int(os.getenv("PORT", "8000"))
