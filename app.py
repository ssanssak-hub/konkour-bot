import os
import logging
import asyncio
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, ContextTypes

# تنظیمات اولیه
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# تنظیمات مستقیماً از محیط
BOT_TOKEN = os.environ.get('BOT_TOKEN', '')
ADMIN_ID = os.environ.get('ADMIN_ID', '')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', 'https://konkour-bot.onrender.com')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'production')

# ایجاد application ربات
application = Application.builder().token(BOT_TOKEN).build()

def setup_handlers():
    """وارد کردن و تنظیم هندلرها"""
    try:
        from handlers.main_menu import setup_main_menu_handlers
        from handlers.countdown import setup_countdown_handlers
        from handlers.calendar import setup_calendar_handlers
        from handlers.reminders import setup_reminders_handlers
        from handlers.messages import setup_messages_handlers
        from handlers.attendance import setup_attendance_handlers
        from handlers.study_plan import setup_study_plan_handlers
        from handlers.statistics import setup_statistics_handlers
        from handlers.help import setup_help_handlers
        from handlers.admin import setup_admin_handlers
        
        # تنظیم هندلرها
        setup_main_menu_handlers(application)
        setup_countdown_handlers(application)
        setup_calendar_handlers(application)
        setup_reminders_handlers(application)
        setup_messages_handlers(application)
        setup_attendance_handlers(application)
        setup_study_plan_handlers(application)
        setup_statistics_handlers(application)
        setup_help_handlers(application)
        setup_admin_handlers(application)
        
        logger.info("✅ تمام هندلرها تنظیم شدند")
        return True
    except Exception as e:
        logger.error(f"❌ خطا در تنظیم هندلرها: {e}")
        return False

def initialize_database():
    """راه‌اندازی اولیه دیتابیس"""
    try:
        from database.base import db
        db.create_tables()
        logger.info("✅ جداول دیتابیس ایجاد شدند")
        return True
    except Exception as e:
        logger.error(f"❌ خطا در ایجاد جداول دیتابیس: {e}")
        return False

async def process_update(update_data):
    """پردازش آپدیت دریافتی"""
    try:
        update = Update.de_json(update_data, application.bot)
        await application.process_update(update)
        return True
    except Exception as e:
        logger.error(f"❌ خطا در پردازش آپدیت: {e}")
        return False

@app.route('/')
def home():
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
            .error { background: #f44336; padding: 10px; border-radius: 5px; margin: 20px 0; }
            .links { margin-top: 30px; }
            .links a { color: white; text-decoration: none; margin: 0 10px; padding: 10px 20px; border: 1px solid white; border-radius: 5px; transition: all 0.3s; }
            .links a:hover { background: white; color: #667eea; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 ربات کنکور ۱۴۰۵</h1>
            <p>ربات مدیریت و برنامه‌ریزی کنکور ۱۴۰۵</p>
            
            <div class="status">
                ✅ سرویس فعال و در حال اجرا
            </div>
            
            <p>ربات با موفقیت deploy شده و آماده دریافت پیام‌هاست.</p>
            
            <div class="links">
                <a href="/health">بررسی سلامت</a>
                <a href="/setup_webhook">تنظیم وب‌هوک</a>
                <a href="https://t.me/konkur1405_bot">ربات تلگرام</a>
            </div>
        </div>
    </html>
    """

@app.route('/health')
def health():
    """بررسی سلامت"""
    return jsonify({
        "status": "healthy",
        "service": "Konkur 1405 Bot",
        "environment": ENVIRONMENT,
        "bot_configured": bool(BOT_TOKEN and BOT_TOKEN != "your_telegram_bot_token_here"),
        "webhook_url": WEBHOOK_URL,
        "server": "konkour-bot.onrender.com"
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """وب‌هوک تلگرام"""
    if request.method == 'POST':
        try:
            update_data = request.get_json()
            logger.info(f"📨 دریافت وب‌هوک: {update_data}")
            
            # پردازش آپدیت به صورت async
            asyncio.run(process_update(update_data))
            
            return jsonify({"status": "success"})
            
        except Exception as e:
            logger.error(f"❌ خطا در پردازش وب‌هوک: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500
    
    return jsonify({"status": "error", "message": "Method not allowed"}), 405

def set_telegram_webhook():
    """تنظیم وب‌هوک در تلگرام"""
    try:
        import requests
        
        webhook_url = f"{WEBHOOK_URL}/webhook"
        
        # حذف وب‌هوک قبلی
        delete_url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
        delete_response = requests.get(delete_url, timeout=10)
        
        # تنظیم وب‌هوک جدید
        set_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
        payload = {
            "url": webhook_url,
            "max_connections": 40,
            "allowed_updates": ["message", "callback_query", "chat_member"]
        }
        
        response = requests.post(set_url, json=payload, timeout=10)
        result = response.json()
        
        if result.get('ok'):
            logger.info(f"✅ وب‌هوک با موفقیت تنظیم شد: {webhook_url}")
            return True, result
        else:
            logger.error(f"❌ خطا در تنظیم وب‌هوک: {result}")
            return False, result
            
    except Exception as e:
        logger.error(f"❌ خطا در تنظیم وب‌هوک: {e}")
        return False, {"error": str(e)}

@app.route('/setup_webhook')
def setup_webhook_route():
    """تنظیم وب‌هوک"""
    try:
        if not BOT_TOKEN or BOT_TOKEN == "your_telegram_bot_token_here":
            return jsonify({
                "status": "error", 
                "message": "BOT_TOKEN تنظیم نشده است"
            }), 400
        
        success, result = set_telegram_webhook()
        
        if success:
            return jsonify({
                "status": "success",
                "message": "✅ وب‌هوک با موفقیت تنظیم شد!",
                "webhook_url": f"{WEBHOOK_URL}/webhook",
                "result": result
            })
        else:
            return jsonify({
                "status": "error",
                "message": "❌ خطا در تنظیم وب‌هوک",
                "result": result
            }), 500
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# راه‌اندازی اولیه
def initialize():
    """راه‌اندازی اولیه ربات"""
    logger.info("🚀 در حال راه‌اندازی ربات...")
    
    # راه‌اندازی دیتابیس
    if not initialize_database():
        logger.error("❌ خطا در راه‌اندازی دیتابیس")
        return False
    
    # تنظیم هندلرها
    if not setup_handlers():
        logger.error("❌ خطا در تنظیم هندلرها")
        return False
    
    # تنظیم وب‌هوک
    if BOT_TOKEN and BOT_TOKEN != "your_telegram_bot_token_here":
        success, _ = set_telegram_webhook()
        if success:
            logger.info("✅ وب‌هوک تنظیم شد")
        else:
            logger.warning("⚠️ خطا در تنظیم وب‌هوک")
    
    logger.info("✅ ربات با موفقیت راه‌اندازی شد")
    return True

# راه‌اندازی هنگام شروع
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    if initialize():
        logger.info(f"🚀 شروع سرویس روی پورت {port}")
        app.run(host='0.0.0.0', port=port, debug=ENVIRONMENT == 'development')
    else:
        logger.error("❌ خطا در راه‌اندازی ربات")

# اجرای راه‌اندازی
initialize()
