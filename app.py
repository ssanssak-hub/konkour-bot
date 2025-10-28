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
        # ایمپورت ربات اصلی
        from main import bot
        
        application = bot.application
        logger.info("✅ ربات با موفقیت import شد")
        
        bot_initialized = True
        return True
        
    except Exception as e:
        logger.error(f"❌ خطا در راه‌اندازی ربات: {e}")
        logger.error(traceback.format_exc())
        return False

async def initialize_bot_async():
    """Initialize bot asynchronously"""
    global application, bot_initialized
    
    if not application:
        logger.error("❌ application موجود نیست")
        return False
        
    try:
        # فقط اگر قبلاً initialize نشده
        if not application.running:
            await application.initialize()
            await application.start()
            logger.info("✅ ربات initialize و start شد")
        
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
        success = loop.run_until_complete(initialize_bot_async())
        if success:
            logger.info("🎉 ربات با موفقیت راه‌اندازی شد")
        else:
            logger.error("💥 خطا در راه‌اندازی ربات")
    except Exception as e:
        logger.error(f"❌ خطا در اجرای async: {e}")

# راه‌اندازی هنگام اولین درخواست
@app.before_request
def startup():
    """Initialize bot on first request"""
    global bot_initialized
    
    if not bot_initialized:
        logger.info("🚀 شروع راه‌اندازی ربات...")
        
        if initialize_bot_sync():
            # اجرای async در background
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
        update_data = request.get_json()
        if not update_data:
            logger.error("❌ داده‌ای دریافت نشد")
            return jsonify({"error": "No data received"}), 400
            
        update_id = update_data.get('update_id', 'unknown')
        logger.info(f"📝 پردازش آپدیت: {update_id}")
        
        # پردازش آپدیت با استفاده از update_queue
        async def process_update():
            await application.update_queue.put(update_data)
        
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
                "webhook_pending_updates": webhook_info.pending_update_count,
                "has_custom_certificate": webhook_info.has_custom_certificate,
                "ip_address": webhook_info.ip_address
            }
        
        info = asyncio.run(get_bot_info())
        return jsonify({"status": "bot_ready", "info": info})
        
    except Exception as e:
        return jsonify({"status": "bot_error", "error": str(e)}), 500

@app.route('/set_webhook', methods=['GET'])
def set_webhook_manual():
    """تنظیم دستی وب‌هوک"""
    if not application:
        return jsonify({"error": "ربات آماده نیست"}), 500
        
    try:
        async def setup_webhook():
            webhook_url = "https://konkour-bot-4i5p.onrender.com/webhook"
            result = await application.bot.set_webhook(
                webhook_url,
                allowed_updates=["message", "callback_query", "chat_member"],
                drop_pending_updates=True
            )
            return result
        
        result = asyncio.run(setup_webhook())
        return jsonify({
            "status": "success",
            "message": "وب‌هوک تنظیم شد",
            "result": result
        })
        
    except Exception as e:
        logger.error(f"❌ خطا در تنظیم وب‌هوک: {e}")
        return jsonify({"error": str(e)}), 500

# راه‌اندازی هنگام استارتاپ
def initialize_on_startup():
    """Initialize bot when the app starts"""
    logger.info("🚀 شروع راه‌اندازی ربات هنگام استارتاپ...")
    
    if initialize_bot_sync():
        # اجرای async در background
        thread = Thread(target=run_async_init)
        thread.daemon = True
        thread.start()
    else:
        logger.error("❌ راه‌اندازی اولیه ربات ناموفق بود")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"🚀 راه‌اندازی سرور روی پورت {port}")
    
    # راه‌اندازی اولیه
    initialize_on_startup()
    
    # اجرای Flask
    app.run(host='0.0.0.0', port=port, debug=False)
