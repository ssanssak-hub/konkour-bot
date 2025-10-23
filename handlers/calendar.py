from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters
from database.operations import DatabaseOperations
import jdatetime
from datetime import datetime, timedelta

class PersianCalendar:
    def __init__(self):
        self.months_fa = [
            "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
            "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
        ]
        
        self.days_fa = ["ش", "ی", "د", "س", "چ", "پ", "ج"]
    
    def generate_calendar(self, year, month):
        """تولید تقویم برای ماه مشخص"""
        first_day = jdatetime.datetime(year, month, 1)
        days_in_month = jdatetime.j_days_in_month[month-1]
        
        # تنظیمات تقویم
        calendar_text = f"📅 تقویم {self.months_fa[month-1]} {year}\n\n"
        
        # هدر روزهای هفته
        calendar_text += " ".join(self.days_fa) + "\n"
        
        # روزهای ماه
        weekday = first_day.weekday()
        days = ["  " for _ in range(weekday+1)]
        
        for day in range(1, days_in_month + 1):
            days.append(f"{day:2d}")
        
        # چیدمان روزها در خطوط
        lines = []
        current_line = []
        
        for i, day in enumerate(days):
            current_line.append(day)
            if (i + 1) % 7 == 0:
                lines.append(" ".join(current_line))
                current_line = []
        
        if current_line:
            lines.append(" ".join(current_line))
        
        calendar_text += "\n".join(lines)
        return calendar_text
    
    def get_events_for_date(self, date_str):
        """دریافت رویدادها برای تاریخ مشخص"""
        # اینجا می‌توانید رویدادها را از دیتابیس بخوانید
        events = {
            "1405-01-01": "عید نوروز 🎉",
            "1405-01-02": "عید نوروز",
            "1405-01-03": "عید نوروز",
            "1405-01-04": "عید نوروز",
            "1405-01-12": "روز جمهوری اسلامی",
            "1405-01-13": "روز طبیعت",
            "1405-02-14": "رحلت امام خمینی",
            "1405-04-11": "کنکور ریاضی و انسانی",
            "1405-04-12": "کنکور تجربی، هنر و زبان",
            "1405-02-17": "کنکور فرهنگیان",
            "1405-02-18": "کنکور فرهنگیان"
        }
        
        return events.get(date_str, "هیچ رویدادی برای این تاریخ ثبت نشده است.")

