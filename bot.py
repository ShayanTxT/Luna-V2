# shayan.txt

import asyncio
import signal
import logging
from pathlib import Path
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from core.config import settings
from core.logger import logger
from core.database import db_manager
from handlers import admin, ai_chat, moderation, captcha, games, knowledge, start
from core.validator import validate_and_report
from middlewares.error_handler import ErrorHandlerMiddleware
from middlewares.logging import LoggingMiddleware

async def create_bot() -> Bot:
    if not settings.is_configured:
        logger.error("BOT_TOKEN not configured")
        raise ValueError("BOT_TOKEN required")
    return Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

async def create_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    # Global middlewares
    dp.message.middleware(ErrorHandlerMiddleware())
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(ErrorHandlerMiddleware())

    # Routers (order matters)
    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(knowledge.router)
    dp.include_router(captcha.router)
    dp.include_router(moderation.router)
    dp.include_router(games.router)
    dp.include_router(ai_chat.router)
    return dp

async def start_bot():
    validate_and_report()
    Path("database").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)

    await db_manager.init()
    # Optional periodic backup
    if settings.DB_BACKUP_ENABLED:
        asyncio.create_task(periodic_backup())

    bot = await create_bot()
    dp = await create_dispatcher()

    me = await bot.get_me()
    logger.info(f"Luna started: @{me.username} ({me.first_name})")
    logger.info(f"Admin panel: http://{settings.WEB_HOST}:{settings.PORT}/admin")

    await dp.start_polling(bot)

async def periodic_backup():
    while True:
        await asyncio.sleep(settings.DB_BACKUP_INTERVAL_HOURS * 3600)
        try:
            await db_manager.backup()
        except Exception as e:
            logger.error(f"Backup error: {e}")

async def start_web():
    import uvicorn
    from web.admin import app
    cfg = uvicorn.Config(app, host=settings.WEB_HOST, port=settings.PORT, log_level="info")
    server = uvicorn.Server(cfg)
    await server.serve()

async def main():
    # Graceful shutdown handling
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, lambda: logger.info(f"Received {sig.name}"))
        except NotImplementedError:
            pass

    await asyncio.gather(start_bot(), start_web())

if __name__ == "__main__":
    asyncio.run(main())
