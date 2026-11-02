# shayan.txt
"""Token bucket rate limiter per user/chat."""

import time
from collections import defaultdict, deque

class RateLimiter:
    def __init__(self, max_requests: int = 5, window: int = 10):
        self.max_requests = max_requests
        self.window = window
        self._buckets: dict[tuple[int,int], deque] = defaultdict(deque)

    def is_limited(self, chat_id: int, user_id: int) -> bool:
        key = (chat_id, user_id)
        now = time.time()
        dq = self._buckets[key]
        while dq and now - dq[0] > self.window:
            dq.popleft()
        if len(dq) >= self.max_requests:
            return True
        dq.append(now)
        return False

    def remaining(self, chat_id: int, user_id: int) -> int:
        key = (chat_id, user_id)
        dq = self._buckets[key]
        return max(0, self.max_requests - len(dq))

limiter = RateLimiter()
