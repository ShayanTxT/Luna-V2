# shayan.txt
"""Throttling middleware to prevent spam."""

from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Dict, Any, Awaitable
from core.rate_limiter import limiter

class ThrottlingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, Message) and event.from_user:
            # Skip admins in throttling (optional)
            if limiter.is_limited(event.chat.id, event.from_user.id):
                # Silently drop
                return None
        return await handler(event, data)
