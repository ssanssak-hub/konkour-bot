"""
کیبوردهای تخصصی سیستم ریمایندر
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def create_reminder_main_menu():
    """منوی اصلی ریمایندر"""
    builder = InlineKeyboardBuilder()
    
    menu_items = [
        ("⏰ یادآوری کنکورها", "reminder_type:exam"),
        ("📝 یادآوری شخصی", "reminder_type:personal"),
        ("🤖 یادآوری خودکار", "reminder_type:auto"),
        ("📊 مدیریت یادآوری‌ها", "reminder_type:manage"),
        ("🏠 منوی اصلی", "main:back")
    ]
    
    for text, callback_data in menu_items:
        builder.button(text=text, callback_data=callback_data)
    
    builder.adjust(1)
    return builder.as_markup()

def create_days_of_week_keyboard(selected_days=None):
    """کیبورد انتخاب روزهای هفته"""
    if selected_days is None:
        selected_days = []
    
    days = [
        ("شنبه", 0),
        ("یکشنبه", 1), 
        ("دوشنبه", 2),
        ("سه‌شنبه", 3),
        ("چهارشنبه", 4),
        ("پنجشنبه", 5),
        ("جمعه", 6)
    ]
    
    builder = InlineKeyboardBuilder()
    
    # ردیف اول: روزهای هفته
    for day_name, day_index in days:
        emoji = "✅" if day_index in selected_days else "◻️"
        builder.button(
            text=f"{emoji} {day_name}", 
            callback_data=f"reminder_day:{day_index}"
        )
    
    builder.adjust(2)
    
    # ردیف دوم: دکمه‌های عملیاتی
    builder.row(
        InlineKeyboardButton(
            text="✅ انتخاب همه روزها" if len(selected_days) < 7 else "🗑️ لغو همه",
            callback_data="reminder_days:all"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="🗑️ پاک کردن", 
            callback_data="reminder_days:clear"
        ),
        InlineKeyboardButton(
            text="➡️ ادامه", 
            callback_data="reminder_days:continue"
        )
    )
    
    return builder.as_markup()

def create_time_selection_keyboard(selected_times=None):
    """کیبورد انتخاب ساعات روز"""
    if selected_times is None:
        selected_times = []
    
    times = [
        "۰۸:۰۰", "۱۰:۰۰", "۱۲:۰۰", "۱۴:۰۰",
        "۱۶:۰۰", "۱۸:۰۰", "۲۰:۰۰", "۲۲:۰۰"
    ]
    
    builder = InlineKeyboardBuilder()
    
    # ساعات پیش‌فرض
    for time in times:
        emoji = "✅" if time in selected_times else "⏰"
        builder.button(
            text=f"{emoji} {time}", 
            callback_data=f"reminder_time:{time}"
        )
    
    builder.adjust(2)
    
    # دکمه‌های اضافی
    builder.row(
        InlineKeyboardButton(
            text="✏️ ساعت دلخواه", 
            callback_data="reminder_time:custom"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="✅ انتخاب همه" if len(selected_times) < len(times) else "🗑️ لغو همه",
            callback_data="reminder_times:all"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="🗑️ پاک کردن", 
            callback_data="reminder_times:clear"
        ),
        InlineKeyboardButton(
            text="➡️ ادامه", 
            callback_data="reminder_times:continue"
        )
    )
    
    return builder.as_markup()

def create_exam_selection_keyboard(selected_exams=None):
    """کیبورد انتخاب کنکورها"""
    if selected_exams is None:
        selected_exams = []
    
    exams = [
        ("🎯 علوم انسانی", "علوم_انسانی"),
        ("📐 ریاضی و فنی", "ریاضی_فنی"),
        ("🔬 علوم تجربی", "علوم_تجربی"),
        ("🎨 هنر", "هنر"),
        ("🔠 زبان خارجه", "زبان_خارجه"),
        ("👨‍🏫 فرهنگیان", "فرهنگیان")
    ]
    
    builder = InlineKeyboardBuilder()
    
    for exam_name, exam_key in exams:
        emoji = "✅" if exam_key in selected_exams else "◻️"
        builder.button(
            text=f"{emoji} {exam_name}",
            callback_data=f"reminder_exam:{exam_key}"
        )
    
    builder.adjust(1)
    
    builder.row(
        InlineKeyboardButton(
            text="✅ انتخاب همه" if len(selected_exams) < len(exams) else "🗑️ لغو همه",
            callback_data="reminder_exams:all"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="➡️ ادامه", 
            callback_data="reminder_exams:continue"
        )
    )
    
    return builder.as_markup()

def create_repetition_type_keyboard():
    """کیبورد انتخاب نوع تکرار"""
    builder = InlineKeyboardBuilder()
    
    types = [
        ("🔘 یکبار", "once"),
        ("🔄 روزانه", "daily"), 
        ("📅 هفتگی", "weekly"),
        ("🗓️ ماهانه", "monthly"),
        ("⚙️ سفارشی", "custom")
    ]
    
    for text, callback_data in types:
        builder.button(
            text=text,
            callback_data=f"reminder_repeat:{callback_data}"
        )
    
    builder.adjust(1)
    return builder.as_markup()

def create_confirmation_keyboard():
    """کیبورد تأیید نهایی"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="✅ تأیید و ایجاد", 
            callback_data="reminder_confirm:create"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="✏️ ویرایش", 
            callback_data="reminder_confirm:edit"
        ),
        InlineKeyboardButton(
            text="❌ لغو", 
            callback_data="reminder_confirm:cancel"
        )
    )
    
    return builder.as_markup()

def create_management_keyboard():
    """کیبورد مدیریت ریمایندرها"""
    builder = InlineKeyboardBuilder()
    
    actions = [
        ("📋 مشاهده همه", "reminder_manage:list"),
        ("✏️ ویرایش", "reminder_manage:edit"),
        ("🗑️ حذف", "reminder_manage:delete"),
        ("🔔 فعال/غیرفعال", "reminder_manage:toggle"),
        ("📊 آمار", "reminder_manage:stats")
    ]
    
    for text, callback_data in actions:
        builder.button(text=text, callback_data=callback_data)
    
    builder.adjust(2)
    
    builder.row(
        InlineKeyboardButton(
            text="🏠 منوی اصلی", 
            callback_data="reminder_manage:back"
        )
    )
    
    return builder.as_markup()
