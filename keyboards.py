from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
    ReplyKeyboardRemove
)
from exam_data import EXAMS_1405

# منوی اصلی با کیبورد معمولی
def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⏳ زمان‌سنجی کنکورها")],
            [KeyboardButton(text="📅 برنامه مطالعاتی پیشرفته")],
            [KeyboardButton(text="📊 آمار مطالعه حرفه‌ای")],
            [KeyboardButton(text="👑 پنل مدیریت")]
        ],
        resize_keyboard=True,
        input_field_placeholder="یک گزینه انتخاب کنید..."
    )

# حذف منو
def remove_menu():
    return ReplyKeyboardRemove()

# منوی آزمون‌ها به‌صورت داینامیک
def exams_menu():
    keyboard = []
    keys = list(EXAMS_1405.keys())
    
    for i in range(0, len(keys), 2):
        row = []
        for j in range(2):
            if i + j < len(keys):
                key = keys[i + j]
                label = EXAMS_1405[key]["name"]
                row.append(InlineKeyboardButton(
                    text=f"🎓 {label}", 
                    callback_data=f"exam:{key}"
                ))
        keyboard.append(row)
    
    # دکمه‌های پایینی
    keyboard.append([
        InlineKeyboardButton(text="📋 همه کنکورها", callback_data="exams:all"),
        InlineKeyboardButton(text="🔄 بروزرسانی", callback_data="exams:refresh")
    ])
    keyboard.append([
        InlineKeyboardButton(text="🏠 منوی اصلی", callback_data="main:back")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# دکمه‌های عملیات برای هر آزمون
def exam_actions_menu(exam_key=None):
    keyboard = []
    
    if exam_key:
        keyboard.append([
            InlineKeyboardButton(text="🔄 بروزرسانی", callback_data=f"refresh:{exam_key}"),
            InlineKeyboardButton(text="📊 جزئیات بیشتر", callback_data=f"details:{exam_key}")
        ])
    
    keyboard.append([
        InlineKeyboardButton(text="📋 همه کنکورها", callback_data="exams:all"),
        InlineKeyboardButton(text="🎯 آزمون بعدی", callback_data="exams:next")
    ])
    keyboard.append([
        InlineKeyboardButton(text="🔄 بروزرسانی همه", callback_data="exams:refresh_all")
    ])
    keyboard.append([
        InlineKeyboardButton(text="🏠 منوی اصلی", callback_data="main:back")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# منوی برنامه مطالعاتی
def study_plan_menu():
    keyboard = [
        [
            InlineKeyboardButton(text="📝 برنامه روزانه", callback_data="study:daily"),
            InlineKeyboardButton(text="📅 برنامه هفتگی", callback_data="study:weekly")
        ],
        [
            InlineKeyboardButton(text="⏱️ ثبت مطالعه", callback_data="study:log"),
            InlineKeyboardButton(text="✅ ثبت پیشرفت", callback_data="study:progress")
        ],
        [
            InlineKeyboardButton(text="📊 آمار پیشرفت", callback_data="study:stats"),
            InlineKeyboardButton(text="🎯 تعیین هدف", callback_data="study:goals")
        ],
        [
            InlineKeyboardButton(text="📋 گزارش کامل", callback_data="study:report"),
            InlineKeyboardButton(text="🔄 بروزرسانی", callback_data="study:refresh")
        ],
        [
            InlineKeyboardButton(text="🏠 منوی اصلی", callback_data="main:back")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# منوی آمار مطالعه
def stats_menu():
    keyboard = [
        [
            InlineKeyboardButton(text="📊 امروز", callback_data="stats:today"),
            InlineKeyboardButton(text="📅 هفته", callback_data="stats:weekly"),
            InlineKeyboardButton(text="📈 ماه", callback_data="stats:monthly")
        ],
        [
            InlineKeyboardButton(text="📋 گزارش کامل", callback_data="stats:full"),
            InlineKeyboardButton(text="📉 نمودارها", callback_data="stats:charts")
        ],
        [
            InlineKeyboardButton(text="🏆 رکوردها", callback_data="stats:records"),
            InlineKeyboardButton(text="🎯 اهداف", callback_data="stats:goals")
        ],
        [
            InlineKeyboardButton(text="⏱️ ثبت مطالعه", callback_data="study:log"),
            InlineKeyboardButton(text="📤 خروجی", callback_data="stats:export")
        ],
        [
            InlineKeyboardButton(text="🔄 بروزرسانی", callback_data="stats:refresh"),
            InlineKeyboardButton(text="🏠 منوی اصلی", callback_data="main:back")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# منوی مدیریت
def admin_menu():
    keyboard = [
        [
            InlineKeyboardButton(text="📢 عضویت اجباری", callback_data="admin:channels"),
            InlineKeyboardButton(text="👥 مدیریت کاربران", callback_data="admin:users")
        ],
        [
            InlineKeyboardButton(text="📊 آمار ربات", callback_data="admin:stats"),
            InlineKeyboardButton(text="⚙️ تنظیمات", callback_data="admin:settings")
        ],
        [
            InlineKeyboardButton(text="📣 ارسال پیام", callback_data="admin:broadcast"),
            InlineKeyboardButton(text="🔍 لاگ‌ها", callback_data="admin:logs")
        ],
        [
            InlineKeyboardButton(text="🏠 منوی اصلی", callback_data="main:back")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# دکمه بازگشت
def back_button_menu(text="🔙 بازگشت", callback_data="main:back"):
    keyboard = [[
        InlineKeyboardButton(text=text, callback_data=callback_data)
    ]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# منوی تأیید/لغو
def confirm_cancel_menu(confirm_data="confirm", cancel_data="cancel"):
    keyboard = [
        [
            InlineKeyboardButton(text="✅ تأیید", callback_data=confirm_data),
            InlineKeyboardButton(text="❌ لغو", callback_data=cancel_data)
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# کیبورد برای ثبت مطالعه
def study_subjects_menu():
    subjects = [
        ("ریاضی", "math"),
        ("فیزیک", "physics"), 
        ("شیمی", "chemistry"),
        ("زیست", "biology"),
        ("ادبیات", "literature"),
        ("عربی", "arabic"),
        ("دینی", "religion"),
        ("زبان", "english")
    ]
    
    keyboard = []
    for subject_name, subject_code in subjects:
        emoji = "📐" if subject_code == "math" else \
                "⚡" if subject_code == "physics" else \
                "🧪" if subject_code == "chemistry" else \
                "🔬" if subject_code == "biology" else \
                "📖" if subject_code == "literature" else \
                "🕌" if subject_code == "arabic" else \
                "📿" if subject_code == "religion" else "🔠"
        
        keyboard.append([
            InlineKeyboardButton(
                text=f"{emoji} {subject_name}", 
                callback_data=f"study:subject:{subject_code}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton(text="🔙 بازگشت", callback_data="stats:back")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# کیبورد عضویت اجباری
def create_membership_keyboard():
    """
    ایجاد کیبورد برای عضویت در کانال‌های اجباری
    """
    from database import Database
    db = Database()
    
    channels = db.get_mandatory_channels()
    keyboard = []
    
    for channel in channels:
        keyboard.append([
            InlineKeyboardButton(
                text=f"📢 {channel['channel_title']}",
                url=f"https://t.me/{channel['channel_username'].lstrip('@')}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton(text="✅ بررسی عضویت", callback_data="check_membership")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# کیبوردهای پیشرفته برای برنامه مطالعاتی
def create_study_plan_keyboard():
    """
    ایجاد کیبورد پیشرفته برای برنامه مطالعاتی
    """
    keyboard = [
        [
            InlineKeyboardButton(text="📝 برنامه روزانه", callback_data="study:daily"),
            InlineKeyboardButton(text="📅 برنامه هفتگی", callback_data="study:weekly")
        ],
        [
            InlineKeyboardButton(text="⏱️ ثبت مطالعه", callback_data="study:log"),
            InlineKeyboardButton(text="✅ ثبت پیشرفت", callback_data="study:progress")
        ],
        [
            InlineKeyboardButton(text="📊 آمار پیشرفت", callback_data="study:stats"),
            InlineKeyboardButton(text="🎯 تعیین هدف", callback_data="study:goals")
        ],
        [
            InlineKeyboardButton(text="📋 گزارش کامل", callback_data="study:report"),
            InlineKeyboardButton(text="🔄 بروزرسانی", callback_data="study:refresh")
        ],
        [
            InlineKeyboardButton(text="🏠 منوی اصلی", callback_data="main:back")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# کیبوردهای پیشرفته برای آمار مطالعه
def create_stats_keyboard():
    """
    ایجاد کیبورد پیشرفته برای آمار مطالعه
    """
    keyboard = [
        [
            InlineKeyboardButton(text="📊 امروز", callback_data="stats:today"),
            InlineKeyboardButton(text="📅 هفته", callback_data="stats:weekly"),
            InlineKeyboardButton(text="📈 ماه", callback_data="stats:monthly")
        ],
        [
            InlineKeyboardButton(text="📋 گزارش کامل", callback_data="stats:full"),
            InlineKeyboardButton(text="📉 نمودارها", callback_data="stats:charts")
        ],
        [
            InlineKeyboardButton(text="🏆 رکوردها", callback_data="stats:records"),
            InlineKeyboardButton(text="🎯 اهداف", callback_data="stats:goals")
        ],
        [
            InlineKeyboardButton(text="⏱️ ثبت مطالعه", callback_data="study:log"),
            InlineKeyboardButton(text="📤 خروجی", callback_data="stats:export")
        ],
        [
            InlineKeyboardButton(text="🔄 بروزرسانی", callback_data="stats:refresh"),
            InlineKeyboardButton(text="🏠 منوی اصلی", callback_data="main:back")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
