# shayan.txt
from fastapi import Request
from core.config import settings
import secrets
import time

SESSIONS: dict[str, float] = {}  # token -> expire

def create_session() -> str:
    token = secrets.token_urlsafe(32)
    SESSIONS[token] = time.time() + 24 * 3600
    return token

def is_valid_session(token: str | None) -> bool:
    if not token:
        return False
    exp = SESSIONS.get(token)
    if not exp:
        return False
    if time.time() > exp:
        SESSIONS.pop(token, None)
        return False
    return True

def get_current_user(request: Request):
    # WEB_SECRET is mandatory - reject weak/empty (enforced in settings.validate)
    if not settings.WEB_SECRET or len(settings.WEB_SECRET) < 32:
        return None
    token = request.cookies.get("luna_session")
    if is_valid_session(token):
        return True
    return None

def is_https_request(request: Request) -> bool:
    # Respect reverse proxy headers (Render, etc.)
    if request.headers.get("x-forwarded-proto") == "https":
        return True
    return request.url.scheme == "https"
