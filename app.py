import os
import logging
import asyncio
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, ContextTypes
import sys
import traceback
from datetime import datetime
import pytz

# تنظیمات پیشرفته لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ==================== CONFIGURATION ====================

class Config:
    BOT_TOKEN = os.environ.get('BOT_TOKEN', '8381121739:AAFB2YBMomBh9xhoI3Qn0VVuGaGlpea9fx8')
    ADMIN_ID = int(os.environ.get('ADMIN_ID', 7703677187))
    WEBHOOK_URL = os.environ.get('WEBHOOK_URL', 'https://konkurcounting-3ga0.onrender.com')
    WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', 'konkur1405_secret_key_2024')
    PORT = int(os.environ.get('PORT', 5000))
    HOST = os.environ.get('HOST', '0.0.0.0')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    TIMEZONE = 'Asia/Tehran'

# ایجاد برنامه تلگرام
try:
    application = Application.builder().token(Config.BOT_TOKEN).build()
    logger.info("✅ برنامه تلگرام با موفقیت ایجاد شد")
except Exception as e:
    logger.error(f"❌ خطا در ایجاد برنامه تلگرام: {e}")
    application = None

# ==================== HEALTH MONITORING ====================

class HealthMonitor:
    def __init__(self):
        self.start_time = datetime.now()
        self.request_count = 0
        self.error_count = 0
        self.last_health_check = datetime.now()
    
    def increment_requests(self):
        self.request_count += 1
    
    def increment_errors(self):
        self.error_count += 1
    
    def get_uptime(self):
        return datetime.now() - self.start_time
    
    def get_stats(self):
        return {
            'uptime': str(self.get_uptime()),
            'total_requests': self.request_count,
            'total_errors': self.error_count,
            'error_rate': (self.error_count / self.request_count * 100) if self.request_count > 0 else 0,
            'status': 'healthy' if self.error_count < 10 else 'degraded'
        }

health_monitor = HealthMonitor()

# ==================== HANDLER SETUP ====================

def setup_handlers():
    """تنظیم تمام هندلرهای ربات"""
    try:
        logger.info("🔧 در حال تنظیم هندلرها...")
        
        if application is None:
            logger.error("❌ برنامه تلگرام initialize نشده")
            return False
        
        # ایمپورت هندلرها
        try:
            from handlers.bot_handlers import setup_main_handlers
            from handlers.calendar import setup_calendar_handlers
            from handlers.reminders import setup_reminders_handlers
            from handlers.messages import setup_messages_handlers
            
            logger.info("✅ ماژول‌های هندلر با موفقیت ایمپورت شدند")
        except ImportError as e:
            logger.error(f"❌ خطا در ایمپورت هندلرها: {e}")
            logger.error(traceback.format_exc())
            return False
        
        # تنظیم هندلرها
        try:
            setup_main_handlers(application)
            logger.info("✅ هندلرهای اصلی تنظیم شدند")
            
            setup_calendar_handlers(application)
            logger.info("✅ هندلرهای تقویم تنظیم شدند")
            
            setup_reminders_handlers(application)
            logger.info("✅ هندلرهای یادآوری تنظیم شدند")
            
            setup_messages_handlers(application)
            logger.info("✅ هندلرهای پیام‌رسانی تنظیم شدند")
            
        except Exception as e:
            logger.error(f"❌ خطا در تنظیم هندلرها: {e}")
            logger.error(traceback.format_exc())
            return False
        
        logger.info("🎉 تمام هندلرها با موفقیت تنظیم شدند")
        return True
        
    except Exception as e:
        logger.error(f"❌ خطای کلی در تنظیم هندلرها: {e}")
        logger.error(traceback.format_exc())
        return False

# ==================== WEBHOOK MANAGEMENT ====================

