# shayan.txt
"""Semantic cache for AI responses"""

import time
import aiosqlite
from database.db import DB_PATH
from core.tokens import hash_prompt

CACHE_TTL = 3600  # 1 hour
CACHE_MAX_TOKENS_SAVED = 0  # stats

async def init_cache():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS ai_cache (
                hash TEXT PRIMARY KEY,
                chat_id INTEGER,
                prompt TEXT,
                response TEXT,
                tokens_saved INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

async def get_cached(prompt: str, chat_id: int) -> str | None:
    h = hash_prompt(f"{chat_id}:{prompt.lower().strip()}")
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT response FROM ai_cache WHERE hash=? AND created_at > datetime('now', '-1 hour')", (h,)) as cur:
            row = await cur.fetchone()
            return row[0] if row else None

async def set_cached(prompt: str, chat_id: int, response: str, tokens: int = 0):
    h = hash_prompt(f"{chat_id}:{prompt.lower().strip()}")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO ai_cache (hash, chat_id, prompt, response, tokens_saved) VALUES (?,?,?,?,?)",
            (h, chat_id, prompt[:500], response[:2000], tokens)
        )
        # Keep only 200 recent entries
        await db.execute("DELETE FROM ai_cache WHERE rowid NOT IN (SELECT rowid FROM ai_cache ORDER BY created_at DESC LIMIT 200)")
        await db.commit()

async def cache_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*), COALESCE(SUM(tokens_saved),0) FROM ai_cache") as cur:
            row = await cur.fetchone()
            return {"entries": row[0], "tokens_saved": row[1]}