async def calendar_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # تاریخ کنونی
    now = jdatetime.datetime.now()
    
    keyboard = [
        [InlineKeyboardButton("📅 تقویم جاری", callback_data="current_calendar")],
        [InlineKeyboardButton("📆 ماه بعد", callback_data="next_month")],
        [InlineKeyboardButton("📆 ماه قبل", callback_data="prev_month")],
        [InlineKeyboardButton("🔍 مشاهده رویدادهای تاریخ", callback_data="view_events")],
        [InlineKeyboardButton("➕ افزودن رویداد", callback_data="add_event")],
        [InlineKeyboardButton("🗑️ حذف رویداد", callback_data="delete_event")],
        [InlineKeyboardButton("🔄 بروزرسانی", callback_data="calendar")],
        [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    calendar = PersianCalendar()
    calendar_text = calendar.generate_calendar(now.year, now.month)
    
    full_text = (
        f"{calendar_text}\n\n"
        f"🕒 زمان دقیق سیستم: {now.strftime('%Y/%m/%d %H:%M:%S')}\n"
        f"📆 امروز: {now.strftime('%A')}\n\n"
        "برای مدیریت رویدادها از دکمه‌های زیر استفاده کنید:"
    )
    
    await query.edit_message_text(full_text, reply_markup=reply_markup)

async def show_current_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    now = jdatetime.datetime.now()
    context.user_data['current_calendar'] = {'year': now.year, 'month': now.month}
    
    calendar = PersianCalendar()
    calendar_text = calendar.generate_calendar(now.year, now.month)
    
    keyboard = [
        [InlineKeyboardButton("📆 ماه بعد", callback_data="next_month")],
        [InlineKeyboardButton("📆 ماه قبل", callback_data="prev_month")],
        [InlineKeyboardButton("🔍 مشاهده رویدادها", callback_data="view_events")],
        [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    full_text = (
        f"{calendar_text}\n\n"
        f"🕒 زمان دقیق: {now.strftime('%Y/%m/%d %H:%M:%S')}"
    )
    
    await query.edit_message_text(full_text, reply_markup=reply_markup)

async def next_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    current = context.user_data.get('current_calendar', {})
    year = current.get('year', jdatetime.datetime.now().year)
    month = current.get('month', jdatetime.datetime.now().month)
    
    month += 1
    if month > 12:
        month = 1
        year += 1
    
    context.user_data['current_calendar'] = {'year': year, 'month': month}
    
    calendar = PersianCalendar()
    calendar_text = calendar.generate_calendar(year, month)
    
    keyboard = [
        [InlineKeyboardButton("📆 ماه بعد", callback_data="next_month")],
        [InlineKeyboardButton("📆 ماه قبل", callback_data="prev_month")],
        [InlineKeyboardButton("📅 تقویم جاری", callback_data="current_calendar")],
        [InlineKeyboardButton("🔍 مشاهده رویدادها", callback_data="view_events")],
        [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    full_text = f"{calendar_text}\n\n📅 {calendar.months_fa[month-1]} {year}"
    
    await query.edit_message_text(full_text, reply_markup=reply_markup)

async def prev_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    current = context.user_data.get('current_calendar', {})
    year = current.get('year', jdatetime.datetime.now().year)
    month = current.get('month', jdatetime.datetime.now().month)
    
    month -= 1
    if month < 1:
        month = 12
        year -= 1
    
    context.user_data['current_calendar'] = {'year': year, 'month': month}
    
    calendar = PersianCalendar()
    calendar_text = calendar.generate_calendar(year, month)
    
    keyboard = [
        [InlineKeyboardButton("📆 ماه بعد", callback_data="next_month")],
        [InlineKeyboardButton("📆 ماه قبل", callback_data="prev_month")],
        [InlineKeyboardButton("📅 تقویم جاری", callback_data="current_calendar")],
        [InlineKeyboardButton("🔍 مشاهده رویدادها", callback_data="view_events")],
        [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    full_text = f"{calendar_text}\n\n📅 {calendar.months_fa[month-1]} {year}"
    
    await query.edit_message_text(full_text, reply_markup=reply_markup)

async def view_events_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    context.user_data['waiting_for_date'] = True
    
    await query.edit_message_text(
        "🔍 مشاهده رویدادهای تاریخ\n\n"
        "لطفاً تاریخ مورد نظر را به فرمت زیر وارد کنید:\n"
        "📅 مثال: 1405-01-01\n\n"
        "یا برای مشاهده رویدادهای امروز، دکمه زیر را بزنید:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📅 رویدادهای امروز", callback_data="today_events")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="calendar")]
        ])
    )

async def show_today_events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    today = jdatetime.datetime.now().strftime("%Y-%m-%d")
    calendar = PersianCalendar()
    events = calendar.get_events_for_date(today)
    
    keyboard = [
        [InlineKeyboardButton("🔍 تاریخ دیگر", callback_data="view_events")],
        [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"📅 رویدادهای امروز ({today}):\n\n{events}",
        reply_markup=reply_markup
    )

async def handle_date_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_for_date'):
        date_str = update.message.text
        
        # اعتبارسنجی تاریخ
        try:
            jdatetime.datetime.strptime(date_str, "%Y-%m-%d")
            
            calendar = PersianCalendar()
            events = calendar.get_events_for_date(date_str)
            
            # پاک کردن وضعیت
            context.user_data.pop('waiting_for_date', None)
            
            keyboard = [
                [InlineKeyboardButton("🔍 تاریخ دیگر", callback_data="view_events")],
                [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"📅 رویدادهای تاریخ {date_str}:\n\n{events}",
                reply_markup=reply_markup
            )
            
        except ValueError:
            await update.message.reply_text(
                "❌ فرمت تاریخ نامعتبر است!\n\n"
                "لطفاً تاریخ را به فرمت صحیح وارد کنید:\n"
                "📅 مثال: 1405-01-01"
            )

async def add_event_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    context.user_data['waiting_for_event_date'] = True
    
    await query.edit_message_text(
        "➕ افزودن رویداد جدید\n\n"
        "لطفاً تاریخ رویداد را به فرمت زیر وارد کنید:\n"
        "📅 مثال: 1405-01-01"
    )

async def handle_event_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_for_event_date'):
        date_str = update.message.text
        
        try:
            jdatetime.datetime.strptime(date_str, "%Y-%m-%d")
            context.user_data['event_date'] = date_str
            context.user_data['waiting_for_event_description'] = True
            context.user_data.pop('waiting_for_event_date', None)
            
            await update.message.reply_text(
                f"✅ تاریخ {date_str} ثبت شد.\n\n"
                "لطفاً توضیحات رویداد را وارد کنید:"
            )
            
        except ValueError:
            await update.message.reply_text(
                "❌ فرمت تاریخ نامعتبر است!\n\n"
                "لطفاً تاریخ را به فرمت صحیح وارد کنید:\n"
                "📅 مثال: 1405-01-01"
            )

def setup_calendar_handlers(application):
    application.add_handler(CallbackQueryHandler(calendar_menu, pattern="^calendar$"))
    application.add_handler(CallbackQueryHandler(show_current_calendar, pattern="^current_calendar$"))
    application.add_handler(CallbackQueryHandler(next_month, pattern="^next_month$"))
    application.add_handler(CallbackQueryHandler(prev_month, pattern="^prev_month$"))
    application.add_handler(CallbackQueryHandler(view_events_menu, pattern="^view_events$"))
    application.add_handler(CallbackQueryHandler(show_today_events, pattern="^today_events$"))
    application.add_handler(CallbackQueryHandler(add_event_menu, pattern="^add_event$"))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_date_input), group=5)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_event_date), group=6)
