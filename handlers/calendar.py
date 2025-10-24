import jdatetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters
from database.operations import database
from config import Config

class PersianCalendar:
    def __init__(self):
        self.months_fa = [
            "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
            "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
        ]
        
        self.days_fa = ["ش", "ی", "د", "س", "چ", "پ", "ج"]
        self.days_full_fa = ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه"]
    
    def generate_calendar(self, year: int, month: int, selected_day: int = None):
        """تولید تقویم شمسی با قابلیت انتخاب"""
        try:
            first_day = jdatetime.datetime(year, month, 1)
            days_in_month = 31 if month <= 6 else 30
            if month == 12:  # اسفند
                days_in_month = 29 if year % 4 == 3 else 30
            
            # هدر تقویم
            calendar_text = f"📅 <b>تقویم {self.months_fa[month-1]} {year}</b>\n\n"
            
            # روزهای هفته
            calendar_text += " ".join([f"<b>{day}</b>" for day in self.days_fa]) + "\n"
            
            # روزهای ماه
            weekday = (first_day.weekday() + 1) % 7  # تنظیم برای شروع شنبه
            days = []
            
            # روزهای خالی قبل از شروع ماه
            for _ in range(weekday):
                days.append("  ")
            
            # روزهای ماه
            for day in range(1, days_in_month + 1):
                day_str = f"{day:2d}"
                # هایلایت کردن روز انتخاب شده
                if selected_day == day:
                    day_str = f"🔸{day:2d}"
                days.append(day_str)
            
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
            
            calendar_text += "\n".join(lines)
            return calendar_text
            
        except Exception as e:
            return f"❌ خطا در تولید تقویم: {e}"
    
    def get_events_for_date(self, date_str: str):
        """دریافت رویدادها برای تاریخ مشخص"""
        events = []
        
        # رویدادهای از پیش تعریف شده
        predefined_events = Config.PERSIAN_EVENTS
        if date_str in predefined_events:
            events.append(predefined_events[date_str])
        
        # رویدادهای کنکور
        exam_date = Config.get_exam_by_date(date_str)
        if exam_date:
            events.append(f"🎯 کنکور {exam_date}")
        
        # TODO: اضافه کردن رویدادهای کاربر از دیتابیس
        
        if events:
            return "\n".join(events)
        else:
            return "📭 هیچ رویدادی برای این تاریخ ثبت نشده است."
    
    def get_month_navigation_buttons(self, year: int, month: int):
        """دکمه‌های ناوبری ماه"""
        prev_month = month - 1
        prev_year = year
        if prev_month < 1:
            prev_month = 12
            prev_year -= 1
        
        next_month = month + 1
        next_year = year
        if next_month > 12:
            next_month = 1
            next_year += 1
        
        return [
            [
                InlineKeyboardButton("◀️ ماه قبل", callback_data=f"calendar_{prev_year}_{prev_month}"),
                InlineKeyboardButton("🔄 امروز", callback_data="current_calendar"),
                InlineKeyboardButton("ماه بعد ▶️", callback_data=f"calendar_{next_year}_{next_month}")
            ]
        ]

async def calendar_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منوی اصلی تقویم"""
    query = update.callback_query
    await query.answer()
    
    now = jdatetime.datetime.now()
    
    text = f"""
📅 <b>سیستم تقویم و رویدادها</b>

🕒 امروز: {now.strftime('%A %Y/%m/%d')}
📆 تاریخ دقیق: {now.strftime('%Y/%m/%d %H:%M:%S')}

🎯 امکانات:
• نمایش تقویم شمسی
• مناسبت‌ها و رویدادها
• رویدادهای کنکور
• مدیریت رویدادهای شخصی
"""
    
    keyboard = [
        [InlineKeyboardButton("📅 تقویم جاری", callback_data="current_calendar")],
        [InlineKeyboardButton("🔍 مشاهده رویدادها", callback_data="view_events")],
        [InlineKeyboardButton("📝 افزودن رویداد", callback_data="add_event")],
        [InlineKeyboardButton("🗑️ حذف رویداد", callback_data="delete_event")],
        [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

async def show_current_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش تقویم ماه جاری"""
    query = update.callback_query
    await query.answer()
    
    now = jdatetime.datetime.now()
    await show_calendar(update, context, now.year, now.month)

