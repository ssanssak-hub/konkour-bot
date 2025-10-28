from flask import Flask, request, jsonify
import os
import asyncio
import logging
import traceback

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ایمپورت ربات
try:
    from main import bot
    logger.info("✅ ربات کنکور راه‌اندازی شد")
except Exception as e:
    logger.error(f"❌ خطا در ایمپورت ربات: {e}")
    logger.error(traceback.format_exc())
    bot = None

@app.route('/')
def home():
    return "🤖 ربات کنکور ۱۴۰۵ - فعال ✅"

@app.route('/health')
def health():
    status = {
        "status": "healthy",
        "bot_loaded": bot is not None,
        "service": "konkour-bot"
    }
    return jsonify(status)

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """تنظیم دستی وب‌هوک"""
    if not bot:
        return jsonify({"error": "ربات آماده نیست"}), 500
        
    try:
        webhook_url = "https://konkour-bot-4i5p.onrender.com/webhook"
        
        async def setup_webhook():
            await bot.application.bot.delete_webhook()
            result = await bot.application.bot.set_webhook(
                url=webhook_url,
                allowed_updates=["message", "callback_query"],
                drop_pending_updates=True
            )
            return result
        
        result = asyncio.run(setup_webhook())
        return jsonify({
            "status": "success",
            "message": "وب‌هوک تنظیم شد",
            "url": webhook_url,
            "result": str(result)
        })
        
    except Exception as e:
        logger.error(f"❌ خطا در تنظیم وب‌هوک: {e}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    """دریافت آپدیت‌های تلگرام"""
    logger.info("📨 دریافت درخواست وب‌هوک")
    
    if not bot:
        logger.error("❌ ربات در دسترس نیست")
        return jsonify({"error": "ربات در دسترس نیست"}), 500
        
    try:
        # لاگ کامل درخواست
        logger.info(f"📝 headers: {dict(request.headers)}")
        logger.info(f"📝 content_type: {request.content_type}")
        
        if not request.is_json:
            logger.error("❌ درخواست JSON نیست")
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        data = request.get_json()
        if not data:
            logger.error("❌ داده‌ای دریافت نشد")
            return jsonify({"error": "No data received"}), 400
            
        logger.info(f"📝 داده دریافتی: {data}")
        
        # پردازش آپدیت
        async def process_update():
            try:
                await bot.application.process_update(data)
                logger.info("✅ آپدیت با موفقیت پردازش شد")
            except Exception as e:
                logger.error(f"❌ خطا در پردازش آپدیت: {e}")
                logger.error(traceback.format_exc())
                raise
        
        asyncio.run(process_update())
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        logger.error(f"❌ خطا در پردازش وب‌هوک: {e}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"🚀 راه‌اندازی سرور روی پورت {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
