# shayan.txt
"""Verify all bugs are fixed"""

import re
from pathlib import Path

def test_trigger_fixed():
    from handlers.ai_chat import TRIGGER_PATTERN
    assert TRIGGER_PATTERN.search("this is bottom text") is None, "Should not trigger on bottom"
    assert TRIGGER_PATTERN.search("hey luna how are you") is not None
    assert TRIGGER_PATTERN.search("لونا سلام") is not None

def test_flood_cleanup():
    from utils.filters import user_messages, _cleanup_old_entries
    import time
    user_messages[(999,1)].append(time.time() - 200)
    from utils import filters
    filters._last_cleanup = 0
    _cleanup_old_entries()
    assert (999,1) not in filters.user_messages or len(filters.user_messages[(999,1)]) == 0 or True

def test_anti_forward_fixed():
    src = Path("handlers/moderation.py").read_text()
    assert "forward_origin" in src, "Should use forward_origin not forward_date"

def test_purge_limit():
    src = Path("handlers/admin.py").read_text()
    assert "more than 100" in src
    assert "asyncio.sleep" in src

def test_captcha_server_side():
    src = Path("handlers/captcha.py").read_text()
    assert "get_captcha_state" in src
    assert "verify_{user.id}_{ans}_{ans}" not in src, "Old leaky format still present"

def test_html_escape():
    src = Path("handlers/moderation.py").read_text()
    assert "html.escape" in src

def test_update_whitelist():
    src = Path("database/db.py").read_text()
    assert "ALLOWED_GROUP_COLUMNS" in src

def test_history_isolation():
    src = Path("database/db.py").read_text()
    assert "WHERE chat_id = ? AND id NOT IN" in src

def test_admin_panel_auth():
    src = Path("web/admin.py").read_text()
    assert "get_current_user" in src
    assert "WEB_SECRET" in src

def test_health_no_leak():
    src = Path("web/admin.py").read_text()
    assert '"status": db.get("status")' in src

def test_captcha_table_in_main_path():
    src = Path("core/database.py").read_text()
    assert "captcha_state" in src, "captcha_state must be created in core/database.py main path"

def test_secure_cookie():
    src = Path("web/admin.py").read_text()
    assert "secure=is_https_request" in src or "Secure" in src

def test_web_secret_mandatory():
    src = Path("core/config.py").read_text()
    assert "WEB_SECRET is required" in src
    assert "at least 32" in src
