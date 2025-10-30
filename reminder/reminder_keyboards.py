"""
کیبوردهای ساده (غیر شیشه‌ای) سیستم ریمایندر
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

def create_reminder_main_menu():
    """منوی اصلی ریمایندر با کیبورد ساده"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⏰ یادآوری کنکورها")],
            [KeyboardButton(text="📝 یادآوری شخصی")],
            [KeyboardButton(text="🤖 یادآوری خودکار")],
            [KeyboardButton(text="📊 مدیریت یادآوری‌ها")],
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

def create_time_selection_menu():
    """منوی انتخاب ساعات"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="۸:۰۰"), KeyboardButton(text="۱۰:۰۰")],
            [KeyboardButton(text="۱۲:۰۰"), KeyboardButton(text="۱۴:۰۰")],
            [KeyboardButton(text="۱۶:۰۰"), KeyboardButton(text="۱۸:۰۰")],
            [KeyboardButton(text="۲۰:۰۰"), KeyboardButton(text="۲۲:۰۰")],
            [KeyboardButton(text="✏️ ساعت دلخواه"), KeyboardButton(text="✅ انتخاب همه")],
            [KeyboardButton(text="🗑️ پاک کردن"), KeyboardButton(text="➡️ ادامه")],
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
    """منوی مدیریت ریمایندرها"""
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
