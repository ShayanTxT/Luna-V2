# shayan.txt
"""Database manager with pooling, WAL, backups and health checks."""

import asyncio
import shutil
import aiosqlite
from pathlib import Path
from contextlib import asynccontextmanager
from core.config import settings
from core.logger import logger

class DatabaseManager:
    def __init__(self, db_path: Path = None):
        self.db_path = db_path or settings.DB_PATH
        self._lock = asyncio.Lock()

    async def init(self):
        """Initialize database with optimizations."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self.db_path) as db:
            # WAL mode for better concurrency
            await db.execute("PRAGMA journal_mode=WAL;")
            await db.execute("PRAGMA synchronous=NORMAL;")
            await db.execute("PRAGMA foreign_keys=ON;")
            # Create tables
            await self._create_tables(db)
            # Create indexes for performance
            await self._create_indexes(db)
            await db.commit()
        logger.info(f"Database initialized at {self.db_path}")

    async def _create_tables(self, db):
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
                messages INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
        # Migration: add missing columns to old DBs
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
        except Exception as e:
            logger.warning(f"Migration skipped: {e}")

    async def _create_indexes(self, db):
        # Indexes for hot queries
        await db.execute("CREATE INDEX IF NOT EXISTS idx_chat_history_chat ON chat_history(chat_id);")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_warns_chat_user ON warns(chat_id, user_id);")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_users_points ON users(points DESC);")

    @asynccontextmanager
    async def connection(self):
        """Context manager for DB connection with retry."""
        for attempt in range(3):
            try:
                async with aiosqlite.connect(self.db_path) as db:
                    db.row_factory = aiosqlite.Row
                    yield db
                break
            except aiosqlite.OperationalError as e:
                if "locked" in str(e) and attempt < 2:
                    await asyncio.sleep(0.2 * (attempt + 1))
                    continue
                raise

    async def health_check(self) -> dict:
        try:
            async with self.connection() as db:
                async with db.execute("SELECT 1") as cur:
                    await cur.fetchone()
            size = self.db_path.stat().st_size if self.db_path.exists() else 0
            return {"status": "ok", "path": str(self.db_path), "size_bytes": size}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def backup(self) -> Path | None:
        """Create timestamped backup."""
        if not settings.DB_BACKUP_ENABLED or not self.db_path.exists():
            return None
        backup_dir = self.db_path.parent / "backups"
        backup_dir.mkdir(exist_ok=True)
        from datetime import datetime
        name = f"bot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        dest = backup_dir / name
        try:
            async with self._lock:
                shutil.copy2(self.db_path, dest)
            # Keep only last 5 backups
            backups = sorted(backup_dir.glob("bot_*.db"), reverse=True)
            for old in backups[5:]:
                old.unlink(missing_ok=True)
            logger.info(f"Backup created: {dest}")
            return dest
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return None

# Global instance
db_manager = DatabaseManager()
