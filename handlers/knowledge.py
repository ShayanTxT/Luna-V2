# shayan.txt
"""Knowledge base management for next-gen RAG"""

from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import Command
from database.db import get_group
from services.rag import add_knowledge, list_knowledge, search_knowledge
import html

router = Router()

async def is_admin(bot: Bot, chat_id: int, user_id: int):
    try:
        m = await bot.get_chat_member(chat_id, user_id)
        return m.status in ["administrator", "creator"]
    except Exception:
        return False

@router.message(Command("learn"))
async def learn_cmd(message: Message, bot: Bot):
    if not await is_admin(bot, message.chat.id, message.from_user.id):
        return await message.reply("Only admins can teach Luna")
    # Format: /learn question | answer
    text = message.text.replace("/learn", "").strip()
    if "|" not in text:
        return await message.reply("Usage: /learn question | answer\nExample: /learn قوانین گروه چیست | 1- احترام 2- بدون اسپم")
    q, a = [x.strip() for x in text.split("|", 1)]
    if len(q) < 5 or len(a) < 5:
        return await message.reply("Question and answer too short")
    await add_knowledge(message.chat.id, q, a, message.from_user.id)
    await message.reply(f"✅ Learned: <b>{html.escape(q)}</b>")

@router.message(Command("knowledge"))
async def knowledge_list(message: Message):
    items = await list_knowledge(message.chat.id)
    if not items:
        return await message.reply("No knowledge yet. Use /learn to teach me")
    text = "📚 <b>Group knowledge:</b>\n\n"
    for i, it in enumerate(items[:10], 1):
        text += f"{i}. <b>{html.escape(it['question'][:40])}</b> - hits: {it['hits']}\n"
    await message.reply(text)

@router.message(Command("ask"))
async def ask_cmd(message: Message, bot: Bot):
    query = message.text.replace("/ask", "").strip()
    if not query:
        return await message.reply("Ask from knowledge: /ask قوانین چیست")
    ans = await search_knowledge(message.chat.id, query)
    if ans:
        await message.reply(f"📚 <b>From knowledge:</b>\n{html.escape(ans)}")
    else:
        await message.reply("Not found in knowledge, try mentioning Luna")

@router.message(Command("summarize"))
async def summarize_cmd(message: Message, bot: Bot):
    from database.db import get_history
    from core.tokens import estimate_tokens
    history = await get_history(message.chat.id, limit=30)
    if len(history) < 5:
        return await message.reply("Not enough messages to summarize")
    # Build prompt for summarization (token efficient: use smallest model)
    conversation = "\n".join(f"{h['role']}: {h['content'][:120]}" for h in history[-20:])
    prompt = f"Summarize this group chat in Persian, 3 bullet points:\n{conversation[:1500]}"
    from utils.ai import get_ai_response
    # Force low tokens
    await bot.send_chat_action(message.chat.id, "typing")
    summary = await get_ai_response(message.chat.id, "System", prompt)
    await message.reply(f"📝 <b>خلاصه:</b>\n{summary}")
