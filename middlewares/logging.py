# shayan.txt

import time
from aiogram import BaseMiddleware
from aiogram.types import Update
from typing import Callable, Dict, Any, Awaitable
from core.logger import logger

class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        start = time.time()
        result = await handler(event, data)
        elapsed = (time.time() - start) * 1000
        # Log slow handlers
        if elapsed > 1000:
            logger.warning(f"Slow handler: {elapsed:.0f}ms")
        return result
