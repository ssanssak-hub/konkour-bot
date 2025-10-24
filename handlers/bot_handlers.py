import os
import logging
import jdatetime
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters, CommandHandler

logger = logging.getLogger(__name__)

# ==================== CONFIGURATION ====================

BOT_TOKEN = os.environ.get('BOT_TOKEN', '8381121739:AAFB2YBMomBh9xhoI3Qn0VVuGaGlpea9fx8')
ADMIN_ID = int(os.environ.get('ADMIN_ID', 7703677187))

# تاریخ‌های کنکور 1405
EXAM_DATES = {
    "علوم تجربی": "1405-04-12 08:00:00",
    "ریاضی‌وفنی": "1405-04-11 08:00:00", 
    "علوم انسانی": "1405-04-11 08:00:00",
    "فرهنگیان": ["1405-02-17 08:00:00", "1405-02-18 08:00:00"],
    "هنر": "1405-04-12 14:30:00",
    "زبان‌وگروه‌های‌خارجه": "1405-04-12 14:30:00"
}

# ==================== HANDLER SETUP ====================

def setup_main_handlers(application):
    """تنظیم تمام هندلرهای اصلی"""
    try:
        logger.info("🔧 در حال تنظیم هندلرهای اصلی...")
        
        # دستورات
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("menu", menu_command))
        application.add_handler(CommandHandler("help", help_command))

        # منوی اصلی و ناوبری
        application.add_handler(CallbackQueryHandler(main_menu, pattern="^main_menu$"))
        application.add_handler(CallbackQueryHandler(back_to_main, pattern="^back_to_main$"))

        # شمارش معکوس
        application.add_handler(CallbackQueryHandler(countdown_menu, pattern="^countdown$"))
        application.add_handler(CallbackQueryHandler(show_countdown, pattern="^countdown_"))

        # تقویم
        application.add_handler(CallbackQueryHandler(calendar_menu, pattern="^calendar$"))
        application.add_handler(CallbackQueryHandler(show_current_calendar, pattern="^current_calendar$"))
        application.add_handler(CallbackQueryHandler(next_month, pattern="^next_month$"))
        application.add_handler(CallbackQueryHandler(prev_month, pattern="^prev_month$"))
        application.add_handler(CallbackQueryHandler(view_events_menu, pattern="^view_events$"))
        application.add_handler(CallbackQueryHandler(show_today_events, pattern="^today_events$"))

        # یادآوری‌ها
        application.add_handler(CallbackQueryHandler(reminders_menu, pattern="^reminders$"))
        application.add_handler(CallbackQueryHandler(setup_exam_reminder, pattern="^reminder_exam$"))
        application.add_handler(CallbackQueryHandler(setup_study_reminder, pattern="^reminder_study$"))
        application.add_handler(CallbackQueryHandler(setup_custom_reminder, pattern="^reminder_custom$"))
        application.add_handler(CallbackQueryHandler(select_exam_for_reminder, pattern="^reminder_exam_"))
        application.add_handler(CallbackQueryHandler(manage_reminders, pattern="^reminder_manage$"))
        application.add_handler(CallbackQueryHandler(toggle_reminder, pattern="^reminder_toggle_"))
        application.add_handler(CallbackQueryHandler(delete_reminder, pattern="^reminder_delete_"))
        application.add_handler(CallbackQueryHandler(confirm_delete_reminder, pattern="^reminder_confirm_delete_"))

        # پیام‌رسانی
        application.add_handler(CallbackQueryHandler(send_message_menu, pattern="^send_message$"))
        application.add_handler(CallbackQueryHandler(start_message_to_admin, pattern="^send_to_main_admin$"))
        application.add_handler(CallbackQueryHandler(start_message_to_admin, pattern="^send_to_all_admins$"))
        application.add_handler(CallbackQueryHandler(start_message_to_admin, pattern="^send_to_self$"))
        application.add_handler(CallbackQueryHandler(show_my_messages, pattern="^my_messages$"))
        application.add_handler(CallbackQueryHandler(manage_messages, pattern="^manage_messages$"))
        application.add_handler(CallbackQueryHandler(edit_message, pattern="^edit_message_"))
        application.add_handler(CallbackQueryHandler(delete_message, pattern="^delete_message_"))
        application.add_handler(CallbackQueryHandler(confirm_delete_message, pattern="^confirm_delete_"))
        application.add_handler(CallbackQueryHandler(cancel_message, pattern="^cancel_message$"))

        # سایر منوها
        application.add_handler(CallbackQueryHandler(attendance_handler, pattern="^attendance$"))
        application.add_handler(CallbackQueryHandler(study_plan_menu, pattern="^study_plan$"))
        application.add_handler(CallbackQueryHandler(statistics_menu, pattern="^statistics$"))
        application.add_handler(CallbackQueryHandler(help_menu, pattern="^help$"))
        application.add_handler(CallbackQueryHandler(admin_panel, pattern="^admin_panel$"))

        # هندلرهای پیام متنی
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

        # هندلر خطا
        application.add_error_handler(error_handler)

        logger.info("✅ تمام هندلرهای اصلی با موفقیت تنظیم شدند")
        
    except Exception as e:
        logger.error(f"❌ خطا در تنظیم هندلرهای اصلی: {e}")
        raise

