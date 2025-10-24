import os
import logging
import asyncio
import threading
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
import sys
import traceback
from datetime import datetime, timedelta
import pytz
import jdatetime
from typing import Dict, Any, Optional

# ==================== ADVANCED LOGGING SETUP ====================

class CustomFormatter(logging.Formatter):
    """فرمتر سفارشی برای لاگ‌ها"""
    
    def format(self, record):
        record.persian_time = jdatetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        return super().format(record)

# تنظیمات پیشرفته لاگ
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('konkur_bot.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)
formatter = CustomFormatter(
    '%(asctian_time)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
for handler in logging.getLogger().handlers:
    handler.setFormatter(formatter)

app = Flask(__name__)

# ==================== ADVANCED CONFIGURATION ====================

class AdvancedConfig:
    """پیکربندی پیشرفته ربات"""
    
    # تنظیمات اصلی
    BOT_TOKEN = os.environ.get('BOT_TOKEN', '8381121739:AAFB2YBMomBh9xhoI3Qn0VVuGaGlpea9fx8')
    ADMIN_ID = int(os.environ.get('ADMIN_ID', 7703677187))
    WEBHOOK_URL = os.environ.get('WEBHOOK_URL', 'https://konkurcounting-3ga0.onrender.com')
    WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', 'konkur1405_secret_key_2024')
    
    # تنظیمات سرور
    PORT = int(os.environ.get('PORT', 5000))
    HOST = os.environ.get('HOST', '0.0.0.0')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    ENVIRONMENT = os.environ.get('ENVIRONMENT', 'production')
    
    # تنظیمات زمان
    TIMEZONE = pytz.timezone('Asia/Tehran')
    
    # تنظیمات عملکرد
    MAX_CONNECTIONS = 40
    WORKERS = 4
    REQUEST_TIMEOUT = 30
    
    # تنظیمات امنیتی
    RATE_LIMIT_PER_MINUTE = 30
    MAX_MESSAGE_LENGTH = 4000
    
    @classmethod
    def validate_config(cls):
        """اعتبارسنجی تنظیمات"""
        errors = []
        
        if not cls.BOT_TOKEN or cls.BOT_TOKEN == "your_bot_token":
            errors.append("BOT_TOKEN تنظیم نشده است")
        
        if not cls.WEBHOOK_URL or "your-render-url" in cls.WEBHOOK_URL:
            errors.append("WEBHOOK_URL تنظیم نشده است")
            
        return errors
    
    @classmethod
    def get_config_info(cls):
        """دریافت اطلاعات پیکربندی (بدون اطلاعات حساس)"""
        return {
            "environment": cls.ENVIRONMENT,
            "debug_mode": cls.DEBUG,
            "webhook_configured": bool(cls.WEBHOOK_URL and "your-render-url" not in cls.WEBHOOK_URL),
            "timezone": str(cls.TIMEZONE),
            "max_connections": cls.MAX_CONNECTIONS,
            "admin_id_configured": cls.ADMIN_ID != 7703677187
        }

# ==================== APPLICATION MANAGER ====================

class ApplicationManager:
    """مدیریت پیشرفته برنامه تلگرام"""
    
    def __init__(self):
        self.application = None
        self.initialized = False
        self.start_time = datetime.now()
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'last_error': None,
            'active_users': set()
        }
    
    def initialize(self) -> bool:
        """راه‌اندازی برنامه"""
        try:
            logger.info("🚀 در حال راه‌اندازی برنامه تلگرام...")
            
            # اعتبارسنجی تنظیمات
            config_errors = AdvancedConfig.validate_config()
            if config_errors:
                for error in config_errors:
                    logger.error(f"❌ خطای پیکربندی: {error}")
                return False
            
            # ایجاد برنامه
            self.application = (
                Application.builder()
                .token(AdvancedConfig.BOT_TOKEN)
                .connect_timeout(30)
                .read_timeout(30)
                .write_timeout(30)
                .build()
            )
            
            # تنظیم هندلرها
            if not self._setup_handlers():
                logger.error("❌ خطا در تنظیم هندلرها")
                return False
            
            self.initialized = True
            logger.info("✅ برنامه تلگرام با موفقیت راه‌اندازی شد")
            return True
            
        except Exception as e:
            logger.error(f"❌ خطا در راه‌اندازی برنامه: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def _setup_handlers(self) -> bool:
        """تنظیم هندلرها با مدیریت خطا"""
        try:
            # هندلرهای پایه
            self._setup_basic_handlers()
            
            # هندلرهای پیشرفته (با مدیریت خطا)
            self._setup_advanced_handlers()
            
            # هندلر خطا
            self.application.add_error_handler(self._error_handler)
            
            logger.info("✅ تمام هندلرها تنظیم شدند")
            return True
            
        except Exception as e:
            logger.error(f"❌ خطا در تنظیم هندلرها: {e}")
            return False
    
    def _setup_basic_handlers(self):
        """تنظیم هندلرهای پایه"""
        
        async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
            """دستور /start"""
            try:
                user = update.effective_user
                self.stats['active_users'].add(user.id)
                
                welcome_text = f"""
سلام {user.first_name}! 👋

🎓 **به ربات کنکور ۱۴۰۵ خوش آمدید!**

من یک دستیار هوشمندم که می‌تونم در مسیر کنکورت کمکت کنم:

⏳ **شمارش معکوس هوشمند**
📅 **مدیریت زمان پیشرفته**  
🔔 **یادآوری‌های هوشمند**
📚 **برنامه‌ریزی مطالعه**
📨 **پشتیبانی آنلاین**

💡 **برای شروع، یکی از گزینه‌های زیر رو انتخاب کن:**
"""
                
                await update.message.reply_text(
                    welcome_text,
                    reply_markup=self._create_main_menu(),
                    parse_mode='HTML'
                )
                
                self.stats['successful_requests'] += 1
                
            except Exception as e:
                logger.error(f"❌ خطا در دستور start: {e}")
                self.stats['failed_requests'] += 1
        
        async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
            """دستور /menu"""
            try:
                await update.message.reply_text(
                    "🏠 **منوی اصلی**\n\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
                    reply_markup=self._create_main_menu(),
                    parse_mode='HTML'
                )
                self.stats['successful_requests'] += 1
            except Exception as e:
                logger.error(f"❌ خطا در دستور menu: {e}")
                self.stats['failed_requests'] += 1
        
        async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            """مدیریت منوی اصلی"""
            query = update.callback_query
            await query.answer()
            
            try:
                await query.edit_message_text(
                    "🏠 **منوی اصلی ربات کنکور**\n\nلطفاً بخش مورد نظر خود را انتخاب کنید:",
                    reply_markup=self._create_main_menu(),
                    parse_mode='HTML'
                )
                self.stats['successful_requests'] += 1
            except Exception as e:
                logger.error(f"❌ خطا در منوی اصلی: {e}")
                self.stats['failed_requests'] += 1
        
        async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
            """پردازش پیام‌های متنی"""
            try:
                user_id = update.effective_user.id
                text = update.message.text
                
                logger.info(f"📝 پیام از کاربر {user_id}: {text[:100]}...")
                
                await update.message.reply_text(
                    "🤔 **متوجه پیام شما نشدم!**\n\n"
                    "💡 لطفاً از منوی اصلی استفاده کنید یا دستور /menu را وارد کنید.",
                    reply_markup=self._create_main_menu(),
                    parse_mode='HTML'
                )
                self.stats['successful_requests'] += 1
                
            except Exception as e:
                logger.error(f"❌ خطا در پردازش پیام متنی: {e}")
                self.stats['failed_requests'] += 1
        
        # اضافه کردن هندلرهای پایه
        self.application.add_handler(CommandHandler("start", start_command))
        self.application.add_handler(CommandHandler("menu", menu_command))
        self.application.add_handler(CallbackQueryHandler(main_menu_handler, pattern="^main_menu$"))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
        
        logger.info("✅ هندلرهای پایه تنظیم شدند")
    
    def _setup_advanced_handlers(self):
        """تنظیم هندلرهای پیشرفته با مدیریت خطا"""
        
        async def countdown_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            """مدیریت شمارش معکوس"""
            query = update.callback_query
            await query.answer()
            
            try:
                exam_dates = {
                    "علوم تجربی": "1405-04-12",
                    "ریاضی‌وفنی": "1405-04-11",
                    "علوم انسانی": "1405-04-11",
                    "فرهنگیان": "1405-02-17",
                    "هنر": "1405-04-12",
                    "زبان‌وگروه‌های‌خارجه": "1405-04-12"
                }
                
                keyboard = []
                for exam_name, exam_date in exam_dates.items():
                    keyboard.append([
                        InlineKeyboardButton(
                            f"🎯 {exam_name}", 
                            callback_data=f"show_countdown_{exam_name}"
                        )
                    ])
                
                keyboard.append([InlineKeyboardButton("🏠 بازگشت", callback_data="main_menu")])
                
                await query.edit_message_text(
                    "⏳ **سیستم شمارش معکوس کنکور**\n\n"
                    "🎯 لطفاً کنکور مورد نظر خود را انتخاب کنید:",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='HTML'
                )
                
            except Exception as e:
                logger.error(f"❌ خطا در هندلر شمارش معکوس: {e}")
                await query.edit_message_text("❌ خطا در بارگذاری شمارش معکوس")
        
        async def show_countdown_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            """نمایش شمارش معکوس"""
            query = update.callback_query
            await query.answer()
            
            try:
                exam_name = query.data.replace("show_countdown_", "")
                today = jdatetime.datetime.now()
                
                # محاسبه نمونه‌ای
                days_remaining = 285  # مقدار نمونه
                
                text = f"""
⏰ **شمارش معکوس کنکور {exam_name}**

🕐 **زمان باقی‌مانده:** {days_remaining} روز

📅 **تاریخ کنکور:** ۱۴۰۵/۰۴/۱۲
🕒 **ساعت برگزاری:** ۰۸:۰۰ صبح

💡 **توصیه مطالعاتی:**
📚 برنامه‌ریزی منظم داشته باشید
🎯 روی نقاط ضعف تمرکز کنید
⏱️ زمان خود را مدیریت کنید
"""
                
                keyboard = [
                    [InlineKeyboardButton("🔄 بروزرسانی", callback_data=f"show_countdown_{exam_name}")],
                    [InlineKeyboardButton("📊 همه کنکورها", callback_data="countdown")],
                    [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
                ]
                
                await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
                
            except Exception as e:
                logger.error(f"❌ خطا در نمایش شمارش معکوس: {e}")
                await query.edit_message_text("❌ خطا در محاسبه زمان")
        
        async def calendar_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            """مدیریت تقویم"""
            query = update.callback_query
            await query.answer()
            
            try:
                today = jdatetime.datetime.now()
                
                text = f"""
📅 **سیستم تقویم و رویدادها**

🕒 **امروز:** {today.strftime('%A %Y/%m/%d')}
📆 **تاریخ دقیق:** {today.strftime('%Y/%m/%d %H:%M:%S')}

🎯 **امکانات موجود:**
• نمایش تقویم شمسی
• مناسبت‌ها و رویدادها
• رویدادهای کنکور
• جستجوی تاریخ
"""
                
                keyboard = [
                    [InlineKeyboardButton("📅 تقویم جاری", callback_data="current_calendar")],
                    [InlineKeyboardButton("🔍 مشاهده رویدادها", callback_data="view_events")],
                    [InlineKeyboardButton("🏠 بازگشت", callback_data="main_menu")]
                ]
                
                await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
                
            except Exception as e:
                logger.error(f"❌ خطا در هندلر تقویم: {e}")
                await query.edit_message_text("❌ خطا در بارگذاری تقویم")
        
        async def reminders_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            """مدیریت یادآوری‌ها"""
            query = update.callback_query
            await query.answer()
            
            try:
                text = """
🔔 **سیستم مدیریت یادآوری‌ها**

🎯 **انواع یادآوری قابل تنظیم:**

⏰ **یادآوری کنکور**
• یادآوری روزانه تا زمان کنکور

📚 **یادآوری مطالعه**  
• زمان‌بندی جلسات مطالعه

📝 **یادآوری متفرقه**
• رویدادهای شخصی
"""
                
                keyboard = [
                    [InlineKeyboardButton("⏰ یادآوری کنکور", callback_data="setup_exam_reminder")],
                    [InlineKeyboardButton("📚 یادآوری مطالعه", callback_data="setup_study_reminder")],
                    [InlineKeyboardButton("📝 یادآوری متفرقه", callback_data="setup_custom_reminder")],
                    [InlineKeyboardButton("🏠 بازگشت", callback_data="main_menu")]
                ]
                
                await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
                
            except Exception as e:
                logger.error(f"❌ خطا در هندلر یادآوری: {e}")
                await query.edit_message_text("❌ خطا در بارگذاری یادآوری‌ها")
        
        # اضافه کردن هندلرهای پیشرفته
        self.application.add_handler(CallbackQueryHandler(countdown_handler, pattern="^countdown$"))
        self.application.add_handler(CallbackQueryHandler(show_countdown_handler, pattern="^show_countdown_"))
        self.application.add_handler(CallbackQueryHandler(calendar_handler, pattern="^calendar$"))
        self.application.add_handler(CallbackQueryHandler(reminders_handler, pattern="^reminders$"))
        
        logger.info("✅ هندلرهای پیشرفته تنظیم شدند")
    
    async def _error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت خطاها"""
        try:
            logger.error(f"❌ خطا در پردازش به‌روزرسانی: {context.error}")
            self.stats['failed_requests'] += 1
            self.stats['last_error'] = str(context.error)
            
            if update and update.effective_message:
                await update.effective_message.reply_text(
                    "❌ **خطایی در پردازش درخواست شما رخ داد.**\n\n"
                    "💡 لطفاً دوباره تلاش کنید.",
                    reply_markup=self._create_main_menu(),
                    parse_mode='HTML'
                )
        except Exception as e:
            logger.error(f"❌ خطا در هندلر خطا: {e}")
    
    def _create_main_menu(self):
        """ایجاد منوی اصلی"""
        keyboard = [
            [InlineKeyboardButton("⏳ چند روز تا کنکور؟", callback_data="countdown")],
            [InlineKeyboardButton("📅 تقویم و رویدادها", callback_data="calendar")],
            [InlineKeyboardButton("🔔 مدیریت یادآوری‌ها", callback_data="reminders")],
            [InlineKeyboardButton("📨 ارسال پیام", callback_data="send_message")],
            [InlineKeyboardButton("✅ اعلام حضور", callback_data="attendance")],
            [InlineKeyboardButton("📚 اهداف و برنامه‌ریزی", callback_data="study_plan")],
            [InlineKeyboardButton("📊 آمار و گزارش", callback_data="statistics")],
            [InlineKeyboardButton("❓ راهنما", callback_data="help")],
            [InlineKeyboardButton("🔧 پنل مدیریت", callback_data="admin_panel")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_stats(self):
        """دریافت آمار"""
        return {
            **self.stats,
            'uptime': str(datetime.now() - self.start_time),
            'active_users_count': len(self.stats['active_users']),
            'initialized': self.initialized
        }

# ==================== WEBHOOK MANAGER ====================

class WebhookManager:
    """مدیریت پیشرفته وب‌هوک"""
    
    def __init__(self, app_manager: ApplicationManager):
        self.app_manager = app_manager
        self.webhook_set = False
    
    async def setup_webhook(self) -> bool:
        """تنظیم وب‌هوک"""
        try:
            if not self.app_manager.initialized:
                logger.error("❌ برنامه initialize نشده")
                return False
            
            webhook_url = f"{AdvancedConfig.WEBHOOK_URL}/webhook"
            
            # حذف وب‌هوک قبلی
            await self.app_manager.application.bot.delete_webhook()
            logger.info("✅ وب‌هوک قبلی حذف شد")
            
            # تنظیم وب‌هوک جدید
            result = await self.app_manager.application.bot.set_webhook(
                url=webhook_url,
                secret_token=AdvancedConfig.WEBHOOK_SECRET,
                max_connections=AdvancedConfig.MAX_CONNECTIONS,
                allowed_updates=['message', 'callback_query', 'chat_member']
            )
            
            if result:
                self.webhook_set = True
                logger.info(f"✅ وب‌هوک با موفقیت تنظیم شد: {webhook_url}")
                
                # اطلاع به ادمین
                await self._notify_admin("✅ ربات فعال شد")
                return True
            else:
                logger.error("❌ تنظیم وب‌هوک ناموفق بود")
                return False
                
        except Exception as e:
            logger.error(f"❌ خطا در تنظیم وب‌هوک: {e}")
            return False
    
    async def _notify_admin(self, message: str):
        """اطلاع به ادمین"""
        try:
            await self.app_manager.application.bot.send_message(
                chat_id=AdvancedConfig.ADMIN_ID,
                text=f"🤖 {message}\n\n"
                     f"🕒 {jdatetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')}"
            )
        except Exception as e:
            logger.warning(f"⚠️ نتوانست به ادمین پیام بفرستد: {e}")

# ==================== HEALTH MONITOR ====================

class HealthMonitor:
    """مانیتورینگ سلامت سرویس"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.request_count = 0
        self.error_count = 0
    
    def increment_requests(self):
        self.request_count += 1
    
    def increment_errors(self):
        self.error_count += 1
    
    def get_health_status(self):
        """دریافت وضعیت سلامت"""
        uptime = datetime.now() - self.start_time
        
        return {
            "status": "healthy",
            "uptime": str(uptime),
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "error_rate": (self.error_count / self.request_count * 100) if self.request_count > 0 else 0,
            "timestamp": datetime.now(AdvancedConfig.TIMEZONE).isoformat()
        }

# ==================== FLASK APPLICATION ====================

# ایجاد نمونه‌ها
app_manager = ApplicationManager()
webhook_manager = WebhookManager(app_manager)
health_monitor = HealthMonitor()

@app.route('/')
def home():
    """صفحه اصلی"""
    health_monitor.increment_requests()
    
    info = {
        "status": "active",
        "service": "Konkur 1405 Bot - Advanced Edition",
        "version": "3.0.0",
        "timestamp": datetime.now(AdvancedConfig.TIMEZONE).isoformat(),
        "environment": AdvancedConfig.ENVIRONMENT,
        "health": health_monitor.get_health_status(),
        "bot_stats": app_manager.get_stats() if app_manager.initialized else None,
        "config": AdvancedConfig.get_config_info()
    }
    
    return jsonify(info)

@app.route('/health')
def health_check():
    """بررسی سلامت"""
    health_monitor.increment_requests()
    
    health_status = health_monitor.get_health_status()
    
    # بررسی وضعیت ربات
    if app_manager.initialized:
        health_status["bot_status"] = "healthy"
        health_status["webhook_status"] = "active"
    else:
        health_status["bot_status"] = "unhealthy"
        health_status["webhook_status"] = "inactive"
    
    status_code = 200 if app_manager.initialized else 503
    
    return jsonify(health_status), status_code

@app.route('/stats')
def stats():
    """آمار عملکرد"""
    health_monitor.increment_requests()
    
    stats_info = {
        "service": "Konkur Bot Statistics",
        "timestamp": datetime.now(AdvancedConfig.TIMEZONE).isoformat(),
        "health_stats": health_monitor.get_health_status(),
        "bot_stats": app_manager.get_stats() if app_manager.initialized else None
    }
    
    return jsonify(stats_info)

@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook_route():
    """تنظیم وب‌هوک"""
    health_monitor.increment_requests()
    
    try:
        async def setup():
            return await webhook_manager.setup_webhook()
        
        success = asyncio.run(setup())
        
        if success:
            return jsonify({
                "status": "success",
                "message": "Webhook set successfully",
                "webhook_url": f"{AdvancedConfig.WEBHOOK_URL}/webhook"
            })
        else:
            return jsonify({
                "status": "error", 
                "message": "Failed to set webhook"
            }), 500
            
    except Exception as e:
        logger.error(f"❌ خطا در تنظیم وب‌هوک: {e}")
        health_monitor.increment_errors()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/webhook', methods=['POST'])
async def webhook():
    """دریافت وب‌هوک از تلگرام"""
    health_monitor.increment_requests()
    
    try:
        # بررسی امنیتی
        if request.headers.get('X-Telegram-Bot-Api-Secret-Token') != AdvancedConfig.WEBHOOK_SECRET:
            logger.warning("⚠️ درخواست وب‌هوک با توکن نامعتبر")
            health_monitor.increment_errors()
            return jsonify({"status": "unauthorized"}), 401
        
        if not app_manager.initialized:
            logger.error("❌ برنامه تلگرام initialize نشده")
            health_monitor.increment_errors()
            return jsonify({"status": "error", "message": "Application not initialized"}), 500
        
        # دریافت داده‌ها
        data = request.get_json()
        
        # لاگ خلاصه
        if data:
            update_id = data.get('update_id', 'unknown')
            logger.info(f"📨 وب‌هوک #{update_id} دریافت شد")
        
        # پردازش آپدیت
        update = Update.de_json(data, app_manager.application.bot)
        await app_manager.application.process_update(update)
        
        logger.info(f"✅ وب‌هوک #{data.get('update_id', 'unknown')} پردازش شد")
        return jsonify({"status": "success"}), 200
        
    except Exception as e:
        logger.error(f"❌ خطا در پردازش وب‌هوک: {e}")
        logger.error(traceback.format_exc())
        health_monitor.increment_errors()
        return jsonify({"status": "error", "message": "Internal server error"}), 200

@app.route('/restart', methods=['POST'])
def restart_bot():
    """راه‌اندازی مجدد ربات (فقط برای ادمین)"""
    health_monitor.increment_requests()
    
    try:
        # بررسی احراز هویت
        auth_token = request.headers.get('Authorization')
        if auth_token != f"Bearer {AdvancedConfig.WEBHOOK_SECRET}":
            return jsonify({"status": "unauthorized"}), 401
        
        # راه‌اندازی مجدد
        success = app_manager.initialize()
        
        if success:
            # تنظیم مجدد وب‌هوک
            asyncio.run(webhook_manager.setup_webhook())
            
            return jsonify({
                "status": "success",
                "message": "Bot restarted successfully"
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to restart bot"
            }), 500
            
    except Exception as e:
        logger.error(f"❌ خطا در راه‌اندازی مجدد: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "status": "error",
        "message": "Endpoint not found",
        "available_endpoints": ["/", "/health", "/stats", "/set_webhook", "/webhook"]
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"status": "error", "message": "Method not allowed"}), 405

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"❌ خطای سرور داخلی: {error}")
    health_monitor.increment_errors()
    return jsonify({"status": "error", "message": "Internal server error"}), 500

# ==================== INITIALIZATION ====================

def initialize_system():
    """راه‌اندازی کامل سیستم"""
    logger.info("🚀 در حال راه‌اندازی سیستم ربات کنکور ۱۴۰۵...")
    
    # نمایش اطلاعات پیکربندی
    config_info = AdvancedConfig.get_config_info()
    logger.info(f"⚙️  پیکربندی سیستم: {config_info}")
    
    # راه‌اندازی ربات
    if not app_manager.initialize():
        logger.error("❌ راه‌اندازی ربات ناموفق بود")
        return False
    
    # تنظیم وب‌هوک
    logger.info("🌐 در حال تنظیم وب‌هوک...")
    webhook_success = asyncio.run(webhook_manager.setup_webhook())
    
    if webhook_success:
        logger.info("✅ سیستم با موفقیت راه‌اندازی شد")
        return True
    else:
        logger.error("❌ تنظیم وب‌هوک ناموفق بود")
        return False

# ==================== MAIN EXECUTION ====================

if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("🤖 راه‌اندازی ربات کنکور ۱۴۰۵ - نسخه پیشرفته")
    logger.info("=" * 60)
    
    # راه‌اندازی سیستم
    if initialize_system():
        logger.info(f"🌐 شروع سرویس Flask روی پورت {AdvancedConfig.PORT}")
        
        # اجرای برنامه Flask
        app.run(
            host=AdvancedConfig.HOST,
            port=AdvancedConfig.PORT,
            debug=AdvancedConfig.DEBUG,
            use_reloader=False
        )
    else:
        logger.error("❌ راه‌اندازی سیستم ناموفق بود")
        sys.exit(1)
