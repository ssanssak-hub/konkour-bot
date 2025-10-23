from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler
from database.operations import database

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # ثبت کاربر در دیتابیس
    db_user = database.add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    keyboard = [
        [InlineKeyboardButton("⏳ چند روز تا کنکور؟", callback_data="countdown")],
        [InlineKeyboardButton("📅 تقویم و رویدادها", callback_data="calendar")],
        [InlineKeyboardButton("🔔 مدیریت یادآوری‌ها", callback_data="reminders")],
        [InlineKeyboardButton("📨 ارسال پیام", callback_data="send_message")],
        [InlineKeyboardButton("✅ اعلام حضور", callback_data="attendance")],
        [InlineKeyboardButton("📚 اهداف و برنامه‌ریزی و ثبت مطالعه", callback_data="study_plan")],
        [InlineKeyboardButton("📊 آمار و گزارش", callback_data="statistics")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")],
        [InlineKeyboardButton("🔧 پنل مدیریت", callback_data="admin_panel")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"سلام {user.first_name}! 👋\n\n"
        "به ربات کنکور ۱۴۰۵ خوش آمدید! 🎓\n\n"
        "من می‌تونم در زمینه‌های زیر بهت کمک کنم:\n"
        "• ⏳ شمارش معکوس تا کنکور\n"
        "• 📅 مدیریت زمان و برنامه‌ریزی\n" 
        "• 🔔 تنظیم یادآوری‌های هوشمند\n"
        "• 📚 ثبت اهداف و پیشرفت مطالعه\n"
        "• 📊 تحلیل آمار و عملکرد\n\n"
        "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=reply_markup
    )

async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("⏳ چند روز تا کنکور؟", callback_data="countdown")],
        [InlineKeyboardButton("📅 تقویم و رویدادها", callback_data="calendar")],
        [InlineKeyboardButton("🔔 مدیریت یادآوری‌ها", callback_data="reminders")],
        [InlineKeyboardButton("📨 ارسال پیام", callback_data="send_message")],
        [InlineKeyboardButton("✅ اعلام حضور", callback_data="attendance")],
        [InlineKeyboardButton("📚 اهداف و برنامه‌ریزی و ثبت مطالعه", callback_data="study_plan")],
        [InlineKeyboardButton("📊 آمار و گزارش", callback_data="statistics")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help")],
        [InlineKeyboardButton("🔧 پنل مدیریت", callback_data="admin_panel")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🏠 منوی اصلی\n\n"
        "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=reply_markup
    )

def setup_main_menu_handlers(application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", main_menu_handler))
    application.add_handler(CallbackQueryHandler(main_menu_handler, pattern="^main_menu$"))
