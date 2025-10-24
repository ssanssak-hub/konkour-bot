import os
import logging
import asyncio
import threading
import time
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
import sys
import traceback
from datetime import datetime, timedelta
import pytz
import jdatetime
from typing import Dict, Any, Optional, List
import json
import requests

# ==================== ADVANCED LOGGING SETUP ====================

class CustomFormatter(logging.Formatter):
    """فرمتر سفارشی پیشرفته برای لاگ‌ها"""
    
    def format(self, record):
        try:
            record.persian_time = jdatetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
            record.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        except:
            record.persian_time = "N/A"
            record.timestamp = "N/A"
        return super().format(record)

def setup_logging():
    """تنظیمات پیشرفته سیستم لاگینگ"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # فرمت سفارشی
    formatter = CustomFormatter(
        '%(timestamp)s | %(persian_time)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | %(message)s'
    )
    
    # Handler برای کنسول
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Handler برای فایل
    file_handler = logging.FileHandler('konkur_bot.log', encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # حذف handlers قبلی و اضافه کردن جدید
    logger.handlers = []
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# راه‌اندازی لاگینگ
logger = setup_logging()

app = Flask(__name__)

# ==================== ADVANCED CONFIGURATION ====================

class AdvancedConfig:
    """پیکربندی پیشرفته و امن ربات"""
    
    # تنظیمات اصلی
    BOT_TOKEN = os.environ.get('BOT_TOKEN', '8381121739:AAFB2YBMomBh9xhoI3Qn0VVuGaGlpea9fx8')
    ADMIN_ID = int(os.environ.get('ADMIN_ID', 7703677187))
    WEBHOOK_URL = os.environ.get('WEBHOOK_URL', 'https://konkour-bot.onrender.com')
    WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', 'konkur1405_secret_key_2024')
    
    # تنظیمات سرور
    PORT = int(os.environ.get('PORT', 10000))
    HOST = os.environ.get('HOST', '0.0.0.0')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    ENVIRONMENT = os.environ.get('ENVIRONMENT', 'production')
    
    # تنظیمات زمان
    TIMEZONE = pytz.timezone('Asia/Tehran')
    
    # تنظیمات عملکرد
    MAX_CONNECTIONS = 40
    WORKERS = 4
    REQUEST_TIMEOUT = 30
    RATE_LIMIT_PER_MINUTE = 30
    MAX_MESSAGE_LENGTH = 4000
    
    # تنظیمات کنکور
    EXAM_DATES = {
        "علوم تجربی": "1405-04-12",
        "ریاضی‌وفنی": "1405-04-11", 
        "علوم انسانی": "1405-04-11",
        "فرهنگیان": "1405-02-17",
        "هنر": "1405-04-12",
        "زبان‌وگروه‌های‌خارجه": "1405-04-12"
    }

# ==================== SIMPLE BOT MANAGER ====================

class SimpleBotManager:
    """مدیریت ساده و مطمئن ربات"""
    
    def __init__(self):
        self.application = None
        self.initialized = False
        self.bot = None
        self.start_time = datetime.now()
        
    def initialize(self):
        """راه‌اندازی سریع و مطمئن ربات"""
        try:
            print("🚀 شروع راه‌اندازی ربات...")
            
            # تست توکن
            test_url = f"https://api.telegram.org/bot{AdvancedConfig.BOT_TOKEN}/getMe"
            response = requests.get(test_url, timeout=10)
            bot_info = response.json()
            
            if not bot_info.get('ok'):
                print(f"❌ توکن نامعتبر: {bot_info}")
                return False
            
            print(f"✅ توکن معتبر: {bot_info['result']['username']}")
            
            # ایجاد برنامه
            self.application = Application.builder().token(AdvancedConfig.BOT_TOKEN).build()
            
            # تنظیم هندلرهای اصلی
            self.setup_basic_handlers()
            
            self.initialized = True
            print("✅ ربات با موفقیت راه‌اندازی شد")
            return True
            
        except Exception as e:
            print(f"❌ خطا در راه‌اندازی: {e}")
            import traceback
            print(traceback.format_exc())
            return False
    
    def setup_basic_handlers(self):
        """تنظیم هندلرهای اصلی"""
        
        async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
            user = update.effective_user
            welcome_text = f"""
👋 **سلام {user.first_name} عزیز!**

🎓 **به ربات کنکور ۱۴۰۵ خوش آمدید!**

🤖 **من یک دستیار هوشمندم که می‌تونم در مسیر کنکورت کمکت کنم:**

⏳ **شمارش معکوس هوشمند کنکور**
📅 **تقویم و برنامه‌ریزی پیشرفته**  
🔔 **سیستم یادآوری هوشمند**

