# shayan.txt
"""Centralized configuration with validation."""

import os
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

def _env_bool(key: str, default: bool = False) -> bool:
    val = os.getenv(key)
    if val is None:
        return default
    return val.lower() in ("1", "true", "yes", "on")

def _env_int(key: str, default: int) -> int:
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        return default

class Settings:
    # Bot
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    BOT_USERNAME: str = os.getenv("BOT_USERNAME", "LunaBot")
    OWNER_ID: int = _env_int("OWNER_ID", 0)

    # Web - WEB_SECRET is mandatory and must be >=32 chars
    PORT: int = _env_int("PORT", 8000)
    WEB_SECRET: str = os.getenv("WEB_SECRET", "")
    WEB_HOST: str = os.getenv("WEB_HOST", "0.0.0.0")

    # Database
    DB_PATH: Path = Path(os.getenv("DB_PATH", str(BASE_DIR / "database" / "bot.db")))
    DB_BACKUP_ENABLED: bool = _env_bool("DB_BACKUP_ENABLED", True)
    DB_BACKUP_INTERVAL_HOURS: int = _env_int("DB_BACKUP_INTERVAL_HOURS", 12)

    # AI - fallback from env (primary is DB panel)
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Cache
    CACHE_TTL: int = _env_int("CACHE_TTL", 300)

    # Rate limiting
    RATE_LIMIT_MESSAGES: int = _env_int("RATE_LIMIT_MESSAGES", 5)
    RATE_LIMIT_WINDOW: int = _env_int("RATE_LIMIT_WINDOW", 10)

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE", "logs/bot.log")

    @property
    def is_configured(self) -> bool:
        return bool(self.BOT_TOKEN and len(self.BOT_TOKEN) > 20)

    def validate(self):
        errors = []
        if not self.BOT_TOKEN:
            errors.append("BOT_TOKEN is required")
        elif len(self.BOT_TOKEN) < 20:
            errors.append("BOT_TOKEN looks invalid")
        # WEB_SECRET is mandatory for panel security
        if not self.WEB_SECRET:
            errors.append("WEB_SECRET is required (min 32 chars) - generate with: openssl rand -hex 32")
        elif len(self.WEB_SECRET) < 32:
            errors.append("WEB_SECRET must be at least 32 characters (weak secret rejected)")
        if errors:
            raise ValueError("; ".join(errors))

settings = Settings()
