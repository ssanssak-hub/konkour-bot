"""
کیبوردهای ساده سیستم ریمایندر
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

def create_reminder_main_menu():
    """منوی اصلی ریمایندر"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⏰ یادآوری کنکورها")],
            [KeyboardButton(text="📝 یادآوری شخصی")],
            [KeyboardButton(text="🤖 یادآوری خودکار")],
            [KeyboardButton(text="📋 مدیریت یادآوری")],
            [KeyboardButton(text="🏠 منوی اصلی")]
        ],
        resize_keyboard=True,
        input_field_placeholder="گزینه مورد نظر را انتخاب کنید..."
    )

def create_exam_selection_menu():
    """منوی انتخاب کنکورها"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎯 علوم انسانی"), KeyboardButton(text="📐 ریاضی و فنی")],
            [KeyboardButton(text="🔬 علوم تجربی"), KeyboardButton(text="🎨 هنر")],
            [KeyboardButton(text="🔠 زبان خارجه"), KeyboardButton(text="👨‍🏫 فرهنگیان")],
            [KeyboardButton(text="✅ انتخاب همه"), KeyboardButton(text="➡️ ادامه")],
            [KeyboardButton(text="🔙 بازگشت")]
        ],
        resize_keyboard=True
    )

def create_days_selection_menu():
    """منوی انتخاب روزهای هفته"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="شنبه"), KeyboardButton(text="یکشنبه")],
            [KeyboardButton(text="دوشنبه"), KeyboardButton(text="سه‌شنبه")],
            [KeyboardButton(text="چهارشنبه"), KeyboardButton(text="پنجشنبه")],
            [KeyboardButton(text="جمعه"), KeyboardButton(text="✅ همه روزها")],
            [KeyboardButton(text="🗑️ پاک کردن"), KeyboardButton(text="➡️ ادامه")],
            [KeyboardButton(text="🔙 بازگشت")]
        ],
        resize_keyboard=True
    )

def create_time_input_menu():
    """منوی ورود ساعت دلخواه"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔙 بازگشت")]
        ],
        resize_keyboard=True
    )

def create_date_input_menu():
    """منوی ورود تاریخ"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📅 امروز")],
            [KeyboardButton(text="🔙 بازگشت")]
        ],
        resize_keyboard=True
    )

def create_repetition_type_menu():
    """منوی انتخاب نوع تکرار"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔘 یکبار")],
            [KeyboardButton(text="🔄 روزانه")],
            [KeyboardButton(text="📅 هفتگی")],
            [KeyboardButton(text="🗓️ ماهانه")],
            [KeyboardButton(text="⚙️ سفارشی")],
            [KeyboardButton(text="🔙 بازگشت")]
        ],
        resize_keyboard=True
    )

def create_confirmation_menu():
    """منوی تأیید نهایی"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ تأیید و ایجاد")],
            [KeyboardButton(text="✏️ ویرایش")],
            [KeyboardButton(text="❌ لغو")],
            [KeyboardButton(text="🔙 بازگشت")]
        ],
        resize_keyboard=True
    )

def create_management_menu():
    """منوی مدیریت یادآوری"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 مشاهده همه")],
            [KeyboardButton(text="✏️ ویرایش"), KeyboardButton(text="🗑️ حذف")],
            [KeyboardButton(text="🔔 فعال"), KeyboardButton(text="🔕 غیرفعال")],
            [KeyboardButton(text="📊 آمار")],
            [KeyboardButton(text="🔙 بازگشت")]
        ],
        resize_keyboard=True
    )

def create_auto_reminders_menu():
    """منوی یادآوری خودکار"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 لیست یادآوری‌ها")],
            [KeyboardButton(text="✅ فعال کردن"), KeyboardButton(text="❌ غیرفعال کردن")],
            [KeyboardButton(text="🔙 بازگشت")]
        ],
        resize_keyboard=True
    )

def create_auto_reminders_admin_menu():
    """منوی مدیریت ریمایندرهای خودکار برای ادمین"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 لیست ریمایندرها")],
            [KeyboardButton(text="➕ افزودن جدید")],
            [KeyboardButton(text="✏️ ویرایش"), KeyboardButton(text="🗑️ حذف")],
            [KeyboardButton(text="✅ فعال کردن"), KeyboardButton(text="❌ غیرفعال کردن")],
            [KeyboardButton(text="🔙 بازگشت")]
        ],
        resize_keyboard=True
    )

def create_auto_reminders_user_menu():
    """منوی ریمایندرهای خودکار برای کاربران عادی"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 لیست ریمایندرها")],
            [KeyboardButton(text="✅ فعال کردن"), KeyboardButton(text="❌ غیرفعال کردن")],
            [KeyboardButton(text="🔙 بازگشت")]
        ],
        resize_keyboard=True
    )

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
