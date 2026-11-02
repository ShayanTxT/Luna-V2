# shayan.txt
"""Global error handling middleware."""

import logging
from aiogram import BaseMiddleware
from aiogram.types import Update
from typing import Callable, Dict, Any, Awaitable

logger = logging.getLogger("luna")

class ErrorHandlerMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as e:
            logger.exception(f"Unhandled error: {e}", exc_info=True)
            # Don't crash polling, just log
            return None