💡 **برای شروع، از منوی زیر انتخاب کن:**
"""
            keyboard = [
                [InlineKeyboardButton("⏳ چند روز تا کنکور؟", callback_data="countdown")],
                [InlineKeyboardButton("📅 تقویم و رویدادها", callback_data="calendar")],
                [InlineKeyboardButton("🔔 مدیریت یادآوری‌ها", callback_data="reminders")],
                [InlineKeyboardButton("❓ راهنما", callback_data="help")]
            ]
            
            await update.message.reply_text(
                welcome_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
        
        async def handle_countdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
            query = update.callback_query
            await query.answer()
            
            keyboard = []
            for exam_name, exam_date in AdvancedConfig.EXAM_DATES.items():
                # محاسبه زمان باقی‌مانده
                today = jdatetime.datetime.now()
                exam_jdate = jdatetime.datetime.strptime(exam_date, "%Y-%m-%d")
                days_remaining = (exam_jdate - today).days
                
                keyboard.append([
                    InlineKeyboardButton(
                        f"🎯 {exam_name} ({days_remaining} روز)", 
                        callback_data=f"show_{exam_name}"
                    )
                ])
            
            keyboard.append([InlineKeyboardButton("🏠 بازگشت", callback_data="back")])
            
            await query.edit_message_text(
                "⏳ **سیستم شمارش معکوس کنکور ۱۴۰۵**\n\n"
                "🎯 لطفاً کنکور مورد نظر خود را انتخاب کنید:",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
        
        async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
            query = update.callback_query
            await query.answer()
            
            help_text = """
❓ **راهنمای ربات کنکور ۱۴۰۵**

🎯 **دستورات اصلی:**
/start - شروع کار با ربات

⏳ **شمارش معکوس:**
• مشاهده زمان باقی‌مانده تا کنکور
• تاریخ دقیق هر رشته

📅 **تقویم:**
• نمایش تاریخ شمسی
• مناسبت‌ها و رویدادها

🔔 **یادآوری:**
• تنظیم یادآوری کنکور
• یادآوری مطالعه
"""
            await query.edit_message_text(
                help_text,
                parse_mode='HTML'
            )
        
        async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
            query = update.callback_query
            await query.answer()
            
            await query.edit_message_text(
                "🏠 **منوی اصلی ربات کنکور**\n\nلطفاً بخش مورد نظر خود را انتخاب کنید:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⏳ چند روز تا کنکور؟", callback_data="countdown")],
                    [InlineKeyboardButton("📅 تقویم و رویدادها", callback_data="calendar")],
                    [InlineKeyboardButton("🔔 مدیریت یادآوری‌ها", callback_data="reminders")],
                    [InlineKeyboardButton("❓ راهنما", callback_data="help")]
                ]),
                parse_mode='HTML'
            )
        
        # اضافه کردن هندلرها
        self.application.add_handler(CommandHandler("start", start))
        self.application.add_handler(CallbackQueryHandler(handle_countdown, pattern="^countdown$"))
        self.application.add_handler(CallbackQueryHandler(handle_help, pattern="^help$"))
        self.application.add_handler(CallbackQueryHandler(handle_back, pattern="^back$"))
        
        # هندلر برای نمایش جزئیات هر کنکور
        for exam_name in AdvancedConfig.EXAM_DATES.keys():
            self.application.add_handler(
                CallbackQueryHandler(
                    lambda update, context, name=exam_name: self.show_exam_details(update, context, name),
                    pattern=f"^show_{exam_name}$"
                )
            )
        
        print("✅ هندلرهای اصلی تنظیم شدند")
    
    async def show_exam_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE, exam_name: str):
        """نمایش جزئیات کنکور"""
        query = update.callback_query
        await query.answer()
        
        exam_date = AdvancedConfig.EXAM_DATES.get(exam_name, "1405-04-12")
        
        # محاسبه زمان باقی‌مانده
        today = jdatetime.datetime.now()
        exam_jdate = jdatetime.datetime.strptime(exam_date, "%Y-%m-%d")
        days_remaining = (exam_jdate - today).days
        
        text = f"""
⏰ **شمارش معکوس کنکور {exam_name}**

🕐 **زمان باقی‌مانده:** {days_remaining} روز
📅 **تاریخ کنکور:** {exam_date.replace('-', '/')}
🕒 **ساعت برگزاری:** ۰۸:۰۰ صبح

💪 **همت بلند دار که مردان روزگار**
**از همت بلند به جایی رسیده‌اند**

