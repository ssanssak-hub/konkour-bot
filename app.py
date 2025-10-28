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

# ایمپورت و initialize ربات
bot = None
application = None

try:
    from main import bot as main_bot
    bot = main_bot
    application = bot.application
    
    # Initialize the application
    async def initialize_bot():
        await application.initialize()
        await application.start()
        logger.info("✅ ربات initialize شد")
    
    asyncio.run(initialize_bot())
    logger.info("✅ ربات کنکور راه‌اندازی شد")
    
except Exception as e:
    logger.error(f"❌ خطا در راه‌اندازی ربات: {e}")
    logger.error(traceback.format_exc())
    bot = None
    application = None

@app.route('/')
def home():
    return "🤖 ربات کنکور ۱۴۰۵ - فعال ✅"

@app.route('/health')
def health():
    status = {
        "status": "healthy",
        "bot_loaded": bot is not None,
        "app_initialized": application is not None,
        "service": "konkour-bot"
    }
    return jsonify(status)

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """تنظیم دستی وب‌هوک"""
    if not application:
        return jsonify({"error": "ربات آماده نیست"}), 500
        
    try:
        webhook_url = "https://konkour-bot-4i5p.onrender.com/webhook"
        
        async def setup_webhook():
            await application.bot.delete_webhook()
            result = await application.bot.set_webhook(
                url=webhook_url,
                allowed_updates=["message", "callback_query"],
                drop_pending_updates=True
            )
            return result
        
        result = asyncio.run(setup_webhook())
        return jsonify({
            "status": "success",
            "message": "وب‌هوک تنظیم شد",
            "url": webhook_url
        })
        
    except Exception as e:
        logger.error(f"❌ خطا در تنظیم وب‌هوک: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    """دریافت آپدیت‌های تلگرام"""
    logger.info("📨 دریافت درخواست وب‌هوک")
    
    if not application:
        logger.error("❌ ربات در دسترس نیست")
        return jsonify({"error": "ربات در دسترس نیست"}), 500
        
    try:
        data = request.get_json()
        if not data:
            logger.error("❌ داده‌ای دریافت نشد")
            return jsonify({"error": "No data received"}), 400
            
        logger.info(f"📝 پردازش آپدیت: {data.get('update_id', 'unknown')}")
        
        # پردازش آپدیت
        async def process_update():
            await application.process_update(data)
        
        asyncio.run(process_update())
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        logger.error(f"❌ خطا در پردازش وب‌هوک: {e}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "Internal server error"}), 500

# Cleanup هنگام خروج
import atexit
async def cleanup():
    if application:
        await application.stop()
        await application.shutdown()

atexit.register(lambda: asyncio.run(cleanup()))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"🚀 راه‌اندازی سرور روی پورت {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
