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
    
    @classmethod
    def validate_config(cls):
        """اعتبارسنجی پیشرفته تنظیمات"""
        errors = []
        
        if not cls.BOT_TOKEN or cls.BOT_TOKEN == "your_bot_token":
            errors.append("BOT_TOKEN تنظیم نشده است")
        elif len(cls.BOT_TOKEN) < 20:
            errors.append("BOT_TOKEN نامعتبر است")
        
        if not cls.WEBHOOK_URL or "your-render-url" in cls.WEBHOOK_URL:
            errors.append("WEBHOOK_URL تنظیم نشده است")
        
        if cls.ADMIN_ID == 7703677187:
            logger.warning("⚠️ ADMIN_ID با مقدار پیش‌فرض استفاده می‌شود")
            
        return errors
    
    @classmethod
    def get_config_info(cls):
        """دریافت اطلاعات پیکربندی (امن)"""
        return {
            "environment": cls.ENVIRONMENT,
            "debug_mode": cls.DEBUG,
            "webhook_configured": bool(cls.WEBHOOK_URL and "your-render-url" not in cls.WEBHOOK_URL),
            "timezone": str(cls.TIMEZONE),
            "max_connections": cls.MAX_CONNECTIONS,
            "admin_configured": cls.ADMIN_ID != 7703677187,
            "bot_token_set": bool(cls.BOT_TOKEN and cls.BOT_TOKEN != "your_bot_token")
        }

# ==================== APPLICATION MANAGER ====================

