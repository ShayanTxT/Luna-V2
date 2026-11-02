# shayan.txt
"""Security helpers."""

import re
import html

# Prevent Telegram HTML injection
def sanitize(text: str, max_len: int = 1000) -> str:
    if not text:
        return ""
    text = text[:max_len]
    # Escape HTML but keep allowed formatting minimal
    return html.escape(text)

def is_valid_token(token: str) -> bool:
    return bool(re.match(r"^\d+:[A-Za-z0-9_-]+$", token))

def redact_key(key: str) -> str:
    if not key or len(key) < 8:
        return "***"
    return key[:4] + "***" + key[-4:]
