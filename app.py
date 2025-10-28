from flask import Flask, request, jsonify
import os
import asyncio
import logging
import traceback
from threading import Thread

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ایمپورت ربات
application = None
bot_initialized = False

def initialize_bot_sync():
    """Initialize bot synchronously"""
    global application, bot_initialized
    
    try:
        # ایمپورت و تنظیم ربات
        from telegram.ext import ApplicationBuilder
        from main import setup_handlers  # فرض می‌کنیم main.py دارید
        
        # ساخت application
        BOT_TOKEN = os.environ.get('BOT_TOKEN', '8381121739:AAFB2YBMomBh9xhoI3Qn0VVuGaGlpea9fx8')
        application = ApplicationBuilder().token(BOT_TOKEN).build()
        
        # تنظیم هندلرها
        setup_handlers(application)  # این تابع باید در main.py باشد
        
        bot_initialized = True
        logger.info("✅ ربات با موفقیت initialize شد")
        return True
        
    except Exception as e:
        logger.error(f"❌ خطا در راه‌اندازی ربات: {e}")
        logger.error(traceback.format_exc())
        return False

async def initialize_bot_async():
    """Initialize bot asynchronously"""
    global application, bot_initialized
    
    if bot_initialized:
        return True
        
    try:
        await application.initialize()
        await application.start()
        
        # تنظیم وب‌هوک
        webhook_url = "https://konkour-bot-4i5p.onrender.com/webhook"
        await application.bot.set_webhook(
            webhook_url,
            allowed_updates=["message", "callback_query", "chat_member"],
            drop_pending_updates=True
        )
        
        bot_initialized = True
        logger.info(f"✅ وب‌هوک تنظیم شد: {webhook_url}")
        return True
        
    except Exception as e:
        logger.error(f"❌ خطا در راه‌اندازی ربات: {e}")
        return False

def run_async_init():
    """Run async initialization in background"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(initialize_bot_async())
    except Exception as e:
        logger.error(f"❌ خطا در اجرای async: {e}")

# راه‌اندازی هنگام استارتاپ
@app.before_first_request
def startup():
    """Initialize bot on startup"""
    logger.info("🚀 شروع راه‌اندازی ربات...")
    
    # اول initialize سینک
    if initialize_bot_sync():
        # سپس اجرای async در background
        thread = Thread(target=run_async_init)
        thread.daemon = True
        thread.start()
    else:
        logger.error("❌ راه‌اندازی اولیه ربات ناموفق بود")

@app.route('/')
def home():
    return "🤖 ربات کنکور ۱۴۰۵ - فعال ✅"

@app.route('/health')
def health():
    status = {
        "status": "healthy",
        "bot_initialized": bot_initialized,
        "service": "konkour-bot"
    }
    return jsonify(status)

@app.route('/webhook', methods=['POST'])
def webhook():
    """دریافت آپدیت‌های تلگرام"""
    logger.info("📨 دریافت درخواست وب‌هوک")
    
    if not application or not bot_initialized:
        logger.error("❌ ربات آماده نیست")
        return jsonify({"error": "ربات آماده نیست"}), 500
        
    try:
        update = request.get_json()
        if not update:
            logger.error("❌ داده‌ای دریافت نشد")
            return jsonify({"error": "No data received"}), 400
            
        update_id = update.get('update_id', 'unknown')
        logger.info(f"📝 پردازش آپدیت: {update_id}")
        
        # پردازش آپدیت با استفاده از update_queue
        async def process_update():
            await application.update_queue.put(update)
        
        # اجرای async
        asyncio.run(process_update())
        
        logger.info(f"✅ آپدیت {update_id} در صف قرار گرفت")
        return jsonify({"status": "ok", "update_id": update_id}), 200
        
    except Exception as e:
        logger.error(f"❌ خطا در پردازش وب‌هوک: {e}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "Internal server error"}), 500

@app.route('/test', methods=['GET'])
def test_bot():
    """تست وضعیت ربات"""
    if not application or not bot_initialized:
        return jsonify({"status": "bot_not_ready"}), 500
    
    try:
        async def get_bot_info():
            bot_info = await application.bot.get_me()
            webhook_info = await application.bot.get_webhook_info()
            return {
                "bot_username": bot_info.username,
                "bot_name": bot_info.first_name,
                "webhook_url": webhook_info.url,
                "webhook_pending_updates": webhook_info.pending_update_count
            }
        
        info = asyncio.run(get_bot_info())
        return jsonify({"status": "bot_ready", "info": info})
        
    except Exception as e:
        return jsonify({"status": "bot_error", "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"🚀 راه‌اندازی سرور روی پورت {port}")
    
    # راه‌اندازی اولیه
    startup()
    
    # اجرای Flask
    app.run(host='0.0.0.0', port=port, debug=False)
