# shayan.txt
from fastapi import Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse
from core.config import settings
import hmac, secrets, time

SESSIONS = {}  # token -> expire

def create_session() -> str:
    token = secrets.token_urlsafe(32)
    SESSIONS[token] = time.time() + 24*3600
    return token

def is_valid_session(token: str) -> bool:
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
    # Deny access when the admin secret is missing or weak
    if not settings.WEB_SECRET or len(settings.WEB_SECRET) < 32:
        return None
    token = request.cookies.get("luna_session")
    if is_valid_session(token):
        return True
    return None
