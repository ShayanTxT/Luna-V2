from pathlib import Path
from typing import Optional
from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from database.db import get_group, get_all_groups, update_group
from database.db import get_all_api_providers, add_api_provider, update_api_provider, delete_api_provider
from core.database import db_manager
from core.config import settings
from web.auth import get_current_user, create_session, is_valid_session
import time, html

app = FastAPI(title="Luna Panel")
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
_started_at = time.time()

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = None):
    return templates.TemplateResponse("login.html", {"request": request, "error": error})

@app.post("/login")
async def login(request: Request, password: str = Form(...)):
    import hmac
    if hmac.compare_digest(password, settings.WEB_SECRET):
        token = create_session()
        resp = RedirectResponse("/admin", status_code=303)
        resp.set_cookie("luna_session", token, httponly=True, max_age=86400)
        return resp
    return templates.TemplateResponse("login.html", {"request": request, "error": "رمز اشتباه"}, status_code=401)

@app.get("/logout")
async def logout():
    resp = RedirectResponse("/login", status_code=303)
    resp.delete_cookie("luna_session")
    return resp

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    if not get_current_user(request):
        return RedirectResponse("/login", status_code=303)
    groups = await get_all_groups()
    return templates.TemplateResponse("admin.html", {"request": request, "groups": groups, "selected": None, "apis": await get_all_api_providers()})

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request, chat_id: Optional[int] = None):
    if not get_current_user(request):
        return RedirectResponse("/login", status_code=303)
    groups = await get_all_groups()
    selected = await get_group(chat_id) if chat_id else None
    apis = await get_all_api_providers()
    if selected and selected.get("welcome_text"):
        selected["welcome_text"] = html.escape(selected["welcome_text"])
    return templates.TemplateResponse("admin.html", {"request": request, "groups": groups, "selected": selected, "apis": apis})

@app.post("/admin/save")
async def save_settings(request: Request, chat_id: int = Form(...), welcome_text: str = Form(""), welcome_enabled: Optional[str] = Form(None), anti_link: Optional[str] = Form(None), anti_forward: Optional[str] = Form(None), anti_sticker: Optional[str] = Form(None), anti_spam: Optional[str] = Form(None), anti_badword: Optional[str] = Form(None), strictness: int = Form(1), warn_limit: int = Form(3), mute_duration: int = Form(300), captcha_enabled: Optional[str] = Form(None), personality: str = Form("shookh")):
    if not get_current_user(request):
        raise HTTPException(401)
    strictness = max(1, min(strictness, 3))
    warn_limit = max(1, min(warn_limit, 10))
    mute_duration = max(60, min(mute_duration, 86400))
    welcome_text = html.escape(welcome_text[:1000])
    if personality not in ["shookh", "naz", "lati", "rok"]:
        personality = "shookh"
    await update_group(chat_id, welcome_text=welcome_text, welcome_enabled=1 if welcome_enabled else 0, anti_link=1 if anti_link else 0, anti_forward=1 if anti_forward else 0, anti_sticker=1 if anti_sticker else 0, anti_spam=1 if anti_spam else 0, anti_badword=1 if anti_badword else 0, strictness=strictness, warn_limit=warn_limit, mute_duration=mute_duration, captcha_enabled=1 if captcha_enabled else 0, personality=personality)
    return RedirectResponse(url=f"/admin?chat_id={chat_id}&saved=1", status_code=303)

@app.post("/admin/api/add")
async def api_add(request: Request, name: str = Form(...), base_url: str = Form(...), api_key: str = Form(...), model: str = Form(...), priority: int = Form(0)):
    if not get_current_user(request): raise HTTPException(401)
    if not base_url.startswith("http"): base_url = "https://" + base_url
    await add_api_provider(name.strip()[:50], base_url.strip()[:200], api_key.strip()[:500], model.strip()[:100], priority)
    return RedirectResponse(url="/admin?api_added=1", status_code=303)

@app.post("/admin/api/delete")
async def api_delete(request: Request, api_id: int = Form(...)):
    if not get_current_user(request): raise HTTPException(401)
    await delete_api_provider(api_id)
    return RedirectResponse(url="/admin?api_deleted=1", status_code=303)

@app.post("/admin/api/toggle")
async def api_toggle(request: Request, api_id: int = Form(...), enabled: int = Form(...)):
    if not get_current_user(request): raise HTTPException(401)
    await update_api_provider(api_id, enabled=0 if enabled else 1)
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/admin/api/edit")
async def api_edit(request: Request, api_id: int = Form(...), name: str = Form(...), base_url: str = Form(...), api_key: str = Form(...), model: str = Form(...), priority: int = Form(0)):
    if not get_current_user(request): raise HTTPException(401)
    await update_api_provider(api_id, name=name.strip()[:50], base_url=base_url.strip()[:200], api_key=api_key.strip()[:500], model=model.strip()[:100], priority=priority)
    return RedirectResponse(url="/admin?api_edited=1", status_code=303)

@app.get("/health")
async def health():
    db = await db_manager.health_check()
    return {"status": "ok", "bot": "Luna v2", "uptime_seconds": int(time.time() - _started_at), "database": {"status": db.get("status")}, "version": "2.5"}

@app.get("/ping")
async def ping():
    return {"pong": True}

@app.get("/metrics")
async def metrics():
    try:
        import psutil
        return {"cpu": psutil.cpu_percent(), "memory": psutil.virtual_memory()._asdict(), "uptime": int(time.time() - _started_at)}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/stats/tokens")
async def token_stats(request: Request):
    if not get_current_user(request): raise HTTPException(401)
    from services.ai_cache import cache_stats
    stats = await cache_stats()
    return {"cache": stats}

@app.get("/api/knowledge/{chat_id}")
async def get_knowledge(request: Request, chat_id: int):
    if not get_current_user(request): raise HTTPException(401)
    from services.rag import list_knowledge
    items = await list_knowledge(chat_id)
    return {"count": len(items), "items": items[:20]}
