from openai import AsyncOpenAI
from config import API_POOL as CONFIG_POOL, PERSONALITIES
from database.db import save_message, get_history, get_group, get_api_providers
from core.tokens import estimate_tokens, truncate_text, is_simple_query
from services.rag import search_knowledge
from services.ai_cache import get_cached, set_cached, init_cache
from core.logger import logger
import random

OFFLINE_RESPONSES = [
    "😂 {name} my brain is offline, try again in a minute!",
]

PERSONALITY_OFFLINE = {
    "shookh": "😜 {name} wow! But my brain is off right now...",
    "naz": "💖 {name} dear, I can't answer now 🥺",
    "lati": "😎 {name} my friend, my brain is down",
    "rok": "🔥 {name} hold on 😂 I'm offline",
}

# Simple intent cache - avoids LLM for greetings
SIMPLE_REPLIES = {
    "سلام": "سلام عزیزم! چطوری؟ 😊",
    "hi": "Hi! How can I help? ✨",
    "hello": "Hello! 👋",
    "مرسی": "قربونت 😘",
}

async def get_api_pool():
    try:
        db_pool = await get_api_providers()
        if db_pool:
            return [{"name": p["name"], "base_url": p["base_url"], "api_key": p["api_key"], "model": p["model"]} for p in db_pool]
    except Exception as e:
        logger.warning(f"DB pool read error: {e}")
    if CONFIG_POOL:
        return CONFIG_POOL
    return []

async def summarize_history(chat_id: int, history: list[dict]) -> list[dict]:
    """If history too long, summarize old part to save tokens"""
    total = sum(estimate_tokens(m["content"]) for m in history)
    if total < 800:
        return history
    # Keep last 6, summarize rest
    old = history[:-6]
    recent = history[-6:]
    # Simple extractive summary (first 200 chars per old message)
    summary = " | ".join(m["content"][:120] for m in old[-4:])
    summary_msg = {"role": "user", "content": f"[Summary of earlier chat: {summary[:400]}]"}
    logger.info(f"History compressed {len(history)} -> {len(recent)+1} (saved ~{total-400} tokens)")
    return [summary_msg] + recent

async def get_ai_response(chat_id: int, user_name: str, user_text: str, reply_to_text: str = None) -> str:
    # Ensure cache table exists
    try:
        await init_cache()
    except Exception:
        pass

    user_text = truncate_text(user_text, 400)  # limit input to 400 tokens

    # 1. Check simple replies (0 tokens)
    simple_key = user_text.strip().lower()
    if simple_key in SIMPLE_REPLIES:
        return SIMPLE_REPLIES[simple_key]

    # 2. Check RAG knowledge base (0 tokens)
    try:
        rag_answer = await search_knowledge(chat_id, user_text)
        if rag_answer:
            logger.info(f"RAG hit for chat {chat_id}")
            return rag_answer + " 📚"
    except Exception as e:
        logger.debug(f"RAG miss: {e}")

    # 3. Check semantic cache (0 tokens)
    cache_key = f"{user_name}:{user_text}"
    try:
        cached = await get_cached(cache_key, chat_id)
        if cached:
            logger.info(f"Cache hit saved tokens")
            return cached
    except Exception:
        pass

    group = await get_group(chat_id)
    personality_key = group["personality"] if group and group.get("personality") else "shookh"
    personality = PERSONALITIES.get(personality_key, PERSONALITIES["shookh"])
    system_prompt = personality["prompt"]

    full_user_msg = f"{user_name}: {user_text}"
    if reply_to_text:
        full_user_msg += f" (in reply to: {reply_to_text[:200]})"

    await save_message(chat_id, "user", full_user_msg)
    history = await get_history(chat_id, limit=14)
    history = await summarize_history(chat_id, history)

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    if not history or history[-1]["content"] != full_user_msg:
        # Avoid duplicate if already in history
        if not any(m["content"] == full_user_msg for m in history):
            messages.append({"role": "user", "content": full_user_msg})

    # Estimate tokens
    input_tokens = sum(estimate_tokens(m["content"]) for m in messages)
    logger.info(f"AI request tokens ~{input_tokens}")

    pool = await get_api_pool()
    if not pool:
        template = PERSONALITY_OFFLINE.get(personality_key, SIMPLE_REPLIES["سلام"])
        answer = template.format(name=user_name)
        await save_message(chat_id, "assistant", answer)
        return answer

    last_error = ""
    for provider in pool:
        try:
            client = AsyncOpenAI(api_key=provider["api_key"], base_url=provider["base_url"])
            # Use lower max_tokens for simple queries to save tokens
            max_out = 120 if is_simple_query(user_text) else 300
            resp = await client.chat.completions.create(
                model=provider["model"],
                messages=messages,
                max_tokens=max_out,
                temperature=0.85,
            )
            answer = resp.choices[0].message.content.strip()
            # Cache it
            try:
                await set_cached(cache_key, chat_id, answer, tokens=input_tokens)
            except Exception:
                pass
            await save_message(chat_id, "assistant", answer)
            return answer
        except Exception as e:
            last_error = str(e)[:150]
            logger.warning(f"Provider {provider['name']} failed: {e}")
            continue

    fallback = f"😵 {user_name} all APIs failed: {last_error[:60]}"
    await save_message(chat_id, "assistant", fallback)
    return fallback
