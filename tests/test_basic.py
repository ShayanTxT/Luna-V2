# shayan.txt
import pytest

def test_config_loads():
    from core.config import settings
    # WEB_SECRET must be at least 32 chars in new strict mode
    assert hasattr(settings, "BOT_TOKEN")
    assert hasattr(settings, "WEB_SECRET")

def test_web_secret_length():
    from core.config import settings
    # In CI we set a 42-char secret, validate enforces >=32
    assert len(settings.WEB_SECRET) >= 32, "WEB_SECRET must be >=32 chars"

def test_sanitize():
    from core.security import sanitize
    assert sanitize("<script>") == "&lt;script&gt;"

def test_rate_limiter():
    from core.rate_limiter import RateLimiter
    rl = RateLimiter(max_requests=2, window=10)
    assert not rl.is_limited(1, 1)
    assert not rl.is_limited(1, 1)
    assert rl.is_limited(1, 1)

def test_auth_uses_get_current_user():
    from pathlib import Path
    src = Path("web/admin.py").read_text()
    # Old verify_auth was renamed to get_current_user
    assert "get_current_user" in src
    assert "verify_auth" not in src
