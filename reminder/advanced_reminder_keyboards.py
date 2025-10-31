"""
کیبوردهای مخصوص ریمایندرهای پیشرفته ادمین
"""
from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
    ReplyKeyboardRemove
)

def create_advanced_reminder_admin_menu():
    """منوی مدیریت ریمایندرهای پیشرفته برای ادمین"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 لیست ریمایندرهای پیشرفته")],
            [KeyboardButton(text="➕ افزودن ریمایندر جدید")],
            [KeyboardButton(text="✏️ ویرایش ریمایندر")],
            [KeyboardButton(text="🗑️ حذف ریمایندر")],
            [KeyboardButton(text="🔔 فعال/غیرفعال")],
            [KeyboardButton(text="🔙 بازگشت به مدیریت")]
        ],
        resize_keyboard=True,
        input_field_placeholder="گزینه مورد نظر را انتخاب کنید..."
    )

def create_start_time_menu():
    """منوی انتخاب ساعت شروع"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⏰ همین الان")],
            [KeyboardButton(text="🔙 بازگشت")]
        ],
        resize_keyboard=True
    )

def create_start_date_menu():
    """منوی انتخاب تاریخ شروع"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📅 امروز")],
            [KeyboardButton(text="🔙 بازگشت")]
        ],
        resize_keyboard=True
    )

def create_end_time_menu():
    """منوی انتخاب ساعت پایان"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⏰ بدون پایان")],
            [KeyboardButton(text="🔙 بازگشت")]
        ],
        resize_keyboard=True
    )

def create_end_date_menu():
    """منوی انتخاب تاریخ پایان"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📅 بدون تاریخ پایان")],
            [KeyboardButton(text="🔙 بازگشت")]
        ],
        resize_keyboard=True
    )

def create_days_of_week_menu(selected_days=None):
    """منوی انتخاب روزهای هفته"""
    if selected_days is None:
        selected_days = []
    
    days = [
        ("شنبه", 0), ("یکشنبه", 1), ("دوشنبه", 2),
        ("سه‌شنبه", 3), ("چهارشنبه", 4), ("پنجشنبه", 5), ("جمعه", 6)
    ]
    
    keyboard = []
    row = []
    
    for day_name, day_num in days:
        emoji = "✅" if day_num in selected_days else "⚪"
        row.append(KeyboardButton(text=f"{emoji} {day_name}"))
        
        if len(row) == 2:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    keyboard.append([KeyboardButton(text="✅ همه روزها")])
    keyboard.append([KeyboardButton(text="🗑️ پاک کردن همه")])
    keyboard.append([KeyboardButton(text="➡️ ادامه")])
    keyboard.append([KeyboardButton(text="🔙 بازگشت")])
    
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def create_repeat_count_menu():
    """منوی انتخاب تعداد تکرار"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="0"), KeyboardButton(text="1"), KeyboardButton(text="2")],
            [KeyboardButton(text="3"), KeyboardButton(text="4"), KeyboardButton(text="5")],
            [KeyboardButton(text="6"), KeyboardButton(text="7"), KeyboardButton(text="8")],
            [KeyboardButton(text="9"), KeyboardButton(text="10")],
            [KeyboardButton(text="🔙 بازگشت")]
        ],
        resize_keyboard=True
    )

def create_repeat_interval_menu():
    """منوی انتخاب فاصله زمانی"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="10"), KeyboardButton(text="20"), KeyboardButton(text="30")],
            [KeyboardButton(text="40"), KeyboardButton(text="50"), KeyboardButton(text="60")],
            [KeyboardButton(text="🔙 بازگشت")]
        ],
        resize_keyboard=True
    )

def create_confirmation_menu():
    """منوی تأیید نهایی"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ تأیید و ایجاد")],
            [KeyboardButton(text="✏️ ویرایش اطلاعات")],
            [KeyboardButton(text="❌ لغو")],
            [KeyboardButton(text="🔙 بازگشت")]
        ],
        resize_keyboard=True
    )

def create_advanced_reminder_list_keyboard(reminders):
    """کیبورد اینلاین برای لیست ریمایندرهای پیشرفته"""
    keyboard = []
    
    for reminder in reminders:
        status_emoji = "✅" if reminder['is_active'] else "❌"
        keyboard.append([
            InlineKeyboardButton(
                text=f"{status_emoji} {reminder['title']}",
                callback_data=f"adv_reminder:{reminder['id']}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton(text="🔙 بازگشت", callback_data="adv_admin:back")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def create_advanced_reminder_actions_keyboard(reminder_id):
    """کیبورد اینلاین برای اقدامات روی ریمایندر"""
    keyboard = [
        [
            InlineKeyboardButton(text="✏️ ویرایش", callback_data=f"adv_edit:{reminder_id}"),
            InlineKeyboardButton(text="🗑️ حذف", callback_data=f"adv_delete:{reminder_id}")
        ],
        [
            InlineKeyboardButton(text="🔔 فعال/غیرفعال", callback_data=f"adv_toggle:{reminder_id}"),
            InlineKeyboardButton(text="📊 آمار", callback_data=f"adv_stats:{reminder_id}")
        ],
        [
            InlineKeyboardButton(text="🔙 بازگشت", callback_data="adv_admin:back")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def create_back_only_menu():
    """فقط دکمه بازگشت"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔙 بازگشت")]
        ],
        resize_keyboard=True
    )

def remove_menu():
    """حذف منو"""
    return ReplyKeyboardRemove()
