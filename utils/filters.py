import re
import time
from collections import defaultdict, deque

BAD_WORDS = ["کسکش", "کیر", "جنده", "کص", "حرومزاده"]

# Improved link pattern - avoid false positives
LINK_PATTERN = re.compile(r"(https?://\S+|t\.me/\S+|telegram\.me/\S+|instagram\.com/\S+)", re.IGNORECASE)

# Track messages per user for flood detection with auto-cleanup
user_messages: dict[tuple[int,int], deque] = defaultdict(deque)
_last_cleanup = time.time()

def _cleanup_old_entries():
    global _last_cleanup
    now = time.time()
    if now - _last_cleanup < 300:  # cleanup every 5 min
        return
    _last_cleanup = now
    # Remove empty or expired entries
    expired = [k for k, dq in user_messages.items() if not dq or now - dq[-1] > 120]
    for k in expired:
        user_messages.pop(k, None)

def contains_link(text: str) -> bool:
    if not text:
        return False
    return bool(LINK_PATTERN.search(text))

def contains_bad_word(text: str) -> bool:
    if not text:
        return False
    # Normalize and use word boundaries to reduce false positives
    text_lower = text.lower().replace("‌", "").replace(" ", "")
    return any(w in text_lower for w in BAD_WORDS)

def is_flood(user_id: int, chat_id: int, limit=5, seconds=10) -> bool:
    _cleanup_old_entries()
    key = (chat_id, user_id)
    now = time.time()
    dq = user_messages[key]
    while dq and now - dq[0] > seconds:
        dq.popleft()
    dq.append(now)
    return len(dq) > limit
