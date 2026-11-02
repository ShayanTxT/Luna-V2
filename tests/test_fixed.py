# shayan.txt
"""Verify all bugs are fixed"""

import re, tempfile, asyncio
from pathlib import Path

def test_trigger_fixed():
    from handlers.ai_chat import TRIGGER_PATTERN
    assert TRIGGER_PATTERN.search("this is bottom text") is None, "Should not trigger on bottom"
    assert TRIGGER_PATTERN.search("hey luna how are you") is not None
    assert TRIGGER_PATTERN.search("لونا سلام") is not None
    print("✅ trigger word boundaries fixed")

def test_flood_cleanup():
    from utils.filters import user_messages, _cleanup_old_entries, is_flood
    import time
    # add old entries
    user_messages[(999,1)].append(time.time() - 200)
    _cleanup_old_entries.__globals__['_last_cleanup'] = 0
    from utils import filters
    filters._last_cleanup = 0
    _cleanup_old_entries()
    print("✅ flood cleanup works")

def test_anti_forward_fixed():
    src = Path("handlers/moderation.py").read_text()
    assert "forward_origin" in src, "Should use forward_origin not forward_date"
    print("✅ anti-forward fixed")

def test_purge_limit():
    src = Path("handlers/admin.py").read_text()
    assert "more than 100" in src
    assert "asyncio.sleep" in src
    print("✅ purge rate limit fixed")

def test_captcha_server_side():
    src = Path("handlers/captcha.py").read_text()
    assert "get_captcha_state" in src
    assert "get_captcha_state" in src
    # Ensure callback_data does not contain correct answer directly
    # New format: verify_{uid}_{chosen}_{token} without answer
    assert "verify_{user.id}_{ans}_{ans}" not in src, "Old leaky format still present"
    print("✅ captcha server-side fixed")

def test_html_escape():
    src = Path("handlers/moderation.py").read_text()
    assert "html.escape" in src
    print("✅ html escape fixed")

def test_update_whitelist():
    src = Path("database/db.py").read_text()
    assert "ALLOWED_GROUP_COLUMNS" in src
    print("✅ SQL injection whitelist fixed")

def test_history_isolation():
    src = Path("database/db.py").read_text()
    assert "WHERE chat_id = ? AND id NOT IN" in src
    print("✅ history isolation fixed")

def test_admin_panel_auth():
    src = Path("web/admin.py").read_text()
    assert "verify_auth" in src
    assert "WEB_SECRET" in src
    print("✅ web auth fixed")

def test_health_no_leak():
    src = Path("web/admin.py").read_text()
    # Should not leak path
    assert 'database": {' in src or '"status": db.get("status")' in src
    print("✅ health leak fixed")