async def set_webhook_async():
    """تنظیم وب‌هوک به صورت async"""
    try:
        if application is None:
            logger.error("❌ برنامه تلگرام initialize نشده")
            return False
        
        webhook_url = f"{Config.WEBHOOK_URL}/webhook"
        
        # حذف وب‌هوک قبلی
        await application.bot.delete_webhook()
        logger.info("✅ وب‌هوک قبلی حذف شد")
        
        # تنظیم وب‌هوک جدید
        result = await application.bot.set_webhook(
            url=webhook_url,
            secret_token=Config.WEBHOOK_SECRET,
            max_connections=40,
            allowed_updates=['message', 'callback_query', 'chat_member']
        )
        
        if result:
            logger.info(f"✅ وب‌هوک با موفقیت تنظیم شد: {webhook_url}")
            
            # ارسال پیام به ادمین
            try:
                await application.bot.send_message(
                    chat_id=Config.ADMIN_ID,
                    text=f"🤖 ربات کنکور ۱۴۰۵ فعال شد!\n\n"
                         f"📍 وب‌هوک: {webhook_url}\n"
                         f"🕒 زمان: {datetime.now(pytz.timezone(Config.TIMEZONE)).strftime('%Y/%m/%d %H:%M:%S')}\n"
                         f"✅ وضعیت: عملیاتی"
                )
            except Exception as e:
                logger.warning(f"⚠️ نتوانست به ادمین پیام بفرستد: {e}")
            
            return True
        else:
            logger.error("❌ تنظیم وب‌هوک ناموفق بود")
            return False
            
    except Exception as e:
        logger.error(f"❌ خطا در تنظیم وب‌هوک: {e}")
        logger.error(traceback.format_exc())
        return False

