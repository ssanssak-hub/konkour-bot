from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
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
from database.base import db
import config
import logging
import os
from flask import Flask, request, jsonify

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# ایجاد اپلیکیشن Flask
app = Flask(__name__)

# ایجاد اپلیکیشن تلگرام
telegram_app = Application.builder().token(config.Config.BOT_TOKEN).build()

def setup_handlers(application):
    """تنظیم تمام هندلرهای ربات"""
    logger.info("🔧 در حال تنظیم هندلرها...")
    
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
    
    # هندلر برای پیام‌های متنی عمومی
    async def handle_unknown_message(update, context):
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        keyboard = [
            [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🤔 متوجه پیام شما نشدم!\n\n"
            "لطفاً از منوی اصلی استفاده کنید یا دستور /start را وارد کنید.",
            reply_markup=reply_markup
        )
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_unknown_message), group=100)

def setup_error_handler(application):
    """تنظیم هندلر خطاها"""
    async def error_handler(update, context):
        logger.error(f"خطا رخ داد: {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ متأسفانه خطایی رخ داد!\n\n"
                "لطفاً دوباره تلاش کنید یا با ادمین تماس بگیرید."
            )
    
    application.add_error_handler(error_handler)

def initialize_database():
    """راه‌اندازی اولیه دیتابیس"""
    try:
        db.create_tables()
        logger.info("✅ جداول دیتابیس ایجاد شدند")
        return True
    except Exception as e:
        logger.error(f"❌ خطا در ایجاد جداول دیتابیس: {e}")
        return False

def initialize_bot():
    """راه‌اندازی اولیه ربات"""
    logger.info("🚀 در حال راه‌اندازی ربات...")
    
    # راه‌اندازی دیتابیس
    if not initialize_database():
        logger.error("❌ خطا در راه‌اندازی دیتابیس")
        return False

    # تنظیم هندلرها
    setup_handlers(telegram_app)
    setup_error_handler(telegram_app)
    
    logger.info("✅ ربات با موفقیت راه‌اندازی شد")
    return True

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
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                text-align: center; 
                padding: 50px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; 
            }
            .container { 
                max-width: 600px; 
                margin: 0 auto; 
                background: rgba(255,255,255,0.1); 
                padding: 30px; 
                border-radius: 15px; 
                backdrop-filter: blur(10px); 
            }
            h1 { 
                font-size: 2.5em; 
                margin-bottom: 20px; 
            }
            .status { 
                background: #4CAF50; 
                padding: 10px; 
                border-radius: 5px; 
                margin: 20px 0; 
            }
            .error { 
                background: #f44336; 
                padding: 10px; 
                border-radius: 5px; 
                margin: 20px 0; 
            }
            .links { 
                margin-top: 30px; 
            }
            .links a { 
                color: white; 
                text-decoration: none; 
                margin: 0 10px; 
                padding: 10px 20px; 
                border: 1px solid white; 
                border-radius: 5px; 
                transition: all 0.3s; 
            }
            .links a:hover { 
                background: white; 
                color: #667eea; 
            }
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
    """بررسی سلامت سرویس"""
    return jsonify({
        "status": "healthy",
        "service": "Konkur 1405 Bot",
        "environment": config.Config.ENVIRONMENT,
        "bot_configured": bool(config.Config.BOT_TOKEN and config.Config.BOT_TOKEN != "your_telegram_bot_token_here"),
        "webhook_url": config.Config.WEBHOOK_URL,
        "database_initialized": True
    })

@app.route('/setup_webhook')
def setup_webhook():
    """تنظیم وب‌هوک تلگرام"""
    try:
        import requests
        
        webhook_url = f"{config.Config.WEBHOOK_URL}/webhook"
        
        # حذف وب‌هوک قبلی
        delete_url = f"https://api.telegram.org/bot{config.Config.BOT_TOKEN}/deleteWebhook"
        delete_response = requests.get(delete_url, timeout=10)
        
        # تنظیم وب‌هوک جدید
        set_url = f"https://api.telegram.org/bot{config.Config.BOT_TOKEN}/setWebhook"
        payload = {
            "url": webhook_url,
            "max_connections": 40,
            "allowed_updates": ["message", "callback_query", "chat_member"]
        }
        
        response = requests.post(set_url, json=payload, timeout=10)
        result = response.json()
        
        if result.get('ok'):
            logger.info(f"✅ وب‌هوک با موفقیت تنظیم شد: {webhook_url}")
            return jsonify({
                "status": "success",
                "message": "✅ وب‌هوک با موفقیت تنظیم شد!",
                "webhook_url": webhook_url,
                "result": result
            })
        else:
            logger.error(f"❌ خطا در تنظیم وب‌هوک: {result}")
            return jsonify({
                "status": "error",
                "message": "❌ خطا در تنظیم وب‌هوک",
                "result": result
            }), 500
            
    except Exception as e:
        logger.error(f"❌ خطا در تنظیم وب‌هوک: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    """دریافت وب‌هوک از تلگرام"""
    if request.method == 'POST':
        try:
            # دریافت آپدیت از تلگرام
            update_data = request.get_json()
            logger.info(f"📨 دریافت وب‌هوک: {update_data}")
            
            # ایجاد آبجکت Update
            update = Update.de_json(update_data, telegram_app.bot)
            
            # پردازش آپدیت به صورت همزمان
            import asyncio
            asyncio.run(telegram_app.process_update(update))
            
            return jsonify({"status": "success"})
            
        except Exception as e:
            logger.error(f"❌ خطا در پردازش وب‌هوک: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500
    
    return jsonify({"status": "error", "message": "Method not allowed"}), 405

@app.route('/remove_webhook')
def remove_webhook():
    """حذف وب‌هوک"""
    try:
        import requests
        
        delete_url = f"https://api.telegram.org/bot{config.Config.BOT_TOKEN}/deleteWebhook"
        response = requests.get(delete_url, timeout=10)
        result = response.json()
        
        if result.get('ok'):
            return jsonify({
                "status": "success", 
                "message": "✅ وب‌هوک با موفقیت حذف شد"
            })
        else:
            return jsonify({
                "status": "error",
                "message": "❌ خطا در حذف وب‌هوک",
                "result": result
            }), 500
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_webhook_info')
def get_webhook_info():
    """دریافت اطلاعات وب‌هوک"""
    try:
        import requests
        
        info_url = f"https://api.telegram.org/bot{config.Config.BOT_TOKEN}/getWebhookInfo"
        response = requests.get(info_url, timeout=10)
        result = response.json()
        
        return jsonify({
            "status": "success",
            "webhook_info": result
        })
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# راه‌اندازی اولیه هنگام import
if initialize_bot():
    logger.info("🤖 ربات آماده دریافت پیام‌ها از طریق وب‌هوک")
else:
    logger.error("❌ خطا در راه‌اندازی ربات")

# برای اجرای مستقیم با Flask
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 شروع سرویس روی پورت {port}")
    logger.info(f"🔧 محیط: {config.Config.ENVIRONMENT}")
    logger.info(f"🌐 سرور: {config.Config.WEBHOOK_URL}")
    
    if not config.Config.BOT_TOKEN or config.Config.BOT_TOKEN == "your_telegram_bot_token_here":
        logger.error("❌ BOT_TOKEN تنظیم نشده است!")
    else:
        logger.info("✅ BOT_TOKEN تنظیم شده است")
    
    app.run(host='0.0.0.0', port=port, debug=config.Config.ENVIRONMENT == 'development')

# این برای Gunicorn لازمه
application = app
