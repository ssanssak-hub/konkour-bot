from flask import Flask, request, jsonify
import os
import asyncio
import logging
import time

# تنظیم لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ایمپورت ربات
try:
    from main import bot
    logger.info("✅ ربات کنکور ایمپورت شد")
except Exception as e:
    logger.error(f"❌ خطا در ایمپورت ربات: {e}")
    bot = None

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>ربات کنکور</title>
    </head>
    <body style="font-family: Tahoma; text-align: center; padding: 50px;">
        <h1>🤖 ربات کنکور ۱۴۰۵</h1>
        <p>✅ سرویس فعال</p>
        <p>ربات آماده دریافت پیام است</p>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return jsonify({"status": "active", "service": "konkoor-bot"})

@app.route('/webhook', methods=['POST'])
def webhook():
    """دریافت آپدیت‌های تلگرام"""
    logger.info("📨 وب‌هوک دریافت شد")
    
    if not bot:
        return jsonify({"error": "ربات در دسترس نیست"}), 500
        
    try:
        update_data = request.get_json()
        update_id = update_data.get('update_id', 'unknown')
        logger.info(f"📝 پردازش آپدیت: {update_id}")
        
        # پردازش آپدیت
        async def process_update():
            await bot.application.process_update(update_data)
        
        asyncio.run(process_update())
        
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        logger.error(f"❌ خطا: {e}")
        return jsonify({"error": "خطای سرور"}), 500

if __name__ == '__main__':
    # استفاده از پورت از environment variable
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 راه‌اندازی سرور روی پورت {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