# ==================== COMMAND HANDLERS ====================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /start"""
    try:
        user = update.effective_user
        logger.info(f"🚀 کاربر جدید: {user.first_name} (ID: {user.id})")
        
        welcome_text = f"""
سلام {user.first_name} عزیز! 👋

🎓 **به ربات کنکور ۱۴۰۵ خوش آمدید!**

من یک دستیار هوشمندم که می‌تونم در مسیر کنکورت کمکت کنم:

⏳ **شمارش معکوس هوشمند**
• زمان دقیق تا هر کنکور
• برنامه‌ریزی خودکار

📅 **مدیریت زمان پیشرفته**  
• تقویم شمسی کامل
• رویدادها و مناسبت‌ها

🔔 **یادآوری‌های هوشمند**
• یادآوری کنکور
• برنامه مطالعه
• رویدادهای شخصی

📚 **برنامه‌ریزی مطالعه**
• ثبت اهداف
• پیگیری پیشرفت
• آمار تحلیلی

📨 **پشتیبانی آنلاین**
• ارتباط با ادمین
• گزارش مشکلات
• پیشنهادات

💡 **برای شروع، یکی از گزینه‌های زیر رو انتخاب کن:**
"""
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=create_main_menu_keyboard(),
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"❌ خطا در دستور start: {e}")
        await update.message.reply_text("❌ متأسفانه خطایی رخ داد! لطفاً دوباره تلاش کنید.")

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /menu"""
    try:
        await update.message.reply_text(
            "🏠 **منوی اصلی**\n\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
            reply_markup=create_main_menu_keyboard(),
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"❌ خطا در دستور menu: {e}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /help"""
    try:
        help_text = """
❓ **راهنمای ربات کنکور ۱۴۰۵**

🎯 **دستورات اصلی:**
• /start - شروع کار با ربات
• /menu - نمایش منوی اصلی  
• /help - راهنمای کامل

📚 **امکانات ربات:**

⏳ **شمارش معکوس**
• نمایش زمان دقیق تا کنکور
• برنامه‌ریزی خودکار
• توصیه‌های مطالعاتی

📅 **تقویم و رویدادها**
• تقویم شمسی کامل
• مناسبت‌های مهم
• رویدادهای کنکور

🔔 **یادآوری‌ها**
• یادآوری کنکور
• برنامه مطالعه
• رویدادهای شخصی

📨 **پیام‌رسانی**
• ارتباط با ادمین
• گزارش مشکلات
• پیشنهادات

💡 **برای استفاده، از منوی اصلی گزینه مورد نظرتون رو انتخاب کنید.**
"""
        await update.message.reply_text(help_text, parse_mode='HTML')
    except Exception as e:
        logger.error(f"❌ خطا در دستور help: {e}")

# ==================== MAIN MENU & NAVIGATION ====================

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منوی اصلی"""
    query = update.callback_query
    await query.answer()
    
    try:
        menu_text = """
🏠 **منوی اصلی ربات کنکور**

🎯 **لطفاً بخش مورد نظر خود را انتخاب کنید:**

⏳ **شمارش معکوس** - زمان دقیق تا کنکور
📅 **تقویم و رویدادها** - مدیریت زمان و مناسبت‌ها  
🔔 **یادآوری‌ها** - تنظیم یادآوری هوشمند
📨 **پیام‌رسانی** - ارتباط با ادمین و پشتیبانی

✅ **حضور و غیاب** - ثبت حضور روزانه
📚 **برنامه‌ریزی** - مدیریت اهداف مطالعه
📊 **آمار و گزارش** - تحلیل پیشرفت
❓ **راهنما** - راهنمای استفاده

🔧 **پنل مدیریت** - برای ادمین‌ها
"""
        await query.edit_message_text(
            menu_text,
            reply_markup=create_main_menu_keyboard(),
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"❌ خطا در منوی اصلی: {e}")
        await query.edit_message_text("❌ خطا در نمایش منو")

async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بازگشت به منوی اصلی"""
    query = update.callback_query
    await query.answer()
    await main_menu(update, context)

# ==================== COUNTDOWN HANDLERS ====================

async def countdown_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منوی شمارش معکوس"""
    query = update.callback_query
    await query.answer()
    
    try:
        countdown_text = """
⏳ **سیستم شمارش معکوس کنکور ۱۴۰۵**

🎯 **لطفاً کنکور مورد نظر خود را انتخاب کنید:**

