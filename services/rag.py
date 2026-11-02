# shayan.txt
"""Per-group knowledge base (lightweight RAG without embeddings)"""

from pathlib import Path
import aiosqlite
from database.db import DB_PATH

async def add_knowledge(chat_id: int, question: str, answer: str, added_by: int = 0):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS group_knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                question TEXT,
                answer TEXT,
                keywords TEXT,
                added_by INTEGER,
                hits INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_chat ON group_knowledge(chat_id);")
        from core.tokens import extract_keywords
        kw = ",".join(extract_keywords(question))
        await db.execute(
            "INSERT INTO group_knowledge (chat_id, question, answer, keywords) VALUES (?,?,?,?)",
            (chat_id, question[:500], answer[:2000], kw)
        )
        await db.commit()

async def search_knowledge(chat_id: int, query: str, threshold: int = 1) -> str | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        from core.tokens import extract_keywords
        kws = extract_keywords(query)
        if not kws:
            return None
        # Simple keyword overlap search
        where = " OR ".join(["keywords LIKE ?" for _ in kws])
        params = [f"%{k}%" for k in kws]
        sql = f"SELECT answer, keywords, hits FROM group_knowledge WHERE chat_id=? AND ({where}) ORDER BY hits DESC LIMIT 3"
        async with db.execute(sql, [chat_id] + params) as cur:
            rows = await cur.fetchall()
            if not rows:
                return None
            # Score by keyword overlap
            best = None
            best_score = 0
            for r in rows:
                score = sum(1 for k in kws if k in r["keywords"])
                if score > best_score:
                    best_score = score
                    best = r
            if best_score >= threshold:
                # Increment hits
                await db.execute("UPDATE group_knowledge SET hits = hits + 1 WHERE answer=? AND chat_id=?", (best["answer"], chat_id))
                await db.commit()
                return best["answer"]
            return None

async def list_knowledge(chat_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM group_knowledge WHERE chat_id=? ORDER BY hits DESC", (chat_id,)) as cur:
            return [dict(r) for r in await cur.fetchall()]
