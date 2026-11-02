# shayan.txt

import aiosqlite
import asyncio
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "bot.db"

# Allowed columns for update_group to prevent SQL injection
ALLOWED_GROUP_COLUMNS = {
    "title", "welcome_text", "welcome_enabled", "welcome_buttons",
    "anti_link", "anti_forward", "anti_sticker", "anti_spam", "anti_badword",
    "strictness", "warn_limit", "mute_duration", "captcha_enabled",
    "personality", "fun_enabled", "games_enabled"
}
ALLOWED_API_COLUMNS = {"name", "base_url", "api_key", "model", "enabled", "priority"}

async def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                chat_id INTEGER PRIMARY KEY,
                title TEXT,
                welcome_text TEXT,
                welcome_enabled INTEGER DEFAULT 1,
                welcome_buttons TEXT DEFAULT '[]',
                anti_link INTEGER DEFAULT 0,
                anti_forward INTEGER DEFAULT 0,
                anti_sticker INTEGER DEFAULT 0,
                anti_spam INTEGER DEFAULT 1,
                anti_badword INTEGER DEFAULT 1,
                strictness INTEGER DEFAULT 1,
                warn_limit INTEGER DEFAULT 3,
                mute_duration INTEGER DEFAULT 300,
                captcha_enabled INTEGER DEFAULT 1,
                personality TEXT DEFAULT 'shookh',
                fun_enabled INTEGER DEFAULT 1,
                games_enabled INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS warns (
                user_id INTEGER,
                chat_id INTEGER,
                count INTEGER DEFAULT 1,
                PRIMARY KEY (user_id, chat_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                points INTEGER DEFAULT 0,
                messages INTEGER DEFAULT 0
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                role TEXT,
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS captcha_state (
                chat_id INTEGER,
                user_id INTEGER,
                correct_answer INTEGER,
                expire_at TIMESTAMP,
                PRIMARY KEY (chat_id, user_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS api_providers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                base_url TEXT NOT NULL,
                api_key TEXT NOT NULL,
                model TEXT NOT NULL,
                enabled INTEGER DEFAULT 1,
                priority INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Performance indexes
        await db.execute("CREATE INDEX IF NOT EXISTS idx_history_chat ON chat_history(chat_id, id DESC);")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_warns ON warns(chat_id, user_id);")
        await db.commit()

        try:
            cur = await db.execute("PRAGMA table_info(groups)")
            cols = [r[1] for r in await cur.fetchall()]
            for col, typ in {
                "welcome_buttons": "TEXT DEFAULT '[]'",
                "anti_forward": "INTEGER DEFAULT 0",
                "anti_sticker": "INTEGER DEFAULT 0",
                "anti_badword": "INTEGER DEFAULT 1",
                "strictness": "INTEGER DEFAULT 1",
                "warn_limit": "INTEGER DEFAULT 3",
                "mute_duration": "INTEGER DEFAULT 300",
                "captcha_enabled": "INTEGER DEFAULT 1",
                "personality": "TEXT DEFAULT 'shookh'",
                "fun_enabled": "INTEGER DEFAULT 1",
                "games_enabled": "INTEGER DEFAULT 1",
            }.items():
                if col not in cols:
                    await db.execute(f"ALTER TABLE groups ADD COLUMN {col} {typ}")
            await db.commit()
        except Exception:
            pass

async def get_group(chat_id):
    # Use cache layer if available
    try:
        from core.cache import group_cache
        cached = group_cache.get(f"group:{chat_id}")
        if cached:
            return cached
    except Exception:
        pass

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM groups WHERE chat_id=?", (chat_id,)) as cur:
            row = await cur.fetchone()
            result = dict(row) if row else None
            if result:
                try:
                    group_cache.set(f"group:{chat_id}", result, ttl=60)
                except Exception:
                    pass
            return result

async def get_all_groups():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM groups ORDER BY title") as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]

async def upsert_group(chat_id, title):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO groups (chat_id, title) VALUES (?,?)", (chat_id, title))
        await db.execute("UPDATE groups SET title=? WHERE chat_id=?", (title, chat_id))
        await db.commit()
    try:
        from core.cache import group_cache
        group_cache.delete(f"group:{chat_id}")
    except Exception:
        pass

async def update_group(chat_id, **kwargs):
    if not kwargs:
        return
    # Whitelist columns to prevent injection
    filtered = {k: v for k, v in kwargs.items() if k in ALLOWED_GROUP_COLUMNS}
    if not filtered:
        return
    set_clause = ", ".join([f"{k}=?" for k in filtered.keys()])
    values = list(filtered.values()) + [chat_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE groups SET {set_clause} WHERE chat_id=?", values)
        await db.commit()
    try:
        from core.cache import group_cache
        group_cache.delete(f"group:{chat_id}")
    except Exception:
        pass

async def add_warn(chat_id, user_id):
    # Atomic increment to avoid race condition
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO warns (chat_id, user_id, count) VALUES (?,?,1)
            ON CONFLICT(chat_id, user_id) DO UPDATE SET count = count + 1
        """, (chat_id, user_id))
        await db.commit()
        async with db.execute("SELECT count FROM warns WHERE chat_id=? AND user_id=?", (chat_id, user_id)) as cur:
            row = await cur.fetchone()
            return row[0] if row else 1

async def reset_warn(chat_id, user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM warns WHERE chat_id=? AND user_id=?", (chat_id, user_id))
        await db.commit()

async def get_warn(chat_id, user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT count FROM warns WHERE chat_id=? AND user_id=?", (chat_id, user_id)) as cur:
            row = await cur.fetchone()
            return row[0] if row else 0

async def add_point(user_id, username, first_name, points=1):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO users (user_id, username, first_name, points, messages)
            VALUES (?,?,?,?,1)
            ON CONFLICT(user_id) DO UPDATE SET
                points = points + ?,
                messages = messages + 1,
                username = excluded.username,
                first_name = excluded.first_name
        """, (user_id, username or "", first_name or "", points, points))
        await db.commit()

async def get_top_users(limit=10):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users ORDER BY points DESC LIMIT ?", (limit,)) as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]

async def save_message(chat_id, role, content):
    # Sanitize content length
    content = content[:2000] if content else ""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO chat_history (chat_id, role, content) VALUES (?,?,?)", (chat_id, role, content))
        # Fixed: add chat_id filter to outer delete to prevent deleting other chats
        await db.execute("""
            DELETE FROM chat_history
            WHERE chat_id = ? AND id NOT IN (
                SELECT id FROM chat_history WHERE chat_id=? ORDER BY id DESC LIMIT 30
            )
        """, (chat_id, chat_id))
        await db.commit()

async def get_history(chat_id, limit=14):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT role, content FROM chat_history WHERE chat_id=? ORDER BY id DESC LIMIT ?", (chat_id, limit)) as cur:
            rows = await cur.fetchall()
            return [{"role": r[0], "content": r[1]} for r in reversed(rows)]

# API Providers
async def get_api_providers():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM api_providers WHERE enabled=1 ORDER BY priority ASC, id ASC") as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]

async def get_all_api_providers():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM api_providers ORDER BY priority ASC") as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]

async def add_api_provider(name, base_url, api_key, model, priority=0):
    # Basic URL validation
    if not re.match(r"^https?://", base_url):
        base_url = "https://" + base_url
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO api_providers (name, base_url, api_key, model, priority) VALUES (?,?,?,?,?)",
            (name.strip()[:50], base_url.strip()[:200], api_key.strip()[:500], model.strip()[:100], priority)
        )
        await db.commit()
        return cur.lastrowid

async def update_api_provider(pid, **kwargs):
    filtered = {k: v for k, v in kwargs.items() if k in ALLOWED_API_COLUMNS}
    if not filtered:
        return
    set_clause = ", ".join([f"{k}=?" for k in filtered.keys()])
    values = list(filtered.values()) + [pid]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE api_providers SET {set_clause} WHERE id=?", values)
        await db.commit()

async def delete_api_provider(pid):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM api_providers WHERE id=?", (pid,))
        await db.commit()

# Captcha state (server-side, not leaked to client)
async def set_captcha_state(chat_id, user_id, correct_answer, expire_seconds=120):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO captcha_state (chat_id, user_id, correct_answer, expire_at) VALUES (?,?,?, datetime('now', ?))",
            (chat_id, user_id, correct_answer, f"+{expire_seconds} seconds")
        )
        await db.commit()

async def get_captcha_state(chat_id, user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT correct_answer FROM captcha_state WHERE chat_id=? AND user_id=? AND expire_at > datetime('now')", (chat_id, user_id)) as cur:
            row = await cur.fetchone()
            return row[0] if row else None

async def clear_captcha_state(chat_id, user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM captcha_state WHERE chat_id=? AND user_id=?", (chat_id, user_id))
        await db.commit()

if __name__ == "__main__":
    asyncio.run(init_db())
