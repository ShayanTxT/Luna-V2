<p align="center">
  <img src="assets/banner.png" alt="Luna Bot Banner" width="100%" />
</p>

<p align="center">
  <a href="https://github.com/ShayanTxT/Luna-V2"><img src="https://img.shields.io/github/stars/ShayanTxT/Luna-V2?style=social" alt="Stars"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/python-3.11+-3776ab?style=flat&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://core.telegram.org/bots"><img src="https://img.shields.io/badge/Telegram-Bot-26A5E4?style=flat&logo=telegram" alt="Telegram"></a>
  <img src="https://img.shields.io/badge/aiogram-3.13-blue" alt="aiogram">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  <a href="README_FA.md">🇮🇷 فارسی</a>
</p>

<h1 align="center">🌙 Luna Bot</h1>
<p align="center">
  <b>Advanced Telegram Group Manager + AI Companion</b><br>
  Smart moderation • 4 Personalities • RAG Knowledge • Token Optimized
</p>

<p align="center">
  <a href="https://render.com/deploy?repo=https://github.com/ShayanTxT/Luna-V2"><img src="https://render.com/images/deploy-to-render-button.svg" alt="Deploy to Render"></a>
  &nbsp;
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-features">Features</a> •
  <a href="#-admin-panel">Panel</a>
</p>

---

## ✨ Features

### 🛡️ Smart Moderation
- Anti-link / forward / sticker / spam / bad-word (toggle per group)
- Strictness levels (1-3), warn system (`/warn` → auto-ban)
- `/ban /kick /mute /unmute /purge /pin`

### 🤖 Next-Gen AI
- **4 personalities** – Shookh 😜, Naz 💖, Lati 😎, Rok 🔥 (`/personality`)
- **RAG knowledge** – `/learn question | answer` → `/ask` (0 tokens)
- **Summarization** – `/summarize` last 30 messages
- **Token optimized** – cache + summarization saves ~60% (`/api/stats/tokens`)

### 🧩 Captcha
- Math captcha on join, auto-kick if not verified in 120s

### 🎮 Fun
- `/jok` `/fal` `/word` `/quiz` `/top` + points & leaderboard

### 🎛️ Web Panel
- Login with `WEB_SECRET` at `/admin`
- Manage groups, filters, personality, **API Pool** (Groq/OpenRouter/OpenAI fallback)

---

## 🚀 Quick Start

**1. Get credentials**
- Bot token: **@BotFather** → `/newbot`
- Free AI: **console.groq.com/keys** (fast & free)

**2. Run**
```bash
cp .env.example .env  # fill BOT_TOKEN, GROQ_API_KEY, WEB_SECRET (min 32 chars)
# Generate WEB_SECRET: openssl rand -hex 32
pip install -r requirements.txt
python bot.py
# Bot polling + Panel http://localhost:8000/admin (login with WEB_SECRET)
```

**3. Add to group**
- Add Luna to your group → Make **Admin** (enable *Delete messages*)
- Send: `لونا سلام` or `/start`

---

## 🐳 Deploy

**Render (1-click)**
Click Deploy button above → Set `BOT_TOKEN`, `GROQ_API_KEY`, `WEB_SECRET` → Deploy

**Docker**
```bash
docker-compose up -d
```

**Manual**
```bash
chmod +x deploy.sh
./deploy.sh  # validates token & inits DB
```

Health: `/health` • Metrics: `/metrics`

---

## 📂 Structure

```
├── bot.py              # Entry (bot + web)
├── core/               # config, database, cache, logger, rate_limiter
├── handlers/           # admin, start, ai_chat, moderation, captcha, games, knowledge
├── services/           # rag, ai_cache, toxicity
├── web/                # admin panel (FastAPI + Jinja2)
├── templates/          # admin.html, login.html
├── database/           # SQLite + backups
└── tests/              # pytest
```

---

## 🎮 Commands

| Command | Description |
|---------|-------------|
| `/start`, `/help`, `/ping` | Welcome & help |
| `/panel`, `/personality` | Panel link, switch personality |
| `/ban`, `/kick`, `/mute`, `/warn` | Moderation (reply) |
| `/ai <q>`, `/ask <q>`, `/summarize` | AI |
| `/learn q \| a`, `/knowledge` | Knowledge base |
| `/jok`, `/fal`, `/word`, `/quiz`, `/top` | Games |

---

## 🔧 Tech

- **aiogram 3.13** • **FastAPI** • **aiosqlite (WAL)**
- **OpenAI-compatible API Pool** with fallback
- **TTL Cache + background tasks**

---

## 🤝 Contributing

PRs welcome! Please run `pytest -q` before submitting.

## 👤 Author

**shayan.txt** – [github.com/ShayanTxT](https://github.com/ShayanTxT)

> Built with ❤️ for Persian Telegram communities

---

<p align="center">
  <sub>Made by <b>shayan.txt</b> • Luna v2.5 • 2024</sub>
</p>