class ApplicationManager:
    """مدیریت پیشرفته و مقاوم در برابر خطای برنامه تلگرام"""
    
    def __init__(self):
        self.application = None
        self.initialized = False
        self.start_time = datetime.now()
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'last_error': None,
            'active_users': set(),
            'commands_processed': 0,
            'messages_processed': 0
        }
        self.retry_count = 0
        self.max_retries = 3
    
    def initialize(self) -> bool:
        """راه‌اندازی مقاوم برنامه"""
        try:
            logger.info("🚀 در حال راه‌اندازی برنامه تلگرام...")
            
            # اعتبارسنجی تنظیمات
            config_errors = AdvancedConfig.validate_config()
            if config_errors:
                for error in config_errors:
                    logger.error(f"❌ خطای پیکربندی: {error}")
                return False
            
            # ایجاد برنامه
            try:
                self.application = (
                    Application.builder()
                    .token(AdvancedConfig.BOT_TOKEN)
                    .build()
                )
            except Exception as e:
                logger.error(f"❌ خطا در ایجاد برنامه: {e}")
                return False
            
            # تنظیم هندلرها
            if not self._setup_handlers():
                return False
            
            self.initialized = True
            logger.info("✅ برنامه تلگرام با موفقیت راه‌اندازی شد")
            return True
            
        except Exception as e:
            logger.error(f"💥 خطا در راه‌اندازی برنامه: {e}")
            return False
    
    def _setup_handlers(self) -> bool:
        """تنظیم پیشرفته هندلرها"""
        try:
            # هندلرهای پایه
            self._setup_basic_handlers()
            
            # هندلرهای پیشرفته
            self._setup_advanced_handlers()
            
            # هندلرهای مدیریتی
            self._setup_admin_handlers()
            
            # هندلر خطا
            self.application.add_error_handler(self._error_handler)
            
            logger.info("✅ تمام هندلرها با موفقیت تنظیم شدند")
            return True
            
        except Exception as e:
            logger.error(f"❌ خطا در تنظیم هندلرها: {e}")
            return False
    
    def _setup_basic_handlers(self):
        """تنظیم هندلرهای اصلی"""
        
        async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
            """دستور /start پیشرفته"""
            try:
                user = update.effective_user
                self.stats['active_users'].add(user.id)
                self.stats['commands_processed'] += 1
                
                welcome_text = f"""
👋 **سلام {user.first_name} عزیز!**

🎓 **به ربات کنکور ۱۴۰۵ خوش آمدید!**

🤖 **من یک دستیار هوشمندم که می‌تونم در مسیر کنکورت کمکت کنم:**

⏳ **شمارش معکوس هوشمند کنکور**
📅 **تقویم و برنامه‌ریزی پیشرفته**  
🔔 **سیستم یادآوری هوشمند**
📚 **مدیریت برنامه مطالعه**
📊 **آنالیز پیشرفت درسی**
🎯 **تعیین هدف و پیگیری**

💡 **برای شروع، از منوی زیر انتخاب کن:**
"""
                
                await update.message.reply_text(
                    welcome_text,
                    reply_markup=self._create_main_menu(),
                    parse_mode='HTML'
                )
                
                self.stats['successful_requests'] += 1
                logger.info(f"✅ دستور start از کاربر {user.id} پردازش شد")
                
            except Exception as e:
                logger.error(f"❌ خطا در دستور start: {e}")
                self.stats['failed_requests'] += 1
        
        async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
            """دستور /menu"""
            try:
                await update.message.reply_text(
                    "🏠 **منوی اصلی ربات کنکور**\n\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
                    reply_markup=self._create_main_menu(),
                    parse_mode='HTML'
                )
                self.stats['successful_requests'] += 1
            except Exception as e:
                logger.error(f"❌ خطا در دستور menu: {e}")
                self.stats['failed_requests'] += 1
        
        async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
            """دستور /help"""
            try:
                help_text = """
❓ **راهنمای ربات کنکور ۱۴۰۵**

🎯 **دستورات اصلی:**
/start - شروع کار با ربات
/menu - نمایش منوی اصلی  
/help - نمایش این راهنما
/about - درباره ربات

⏳ **شمارش معکوس:**
• مشاهده زمان باقی‌مانده تا کنکور
• تاریخ دقیق هر رشته

📅 **تقویم:**
• نمایش تاریخ شمسی
• مناسبت‌ها و رویدادها

🔔 **یادآوری:**
• تنظیم یادآوری کنکور
• یادآوری مطالعه
• رویدادهای شخصی

💡 **نکته:** برای بهترین تجربه، از منوی اصلی استفاده کن.
"""
                await update.message.reply_text(help_text, parse_mode='HTML')
                self.stats['successful_requests'] += 1
            except Exception as e:
                logger.error(f"❌ خطا در دستور help: {e}")
                self.stats['failed_requests'] += 1
        
        async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
            """دستور /about"""
            try:
                about_text = f"""
🤖 **درباره ربات کنکور ۱۴۰۵**

🎓 **هدف:** کمک به داوطلبان کنکور ۱۴۰۵
🕒 **آخرین بروزرسانی:** {jdatetime.datetime.now().strftime('%Y/%m/%d')}
⚙️ **ورژن:** 4.0.0 Professional
👨‍💻 **توسعه:** سیستم مدیریت پیشرفته

📊 **آمار فعلی:**
• کاربران فعال: {len(self.stats['active_users'])}
• درخواست‌های موفق: {self.stats['successful_requests']}
• آپتایم: {str(datetime.now() - self.start_time).split('.')[0]}

💚 **با افتخار در خدمت شما**
"""
                await update.message.reply_text(about_text, parse_mode='HTML')
                self.stats['successful_requests'] += 1
            except Exception as e:
                logger.error(f"❌ خطا در دستور about: {e}")
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
                self.stats['messages_processed'] += 1
                
                logger.info(f"📝 پیام از کاربر {user_id}: {text[:100]}...")
                
                # پاسخ هوشمند
                responses = {
                    "سلام": "سلام! 👋 چطور می‌تونم کمکت کنم?",
                    "خداحافظ": "خداحافظ! 🫡 موفق باشی در مسیر کنکور!",
                    "تشکر": "خواهش می‌کنم! 😊 خوشحالم می‌تونم کمک کنم",
                    "کنکور": "آماده‌ای برای کنکور? از منوی اصلی می‌تونی زمان‌بندی رو ببینی 🎯"
                }
                
                response = responses.get(text, 
                    "🤔 **متوجه پیام شما نشدم!**\n\n"
                    "💡 لطفاً از منوی اصلی استفاده کنید یا دستور /menu را وارد کنید."
                )
                
                await update.message.reply_text(
                    response,
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
        self.application.add_handler(CommandHandler("help", help_command))
        self.application.add_handler(CommandHandler("about", about_command))
        self.application.add_handler(CallbackQueryHandler(main_menu_handler, pattern="^main_menu$"))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
        
        logger.info("✅ هندلرهای پایه تنظیم شدند")
    
    def _setup_advanced_handlers(self):
        """تنظیم هندلرهای پیشرفته"""
        
        async def countdown_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            """مدیریت شمارش معکوس"""
            query = update.callback_query
            await query.answer()
            
            try:
                keyboard = []
                for exam_name in AdvancedConfig.EXAM_DATES.keys():
                    keyboard.append([
                        InlineKeyboardButton(
                            f"🎯 {exam_name}", 
                            callback_data=f"show_countdown_{exam_name}"
                        )
                    ])
                
                keyboard.append([InlineKeyboardButton("🏠 بازگشت به منوی اصلی", callback_data="main_menu")])
                
                await query.edit_message_text(
                    "⏳ **سیستم شمارش معکوس کنکور ۱۴۰۵**\n\n"
                    "🎯 لطفاً کنکور مورد نظر خود را انتخاب کنید:\n\n"
                    "💡 *تاریخ‌ها بر اساس اعلام سازمان سنجش می‌باشد*",
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
                exam_date = AdvancedConfig.EXAM_DATES.get(exam_name, "1405-04-12")
                
                # محاسبه زمان باقی‌مانده
                today = jdatetime.datetime.now()
                exam_jdate = jdatetime.datetime.strptime(exam_date, "%Y-%m-%d")
                days_remaining = (exam_jdate - today).days
                
                # تولید متن بر اساس زمان باقی‌مانده
                if days_remaining > 0:
                    time_text = f"🕐 **زمان باقی‌مانده:** {days_remaining} روز"
                    motivation = "💪 **همت بلند دار که مردان روزگار**\n**از همت بلند به جایی رسیده‌اند**"
                else:
                    time_text = "🎉 **کنکور برگزار شده است**"
                    motivation = "✅ **پشت سر گذاشته شد!**"
                
                text = f"""
⏰ **شمارش معکوس کنکور {exam_name}**

{time_text}

📅 **تاریخ کنکور:** {exam_date.replace('-', '/')}
🕒 **ساعت برگزاری:** ۰۸:۰۰ صبح

{motivation}

💡 **توصیه مطالعاتی:**
📚 برنامه‌ریزی منظم روزانه داشته باشید
🎯 روی نقاط ضعف خود تمرکز کنید  
⏱️ زمان خود را هوشمندانه مدیریت کنید
🧘 استراحت و سلامت روان را فراموش نکنید
"""
                
                keyboard = [
                    [InlineKeyboardButton("🔄 بروزرسانی زمان", callback_data=f"show_countdown_{exam_name}")],
                    [InlineKeyboardButton("📊 همه کنکورها", callback_data="countdown")],
                    [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
                ]
                
                await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
                
            except Exception as e:
                logger.error(f"❌ خطا در نمایش شمارش معکوس: {e}")
                await query.edit_message_text("❌ خطا در محاسبه زمان باقی‌مانده")
        
        async def calendar_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            """مدیریت تقویم"""
            query = update.callback_query
            await query.answer()
            
            try:
                today = jdatetime.datetime.now()
                today_formatted = today.strftime('%A %Y/%m/%d')
                
                text = f"""
📅 **سیستم تقویم و رویدادهای کنکور**

🕒 **امروز:** {today_formatted}
📆 **تاریخ دقیق:** {today.strftime('%Y/%m/%d %H:%M:%S')}

🎯 **امکانات موجود:**
• 📅 نمایش تقویم شمسی جاری
• 🎉 مناسبت‌ها و رویدادهای ملی
• 🎓 رویدادهای مهم کنکوری
• 🔍 جستجوی تاریخ‌های مهم
• ⏰ یادآوری رویدادها

💡 *برای مشاهده جزئیات بیشتر گزینه مورد نظر را انتخاب کنید*
"""
                
                keyboard = [
                    [InlineKeyboardButton("📅 تقویم جاری", callback_data="current_calendar")],
                    [InlineKeyboardButton("🎓 رویدادهای کنکور", callback_data="exam_events")],
                    [InlineKeyboardButton("🎉 مناسبت‌ها", callback_data="events_list")],
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
🔔 **سیستم مدیریت یادآوری‌های هوشمند**

🎯 **انواع یادآوری قابل تنظیم:**

⏰ **یادآوری کنکور**
• یادآوری روزانه تا زمان کنکور
• یادآوری هفتگی پیشرفت

📚 **یادآوری مطالعه**  
• زمان‌بندی جلسات مطالعه
• یادآوری استراحت بین مطالعه

📝 **یادآوری متفرقه**
• رویدادهای شخصی
• مناسبت‌های مهم

💡 *یادآوری‌ها به صورت خودکار ارسال می‌شوند*
"""
                
                keyboard = [
                    [InlineKeyboardButton("⏰ یادآوری کنکور", callback_data="setup_exam_reminder")],
                    [InlineKeyboardButton("📚 یادآوری مطالعه", callback_data="setup_study_reminder")],
                    [InlineKeyboardButton("📝 یادآوری متفرقه", callback_data="setup_custom_reminder")],
                    [InlineKeyboardButton("📋 یادآوری‌های فعال", callback_data="active_reminders")],
                    [InlineKeyboardButton("🏠 بازگشت", callback_data="main_menu")]
                ]
                
                await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
                
            except Exception as e:
                logger.error(f"❌ خطا در هندلر یادآوری: {e}")
                await query.edit_message_text("❌ خطا در بارگذاری یادآوری‌ها")
        
        async def statistics_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            """آمار و گزارش"""
            query = update.callback_query
            await query.answer()
            
            try:
                stats = self.get_stats()
                text = f"""
📊 **آمار و گزارش عملکرد ربات**

👥 **کاربران:**
• کاربران فعال: {stats['active_users_count']}
• کاربران منحصر به فرد: {len(stats['active_users'])}

📈 **عملکرد:**
• درخواست‌های موفق: {stats['successful_requests']}
• درخواست‌های ناموفق: {stats['failed_requests']}
• مجموع درخواست‌ها: {stats['total_requests']}

⏰ **زمان‌بندی:**
• آپتایم: {stats['uptime']}
• آخرین خطا: {stats['last_error'] or 'ندارد'}

💡 *آمار به صورت real-time بروز می‌شود*
"""
                
                keyboard = [
                    [InlineKeyboardButton("🔄 بروزرسانی آمار", callback_data="statistics")],
                    [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
                ]
                
                await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
                
            except Exception as e:
                logger.error(f"❌ خطا در هندلر آمار: {e}")
                await query.edit_message_text("❌ خطا در بارگذاری آمار")
        
        # اضافه کردن هندلرهای پیشرفته
        self.application.add_handler(CallbackQueryHandler(countdown_handler, pattern="^countdown$"))
        self.application.add_handler(CallbackQueryHandler(show_countdown_handler, pattern="^show_countdown_"))
        self.application.add_handler(CallbackQueryHandler(calendar_handler, pattern="^calendar$"))
        self.application.add_handler(CallbackQueryHandler(reminders_handler, pattern="^reminders$"))
        self.application.add_handler(CallbackQueryHandler(statistics_handler, pattern="^statistics$"))
        
        logger.info("✅ هندلرهای پیشرفته تنظیم شدند")
    
    def _setup_admin_handlers(self):
        """تنظیم هندلرهای مدیریتی"""
        
        async def admin_panel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            """پنل مدیریت"""
            query = update.callback_query
            await query.answer()
            
            try:
                user_id = update.effective_user.id
                if user_id != AdvancedConfig.ADMIN_ID:
                    await query.edit_message_text("⛔ **دسترسی رد شد**\n\nاین بخش فقط برای ادمین قابل دسترسی است.")
                    return
                
                stats = self.get_stats()
                text = f"""
🔧 **پنل مدیریت ربات**

📊 **آمار سیستم:**
• کاربران فعال: {stats['active_users_count']}
• درخواست‌ها: {stats['total_requests']}
• خطاها: {stats['failed_requests']}
• آپتایم: {stats['uptime']}

⚙️ **عملیات مدیریتی:**
"""
                
                keyboard = [
                    [InlineKeyboardButton("📊 آمار کامل", callback_data="full_stats")],
                    [InlineKeyboardButton("🔄 راه‌اندازی مجدد", callback_data="restart_bot")],
                    [InlineKeyboardButton("📢 ارسال پیام همگانی", callback_data="broadcast")],
                    [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
                ]
                
                await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
                
            except Exception as e:
                logger.error(f"❌ خطا در پنل مدیریت: {e}")
                await query.edit_message_text("❌ خطا در بارگذاری پنل مدیریت")
        
        self.application.add_handler(CallbackQueryHandler(admin_panel_handler, pattern="^admin_panel$"))
        logger.info("✅ هندلرهای مدیریتی تنظیم شدند")
    
    async def _error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت پیشرفته خطاها"""
        try:
            error_msg = str(context.error)
            logger.error(f"❌ خطا در پردازش به‌روزرسانی: {error_msg}")
            
            self.stats['failed_requests'] += 1
            self.stats['last_error'] = error_msg
            
            # اطلاع به ادمین در صورت خطای شدید
            if "critical" in error_msg.lower() or "token" in error_msg.lower():
                await self._notify_admin(f"🚨 خطای بحرانی: {error_msg}")
            
            if update and update.effective_message:
                await update.effective_message.reply_text(
                    "❌ **خطایی در پردازش درخواست شما رخ داد.**\n\n"
                    "💡 لطفاً دوباره تلاش کنید یا از دستور /menu استفاده کنید.",
                    reply_markup=self._create_main_menu(),
                    parse_mode='HTML'
                )
        except Exception as e:
            logger.error(f"❌ خطا در هندلر خطا: {e}")
    
    async def _notify_admin(self, message: str):
        """اطلاع به ادمین"""
        try:
            if self.application and self.initialized:
                await self.application.bot.send_message(
                    chat_id=AdvancedConfig.ADMIN_ID,
                    text=f"🤖 {message}\n\n"
                         f"🕒 {jdatetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')}\n"
                         f"📊 کاربران فعال: {len(self.stats['active_users'])}"
                )
        except Exception as e:
            logger.warning(f"⚠️ نتوانست به ادمین پیام بفرستد: {e}")
    
    def _create_main_menu(self):
        """ایجاد منوی اصلی پیشرفته"""
        keyboard = [
            [InlineKeyboardButton("⏳ چند روز تا کنکور؟", callback_data="countdown")],
            [InlineKeyboardButton("📅 تقویم و رویدادها", callback_data="calendar")],
            [InlineKeyboardButton("🔔 مدیریت یادآوری‌ها", callback_data="reminders")],
            [InlineKeyboardButton("📊 آمار و گزارش", callback_data="statistics")],
            [InlineKeyboardButton("❓ راهنما", callback_data="help_menu")],
            [InlineKeyboardButton("🔧 پنل مدیریت", callback_data="admin_panel")]
        ]
        return InlineKeyboardMarkup(keyboard)

    def get_stats(self):
        """دریافت آمار پیشرفته"""
        return {
            'total_requests': self.stats['total_requests'],
            'successful_requests': self.stats['successful_requests'],
            'failed_requests': self.stats['failed_requests'],
            'last_error': self.stats['last_error'],
            'active_users': list(self.stats['active_users']),
            'active_users_count': len(self.stats['active_users']),
            'commands_processed': self.stats['commands_processed'],
            'messages_processed': self.stats['messages_processed'],
            'uptime': str(datetime.now() - self.start_time).split('.')[0],
            'initialized': self.initialized,
            'application_status': 'active' if self.initialized else 'inactive',
            'retry_count': self.retry_count
        }

# ==================== WEBHOOK MANAGER ====================

class WebhookManager:
    """مدیریت پیشرفته وب‌هوک"""
    
    def __init__(self, app_manager: ApplicationManager):
        self.app_manager = app_manager
        self.webhook_set = False
        self.last_setup_time = None
    
    async def setup_webhook(self) -> bool:
        """تنظیم وب‌هوک با قابلیت تلاش مجدد"""
        try:
            if not self.app_manager.initialized:
                logger.error("❌ برنامه initialize نشده - نمی‌توان وب‌هوک تنظیم کرد")
                return False
            
            webhook_url = f"{AdvancedConfig.WEBHOOK_URL}/webhook"
            logger.info(f"🌐 در حال تنظیم وب‌هوک: {webhook_url}")
            
            # حذف وب‌هوک قبلی
            try:
                await self.app_manager.application.bot.delete_webhook()
                logger.info("✅ وب‌هوک قبلی حذف شد")
                await asyncio.sleep(1)
            except Exception as e:
                logger.warning(f"⚠️ خطا در حذف وب‌هوک قبلی: {e}")
            
            # تنظیم وب‌هوک جدید
            try:
                result = await self.app_manager.application.bot.set_webhook(
                    url=webhook_url,
                    secret_token=AdvancedConfig.WEBHOOK_SECRET,
                    max_connections=AdvancedConfig.MAX_CONNECTIONS,
                    allowed_updates=['message', 'callback_query', 'chat_member', 'inline_query']
                )
                
                if result:
                    self.webhook_set = True
                    self.last_setup_time = datetime.now()
                    logger.info(f"✅ وب‌هوک با موفقیت تنظیم شد: {webhook_url}")
                    return True
                else:
                    logger.error("❌ تنظیم وب‌هوک ناموفق بود")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ خطا در تنظیم وب‌هوک: {e}")
                return False
                
        except Exception as e:
            logger.error(f"❌ خطای کلی در تنظیم وب‌هوک: {e}")
            return False

# ==================== HEALTH MONITOR ====================

class HealthMonitor:
    """مانیتورینگ پیشرفته سلامت سرویس"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.request_count = 0
        self.error_count = 0
        self.last_health_check = None
        self.health_status = "healthy"
    
    def increment_requests(self):
        self.request_count += 1
    
    def increment_errors(self):
        self.error_count += 1
        if self.error_count > 10:
            self.health_status = "degraded"
    
    def get_health_status(self):
        """دریافت وضعیت سلامت پیشرفته"""
        uptime = datetime.now() - self.start_time
        current_time = datetime.now(AdvancedConfig.TIMEZONE)
        
        health_data = {
            "status": self.health_status,
            "uptime": str(uptime).split('.')[0],
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "error_rate": round((self.error_count / self.request_count * 100), 2) if self.request_count > 0 else 0,
            "timestamp": current_time.isoformat(),
            "persian_time": jdatetime.datetime.fromgregorian(datetime=current_time).strftime('%Y/%m/%d %H:%M:%S'),
            "service": "Konkur 1405 Bot API"
        }
        
        self.last_health_check = current_time
        return health_data

# ==================== FLASK APPLICATION ====================

# ایجاد نمونه‌ها
app_manager = ApplicationManager()
webhook_manager = WebhookManager(app_manager)
health_monitor = HealthMonitor()

@app.route('/')
def home():
    """صفحه اصلی پیشرفته"""
    health_monitor.increment_requests()
    
    bot_stats = app_manager.get_stats() if hasattr(app_manager, 'initialized') and app_manager.initialized else None
    if bot_stats and 'active_users' in bot_stats:
        bot_stats['active_users'] = list(bot_stats['active_users'])
    
    info = {
        "status": "active",
        "service": "Konkur 1405 Bot - Professional Edition",
        "version": "4.0.0",
        "timestamp": datetime.now(AdvancedConfig.TIMEZONE).isoformat(),
        "persian_time": jdatetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
        "environment": AdvancedConfig.ENVIRONMENT,
        "health": health_monitor.get_health_status(),
        "bot_stats": bot_stats,
        "config": AdvancedConfig.get_config_info(),
        "endpoints": {
            "health": "/health",
            "stats": "/stats", 
            "set_webhook": "/set_webhook",
            "webhook": "/webhook",
            "restart": "/restart"
        }
    }
    
    return jsonify(info)

@app.route('/health')
def health_check():
    """بررسی سلامت پیشرفته"""
    health_monitor.increment_requests()
    
    health_status = health_monitor.get_health_status()
    
    # بررسی وضعیت ربات
    if app_manager.initialized:
        health_status["bot_status"] = "healthy"
        health_status["webhook_status"] = "active" if webhook_manager.webhook_set else "inactive"
        health_status["application_ready"] = True
    else:
        health_status["bot_status"] = "unhealthy"
        health_status["webhook_status"] = "inactive"
        health_status["application_ready"] = False
    
    # وضعیت کلی
    overall_status = "healthy" if (
        health_status["bot_status"] == "healthy" and 
        health_status["error_rate"] < 10
    ) else "unhealthy"
    
    health_status["overall_status"] = overall_status
    status_code = 200 if overall_status == "healthy" else 503
    
    return jsonify(health_status), status_code

@app.route('/stats')
def stats():
    """آمار عملکرد پیشرفته"""
    health_monitor.increment_requests()
    
    stats_info = {
        "service": "Konkur Bot Statistics - Professional",
        "timestamp": datetime.now(AdvancedConfig.TIMEZONE).isoformat(),
        "persian_time": jdatetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
        "health_stats": health_monitor.get_health_status(),
        "bot_stats": app_manager.get_stats() if app_manager.initialized else {"status": "not_initialized"},
        "system_info": {
            "python_version": sys.version,
            "platform": sys.platform,
            "environment": AdvancedConfig.ENVIRONMENT
        }
    }
    
    return jsonify(stats_info)

@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook_route():
    """تنظیم وب‌هوک - نسخه حرفه‌ای"""
    health_monitor.increment_requests()
    
    try:
        # حذف وب‌هوک قبلی
        delete_url = f"https://api.telegram.org/bot{AdvancedConfig.BOT_TOKEN}/deleteWebhook"
        delete_response = requests.get(delete_url, timeout=10)
        logger.info(f"🗑️ نتیجه حذف وب‌هوک: {delete_response.json()}")
        
        # تنظیم وب‌هوک جدید
        webhook_url = f"https://api.telegram.org/bot{AdvancedConfig.BOT_TOKEN}/setWebhook"
        params = {
            'url': f'{AdvancedConfig.WEBHOOK_URL}/webhook',
            'secret_token': AdvancedConfig.WEBHOOK_SECRET,
            'max_connections': AdvancedConfig.MAX_CONNECTIONS,
            'allowed_updates': json.dumps(['message', 'callback_query', 'chat_member'])
        }
        
        setup_response = requests.get(webhook_url, params=params, timeout=10)
        result = setup_response.json()
        
        logger.info(f"🌐 نتیجه تنظیم وب‌هوک: {result}")
        
        if result.get('ok'):
            webhook_manager.webhook_set = True
            webhook_manager.last_setup_time = datetime.now()
            
            return jsonify({
                "status": "success",
                "message": "Webhook set successfully",
                "webhook_url": f"{AdvancedConfig.WEBHOOK_URL}/webhook",
                "telegram_response": result,
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "status": "error", 
                "message": result.get('description', 'Unknown error from Telegram'),
                "telegram_response": result
            }), 500
            
    except Exception as e:
        logger.error(f"❌ خطا در تنظیم وب‌هوک: {e}")
        health_monitor.increment_errors()
        return jsonify({
            "status": "error", 
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    """وب‌هوک حرفه‌ای با مدیریت خطای پیشرفته"""
    health_monitor.increment_requests()
    
    try:
        # دریافت داده‌ها
        data = request.get_json()
        
        if not data:
            logger.warning("⚠️ درخواست وب‌هوک بدون داده دریافت شد")
            return jsonify({"status": "success", "message": "No data"}), 200
        
        update_id = data.get('update_id', 'unknown')
        logger.info(f"📨 وب‌هوک دریافت شد - آپدیت: {update_id}")
        
        # بررسی وضعیت ربات
        if not app_manager.initialized:
            logger.warning("🤖 ربات initialize نشده - پاسخ پایه ارسال می‌شود")
            return jsonify({
                "status": "success", 
                "message": "Bot initializing",
                "update_id": update_id
            }), 200
        
        # پردازش غیرهمزمان در thread جداگانه
        def process_async():
            try:
                # ایجاد event loop جدید
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                async def process_update():
                    try:
                        update = Update.de_json(data, app_manager.application.bot)
                        await app_manager.application.process_update(update)
                        logger.info(f"✅ آپدیت #{update_id} پردازش شد")
                    except Exception as e:
                        logger.error(f"❌ خطا در پردازش آپدیت #{update_id}: {e}")
                
                loop.run_until_complete(process_update())
                loop.close()
                
            except Exception as e:
                logger.error(f"❌ خطا در پردازش async: {e}")
        
        # اجرا در thread جداگانه
        thread = threading.Thread(target=process_async)
        thread.daemon = True
        thread.start()
        
        logger.info(f"🚀 آپدیت #{update_id} برای پردازش ارسال شد")
        return jsonify({
            "status": "success", 
            "message": "Update queued for processing",
            "update_id": update_id,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"💥 خطای کلی در وب‌هوک: {e}")
        logger.error(traceback.format_exc())
        health_monitor.increment_errors()
        
        return jsonify({
            "status": "success",
            "message": "Error handled gracefully",
            "timestamp": datetime.now().isoformat()
        }), 200

@app.route('/restart', methods=['POST'])
def restart_bot():
    """راه‌اندازی مجدد ربات"""
    health_monitor.increment_requests()
    
    try:
        # بررسی احراز هویت
        auth_token = request.headers.get('Authorization')
        if auth_token != f"Bearer {AdvancedConfig.WEBHOOK_SECRET}":
            return jsonify({"status": "unauthorized"}), 401
        
        logger.info("🔄 درخواست راه‌اندازی مجدد ربات")
        
        # راه‌اندازی مجدد
        success = app_manager.initialize()
        
        if success:
            # تنظیم مجدد وب‌هوک
            try:
                asyncio.run(webhook_manager.setup_webhook())
            except:
                logger.warning("⚠️ تنظیم مجدد وب‌هوک ناموفق بود")
            
            return jsonify({
                "status": "success",
                "message": "Bot restarted successfully",
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to restart bot",
                "timestamp": datetime.now().isoformat()
            }), 500
            
    except Exception as e:
        logger.error(f"❌ خطا در راه‌اندازی مجدد: {e}")
        return jsonify({
            "status": "error", 
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "status": "error",
        "message": "Endpoint not found",
        "available_endpoints": [
            {"path": "/", "description": "صفحه اصلی"},
            {"path": "/health", "description": "بررسی سلامت"},
            {"path": "/stats", "description": "آمار عملکرد"},
            {"path": "/set_webhook", "description": "تنظیم وب‌هوک"},
            {"path": "/webhook", "description": "دریافت وب‌هوک تلگرام"}
        ],
        "timestamp": datetime.now().isoformat()
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "status": "error", 
        "message": "Method not allowed",
        "timestamp": datetime.now().isoformat()
    }), 405

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"❌ خطای سرور داخلی: {error}")
    health_monitor.increment_errors()
    return jsonify({
        "status": "error", 
        "message": "Internal server error",
        "timestamp": datetime.now().isoformat()
    }), 500

# ==================== INITIALIZATION ====================

def initialize_system():
    """راه‌اندازی کامل و مقاوم سیستم"""
    logger.info("🚀 در حال راه‌اندازی سیستم ربات کنکور ۱۴۰۵...")
    
    try:
        # نمایش اطلاعات پیکربندی
        config_info = AdvancedConfig.get_config_info()
        logger.info(f"⚙️ اطلاعات پیکربندی: {config_info}")
        
        # اعتبارسنجی تنظیمات
        config_errors = AdvancedConfig.validate_config()
        if config_errors:
            for error in config_errors:
                logger.error(f"❌ خطای پیکربندی: {error}")
            return False
        
        # راه‌اندازی ربات
        logger.info("🤖 در حال راه‌اندازی ربات تلگرام...")
        if not app_manager.initialize():
            logger.error("❌ راه‌اندازی ربات ناموفق بود")
            return False
        
        logger.info("✅ ربات تلگرام راه‌اندازی شد")
        
        # تنظیم وب‌هوک
        logger.info("🌐 در حال تنظیم وب‌هوک...")
        try:
            webhook_success = asyncio.run(webhook_manager.setup_webhook())
            if webhook_success:
                logger.info("✅ وب‌هوک تنظیم شد")
            else:
                logger.warning("⚠️ تنظیم وب‌هوک ناموفق بود - ربات همچنان کار می‌کند")
        except Exception as e:
            logger.warning(f"⚠️ خطا در تنظیم وب‌هوک: {e} - ربات همچنان کار می‌کند")
        
        logger.info("🎉 سیستم با موفقیت راه‌اندازی شد")
        return True
        
    except Exception as e:
        logger.error(f"💥 خطای شدید در راه‌اندازی سیستم: {e}")
        logger.error(traceback.format_exc())
        return False

# ==================== QUICK FIX ====================
def quick_initialize():
    """راه‌اندازی سریع و تضمینی ربات"""
    print("🚀 راه‌اندازی سریع ربات...")
    
    try:
        # تست توکن
        import requests
        token = AdvancedConfig.BOT_TOKEN
        test_url = f"https://api.telegram.org/bot{token}/getMe"
        
        response = requests.get(test_url, timeout=10)
        print(f"✅ تست توکن: {response.json()}")
        
        # راه‌اندازی مستقیم
        from telegram.ext import Application
        
        app_manager.application = Application.builder().token(token).build()
        
        # اضافه کردن یک هندلر ساده
        async def start(update, context):
            await update.message.reply_text("🎉 ربات فعال شد! به ربات کنکور خوش آمدید!")
        
        app_manager.application.add_handler(CommandHandler("start", start))
        app_manager.application.add_handler(CommandHandler("help", start))
        
        app_manager.initialized = True
        print("✅ ربات با موفقیت راه‌اندازی شد")
        
        # تنظیم وب‌هوک
        try:
            import asyncio
            asyncio.run(webhook_manager.setup_webhook())
        except Exception as e:
            print(f"⚠️ وب‌هوک: {e}")
            
    except Exception as e:
        print(f"❌ خطا در راه‌اندازی سریع: {e}")

# اجرای راه‌اندازی سریع
quick_initialize()
# ==================== MAIN EXECUTION ====================

if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("🤖 راه‌اندازی ربات کنکور ۱۴۰۵ - نسخه حرفه‌ای")
    logger.info("=" * 60)
    
    # راه‌اندازی سیستم
    if initialize_system():
        logger.info(f"🌐 شروع سرویس Flask روی پورت {AdvancedConfig.PORT}")
        logger.info(f"✅ وضعیت نهایی: initialized={app_manager.initialized}")
        
        # اجرای برنامه Flask
        app.run(
            host=AdvancedConfig.HOST,
            port=AdvancedConfig.PORT,
            debug=AdvancedConfig.DEBUG,
            use_reloader=False
        )
    else:
        logger.error("❌ راه‌اندازی سیستم ناموفق بود")
        
        # اجرای سرویس در حالت محدود
        logger.info("🔄 اجرای سرویس در حالت پایه...")
        app.run(
            host=AdvancedConfig.HOST,
            port=AdvancedConfig.PORT,
            debug=AdvancedConfig.DEBUG,
            use_reloader=False
        )