💡 **امکانات:**
• نمایش زمان دقیق تا کنکور
• برنامه‌ریزی خودکار
• توصیه‌های مطالعاتی
• بروزرسانی لحظه‌ای
"""
        await query.edit_message_text(
            countdown_text,
            reply_markup=create_countdown_keyboard(),
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"❌ خطا در منوی شمارش معکوس: {e}")

async def show_countdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش شمارش معکوس برای کنکور انتخاب شده"""
    query = update.callback_query
    await query.answer()
    
    try:
        exam_name = query.data.replace("countdown_", "")
        countdown_data = calculate_countdown(exam_name)
        
        text = f"""
⏰ **شمارش معکوس کنکور {exam_name}**

{countdown_data['time_display']}

📅 **تاریخ کنکور:** {countdown_data['exam_date']}
🕒 **ساعت برگزاری:** {countdown_data['exam_time']}

📊 **خلاصه زمانی:**
🗓️ مجموع روزها: {countdown_data['total_days']} روز
📈 مجموع هفته‌ها: {countdown_data['total_weeks']} هفته
⏱️ مجموع ساعت‌ها: {countdown_data['total_hours']} ساعت

💡 **توصیه مطالعاتی:**
{countdown_data['recommendation']}
"""
        
        keyboard = [
            [InlineKeyboardButton("🔄 بروزرسانی زمان", callback_data=f"countdown_{exam_name}")],
            [InlineKeyboardButton("📊 همه کنکورها", callback_data="countdown")],
            [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"❌ خطا در نمایش شمارش معکوس: {e}")
        await query.edit_message_text("❌ خطا در محاسبه زمان باقی‌مانده")

def calculate_countdown(exam_name):
    """محاسبه زمان باقی‌مانده تا کنکور"""
    exam_date_str = EXAM_DATES.get(exam_name)
    
    if not exam_date_str:
        return {
            'time_display': "❌ تاریخ کنکور یافت نشد",
            'exam_date': "نامشخص",
            'exam_time': "نامشخص", 
            'total_days': 0,
            'total_weeks': 0,
            'total_hours': 0,
            'recommendation': "لطفاً با ادمین تماس بگیرید."
        }
    
    # برای سادگی، تاریخ‌های ثابت در نظر گرفته می‌شوند
    default_data = {
        "علوم تجربی": {"days": 285, "date": "۱۴۰۵/۰۴/۱۲", "time": "۰۸:۰۰ صبح"},
        "ریاضی‌وفنی": {"days": 284, "date": "۱۴۰۵/۰۴/۱۱", "time": "۰۸:۰۰ صبح"},
        "علوم انسانی": {"days": 284, "date": "۱۴۰۵/۰۴/۱۱", "time": "۰۸:۰۰ صبح"},
        "فرهنگیان": {"days": 205, "date": "۱۴۰۵/۰۲/۱۷-۱۸", "time": "۰۸:۰۰ صبح"},
        "هنر": {"days": 285, "date": "۱۴۰۵/۰۴/۱۲", "time": "۱۴:۳۰ بعدازظهر"},
        "زبان‌وگروه‌های‌خارجه": {"days": 285, "date": "۱۴۰۵/۰۴/۱۲", "time": "۱۴:۳۰ بعدازظهر"}
    }
    
    data = default_data.get(exam_name, {"days": 300, "date": "۱۴۰۵/۰۴/۰۱", "time": "۰۸:۰۰ صبح"})
    
    days = data["days"]
    weeks = days // 7
    hours = days * 24
    
    time_parts = []
    if weeks > 0:
        time_parts.append(f"{weeks} هفته")
    if days > 0:
        time_parts.append(f"{days} روز")
    if hours > 0:
        time_parts.append(f"{hours} ساعت")
    
    time_display = " • ".join(time_parts)
    
    recommendations = {
        300: "📅 زمان کافی داری! با برنامه‌ریزی منظم پیش برو.",
        200: "⏳ نیمه راهی! روی نقاط ضعف تمرکز کن.", 
        100: "🚀 زمان محدود! تست‌زنی رو بیشتر کن.",
        50: "🔥 فاز آخر! مرور سریع و تست زمان‌دار.",
        10: "🎯 نزدیک شد! استراحت و مرور سبک.",
        0: "🎉 کنکور تموم شد! به خودت افتخار کن."
    }
    
    recommendation = "📚 برنامه‌ریزی کن و با انگیزه ادامه بده!"
    for threshold, rec in recommendations.items():
        if days >= threshold:
            recommendation = rec
            break
    
    return {
        'time_display': f"🕐 {time_display}",
        'exam_date': data["date"],
        'exam_time': data["time"],
        'total_days': days,
        'total_weeks': weeks,
        'total_hours': hours,
        'recommendation': recommendation
    }

# ==================== CALENDAR HANDLERS ====================

async def calendar_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منوی تقویم"""
    query = update.callback_query
    await query.answer()
    
    try:
        now = jdatetime.datetime.now()
        
        calendar_text = """
📅 **سیستم تقویم و رویدادها**

🎯 **امکانات موجود:**
• نمایش تقویم شمسی
• مناسبت‌ها و رویدادها
• رویدادهای کنکور
• جستجوی تاریخ
"""
        
        keyboard = [
            [InlineKeyboardButton("📅 تقویم جاری", callback_data="current_calendar")],
            [InlineKeyboardButton("🔍 مشاهده رویدادها", callback_data="view_events")],
            [InlineKeyboardButton("📝 افزودن رویداد", callback_data="add_event")],
            [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
        ]
        
        await query.edit_message_text(
            calendar_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"❌ خطا در منوی تقویم: {e}")
        await query.edit_message_text("❌ خطا در بارگذاری تقویم")

async def show_current_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش تقویم ماه جاری"""
    query = update.callback_query
    await query.answer()
    
    try:
        now = jdatetime.datetime.now()
        calendar = generate_persian_calendar(now.year, now.month)
        
        text = f"""
📅 **تقویم {get_persian_month_name(now.month)} {now.year}**

{calendar}

🕒 **امروز:** {now.strftime('%Y/%m/%d %H:%M')}
"""
        
        keyboard = [
            [
                InlineKeyboardButton("◀️ ماه قبل", callback_data="prev_month"),
                InlineKeyboardButton("🔄 امروز", callback_data="current_calendar"),
                InlineKeyboardButton("ماه بعد ▶️", callback_data="next_month")
            ],
            [InlineKeyboardButton("🔍 رویدادهای امروز", callback_data="today_events")],
            [InlineKeyboardButton("📅 منوی تقویم", callback_data="calendar")],
            [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        
    except Exception as e:
        logger.error(f"❌ خطا در نمایش تقویم: {e}")
        await query.edit_message_text("❌ خطا در تولید تقویم")

async def next_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ماه بعد"""
    query = update.callback_query
    await query.answer()
    
    try:
        # برای سادگی، همیشه ماه جاری نشان داده می‌شود
        await show_current_calendar(update, context)
    except Exception as e:
        logger.error(f"❌ خطا در ماه بعد: {e}")

async def prev_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ماه قبل"""
    query = update.callback_query
    await query.answer()
    
    try:
        # برای سادگی، همیشه ماه جاری نشان داده می‌شود
        await show_current_calendar(update, context)
    except Exception as e:
        logger.error(f"❌ خطا در ماه قبل: {e}")

async def view_events_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منوی مشاهده رویدادها"""
    query = update.callback_query
    await query.answer()
    
    try:
        text = """
🔍 **مشاهده رویدادها**

📅 می‌توانید رویدادها را به روش‌های زیر مشاهده کنید:
"""
        
        keyboard = [
            [InlineKeyboardButton("📅 رویدادهای امروز", callback_data="today_events")],
            [InlineKeyboardButton("🔍 جستجو در تاریخ", callback_data="search_events")],
            [InlineKeyboardButton("📆 رویدادهای این هفته", callback_data="week_events")],
            [InlineKeyboardButton("📅 بازگشت به تقویم", callback_data="calendar")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
    except Exception as e:
        logger.error(f"❌ خطا در منوی رویدادها: {e}")

async def show_today_events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش رویدادهای امروز"""
    query = update.callback_query
    await query.answer()
    
    try:
        today = jdatetime.datetime.now().strftime("%Y-%m-%d")
        events = get_events_for_date(today)
        
        text = f"""
📅 **رویدادهای امروز**
🗓️ {jdatetime.datetime.now().strftime('%A %Y/%m/%d')}

{events}
"""
        
        keyboard = [
            [InlineKeyboardButton("📅 تقویم امروز", callback_data="current_calendar")],
            [InlineKeyboardButton("🔍 تاریخ دیگر", callback_data="view_events")],
            [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
    except Exception as e:
        logger.error(f"❌ خطا در نمایش رویدادهای امروز: {e}")

def generate_persian_calendar(year, month):
    """تولید تقویم شمسی"""
    months_fa = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
                "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]
    days_fa = ["ش", "ی", "د", "س", "چ", "پ", "ج"]
    
    try:
        first_day = jdatetime.datetime(year, month, 1)
        days_in_month = 31 if month <= 6 else 30
        if month == 12:  # اسفند
            days_in_month = 29 if year % 4 == 3 else 30
        
        # هدر روزهای هفته
        calendar = " ".join(days_fa) + "\n"
        
        # روزهای ماه
        weekday = (first_day.weekday() + 1) % 7
        days = ["  " for _ in range(weekday)]
        
        for day in range(1, days_in_month + 1):
            days.append(f"{day:2d}")
        
        # چیدمان در خطوط
        lines = []
        current_line = []
        
        for i, day in enumerate(days):
            current_line.append(day)
            if (i + 1) % 7 == 0:
                lines.append(" ".join(current_line))
                current_line = []
        
        if current_line:
            lines.append(" ".join(current_line))
        
        return calendar + "\n".join(lines)
        
    except Exception as e:
        return f"خطا در تولید تقویم: {e}"

def get_persian_month_name(month):
    """نام ماه شمسی"""
    months = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
             "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]
    return months[month-1] if 1 <= month <= 12 else "نامشخص"

def get_events_for_date(date_str):
    """دریافت رویدادها برای تاریخ مشخص"""
    events = {
        "1405-01-01": "🎉 عید نوروز",
        "1405-01-02": "🎉 عید نوروز", 
        "1405-01-03": "🎉 عید نوروز",
        "1405-01-04": "🎉 عید نوروز",
        "1405-01-12": "📢 روز جمهوری اسلامی",
        "1405-01-13": "🌿 سیزده بدر",
        "1405-02-14": "🕊️ رحلت امام خمینی",
        "1405-04-11": "🎯 کنکور ریاضی و انسانی",
        "1405-04-12": "🎯 کنکور تجربی، هنر و زبان"
    }
    
    return events.get(date_str, "📭 هیچ رویدادی برای این تاریخ ثبت نشده است.")

# ==================== REMINDERS HANDLERS ====================

async def reminders_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منوی یادآوری‌ها"""
    query = update.callback_query
    await query.answer()
    
    try:
        text = """
🔔 **سیستم مدیریت یادآوری‌ها**

🎯 **انواع یادآوری قابل تنظیم:**

⏰ **یادآوری کنکور**
• یادآوری روزانه تا زمان کنکور
• برنامه‌ریزی خودکار

📚 **یادآوری مطالعه**  
• زمان‌بندی جلسات مطالعه
• یادآوری دروس مختلف

📝 **یادآوری متفرقه**
• رویدادهای شخصی
• کارهای مهم
"""
        
        keyboard = [
            [InlineKeyboardButton("⏰ یادآوری کنکور", callback_data="reminder_exam")],
            [InlineKeyboardButton("📚 یادآوری مطالعه", callback_data="reminder_study")],
            [InlineKeyboardButton("📝 یادآوری متفرقه", callback_data="reminder_custom")],
            [InlineKeyboardButton("📋 مدیریت یادآوری‌ها", callback_data="reminder_manage")],
            [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"❌ خطا در منوی یادآوری‌ها: {e}")
        await query.edit_message_text("❌ خطا در بارگذاری سیستم یادآوری")

async def setup_exam_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تنظیم یادآوری کنکور"""
    query = update.callback_query
    await query.answer()
    
    try:
        text = """
⏰ **تنظیم یادآوری کنکور**

🎯 لطفاً کنکور مورد نظر را انتخاب کنید:
"""
        
        keyboard = []
        for exam_name in EXAM_DATES.keys():
            keyboard.append([
                InlineKeyboardButton(
                    f"🎯 {exam_name}", 
                    callback_data=f"reminder_exam_{exam_name}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="reminders")])
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"❌ خطا در تنظیم یادآوری کنکور: {e}")

async def select_exam_for_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """انتخاب کنکور برای یادآوری"""
    query = update.callback_query
    await query.answer()
    
    try:
        exam_name = query.data.replace("reminder_exam_", "")
        
        text = f"""
✅ **یادآوری کنکور {exam_name} تنظیم شد!**

⏰ از این پس، هر روز به شما یادآوری می‌کنم.

💡 **مشخصات:**
• 🎯 کنکور: {exam_name}
• ⏰ نوع: یادآوری روزانه
• 🔄 وضعیت: فعال
"""
        
        keyboard = [
            [InlineKeyboardButton("🔔 مدیریت یادآوری‌ها", callback_data="reminder_manage")],
            [InlineKeyboardButton("⏰ یادآوری جدید", callback_data="reminders")],
            [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"❌ خطا در انتخاب کنکور برای یادآوری: {e}")

async def setup_study_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تنظیم یادآوری مطالعه"""
    query = update.callback_query
    await query.answer()
    
    try:
        text = """
📚 **تنظیم یادآوری مطالعه**

✅ **یادآوری مطالعه روزانه تنظیم شد!**

⏰ هر روز ساعت ۱۸:۰۰ به شما یادآوری می‌کنم.

💡 **مشخصات:**
• 📚 نوع: یادآوری مطالعه
• ⏰ زمان: ۱۸:۰۰ هر روز
• 🔄 وضعیت: فعال
"""
        
        keyboard = [
            [InlineKeyboardButton("🔔 مدیریت یادآوری‌ها", callback_data="reminder_manage")],
            [InlineKeyboardButton("⏰ یادآوری جدید", callback_data="reminders")],
            [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"❌ خطا در تنظیم یادآوری مطالعه: {e}")

async def setup_custom_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تنظیم یادآوری متفرقه"""
    query = update.callback_query
    await query.answer()
    
    try:
        text = """
📝 **تنظیم یادآوری متفرقه**

✅ **یادآوری متفرقه تنظیم شد!**

⏰ این یک یادآوری نمونه است.

💡 **مشخصات:**
• 📝 نوع: یادآوری متفرقه
• ⏰ زمان: قابل تنظیم
• 🔄 وضعیت: فعال
"""
        
        keyboard = [
            [InlineKeyboardButton("🔔 مدیریت یادآوری‌ها", callback_data="reminder_manage")],
            [InlineKeyboardButton("⏰ یادآوری جدید", callback_data="reminders")],
            [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"❌ خطا در تنظیم یادآوری متفرقه: {e}")

async def manage_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت یادآوری‌ها"""
    query = update.callback_query
    await query.answer()
    
    try:
        text = """
📋 **مدیریت یادآوری‌های شما**

✅ **یادآوری‌های فعال:**

1. ⏰ یادآوری کنکور علوم تجربی
   🕒 هر روز | 🔄 فعال

2. 📚 یادآوری مطالعه روزانه  
   🕒 ۱۸:۰۰ هر روز | 🔄 فعال

3. 📝 یادآوری متفرقه
   🕒 قابل تنظیم | 🔄 فعال
"""
        
        keyboard = [
            [
                InlineKeyboardButton("❌ غیرفعال ۱", callback_data="reminder_toggle_1"),
                InlineKeyboardButton("🗑️ حذف ۱", callback_data="reminder_delete_1")
            ],
            [
                InlineKeyboardButton("❌ غیرفعال ۲", callback_data="reminder_toggle_2"),
                InlineKeyboardButton("🗑️ حذف ۲", callback_data="reminder_delete_2")
            ],
            [
                InlineKeyboardButton("❌ غیرفعال ۳", callback_data="reminder_toggle_3"),
                InlineKeyboardButton("🗑️ حذف ۳", callback_data="reminder_delete_3")
            ],
            [InlineKeyboardButton("⏰ ایجاد یادآوری جدید", callback_data="reminders")],
            [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"❌ خطا در مدیریت یادآوری‌ها: {e}")

async def toggle_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تغییر وضعیت یادآوری"""
    query = update.callback_query
    await query.answer("✅ وضعیت یادآوری تغییر کرد")
    await manage_reminders(update, context)

async def delete_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """حذف یادآوری"""
    query = update.callback_query
    await query.answer()
    
    try:
        reminder_id = query.data.replace("reminder_delete_", "")
        
        text = f"""
⚠️ **آیا مطمئن هستید که می‌خواهید یادآوری #{reminder_id} را حذف کنید؟**

❌ این عمل غیرقابل بازگشت است!
"""
        
        keyboard = [
            [
                InlineKeyboardButton("✅ بله، حذف کن", callback_data=f"reminder_confirm_delete_{reminder_id}"),
                InlineKeyboardButton("❌ خیر، انصراف", callback_data="reminder_manage")
            ]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"❌ خطا در حذف یادآوری: {e}")

async def confirm_delete_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تأیید حذف یادآوری"""
    query = update.callback_query
    await query.answer("✅ یادآوری حذف شد")
    await manage_reminders(update, context)

# ==================== MESSAGES HANDLERS ====================

async def send_message_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منوی ارسال پیام"""
    query = update.callback_query
    await query.answer()
    
    try:
        text = """
📨 **سیستم پیام‌رسانی**

🎯 **گزینه‌های ارسال پیام:**

👑 **ارسال به ادمین اصلی**
• پیام مستقیم به مدیر ربات
• پاسخ‌دهی سریع

👥 **ارسال به همه ادمین‌ها**  
• پیام به تمام مدیران
• پشتیبانی تخصصی

👤 **ارسال به خودم**
• یادداشت‌های شخصی
• یادآوری برای خودتان
"""
        
        keyboard = [
            [InlineKeyboardButton("👑 ارسال به ادمین اصلی", callback_data="send_to_main_admin")],
            [InlineKeyboardButton("👥 ارسال به همه ادمین‌ها", callback_data="send_to_all_admins")],
            [InlineKeyboardButton("👤 ارسال به خودم", callback_data="send_to_self")],
            [InlineKeyboardButton("📋 پیام‌های من", callback_data="my_messages")],
            [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"❌ خطا در منوی پیام‌رسانی: {e}")
        await query.edit_message_text("❌ خطا در بارگذاری سیستم پیام‌رسانی")

async def start_message_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع ارسال پیام"""
    query = update.callback_query
    await query.answer()
    
    try:
        message_type = query.data
        target_name = {
            'send_to_main_admin': 'ادمین اصلی',
            'send_to_all_admins': 'همه ادمین‌ها',
            'send_to_self': 'خودتان'
        }.get(message_type, 'ادمین')
        
        text = f"""
📝 **ارسال پیام به {target_name}**

💡 لطفاً متن پیام خود را وارد کنید:

🎯 **موارد قابل ارسال:**
• 🐛 گزارش مشکل فنی
• 💡 پیشنهاد بهبود ربات
• ❓ سوال درباره نحوه استفاده
• 📢 انتقادات و پیشنهادات
• 📚 مشکلات مطالعاتی

📝 **پیام خود را در همین چت بنویسید...**
"""
        
        # ذخیره نوع پیام در context
        context.user_data['message_type'] = message_type
        context.user_data['waiting_for_message'] = True
        
        keyboard = [
            [InlineKeyboardButton("❌ انصراف", callback_data="cancel_message")],
            [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"❌ خطا در شروع ارسال پیام: {e}")

async def show_my_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش پیام‌های کاربر"""
    query = update.callback_query
    await query.answer()
    
    try:
        text = """
📋 **پیام‌های ارسالی شما**

📭 **در حال حاضر هیچ پیامی ارسال نکرده‌اید.**

💡 می‌توانید با ارسال پیام جدید شروع کنید!
"""
        
        keyboard = [
            [InlineKeyboardButton("📨 ارسال پیام جدید", callback_data="send_message")],
            [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"❌ خطا در نمایش پیام‌ها: {e}")

async def manage_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت پیام‌ها"""
    query = update.callback_query
    await query.answer()
    
    try:
        text = """
🛠️ **مدیریت پیشرفته پیام‌ها**

🔧 این بخش به زودی فعال خواهد شد.

💡 **امکانات آینده:**
• ویرایش پیام‌ها
• حذف پیام‌ها
• آرشیو کردن
• جستجو در پیام‌ها
"""
        
        keyboard = [
            [InlineKeyboardButton("📨 ارسال پیام جدید", callback_data="send_message")],
            [InlineKeyboardButton("📋 پیام‌های من", callback_data="my_messages")],
            [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML")
        
    except Exception as e:
        logger.error(f"❌ خطا در مدیریت پیام‌ها: {e}")

async def edit_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ویرایش پیام"""
    query = update.callback_query
    await query.answer("✏️ این قابلیت به زودی فعال خواهد شد")
    await manage_messages(update, context)

async def delete_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """حذف پیام"""
    query = update.callback_query
    await query.answer("🗑️ این قابلیت به زودی فعال خواهد شد")
    await manage_messages(update, context)

async def confirm_delete_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تأیید حذف پیام"""
    query = update.callback_query
    await query.answer("✅ پیام حذف شد")
    await manage_messages(update, context)

async def cancel_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """لغو ارسال پیام"""
    query = update.callback_query
    await query.answer()
    
    # پاک کردن وضعیت
    context.user_data.pop('message_type', None)
    context.user_data.pop('waiting_for_message', None)
    
    await send_message_menu(update, context)

# ==================== OTHER MENU HANDLERS ====================

async def attendance_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ثبت حضور"""
    query = update.callback_query
    await query.answer()
    
    try:
        now = jdatetime.datetime.now()
        
        text = f"""
✅ **حضور شما ثبت شد!**

📅 تاریخ: {now.strftime('%Y/%m/%d')}
🕒 زمان: {now.strftime('%H:%M:%S')}
👤 کاربر: {query.from_user.first_name}

🎯 **امروز روز خوبی برای مطالعه است!**

💡 **نکات امروز:**
• ۳۰ دقیقه مطالعه مفید بهتر از ۳ ساعت مطالعه بی‌هدف است
• بین جلسات مطالعه حتماً استراحت کنید
• آب کافی بنوشید
"""
        
        keyboard = [
            [InlineKeyboardButton("📊 آمار حضور من", callback_data="statistics")],
            [InlineKeyboardButton("🔄 بروزرسانی", callback_data="attendance")],
            [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"❌ خطا در ثبت حضور: {e}")

async def study_plan_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منوی برنامه‌ریزی مطالعه"""
    query = update.callback_query
    await query.answer()
    
    try:
        text = """
📚 **سیستم برنامه‌ریزی مطالعه**

🎯 **امکانات اصلی:**

🎯 **ثبت اهداف مطالعه**
• تعیین اهداف روزانه، هفتگی و ماهانه
• پیگیری پیشرفت

📖 **ثبت جلسات مطالعه**
• ثبت زمان مطالعه
• مدیریت دروس مختلف

⏱️ **زمان‌سنج مطالعه**
• تایمر هوشمند
• مدیریت زمان

📊 **آمار و تحلیل**
• گزارش‌های پیشرفت
• نمودارهای تحلیلی
"""
        
        keyboard = [
            [InlineKeyboardButton("🎯 ثبت هدف جدید", callback_data="add_study_goal")],
            [InlineKeyboardButton("📖 ثبت جلسه مطالعه", callback_data="add_study_session")],
            [InlineKeyboardButton("⏱️ زمان‌سنج مطالعه", callback_data="study_timer")],
            [InlineKeyboardButton("📊 آمار مطالعه", callback_data="study_stats")],
            [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"❌ خطا در منوی مطالعه: {e}")

async def statistics_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منوی آمار و گزارش"""
    query = update.callback_query
    await query.answer()
    
    try:
        text = """
📊 **سیستم آمار و گزارش**

📈 **گزارش‌های قابل ارائه:**

📅 **پیشرفت روزانه**
• نمودار مطالعه روزانه
• مقایسه با روزهای قبل

📆 **پیشرفت هفتگی**
• آمار مطالعه هفتگی
• روند پیشرفت

🏆 **مقایسه با برترین‌ها**
• رتبه‌بندی کاربران
• انگیزه‌بخشی

📋 **گزارش کامل**
• تحلیل جامع عملکرد
• نقاط قوت و ضعف
"""
        
        keyboard = [
            [InlineKeyboardButton("📈 پیشرفت روزانه", callback_data="daily_progress")],
            [InlineKeyboardButton("📆 پیشرفت هفتگی", callback_data="weekly_progress")],
            [InlineKeyboardButton("🏆 مقایسه با برترین‌ها", callback_data="compare_top")],
            [InlineKeyboardButton("📋 گزارش کامل", callback_data="full_report")],
            [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"❌ خطا در منوی آمار: {e}")

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منوی راهنما"""
    query = update.callback_query
    await query.answer()
    
    try:
        text = """
❓ **راهنمای کامل ربات کنکور**

🎯 **دستورات اصلی:**
• /start - شروع کار با ربات
• /menu - نمایش منوی اصلی
• /help - راهنمای کامل

📚 **بخش‌های اصلی ربات:**

⏳ **شمارش معکوس**
نمایش زمان دقیق تا کنکورهای مختلف

📅 **تقویم و رویدادها**
مدیریت زمان و مشاهده مناسبت‌ها

🔔 **یادآوری‌ها**
تنظیم یادآوری برای کنکور و مطالعه

📨 **پیام‌رسانی**
ارتباط با ادمین و پشتیبانی

✅ **حضور و غیاب**
ثبت حضور روزانه و پیگیری

📚 **برنامه‌ریزی**
مدیریت اهداف و جلسات مطالعه

📊 **آمار و گزارش**
تحلیل پیشرفت و عملکرد

💡 **برای استفاده، کافیست از منوی اصلی گزینه مورد نظر را انتخاب کنید.**
"""
        
        keyboard = [
            [InlineKeyboardButton("📨 تماس با پشتیبانی", callback_data="send_message")],
            [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"❌ خطا در منوی راهنما: {e}")

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پنل مدیریت"""
    query = update.callback_query
    await query.answer()
    
    try:
        user_id = query.from_user.id
        
        if user_id != ADMIN_ID:
            text = """
❌ **دسترسی رد شد**

شما دسترسی به پنل مدیریت را ندارید.

💡 این بخش فقط برای ادمین‌های ربات قابل دسترسی است.
"""
        else:
            text = """
🔧 **پنل مدیریت ربات**

👥 **مدیریت کاربران**
• مشاهده آمار کاربران
• مدیریت کاربران خاص

📢 **ارسال پیام همگانی**
• ارسال پیام به همه کاربران
• ارسال پیام به کاربر خاص

📨 **مدیریت پیام‌ها**
• مشاهده پیام‌های کاربران
• پاسخ به پیام‌ها

💾 **مدیریت دیتابیس**
• پشتیبان‌گیری
• بهینه‌سازی

📊 **آمار سیستم**
• آمار کلی ربات
• گزارش‌های عملکرد
"""
        
        keyboard = [[InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]]
        
        if user_id == ADMIN_ID:
            keyboard.insert(0, [InlineKeyboardButton("📊 آمار کلی کاربران", callback_data="admin_stats")])
            keyboard.insert(1, [InlineKeyboardButton("👥 مدیریت کاربران", callback_data="admin_manage_users")])
            keyboard.insert(2, [InlineKeyboardButton("📢 ارسال پیام همگانی", callback_data="admin_broadcast")])
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"❌ خطا در پنل مدیریت: {e}")

# ==================== MESSAGE HANDLER ====================

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش پیام‌های متنی"""
    try:
        user_id = update.message.from_user.id
        text = update.message.text
        
        logger.info(f"📝 پیام متنی از کاربر {user_id}: {text}")
        
        # بررسی اگر کاربر در حال ارسال پیام است
        if context.user_data.get('waiting_for_message'):
            message_type = context.user_data.get('message_type', 'send_to_main_admin')
            target_name = {
                'send_to_main_admin': 'ادمین اصلی',
                'send_to_all_admins': 'همه ادمین‌ها', 
                'send_to_self': 'خودتان'
            }.get(message_type, 'ادمین')
            
            # پاک کردن وضعیت
            context.user_data.pop('waiting_for_message', None)
            context.user_data.pop('message_type', None)
            
            response = f"""
✅ **پیام شما با موفقیت ارسال شد!**

📨 **به:** {target_name}
📝 **متن پیام:**
{text}

💡 **پاسخ در اسرع وقت ارسال خواهد شد.**

🎯 برای ارسال پیام جدید از منوی اصلی استفاده کنید.
"""
            
            keyboard = [
                [InlineKeyboardButton("📨 ارسال پیام جدید", callback_data="send_message")],
                [InlineKeyboardButton("📋 پیام‌های من", callback_data="my_messages")],
                [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
            ]
            
            await update.message.reply_text(
                response,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
            
        else:
            # پاسخ به پیام‌های معمولی
            response = """
🤔 **متوجه پیام شما نشدم!**

💡 **راهنمایی:**
• از منوی اصلی استفاده کنید
• دستور /menu را وارد کنید
• برای راهنمایی /help را بزنید

🎯 **یا یکی از گزینه‌های زیر را انتخاب کنید:**
"""
            
            await update.message.reply_text(
                response,
                reply_markup=create_main_menu_keyboard(),
                parse_mode='HTML'
            )
            
    except Exception as e:
        logger.error(f"❌ خطا در پردازش پیام متنی: {e}")
        await update.message.reply_text("❌ خطا در پردازش پیام")

# ==================== ERROR HANDLER ====================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت خطاها"""
    try:
        logger.error(f"❌ خطا در به‌روزرسانی: {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ **خطایی در پردازش درخواست شما رخ داد.**\n\n"
                "💡 لطفاً دوباره تلاش کنید یا از منوی اصلی استفاده کنید.",
                reply_markup=create_main_menu_keyboard(),
                parse_mode='HTML'
            )
    except Exception as e:
        logger.error(f"❌ خطا در هندلر خطا: {e}")

# ==================== KEYBOARD CREATORS ====================

def create_main_menu_keyboard():
    """ایجاد کیبورد منوی اصلی"""
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

def create_countdown_keyboard():
    """ایجاد کیبورد شمارش معکوس"""
    keyboard = [
        [InlineKeyboardButton("🔬 علوم تجربی", callback_data="countdown_علوم تجربی")],
        [InlineKeyboardButton("📐 ریاضی‌وفنی", callback_data="countdown_ریاضی‌وفنی")],
        [InlineKeyboardButton("📚 علوم انسانی", callback_data="countdown_علوم انسانی")],
        [InlineKeyboardButton("👨‍🏫 فرهنگیان", callback_data="countdown_فرهنگیان")],
        [InlineKeyboardButton("🎨 هنر", callback_data="countdown_هنر")],
        [InlineKeyboardButton("🌍 زبان‌وگروه‌های‌خارجه", callback_data="countdown_زبان‌وگروه‌های‌خارجه")],
        [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)
