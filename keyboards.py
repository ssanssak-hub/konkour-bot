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
                    callback_data=f"exam_{key}"
                ))
        keyboard.append(row)
    
    # دکمه‌های پایینی
    keyboard.append([
        InlineKeyboardButton(text="📋 همه کنکورها", callback_data="show_all_exams"),
        InlineKeyboardButton(text="🔄 بروزرسانی", callback_data="refresh_exams")
    ])
    keyboard.append([
        InlineKeyboardButton(text="🏠 منوی اصلی", callback_data="back_to_main")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# دکمه‌های عملیات برای هر آزمون
def exam_actions_menu(exam_key=None):
    keyboard = []
    
    if exam_key:
        keyboard.append([
            InlineKeyboardButton(text="🔄 بروزرسانی", callback_data=f"refresh_{exam_key}"),
            InlineKeyboardButton(text="📊 جزئیات بیشتر", callback_data=f"details_{exam_key}")
        ])
    
    keyboard.append([
        InlineKeyboardButton(text="📋 همه کنکورها", callback_data="show_all_exams"),
        InlineKeyboardButton(text="🎯 آزمون بعدی", callback_data="next_exam")
    ])
    keyboard.append([
        InlineKeyboardButton(text="🏠 منوی اصلی", callback_data="back_to_main")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# منوی برنامه مطالعاتی
def study_plan_menu():
    keyboard = [
        [
            InlineKeyboardButton(text="📝 ایجاد برنامه", callback_data="create_plan"),
            InlineKeyboardButton(text="📊 مشاهده برنامه", callback_data="view_plan")
        ],
        [
            InlineKeyboardButton(text="⏱️ ثبت مطالعه", callback_data="log_study"),
            InlineKeyboardButton(text="✅ ثبت پیشرفت", callback_data="log_progress")
        ],
        [
            InlineKeyboardButton(text="📈 آمار پیشرفت", callback_data="view_progress"),
            InlineKeyboardButton(text="🎯 اهداف", callback_data="set_goals")
        ],
        [
            InlineKeyboardButton(text="🏠 منوی اصلی", callback_data="back_to_main")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# منوی آمار مطالعه
def stats_menu():
    keyboard = [
        [
            InlineKeyboardButton(text="📊 آمار امروز", callback_data="today_stats"),
            InlineKeyboardButton(text="📅 آمار هفته", callback_data="weekly_stats")
        ],
        [
            InlineKeyboardButton(text="📈 نمودار پیشرفت", callback_data="progress_chart"),
            InlineKeyboardButton(text="🏆 رکوردها", callback_data="records")
        ],
        [
            InlineKeyboardButton(text="⏱️ ثبت مطالعه", callback_data="log_study"),
            InlineKeyboardButton(text="📋 گزارش کامل", callback_data="full_report")
        ],
        [
            InlineKeyboardButton(text="🏠 منوی اصلی", callback_data="back_to_main")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# منوی مدیریت
def admin_menu():
    keyboard = [
        [
            InlineKeyboardButton(text="📢 عضویت اجباری", callback_data="admin_mandatory_channels"),
            InlineKeyboardButton(text="👥 مدیریت کاربران", callback_data="admin_users")
        ],
        [
            InlineKeyboardButton(text="📊 آمار ربات", callback_data="admin_stats"),
            InlineKeyboardButton(text="⚙️ تنظیمات", callback_data="admin_settings")
        ],
        [
            InlineKeyboardButton(text="📣 ارسال پیام", callback_data="admin_broadcast"),
            InlineKeyboardButton(text="🔍 لاگ‌ها", callback_data="admin_logs")
        ],
        [
            InlineKeyboardButton(text="🏠 منوی اصلی", callback_data="back_to_main")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# دکمه بازگشت
def back_button_menu(text="🔙 بازگشت", callback_data="back_to_main"):
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