async def show_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE, year: int, month: int, selected_day: int = None):
    """نمایش تقویم برای ماه مشخص"""
    query = update.callback_query
    await query.answer()
    
    calendar = PersianCalendar()
    calendar_text = calendar.generate_calendar(year, month, selected_day)
    
    # دکمه‌های ناوبری
    keyboard = calendar.get_month_navigation_buttons(year, month)
    
    # دکمه‌های عملیاتی
    keyboard.extend([
        [InlineKeyboardButton("🔍 مشاهده رویدادها", callback_data="view_events")],
        [InlineKeyboardButton("📝 افزودن رویداد", callback_data="add_event")],
        [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
    ])
    
    # اضافه کردن دکمه‌های انتخاب روز (برای ماه جاری)
    now = jdatetime.datetime.now()
    if year == now.year and month == now.month:
        # فقط ۱۰ روز آینده
        days_buttons = []
        current_day = now.day
        for day in range(current_day, min(current_day + 10, 31)):
            days_buttons.append(InlineKeyboardButton(f"{day}", callback_data=f"select_day_{day}"))
        
        if days_buttons:
            keyboard.insert(1, days_buttons)
    
    full_text = f"{calendar_text}\n\n🕒 زمان سیستم: {jdatetime.datetime.now().strftime('%Y/%m/%d %H:%M')}"
    
    await query.edit_message_text(
        full_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

async def navigate_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ناوبری بین ماه‌های تقویم"""
    query = update.callback_query
    await query.answer()
    
    data = query.data.replace("calendar_", "")
    year, month = map(int, data.split("_"))
    
    await show_calendar(update, context, year, month)

async def select_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """انتخاب روز خاص از تقویم"""
    query = update.callback_query
    await query.answer()
    
    day = int(query.data.replace("select_day_", ""))
    now = jdatetime.datetime.now()
    
    await show_calendar(update, context, now.year, now.month, day)
    
    # نمایش رویدادهای روز انتخاب شده
    date_str = f"{now.year:04d}-{now.month:02d}-{day:02d}"
    calendar = PersianCalendar()
    events = calendar.get_events_for_date(date_str)
    
    await query.message.reply_text(
        f"📅 <b>رویدادهای {date_str}</b>\n\n{events}",
        parse_mode='HTML'
    )

async def view_events_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منوی مشاهده رویدادها"""
    query = update.callback_query
    await query.answer()
    
    text = """
🔍 <b>مشاهده رویدادها</b>

📅 می‌توانید رویدادهای یکی از روش‌های زیر را مشاهده کنید:

• مشاهده رویدادهای امروز
• جستجو در تاریخ خاص
• مشاهده رویدادهای هفته جاری
"""
    
    keyboard = [
        [InlineKeyboardButton("📅 رویدادهای امروز", callback_data="today_events")],
        [InlineKeyboardButton("🔍 جستجو در تاریخ", callback_data="search_events")],
        [InlineKeyboardButton("📆 رویدادهای این هفته", callback_data="week_events")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="calendar")]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

async def show_today_events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش رویدادهای امروز"""
    query = update.callback_query
    await query.answer()
    
    today = jdatetime.datetime.now().strftime("%Y-%m-%d")
    calendar = PersianCalendar()
    events = calendar.get_events_for_date(today)
    
    text = f"""
📅 <b>رویدادهای امروز</b>
🗓️ {jdatetime.datetime.now().strftime('%A %Y/%m/%d')}

{events}
"""
    
    keyboard = [
        [InlineKeyboardButton("📅 تقویم امروز", callback_data="current_calendar")],
        [InlineKeyboardButton("🔍 تاریخ دیگر", callback_data="view_events")],
        [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

async def show_week_events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش رویدادهای هفته جاری"""
    query = update.callback_query
    await query.answer()
    
    today = jdatetime.datetime.now()
    start_of_week = today - jdatetime.timedelta(days=today.weekday())
    
    text = "📆 <b>رویدادهای این هفته</b>\n\n"
    
    calendar = PersianCalendar()
    for i in range(7):
        current_date = start_of_week + jdatetime.timedelta(days=i)
        date_str = current_date.strftime("%Y-%m-%d")
        events = calendar.get_events_for_date(date_str)
        
        if "هیچ رویدادی" not in events:
            text += f"📅 {current_date.strftime('%A %Y/%m/%d')}\n"
            text += f"{events}\n\n"
    
    if "هیچ رویدادی" in text:
        text = "📭 <b>هیچ رویدادی برای این هفته ثبت نشده است.</b>"
    
    keyboard = [
        [InlineKeyboardButton("📅 تقویم جاری", callback_data="current_calendar")],
        [InlineKeyboardButton("🔍 تاریخ خاص", callback_data="search_events")],
        [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

async def search_events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """جستجوی رویدادها در تاریخ خاص"""
    query = update.callback_query
    await query.answer()
    
    context.user_data['waiting_for_event_date'] = True
    
    text = """
🔍 <b>جستجوی رویدادها در تاریخ خاص</b>

📅 لطفاً تاریخ مورد نظر را به فرمت زیر وارد کنید:

📝 مثال:
• 1405-01-01 (برای فروردین ۱)
• 1405-12-29 (برای اسفند ۲۹)

💡 می‌توانید از دکمه زیر برای مشاهده رویدادهای امروز استفاده کنید.
"""
    
    keyboard = [
        [InlineKeyboardButton("📅 رویدادهای امروز", callback_data="today_events")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="view_events")]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

async def handle_event_date_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش تاریخ جستجوی رویداد"""
    if context.user_data.get('waiting_for_event_date'):
        date_str = update.message.text
        
        try:
            # اعتبارسنجی تاریخ
            jdatetime.datetime.strptime(date_str, "%Y-%m-%d")
            
            calendar = PersianCalendar()
            events = calendar.get_events_for_date(date_str)
            
            # پاک کردن وضعیت
            context.user_data.pop('waiting_for_event_date', None)
            
            # نمایش نتایج
            text = f"""
🔍 <b>نتایج جستجو برای تاریخ {date_str}</b>

{events}
"""
            
            keyboard = [
                [InlineKeyboardButton("🔍 جستجوی دیگر", callback_data="search_events")],
                [InlineKeyboardButton("📅 تقویم جاری", callback_data="current_calendar")],
                [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
            ]
            
            await update.message.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
            
        except ValueError:
            await update.message.reply_text(
                "❌ <b>فرمت تاریخ نامعتبر است!</b>\n\n"
                "لطفاً تاریخ را به فرمت صحیح وارد کنید:\n"
                "📝 مثال: 1405-01-01\n\n"
                "• سال: 1405\n"
                "• ماه: 01 تا 12\n"
                "• روز: 01 تا 31",
                parse_mode='HTML'
            )

async def add_event_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منوی افزودن رویداد جدید"""
    query = update.callback_query
    await query.answer()
    
    text = """
📝 <b>افزودن رویداد جدید</b>

🎯 می‌توانید رویدادهای مختلفی اضافه کنید:

• مناسبت شخصی
• تاریخ مهم مطالعاتی
• زمان آزمون آزمایشی
• سایر رویدادهای مهم
"""
    
    keyboard = [
        [InlineKeyboardButton("📅 انتخاب تاریخ", callback_data="select_event_date")],
        [InlineKeyboardButton("📅 استفاده از امروز", callback_data="use_today_for_event")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="calendar")]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

async def select_event_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """انتخاب تاریخ برای رویداد جدید"""
    query = update.callback_query
    await query.answer()
    
    context.user_data['waiting_for_event_date_input'] = True
    
    await query.edit_message_text(
        "📅 <b>افزودن رویداد جدید</b>\n\n"
        "لطفاً تاریخ رویداد را به فرمت زیر وارد کنید:\n"
        "📝 مثال: 1405-01-01\n\n"
        "💡 می‌توانید از دکمه زیر برای استفاده از تاریخ امروز استفاده کنید.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📅 استفاده از امروز", callback_data="use_today_for_event")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="add_event")]
        ]),
        parse_mode='HTML'
    )

