# shayan.txt
import pytest

def test_config_loads():
    from core.config import settings
    assert hasattr(settings, "BOT_TOKEN")

def test_sanitize():
    from core.security import sanitize
    assert sanitize("<script>") == "&lt;script&gt;"

def test_rate_limiter():
    from core.rate_limiter import RateLimiter
    rl = RateLimiter(max_requests=2, window=10)
    assert not rl.is_limited(1, 1)
    assert not rl.is_limited(1, 1)
    assert rl.is_limited(1, 1)
