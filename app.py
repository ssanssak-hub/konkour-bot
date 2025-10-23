from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import os
import logging
from main import setup_handlers, setup_error_handler, initialize_database
import config

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ایجاد اپلیکیشن تلگرام - اینجا مشکل بود
application = Application.builder().token(config.Config.BOT_TOKEN).build()

# تنظیم هندلرها (استفاده از توابع مشترک با main.py)
setup_handlers(application)
setup_error_handler(application)

@app.route('/')
def home():
    """صفحه اصلی"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ربات کنکور ۱۴۰۵</title>
        <meta charset="utf-8">
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
            .container { max-width: 600px; margin: 0 auto; background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; backdrop-filter: blur(10px); }
            h1 { font-size: 2.5em; margin-bottom: 20px; }
            .status { background: #4CAF50; padding: 10px; border-radius: 5px; margin: 20px 0; }
            .links { margin-top: 30px; }
            .links a { color: white; text-decoration: none; margin: 0 10px; padding: 10px 20px; border: 1px solid white; border-radius: 5px; transition: all 0.3s; }
            .links a:hover { background: white; color: #667eea; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 ربات کنکور ۱۴۰۵</h1>
            <p>ربات مدیریت و برنامه‌ریزی کنکور ۱۴۰۵</p>
            <div class="status">✅ سرویس فعال و در حال اجرا</div>
            <div class="links">
                <a href="/health">بررسی سلامت</a>
                <a href="/stats">آمار سیستم</a>
            </div>
        </div>
    </html>
    """

@app.route('/webhook', methods=['POST'])
async def webhook():
    """دریافت به‌روزرسانی‌ها از تلگرام"""
    try:
        # دریافت داده‌های وب‌هوک
        json_data = request.get_json()
        
        if not json_data:
            logger.warning("درخواست وب‌هوک بدون داده دریافت شد")
            return jsonify({"status": "error", "message": "No data received"}), 400
        
        # ایجاد آبجکت Update از داده‌های دریافتی
        update = Update.de_json(json_data, application.bot)
        
        # پردازش به‌روزرسانی
        await application.process_update(update)
        
        logger.debug("وب‌هوک با موفقیت پردازش شد")
        return jsonify({"status": "success"}), 200
    
    except Exception as e:
        logger.error(f"خطا در پردازش وب‌هوک: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/set_webhook', methods=['GET', 'POST'])
async def set_webhook():
    """تنظیم وب‌هوک در تلگرام"""
    try:
        webhook_url = f"{config.Config.WEBHOOK_URL}/webhook"
        
        # حذف وب‌هوک قبلی
        await application.bot.delete_webhook()
        
        # تنظیم وب‌هوک جدید
        result = await application.bot.set_webhook(
            url=webhook_url,
            max_connections=40,
            allowed_updates=["message", "callback_query", "chat_member", "my_chat_member"]
        )
        
        webhook_info = await application.bot.get_webhook_info()
        
        response_data = {
            "status": "success",
            "webhook_url": webhook_url,
            "webhook_info": {
                "url": webhook_info.url,
                "has_custom_certificate": webhook_info.has_custom_certificate,
                "pending_update_count": webhook_info.pending_update_count,
                "max_connections": webhook_info.max_connections,
                "allowed_updates": webhook_info.allowed_updates
            }
        }
        
        logger.info(f"وب‌هوک با موفقیت تنظیم شد: {webhook_url}")
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"خطا در تنظیم وب‌هوک: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/remove_webhook', methods=['GET'])
async def remove_webhook():
    """حذف وب‌هوک"""
    try:
        result = await application.bot.delete_webhook()
        logger.info("وب‌هوک با موفقیت حذف شد")
        return jsonify({"status": "success", "message": "Webhook removed successfully"}), 200
    except Exception as e:
        logger.error(f"خطا در حذف وب‌هوک: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """بررسی سلامت سرور"""
    try:
        # بررسی سلامت پایه
        health_data = {
            "status": "healthy",
            "service": "Konkur 1405 Bot",
            "timestamp": "2024",
            "environment": config.Config.ENVIRONMENT,
            "bot_token_set": bool(config.Config.BOT_TOKEN and config.Config.BOT_TOKEN != "your_telegram_bot_token_here")
        }
        
        return jsonify(health_data), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

@app.route('/stats', methods=['GET'])
def stats():
    """آمار سیستم"""
    try:
        stats_data = {
            "environment": config.Config.ENVIRONMENT,
            "webhook_url": config.Config.WEBHOOK_URL,
            "bot_username": config.Config.BOT_USERNAME,
            "admin_id": config.Config.ADMIN_ID,
            "database_url": config.Config.DATABASE_URL
        }
        
        return jsonify(stats_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/test', methods=['GET'])
def test():
    """صفحه تست برای بررسی عملکرد"""
    return jsonify({
        "message": "ربات کنکور ۱۴۰۵ فعال است",
        "status": "operational",
        "timestamp": "2024",
        "environment": config.Config.ENVIRONMENT
    })

# راه‌اندازی اولیه
@app.before_first_request
def initialize():
    """راه‌اندازی اولیه برنامه"""
    try:
        if initialize_database():
            logger.info("✅ برنامه با موفقیت راه‌اندازی شد")
        else:
            logger.error("❌ خطا در راه‌اندازی برنامه")
    except Exception as e:
        logger.error(f"❌ خطا در راه‌اندازی اولیه: {e}")

# راه‌اندازی سرور
if __name__ == '__main__':
    # مقدار PORT توسط رندر ارائه می‌شود
    port = int(os.environ.get('PORT', 5000))
    
    logger.info(f"🌐 شروع سرویس Flask روی پورت {port}")
    logger.info(f"🎯 محیط: {config.Config.ENVIRONMENT}")
    logger.info("💡 برای تنظیم وب‌هوک به /set_webhook مراجعه کنید")
    
    app.run(host='0.0.0.0', port=port, debug=config.Config.DEBUG)