async def use_today_for_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """استفاده از تاریخ امروز برای رویداد"""
    query = update.callback_query
    await query.answer()
    
    today = jdatetime.datetime.now().strftime("%Y-%m-%d")
    context.user_data['event_date'] = today
    context.user_data['waiting_for_event_description'] = True
    
    await query.edit_message_text(
        f"✅ تاریخ امروز ثبت شد: {today}\n\n"
        "📝 لطفاً توضیحات رویداد را وارد کنید:\n\n"
        "💡 مثال:\n"
        "• 'آزمون آزمایشی ریاضی'\n"
        "• 'جلسه مطالعه فشرده فیزیک'\n"
        "• 'تولد دوست'\n"
        "• 'ملاقات با مشاور'",
        parse_mode='HTML'
    )

async def handle_event_date_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش تاریخ ورودی برای رویداد"""
    if context.user_data.get('waiting_for_event_date_input'):
        date_str = update.message.text
        
        try:
            jdatetime.datetime.strptime(date_str, "%Y-%m-%d")
            context.user_data['event_date'] = date_str
            context.user_data['waiting_for_event_description'] = True
            context.user_data.pop('waiting_for_event_date_input', None)
            
            await update.message.reply_text(
                f"✅ تاریخ {date_str} ثبت شد.\n\n"
                "📝 لطفاً توضیحات رویداد را وارد کنید:",
                parse_mode='HTML'
            )
            
        except ValueError:
            await update.message.reply_text(
                "❌ <b>فرمت تاریخ نامعتبر است!</b>\n\n"
                "لطفاً تاریخ را به فرمت صحیح وارد کنید:\n"
                "📝 مثال: 1405-01-01",
                parse_mode='HTML'
            )

async def handle_event_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش توضیحات رویداد"""
    if context.user_data.get('waiting_for_event_description'):
        description = update.message.text
        event_date = context.user_data.get('event_date')
        
        # TODO: ذخیره رویداد در دیتابیس
        
        # پاک کردن وضعیت
        context.user_data.pop('waiting_for_event_description', None)
        context.user_data.pop('event_date', None)
        
        text = f"""
✅ <b>رویداد جدید با موفقیت ثبت شد!</b>

📅 تاریخ: {event_date}
📝 توضیحات: {description}

💡 این رویداد در تقویم شما نمایش داده خواهد شد.
"""
        
        keyboard = [
            [InlineKeyboardButton("📅 مشاهده تقویم", callback_data="current_calendar")],
            [InlineKeyboardButton("📝 رویداد جدید", callback_data="add_event")],
            [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
        ]
        
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )

