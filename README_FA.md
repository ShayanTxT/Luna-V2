<p align="center">
  <img src="assets/banner.png" alt="بنر لونا" width="100%" />
</p>

<p align="center">
  <a href="https://github.com/ShayanTxT/luna-bot"><img src="https://img.shields.io/github/stars/ShayanTxT/luna-bot?style=social" alt="Stars"></a>
  <img src="https://img.shields.io/badge/python-3.11+-3776ab?style=flat&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Telegram-Bot-26A5E4?style=flat&logo=telegram" alt="Telegram">
  <a href="README.md">🇬🇧 English</a>
</p>

<h1 align="center">🌙 لونا - ربات مدیریت گروه</h1>
<p align="center">
  <b>مدیر هوشمند گروه + دوست باحال</b><br>
  ضد لینک و اسپم • کپچا • ۴ شخصیت • دانش گروه • کم‌مصرف
</p>

<p align="center">
  <a href="https://render.com/deploy?repo=https://github.com/ShayanTxT/luna-bot"><img src="https://render.com/images/deploy-to-render-button.svg" alt="Deploy"></a>
</p>

---

## ✨ قابلیت‌ها

### 🛡️ مدیریت هوشمند
- ضد لینک / فوروارد / استیکر / اسپم / فحش (هر کدام جدا)
- درجه سختی ۱ تا ۳، سیستم اخطار (`/warn` → بن خودکار)
- `/ban /kick /mute /unmute /purge /pin`

### 🤖 هوش نسل بعدی
- **۴ شخصیت:** شوخ 😜، ناز 💖، لات 😎، رُک 🔥 (`/personality`)
- **دانش گروه:** `/learn سوال | جواب` → `/ask` بدون مصرف توکن
- **خلاصه چت:** `/summarize` برای ۳۰ پیام آخر
- **بهینه توکن:** تا ۶۰٪ ذخیره با کش و خلاصه‌سازی

### 🧩 کپچا
- سوال ریاضی بدو ورود، اگر ۱۲۰ ثانیه تایید نکند کیک

### 🎮 سرگرمی
- `/jok` جوک، `/fal` فال، `/word` حدس کلمه، `/quiz`، `/top`

### 🎛️ پنل وب
- ورود با `WEB_SECRET` در `/admin`
- مدیریت گروه‌ها، فیلترها، شخصیت و **API Pool** (چرخش خودکار Groq/OpenRouter)

---

## 🚀 راه‌اندازی سریع

**۱. توکن بگیر**
- ربات: **@BotFather** → `/newbot`
- هوش رایگان: **console.groq.com/keys**

**۲. اجرا**
```bash
cp .env.example .env  # توکن و کلید را پر کن
pip install -r requirements.txt
python bot.py
# ربات + پنل http://localhost:8000/admin
```

**۳. به گروه اضافه کن**
- لونا را ادمین کن (تیک حذف پیام)
- بفرست: `لونا سلام` یا `/start`

---

## 🐳 دیپلوی

**Render (یک کلیک):** دکمه بالا → `BOT_TOKEN` و `WEB_SECRET` را بذار → Deploy

**Docker:**
```bash
docker-compose up -d
```

سلامتی: `/health` • متریک: `/metrics`

---

## 📂 ساختار

```
├── bot.py
├── core/         # تنظیمات، دیتابیس، کش، لاگر
├── handlers/     # ادمین، هوش، مدیریت، کپچا، بازی، دانش
├── services/     # RAG، کش هوش
├── web/          # پنل ادمین
└── tests/
```

---

## 🎮 دستورات

| دستور | توضیح |
|-------|--------|
| `/start` `/help` `/ping` | خوش‌آمد و راهنما |
| `/panel` `/personality` | پنل، تغییر شخصیت |
| `/ban` `/warn` `/purge` | مدیریت |
| `/ai` `/ask` `/summarize` | هوش |
| `/learn` `/knowledge` | آموزش ربات |
| `/jok` `/word` `/quiz` | بازی |

---

## 👤 سازنده

**shayan.txt** – [github.com/ShayanTxT](https://github.com/ShayanTxT)

> با ❤️ برای گروه‌های ایرانی

<p align="center">
  <sub>ساخته شده توسط <b>shayan.txt</b> • نسخه ۲.۵</sub>
</p>