💡 **توصیه مطالعاتی:**
📚 برنامه‌ریزی منظم روزانه داشته باشید
🎯 روی نقاط ضعف خود تمرکز کنید  
⏱️ زمان خود را هوشمندانه مدیریت کنید
"""
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📊 همه کنکورها", callback_data="countdown")],
                [InlineKeyboardButton("🏠 منوی اصلی", callback_data="back")]
            ]),
            parse_mode='HTML'
        )

# ==================== WEBHOOK MANAGER ====================

class WebhookManager:
    """مدیریت وب‌هوک"""
    
    def __init__(self, bot_manager):
        self.bot_manager = bot_manager
        self.webhook_set = False
    
    def setup_webhook(self):
        """تنظیم وب‌هوک"""
        try:
            webhook_url = f"{AdvancedConfig.WEBHOOK_URL}/webhook"
            print(f"🌐 تنظیم وب‌هوک: {webhook_url}")
            
            # تنظیم وب‌هوک
            setup_url = f"https://api.telegram.org/bot{AdvancedConfig.BOT_TOKEN}/setWebhook"
            params = {
                'url': webhook_url,
                'secret_token': AdvancedConfig.WEBHOOK_SECRET,
                'max_connections': 40
            }
            
            response = requests.get(setup_url, params=params, timeout=10)
            result = response.json()
            
            if result.get('ok'):
                self.webhook_set = True
                print("✅ وب‌هوک تنظیم شد")
                return True
            else:
                print(f"❌ خطا در تنظیم وب‌هوک: {result}")
                return False
                
        except Exception as e:
            print(f"❌ خطا در تنظیم وب‌هوک: {e}")
            return False

# ==================== FLASK APPLICATION ====================

# ایجاد نمونه‌ها
bot_manager = SimpleBotManager()
webhook_manager = WebhookManager(bot_manager)

# راه‌اندازی اولیه
print("🔧 راه‌اندازی اولیه سیستم...")
if bot_manager.initialize():
    print("✅ ربات راه‌اندازی شد - تنظیم وب‌هوک...")
    webhook_manager.setup_webhook()
else:
    print("❌ ربات راه‌اندازی نشد")

@app.route('/')
def home():
    """صفحه اصلی"""
    return jsonify({
        "status": "active",
        "service": "Konkur 1405 Bot",
        "version": "3.0.0",
        "timestamp": datetime.now().isoformat(),
        "persian_time": jdatetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
        "bot_initialized": bot_manager.initialized,
        "webhook_set": webhook_manager.webhook_set
    })

@app.route('/health')
def health_check():
    """بررسی سلامت"""
    return jsonify({
        "status": "healthy",
        "bot_initialized": bot_manager.initialized,
        "webhook_set": webhook_manager.webhook_set,
        "timestamp": datetime.now().isoformat(),
        "persian_time": jdatetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    })

@app.route('/set_webhook')
def set_webhook():
    """تنظیم وب‌هوک"""
    success = webhook_manager.setup_webhook()
    return jsonify({
        "status": "success" if success else "error",
        "webhook_set": webhook_manager.webhook_set,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """دریافت وب‌هوک از تلگرام"""
    try:
        data = request.get_json()
        
        if not data:
            print("⚠️ درخواست وب‌هوک بدون داده")
            return jsonify({"status": "success"}), 200
        
        update_id = data.get('update_id', 'unknown')
        print(f"📨 وب‌هوک دریافت شد - آپدیت: {update_id}")
        
        # اگر ربات initialize نشده، سعی کن راه‌اندازی کن
        if not bot_manager.initialized:
            print("🔄 ربات initialize نشده - تلاش برای راه‌اندازی...")
            if bot_manager.initialize():
                print("✅ ربات راه‌اندازی شد")
            else:
                print("❌ راه‌اندازی ناموفق")
                return jsonify({"status": "success", "message": "Bot initializing"}), 200
        
        # پردازش آپدیت
        def process_update():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                async def process():
                    update = Update.de_json(data, bot_manager.application.bot)
                    await bot_manager.application.process_update(update)
                    print(f"✅ آپدیت #{update_id} پردازش شد")
                
                loop.run_until_complete(process())
                loop.close()
                
            except Exception as e:
                print(f"❌ خطا در پردازش آپدیت: {e}")
        
        thread = threading.Thread(target=process_update)
        thread.daemon = True
        thread.start()
        
        return jsonify({"status": "success"}), 200
        
    except Exception as e:
        print(f"💥 خطای کلی در وب‌هوک: {e}")
        return jsonify({"status": "success"}), 200

@app.route('/restart')
def restart():
    """راه‌اندازی مجدد"""
    print("🔄 راه‌اندازی مجدد ربات...")
    success = bot_manager.initialize()
    return jsonify({
        "status": "success" if success else "error",
        "bot_initialized": bot_manager.initialized,
        "timestamp": datetime.now().isoformat()
    })

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "status": "error",
        "message": "Endpoint not found",
        "timestamp": datetime.now().isoformat()
    }), 404

@app.errorhandler(500)
def internal_error(error):
    print(f"❌ خطای سرور: {error}")
    return jsonify({
        "status": "error", 
        "message": "Internal server error",
        "timestamp": datetime.now().isoformat()
    }), 500

# ==================== MAIN EXECUTION ====================

if __name__ == '__main__':
    print("=" * 50)
    print("🤖 ربات کنکور ۱۴۰۵ - نسخه ساده و مطمئن")
    print("=" * 50)
    
    print(f"🌐 شروع سرویس روی پورت {AdvancedConfig.PORT}")
    app.run(
        host=AdvancedConfig.HOST,
        port=AdvancedConfig.PORT,
        debug=AdvancedConfig.DEBUG,
        use_reloader=False
    )