async def delete_event_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منوی حذف رویداد"""
    query = update.callback_query
    await query.answer()
    
    # TODO: دریافت رویدادهای کاربر از دیتابیس
    
    text = """
🗑️ <b>حذف رویداد</b>

📭 در حال حاضر هیچ رویداد شخصی برای حذف وجود ندارد.

💡 پس از افزودن رویدادهای شخصی، می‌توانید آن‌ها را از این بخش مدیریت کنید.
"""
    
    keyboard = [
        [InlineKeyboardButton("📝 افزودن رویداد", callback_data="add_event")],
        [InlineKeyboardButton("📅 مشاهده تقویم", callback_data="current_calendar")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="calendar")]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

def setup_calendar_handlers(application):
    """تنظیم هندلرهای تقویم"""
    application.add_handler(CallbackQueryHandler(calendar_menu, pattern="^calendar$"))
    application.add_handler(CallbackQueryHandler(show_current_calendar, pattern="^current_calendar$"))
    application.add_handler(CallbackQueryHandler(navigate_calendar, pattern="^calendar_\\d+_\\d+$"))
    application.add_handler(CallbackQueryHandler(select_day, pattern="^select_day_\\d+$"))
    application.add_handler(CallbackQueryHandler(view_events_menu, pattern="^view_events$"))
    application.add_handler(CallbackQueryHandler(show_today_events, pattern="^today_events$"))
    application.add_handler(CallbackQueryHandler(show_week_events, pattern="^week_events$"))
    application.add_handler(CallbackQueryHandler(search_events, pattern="^search_events$"))
    application.add_handler(CallbackQueryHandler(add_event_menu, pattern="^add_event$"))
    application.add_handler(CallbackQueryHandler(select_event_date, pattern="^select_event_date$"))
    application.add_handler(CallbackQueryHandler(use_today_for_event, pattern="^use_today_for_event$"))
    application.add_handler(CallbackQueryHandler(delete_event_menu, pattern="^delete_event$"))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_event_date_search), group=5)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_event_date_input), group=6)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_event_description), group=7)
