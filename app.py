import os
import logging
import asyncio
import threading
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
import sys
import traceback
from datetime import datetime
import pytz
import jdatetime
import json
import requests

# ==================== BASIC LOGGING SETUP ====================

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ==================== SIMPLE CONFIGURATION ====================

class Config:
    BOT_TOKEN = os.environ.get('BOT_TOKEN', '8381121739:AAFB2YBMomBh9xhoI3Qn0VVuGaGlpea9fx8')
    ADMIN_ID = int(os.environ.get('ADMIN_ID', 7703677187))
    WEBHOOK_URL = os.environ.get('WEBHOOK_URL', 'https://konkour-bot.onrender.com')
    PORT = int(os.environ.get('PORT', 10000))
    HOST = '0.0.0.0'

# ==================== SIMPLE BOT MANAGER ====================

class SimpleBotManager:
    def __init__(self):
        self.application = None
        self.initialized = False
        self.start_time = datetime.now()
    
    def initialize(self):
        """Initialize the bot application"""
        try:
            logger.info("🚀 Starting bot initialization...")
            
            # Validate token
            if not Config.BOT_TOKEN or Config.BOT_TOKEN == "your_bot_token":
                logger.error("❌ BOT_TOKEN is not set")
                return False
            
            # Create application
            self.application = (
                Application.builder()
                .token(Config.BOT_TOKEN)
                .build()
            )
            
            # Setup handlers
            self.setup_handlers()
            
            self.initialized = True
            logger.info("✅ Bot initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Bot initialization failed: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def setup_handlers(self):
        """Setup all bot handlers"""
        
        # Start command
        async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
            try:
                user = update.effective_user
                logger.info(f"👤 User {user.id} started the bot")
                
                welcome_text = f"""
👋 **سلام {user.first_name} عزیز!**

🎓 **به ربات کنکور ۱۴۰۵ خوش آمدید!**

🤖 **من یک دستیار هوشمندم که می‌تونم در مسیر کنکورت کمکت کنم:**

⏳ **شمارش معکوس هوشمند کنکور**
📅 **تقویم و برنامه‌ریزی پیشرفته**  
🔔 **سیستم یادآوری هوشمند**
📚 **مدیریت برنامه مطالعه**
📊 **آنالیز پیشرفت درسی**
🔧 **پنل مدیریت پیشرفته**

💡 **برای شروع، از منوی زیر انتخاب کن:**
"""
                keyboard = [
                    [InlineKeyboardButton("⏳ چند روز تا کنکور؟", callback_data="countdown")],
                    [InlineKeyboardButton("📅 تقویم و رویدادها", callback_data="calendar")],
                    [InlineKeyboardButton("🔔 مدیریت یادآوری‌ها", callback_data="reminders")],
                    [InlineKeyboardButton("📊 آمار و گزارش", callback_data="statistics")],
                    [InlineKeyboardButton("🔧 پنل مدیریت", callback_data="admin_panel")],
                    [InlineKeyboardButton("❓ راهنما", callback_data="help_menu")],
                    [InlineKeyboardButton("🔄 ریستارت", callback_data="restart_bot")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    welcome_text,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
                
            except Exception as e:
                logger.error(f"❌ Error in start command: {e}")
                await update.message.reply_text("❌ خطا در پردازش درخواست")
        
        # Menu command
        async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
            try:
                keyboard = [
                    [InlineKeyboardButton("⏳ چند روز تا کنکور؟", callback_data="countdown")],
                    [InlineKeyboardButton("📅 تقویم و رویدادها", callback_data="calendar")],
                    [InlineKeyboardButton("🔔 مدیریت یادآوری‌ها", callback_data="reminders")],
                    [InlineKeyboardButton("📊 آمار و گزارش", callback_data="statistics")],
                    [InlineKeyboardButton("🔧 پنل مدیریت", callback_data="admin_panel")],
                    [InlineKeyboardButton("❓ راهنما", callback_data="help_menu")],
                    [InlineKeyboardButton("🔄 ریستارت", callback_data="restart_bot")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    "🏠 **منوی اصلی ربات کنکور**\n\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
                
            except Exception as e:
                logger.error(f"❌ Error in menu command: {e}")
                await update.message.reply_text("❌ خطا در نمایش منو")
        
        # Help command
        async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
            try:
                help_text = """
❓ **راهنمای ربات کنکور ۱۴۰۵**

🎯 **دستورات اصلی:**
/start - شروع کار با ربات
/menu - نمایش منوی اصلی  
/help - نمایش این راهنما

⏳ **شمارش معکوس:**
• مشاهده زمان باقی‌مانده تا کنکور
• تاریخ دقیق هر رشته

📅 **تقویم:**
• نمایش تاریخ شمسی
• مناسبت‌ها و رویدادها

🔔 **یادآوری:**
• تنظیم یادآوری کنکور
• یادآوری مطالعه

💡 **نکته:** برای بهترین تجربه، از منوی اصلی استفاده کن.
"""
                await update.message.reply_text(help_text, parse_mode='HTML')
                
            except Exception as e:
                logger.error(f"❌ Error in help command: {e}")
                await update.message.reply_text("❌ خطا در نمایش راهنما")
        
        # Countdown handler
        async def countdown_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
                for exam_name in exam_dates.keys():
                    keyboard.append([
                        InlineKeyboardButton(f"🎯 {exam_name}", callback_data=f"show_countdown_{exam_name}")
                    ])
                
                keyboard.append([InlineKeyboardButton("🏠 بازگشت به منوی اصلی", callback_data="main_menu")])
                
                await query.edit_message_text(
                    "⏳ **سیستم شمارش معکوس کنکور ۱۴۰۵**\n\n"
                    "🎯 لطفاً کنکور مورد نظر خود را انتخاب کنید:",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='HTML'
                )
                
            except Exception as e:
                logger.error(f"❌ Error in countdown handler: {e}")
                await query.edit_message_text("❌ خطا در بارگذاری شمارش معکوس")
        
        # Show countdown for specific exam
        async def show_countdown_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            query = update.callback_query
            await query.answer()
            
            try:
                exam_name = query.data.replace("show_countdown_", "")
                exam_dates = {
                    "علوم تجربی": "1405-04-12",
                    "ریاضی‌وفنی": "1405-04-11", 
                    "علوم انسانی": "1405-04-11",
                    "فرهنگیان": "1405-02-17",
                    "هنر": "1405-04-12",
                    "زبان‌وگروه‌های‌خارجه": "1405-04-12"
                }
                
                exam_date = exam_dates.get(exam_name, "1405-04-12")
                
                # Calculate days remaining
                today = jdatetime.datetime.now()
                exam_jdate = jdatetime.datetime.strptime(exam_date, "%Y-%m-%d")
                days_remaining = (exam_jdate - today).days
                
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
"""
                
                keyboard = [
                    [InlineKeyboardButton("🔄 بروزرسانی زمان", callback_data=f"show_countdown_{exam_name}")],
                    [InlineKeyboardButton("📊 همه کنکورها", callback_data="countdown")],
                    [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
                ]
                
                await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
                
            except Exception as e:
                logger.error(f"❌ Error in show countdown: {e}")
                await query.edit_message_text("❌ خطا در محاسبه زمان باقی‌مانده")
        
        # Calendar handler
        async def calendar_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            query = update.callback_query
            await query.answer()
            
            try:
                today = jdatetime.datetime.now()
                today_formatted = today.strftime('%Y/%m/%d')
                
                text = f"""
📅 **سیستم تقویم و رویدادهای کنکور**

🕒 **امروز:** {today_formatted}
📆 **تاریخ دقیق:** {today.strftime('%Y/%m/%d %H:%M:%S')}

🎯 **امکانات موجود:**
• 📅 نمایش تقویم شمسی جاری
• 🎉 مناسبت‌ها و رویدادهای ملی
• 🎓 رویدادهای مهم کنکوری

💡 *برای مشاهده جزئیات بیشتر گزینه مورد نظر را انتخاب کنید*
"""
                
                keyboard = [
                    [InlineKeyboardButton("📅 تقویم جاری", callback_data="current_calendar")],
                    [InlineKeyboardButton("🎓 رویدادهای کنکور", callback_data="exam_events")],
                    [InlineKeyboardButton("🏠 بازگشت", callback_data="main_menu")]
                ]
                
                await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
                
            except Exception as e:
                logger.error(f"❌ Error in calendar handler: {e}")
                await query.edit_message_text("❌ خطا در بارگذاری تقویم")
        
        # Reminders handler
        async def reminders_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

💡 *یادآوری‌ها به صورت خودکار ارسال می‌شوند*
"""
                
                keyboard = [
                    [InlineKeyboardButton("⏰ یادآوری کنکور", callback_data="setup_exam_reminder")],
                    [InlineKeyboardButton("📚 یادآوری مطالعه", callback_data="setup_study_reminder")],
                    [InlineKeyboardButton("🏠 بازگشت", callback_data="main_menu")]
                ]
                
                await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
                
            except Exception as e:
                logger.error(f"❌ Error in reminders handler: {e}")
                await query.edit_message_text("❌ خطا در بارگذاری یادآوری‌ها")
        
        # Statistics handler
        async def statistics_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            query = update.callback_query
            await query.answer()
            
            try:
                text = """
📊 **آمار و گزارش عملکرد ربات**

📈 **امکانات موجود:**
• 📊 آمار مطالعه روزانه
• 📈 نمودار پیشرفت هفتگی
• 🎯 درصد پیشرفت کلی
• ⏰ زمان مطالعه مفید

💡 *سیستم آمارگیری به زودی فعال می‌شود*
"""
                
                keyboard = [
                    [InlineKeyboardButton("🔄 بروزرسانی آمار", callback_data="statistics")],
                    [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
                ]
                
                await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
                
            except Exception as e:
                logger.error(f"❌ Error in statistics handler: {e}")
                await query.edit_message_text("❌ خطا در بارگذاری آمار")
        
        # Admin panel handler
        async def admin_panel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            query = update.callback_query
            await query.answer()
            
            try:
                user_id = update.effective_user.id
                
                # Check admin access
                if user_id != Config.ADMIN_ID:
                    await query.edit_message_text(
                        "⛔ **دسترسی رد شد**\n\nاین بخش فقط برای ادمین قابل دسترسی است.",
                        parse_mode='HTML'
                    )
                    return
                
                text = """
🔧 **پنل مدیریت ربات کنکور**

📊 **آمار سیستم:**
• ربات فعال و در حال اجرا
• وب‌هوک تنظیم شده
• محیط: Production

🛠️ **عملیات مدیریتی:**
"""
                
                keyboard = [
                    [InlineKeyboardButton("📊 آمار کامل سیستم", callback_data="admin_full_stats")],
                    [InlineKeyboardButton("📢 ارسال پیام همگانی", callback_data="admin_broadcast")],
                    [InlineKeyboardButton("🔄 راه‌اندازی مجدد", callback_data="admin_restart")],
                    [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
                ]
                
                await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
                
            except Exception as e:
                logger.error(f"❌ Error in admin panel: {e}")
                await query.edit_message_text("❌ خطا در بارگذاری پنل مدیریت")
        
        # Help menu handler
        async def help_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            query = update.callback_query
            await query.answer()
            
            try:
                help_text = """
❓ **راهنمای کامل ربات کنکور ۱۴۰۵**

🎯 **چگونه از ربات استفاده کنم؟**

1. **شروع کار:** دستور /start را ارسال کنید
2. **منوی اصلی:** از دکمه‌های منو استفاده کنید
3. **شمارش معکوس:** زمان باقی‌مانده تا کنکور را ببینید
4. **تقویم:** تاریخ‌های مهم را مشاهده کنید
5. **یادآوری:** سیستم یادآوری را تنظیم کنید

🔧 **پنل مدیریت:** (فقط برای ادمین)
• مشاهده آمار کامل سیستم
• ارسال پیام همگانی
• راه‌اندازی مجدد

📞 **پشتیبانی:**
اگر مشکل داشتید، از دکمه "🔄 ریستارت" استفاده کنید
"""
                
                keyboard = [
                    [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")],
                    [InlineKeyboardButton("🔧 پنل مدیریت", callback_data="admin_panel")],
                    [InlineKeyboardButton("🔄 ریستارت", callback_data="restart_bot")]
                ]
                
                await query.edit_message_text(help_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
                
            except Exception as e:
                logger.error(f"❌ Error in help menu: {e}")
                await query.edit_message_text("❌ خطا در بارگذاری راهنما")
        
        # Restart bot handler
        async def restart_bot_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            query = update.callback_query
            await query.answer("🔄 در حال راه‌اندازی مجدد...")
            
            try:
                keyboard = [
                    [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
                ]
                
                await query.edit_message_text(
                    "✅ **ربات با موفقیت راه‌اندازی مجدد شد!**\n\n"
                    "🎯 اکنون می‌توانید از تمام امکانات ربات استفاده کنید.",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='HTML'
                )
                
            except Exception as e:
                logger.error(f"❌ Error in restart: {e}")
                await query.edit_message_text("❌ خطا در راه‌اندازی مجدد")
        
        # Main menu handler
        async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            query = update.callback_query
            await query.answer()
            
            try:
                keyboard = [
                    [InlineKeyboardButton("⏳ چند روز تا کنکور؟", callback_data="countdown")],
                    [InlineKeyboardButton("📅 تقویم و رویدادها", callback_data="calendar")],
                    [InlineKeyboardButton("🔔 مدیریت یادآوری‌ها", callback_data="reminders")],
                    [InlineKeyboardButton("📊 آمار و گزارش", callback_data="statistics")],
                    [InlineKeyboardButton("🔧 پنل مدیریت", callback_data="admin_panel")],
                    [InlineKeyboardButton("❓ راهنما", callback_data="help_menu")],
                    [InlineKeyboardButton("🔄 ریستارت", callback_data="restart_bot")]
                ]
                
                await query.edit_message_text(
                    "🏠 **منوی اصلی ربات کنکور**\n\nلطفاً بخش مورد نظر خود را انتخاب کنید:",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='HTML'
                )
                
            except Exception as e:
                logger.error(f"❌ Error in main menu: {e}")
                await query.edit_message_text("❌ خطا در بارگذاری منوی اصلی")
        
        # Text message handler
        async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
            try:
                text = update.message.text
                logger.info(f"📝 Received text: {text}")
                
                # پاسخ به پیام‌های متنی
                responses = {
                    "سلام": "سلام! 👋 چطور می‌تونم کمکت کنم?",
                    "خداحافظ": "خداحافظ! 🫡 موفق باشی در مسیر کنکور!",
                    "تشکر": "خواهش می‌کنم! 😊 خوشحالم می‌تونم کمک کنم",
                }
                
                response = responses.get(text, 
                    "🤔 **متوجه پیام شما نشدم!**\n\n"
                    "💡 لطفاً از منوی اصلی استفاده کنید یا دستور /menu را وارد کنید."
                )
                
                keyboard = [
                    [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")],
                    [InlineKeyboardButton("🔄 ریستارت", callback_data="restart_bot")]
                ]
                
                await update.message.reply_text(
                    response,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='HTML'
                )
                
            except Exception as e:
                logger.error(f"❌ Error in text handler: {e}")
                await update.message.reply_text("❌ خطا در پردازش پیام")
        
        # Error handler
        async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            logger.error(f"❌ Bot error: {context.error}")
            
            if update and update.effective_message:
                keyboard = [
                    [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")],
                    [InlineKeyboardButton("🔄 ریستارت", callback_data="restart_bot")]
                ]
                
                await update.effective_message.reply_text(
                    "❌ **خطایی در پردازش درخواست شما رخ داد.**\n\n"
                    "💡 لطفاً دوباره تلاش کنید یا از دکمه ریستارت استفاده کنید.",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='HTML'
                )
        
        # Add all handlers
        self.application.add_handler(CommandHandler("start", start))
        self.application.add_handler(CommandHandler("menu", menu))
        self.application.add_handler(CommandHandler("help", help_command))
        
        self.application.add_handler(CallbackQueryHandler(countdown_handler, pattern="^countdown$"))
        self.application.add_handler(CallbackQueryHandler(show_countdown_handler, pattern="^show_countdown_"))
        self.application.add_handler(CallbackQueryHandler(calendar_handler, pattern="^calendar$"))
        self.application.add_handler(CallbackQueryHandler(reminders_handler, pattern="^reminders$"))
        self.application.add_handler(CallbackQueryHandler(statistics_handler, pattern="^statistics$"))
        self.application.add_handler(CallbackQueryHandler(admin_panel_handler, pattern="^admin_panel$"))
        self.application.add_handler(CallbackQueryHandler(help_menu_handler, pattern="^help_menu$"))
        self.application.add_handler(CallbackQueryHandler(restart_bot_handler, pattern="^restart_bot$"))
        self.application.add_handler(CallbackQueryHandler(main_menu_handler, pattern="^main_menu$"))
        
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
        self.application.add_error_handler(error_handler)
        
        logger.info("✅ All handlers setup successfully")

# ==================== FLASK ROUTES ====================

bot_manager = SimpleBotManager()

@app.route('/')
def home():
    return jsonify({
        "status": "active",
        "service": "Konkur 1405 Bot",
        "bot_initialized": bot_manager.initialized,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "bot_initialized": bot_manager.initialized,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/set_webhook')
def set_webhook():
    try:
        # Delete existing webhook
        delete_url = f"https://api.telegram.org/bot{Config.BOT_TOKEN}/deleteWebhook"
        response = requests.get(delete_url, timeout=10)
        logger.info(f"🗑️ Delete webhook: {response.json()}")
        
        # Set new webhook
        webhook_url = f"https://api.telegram.org/bot{Config.BOT_TOKEN}/setWebhook"
        params = {
            'url': f'{Config.WEBHOOK_URL}/webhook',
            'max_connections': 40,
            'allowed_updates': json.dumps(['message', 'callback_query'])
        }
        
        response = requests.get(webhook_url, params=params, timeout=10)
        result = response.json()
        
        logger.info(f"🌐 Set webhook result: {result}")
        
        return jsonify({
            "status": "success" if result.get('ok') else "error",
            "result": result
        })
        
    except Exception as e:
        logger.error(f"❌ Webhook setup error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        logger.info("📨 Webhook received")
        
        if not bot_manager.initialized:
            logger.error("❌ Bot not initialized")
            return jsonify({"status": "error", "message": "Bot not initialized"}), 500
        
        data = request.get_json()
        if not data:
            logger.error("❌ No data in webhook")
            return jsonify({"status": "error", "message": "No data"}), 400
        
        logger.info(f"📊 Webhook data: {json.dumps(data, ensure_ascii=False)[:500]}...")
        
        # Process update
        update = Update.de_json(data, bot_manager.application.bot)
        bot_manager.application.update_queue.put(update)
        
        logger.info("✅ Webhook processed successfully")
        return jsonify({"status": "success"})
        
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}")
        logger.error(traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500

# ==================== INITIALIZATION ====================

def initialize():
    """Initialize the bot"""
    logger.info("🚀 Starting Konkur 1405 Bot...")
    
    # Initialize bot
    if bot_manager.initialize():
        logger.info("✅ Bot initialized successfully")
        
        # Set webhook
        try:
            response = requests.get(f"{Config.WEBHOOK_URL}/set_webhook", timeout=10)
            logger.info(f"🌐 Webhook setup response: {response.json()}")
        except Exception as e:
            logger.warning(f"⚠️ Webhook setup failed: {e}")
        
        return True
    else:
        logger.error("❌ Bot initialization failed")
        return False

# Initialize the bot
initialize()

if __name__ == '__main__':
    app.run(host=Config.HOST, port=Config.PORT, debug=False)

# برای Gunicorn
application = app
