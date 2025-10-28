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
application = None
bot_initialized = False

def initialize_bot():
    """Initialize bot"""
    global application, bot_initialized
    
    try:
        from main import get_application
        
        application = get_application()
        logger.info("✅ ربات با موفقیت import شد")
        
        bot_initialized = True
        return True
        
    except Exception as e:
        logger.error(f"❌ خطا در راه‌اندازی ربات: {e}")
        logger.error(traceback.format_exc())
        return False

async def setup_webhook_async():
    """Setup webhook asynchronously"""
    global application
    
    if not application:
        return False
        
    try:
        webhook_url = "https://konkour-bot-4i5p.onrender.com/webhook"
        await application.bot.set_webhook(
            webhook_url,
            allowed_updates=["message", "callback_query", "chat_member"],
            drop_pending_updates=True
        )
        logger.info(f"✅ وب‌هوک تنظیم شد: {webhook_url}")
        return True
        
    except Exception as e:
        logger.error(f"❌ خطا در تنظیم وب‌هوک: {e}")
        return False

# راه‌اندازی هنگام استارتاپ
@app.before_request
def startup():
    """Initialize bot on first request"""
    global bot_initialized
    
    if not bot_initialized:
        logger.info("🚀 شروع راه‌اندازی ربات...")
        if initialize_bot():
            # تنظیم وب‌هوک
            asyncio.run(setup_webhook_async())
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
        
        # پردازش آپدیت
        async def process_update():
            await application.process_update(update_data)
        
        asyncio.run(process_update())
        
        logger.info(f"✅ آپدیت {update_id} پردازش شد")
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
        result = asyncio.run(setup_webhook_async())
        return jsonify({
            "status": "success" if result else "error",
            "message": "وب‌هوک تنظیم شد" if result else "خطا در تنظیم وب‌هوک"
        })
        
    except Exception as e:
        logger.error(f"❌ خطا در تنظیم وب‌هوک: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"🚀 راه‌اندازی سرور روی پورت {port}")
    
    # راه‌اندازی اولیه
    initialize_bot()
    asyncio.run(setup_webhook_async())
    
    # اجرای Flask
    app.run(host='0.0.0.0', port=port, debug=False)