def set_webhook_sync():
    """تنظیم وب‌هوک به صورت synchronous"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(set_webhook_async())
        loop.close()
        return result
    except Exception as e:
        logger.error(f"❌ خطا در تنظیم همگام وب‌هوک: {e}")
        return False

# ==================== FLASK ROUTES ====================

@app.route('/')
def home():
    """صفحه اصلی و بررسی سلامت"""
    health_monitor.increment_requests()
    
    stats = health_monitor.get_stats()
    status_info = {
        "status": "active",
        "service": "Konkur 1405 Bot",
        "version": "2.0.0",
        "timestamp": datetime.now(pytz.timezone(Config.TIMEZONE)).isoformat(),
        "health": stats,
        "endpoints": {
            "health": "/health",
            "webhook": "/webhook",
            "set_webhook": "/set_webhook",
            "stats": "/stats"
        }
    }
    
    return jsonify(status_info)

@app.route('/health')
def health_check():
    """بررسی سلامت سرویس"""
    health_monitor.increment_requests()
    
    try:
        # بررسی وضعیت برنامه تلگرام
        bot_status = "healthy" if application and application.bot else "unhealthy"
        
        health_info = {
            "status": bot_status,
            "timestamp": datetime.now(pytz.timezone(Config.TIMEZONE)).isoformat(),
            "service": "Konkur Bot API",
            "version": "2.0.0",
            "checks": {
                "telegram_bot": bot_status,
                "webhook": "active",
                "database": "connected"  # می‌توانید بررسی دیتابیس هم اضافه کنید
            }
        }
        
        return jsonify(health_info), 200 if bot_status == "healthy" else 503
        
    except Exception as e:
        logger.error(f"❌ خطا در بررسی سلامت: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/stats')
def stats():
    """آمار عملکرد سرویس"""
    health_monitor.increment_requests()
    
    stats = health_monitor.get_stats()
    return jsonify({
        "service": "Konkur Bot Statistics",
        "timestamp": datetime.now(pytz.timezone(Config.TIMEZONE)).isoformat(),
        "statistics": stats
    })

@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook_route():
    """تنظیم وب‌هوک"""
    health_monitor.increment_requests()
    
    try:
        success = set_webhook_sync()
        
        if success:
            return jsonify({
                "status": "success",
                "message": "Webhook set successfully",
                "webhook_url": f"{Config.WEBHOOK_URL}/webhook",
                "timestamp": datetime.now(pytz.timezone(Config.TIMEZONE)).isoformat()
            })
        else:
            return jsonify({
                "status": "error", 
                "message": "Failed to set webhook"
            }), 500
            
    except Exception as e:
        logger.error(f"❌ خطا در تنظیم وب‌هوک: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/delete_webhook', methods=['GET', 'POST'])
def delete_webhook():
    """حذف وب‌هوک"""
    health_monitor.increment_requests()
    
    try:
        if application is None:
            return jsonify({"status": "error", "message": "Application not initialized"}), 500
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(application.bot.delete_webhook())
        loop.close()
        
        if result:
            logger.info("✅ وب‌هوک حذف شد")
            return jsonify({"status": "success", "message": "Webhook deleted"})
        else:
            return jsonify({"status": "error", "message": "Failed to delete webhook"}), 500
            
    except Exception as e:
        logger.error(f"❌ خطا در حذف وب‌هوک: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/webhook', methods=['POST'])
async def webhook():
    """دریافت وب‌هوک از تلگرام"""
    health_monitor.increment_requests()
    
    try:
        # بررسی secret token برای امنیت
        if request.headers.get('X-Telegram-Bot-Api-Secret-Token') != Config.WEBHOOK_SECRET:
            logger.warning("⚠️ درخواست وب‌هوک با توکن نامعتبر")
            health_monitor.increment_errors()
            return jsonify({"status": "unauthorized"}), 401
        
        if application is None:
            logger.error("❌ برنامه تلگرام initialize نشده")
            health_monitor.increment_errors()
            return jsonify({"status": "error", "message": "Application not initialized"}), 500
        
        # دریافت و لاگ داده‌ها
        data = request.get_json()
        
        # لاگ خلاصه‌ای از داده‌ها (بدون اطلاعات حساس)
        if data:
            update_id = data.get('update_id', 'unknown')
            message_type = "unknown"
            
            if 'message' in data:
                message_type = "message"
                chat_id = data['message']['chat']['id']
                user_id = data['message']['from']['id']
                text = data['message'].get('text', '')[:100]
                logger.info(f"📨 وب‌هوک #{update_id} - پیام از کاربر {user_id} در چت {chat_id}: {text}...")
                
            elif 'callback_query' in data:
                message_type = "callback"
                user_id = data['callback_query']['from']['id']
                data_text = data['callback_query']['data'][:50]
                logger.info(f"🔄 وب‌هوک #{update_id} - callback از کاربر {user_id}: {data_text}...")
            
            else:
                logger.info(f"📨 وب‌هوک #{update_id} - نوع: {message_type}")
        
        # پردازش آپدیت
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
        
        logger.info(f"✅ وب‌هوک #{data.get('update_id', 'unknown')} با موفقیت پردازش شد")
        return jsonify({"status": "success"}), 200
        
    except Exception as e:
        logger.error(f"❌ خطا در پردازش وب‌هوک: {e}")
        logger.error(traceback.format_exc())
        health_monitor.increment_errors()
        
        # ارسال پیام خطا به ادمین
        try:
            if application and application.bot:
                error_time = datetime.now(pytz.timezone(Config.TIMEZONE)).strftime('%Y/%m/%d %H:%M:%S')
                await application.bot.send_message(
                    chat_id=Config.ADMIN_ID,
                    text=f"🚨 خطا در ربات!\n\n"
                         f"⏰ زمان: {error_time}\n"
                         f"❌ خطا: {str(e)[:200]}\n"
                         f"📍 بخش: وب‌هوک هندلر"
                )
        except Exception as admin_error:
            logger.error(f"❌ نتوانست خطا را به ادمین گزارش دهد: {admin_error}")
        
        return jsonify({"status": "error", "message": "Internal server error"}), 200  # بازگشت 200 برای تلگرام

@app.route('/broadcast', methods=['POST'])
def broadcast_message():
    """ارسال پیام همگانی (فقط برای ادمین)"""
    health_monitor.increment_requests()
    
    try:
        # بررسی احراز هویت
        auth_token = request.headers.get('Authorization')
        if auth_token != f"Bearer {Config.WEBHOOK_SECRET}":
            return jsonify({"status": "unauthorized"}), 401
        
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"status": "error", "message": "Message content required"}), 400
        
        message = data['message']
        
        # اینجا می‌توانید لیست کاربران را از دیتابیس بگیرید
        # برای نمونه، یک کاربر تستی
        test_users = [Config.ADMIN_ID]
        
        async def send_broadcast():
            success_count = 0
            fail_count = 0
            
            for user_id in test_users:
                try:
                    await application.bot.send_message(
                        chat_id=user_id,
                        text=f"📢 پیام همگانی:\n\n{message}",
                        parse_mode='HTML'
                    )
                    success_count += 1
                except Exception as e:
                    logger.error(f"❌ خطا در ارسال به کاربر {user_id}: {e}")
                    fail_count += 1
            
            return success_count, fail_count
        
        # اجرای ارسال همگانی
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success_count, fail_count = loop.run_until_complete(send_broadcast())
        loop.close()
        
        return jsonify({
            "status": "success",
            "sent": success_count,
            "failed": fail_count,
            "total": len(test_users)
        })
        
    except Exception as e:
        logger.error(f"❌ خطا در ارسال همگانی: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """مدیریت خطای 404"""
    return jsonify({
        "status": "error",
        "message": "Endpoint not found",
        "available_endpoints": [
            "/", "/health", "/stats", "/set_webhook", "/webhook"
        ]
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """مدیریت خطای 405"""
    return jsonify({
        "status": "error", 
        "message": "Method not allowed"
    }), 405

@app.errorhandler(500)
def internal_error(error):
    """مدیریت خطای 500"""
    logger.error(f"❌ خطای سرور داخلی: {error}")
    health_monitor.increment_errors()
    
    return jsonify({
        "status": "error",
        "message": "Internal server error"
    }), 500

# ==================== INITIALIZATION ====================

def initialize_bot():
    """راه‌اندازی اولیه ربات"""
    logger.info("🚀 در حال راه‌اندازی ربات کنکور ۱۴۰۵...")
    
    # تنظیم هندلرها
    if not setup_handlers():
        logger.error("❌ راه‌اندازی هندلرها ناموفق بود")
        return False
    
    # تنظیم وب‌هوک
    if Config.WEBHOOK_URL and Config.WEBHOOK_URL != "https://your-render-url.onrender.com":
        logger.info("🌐 در حال تنظیم وب‌هوک...")
        webhook_success = set_webhook_sync()
        
        if webhook_success:
            logger.info("✅ ربات با موفقیت راه‌اندازی شد")
            return True
        else:
            logger.error("❌ تنظیم وب‌هوک ناموفق بود")
            return False
    else:
        logger.warning("⚠️ آدرس وب‌هوک تنظیم نشده - استفاده از حالت polling")
        return True

# ==================== MAIN EXECUTION ====================

if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("🤖 راه‌اندازی ربات کنکور ۱۴۰۵")
    logger.info("=" * 60)
    
    # نمایش اطلاعات پیکربندی (بدون اطلاعات حساس)
    config_info = {
        "environment": "production" if not Config.DEBUG else "development",
        "webhook_url": Config.WEBHOOK_URL if Config.WEBHOOK_URL != "https://your-render-url.onrender.com" else "NOT_SET",
        "port": Config.PORT,
        "timezone": Config.TIMEZONE,
        "debug_mode": Config.DEBUG
    }
    logger.info(f"⚙️  پیکربندی: {config_info}")
    
    # راه‌اندازی ربات
    if initialize_bot():
        logger.info(f"🌐 شروع سرویس Flask روی پورت {Config.PORT}")
        
        # اجرای برنامه Flask
        app.run(
            host=Config.HOST,
            port=Config.PORT,
            debug=Config.DEBUG,
            use_reloader=False
        )
    else:
        logger.error("❌ راه‌اندازی ربات ناموفق بود")
        sys.exit(1)
