# 🤖 ربات کنکور ۱۴۰۵ - راهنمای نصب

## 🚀 استقرار در رندر (Render.com)

### ۱. آماده‌سازی
- فایل‌های پروژه را در GitHub آپلود کنید
- به [Render.com](https://render.com) بروید و حساب ایجاد کنید

### ۲. ایجاد سرویس جدید
- روی "New +" کلیک کنید
- "Web Service" را انتخاب کنید
- ریپازیتوری GitHub خود را connect کنید

### ۳. تنظیمات استقرار
- **Name**: `konkur-bot`
- **Environment**: `Python`
- **Region**: `Frankfurt` (یا نزدیک‌ترین)
- **Branch**: `main`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app --config gunicorn_config.py`

### ۴. تنظیم متغیرهای محیطی
- `ENVIRONMENT`: `production`

### ۵. استقرار
- روی "Create Web Service" کلیک کنید
- منتظر بمانید تا استقرار کامل شود

### ۶. تنظیم وب‌هوک
پس از استقرار، آدرس زیر را در مرورگر باز کنید:
