from flask import Flask, request, jsonify
import os
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

try:
    from main import bot
    logger.info("✅ ربات لود شد")
except Exception as e:
    logger.error(f"❌ خطا: {e}")
    bot = None

@app.route('/')
def home():
    return "🤖 ربات کنکور ۱۴۰۵ - فعال ✅"

@app.route('/health')
def health():
    return jsonify({"status": "active", "service": "konkoor-bot"})

@app.route('/webhook', methods=['POST'])
def webhook():
    if not bot:
        return jsonify({"error": "ربات آماده نیست"}), 500
        
    try:
        data = request.get_json()
        logger.info(f"📨 دریافت پیام: {data}")
        
        async def process():
            await bot.application.process_update(data)
        
        asyncio.run(process())
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        logger.error(f"❌ خطا: {e}")
        return jsonify({"error": "خطای پردازش"}), 500

if __name__ == '__main__':
    # استفاده از HOST 0.0.0.0 برای دسترسی از بیرون
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 اجرای سرور روی 0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
