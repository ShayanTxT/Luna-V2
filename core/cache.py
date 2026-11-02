# shayan.txt
"""Simple TTL cache for hot data."""

import time
from typing import Any, Optional

class TTLCache:
    def __init__(self, ttl: int = 300, max_size: int = 500):
        self.ttl = ttl
        self.max_size = max_size
        self._store: dict[str, tuple[Any, float]] = {}

    def get(self, key: str) -> Optional[Any]:
        item = self._store.get(key)
        if not item:
            return None
        value, exp = item
        if time.time() > exp:
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any, ttl: int = None):
        if len(self._store) >= self.max_size:
            # Evict oldest
            oldest = next(iter(self._store))
            self._store.pop(oldest)
        exp = time.time() + (ttl or self.ttl)
        self._store[key] = (value, exp)

    def delete(self, key: str):
        self._store.pop(key, None)

    def clear(self):
        self._store.clear()

# Global caches
group_cache = TTLCache(ttl=60)
user_cache = TTLCache(ttl=120)
