# shayan.txt
"""Startup validator with helpful errors"""

import re
from core.config import settings
from core.logger import logger

def validate_and_report():
    errors = []
    warnings = []

    # Token check
    if not settings.BOT_TOKEN:
        errors.append("❌ BOT_TOKEN missing - get from @BotFather and set in .env")
    elif not re.match(r"^\d+:[A-Za-z0-9_-]{30,}", settings.BOT_TOKEN):
        errors.append("❌ BOT_TOKEN looks invalid")

    # API check
    from config import API_POOL
    try:
        from database.db import DB_PATH
        import aiosqlite, asyncio
        # check DB panel
        async def check_db():
            import pathlib
            if DB_PATH.exists():
                import aiosqlite
                async with aiosqlite.connect(DB_PATH) as db:
                    async with db.execute("SELECT COUNT(*) FROM api_providers WHERE enabled=1") as cur:
                        row = await cur.fetchone()
                        return row[0]
            return 0
        # we can't await here, just warn if both empty
        if not API_POOL:
            warnings.append("⚠️ No API keys in .env - add GROQ_API_KEY or use panel /admin")
    except Exception:
        pass

    if errors:
        for e in errors:
            logger.error(e)
        raise SystemExit("\n".join(errors))

    for w in warnings:
        logger.warning(w)

    logger.info("✅ Config validated")
    return True
