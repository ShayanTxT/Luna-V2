#!/bin/bash
# shayan.txt - one-click deploy helper
set -e
echo "🌙 Luna Deploy"
if [ -z "$BOT_TOKEN" ]; then
  echo "❌ BOT_TOKEN missing! Get from @BotFather then:"
  echo "   export BOT_TOKEN='1234:AAH...'"
  exit 1
fi
if ! echo "$BOT_TOKEN" | grep -qE "^[0-9]+:[A-Za-z0-9_-]{30,}"; then
  echo "❌ BOT_TOKEN invalid"
  exit 1
fi
echo "✅ Token ok"
echo "📦 Installing..."
pip install -q -r requirements.txt
echo "🗄️ Init DB..."
python -c "import asyncio; from core.database import db_manager; asyncio.run(db_manager.init())"
echo "🚀 Starting..."
exec python bot.py
