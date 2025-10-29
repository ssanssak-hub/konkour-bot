from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from exam_data import EXAMS_1405

# منوی اصلی با کیبورد معمولی
def main_menu():
    keyboard = [
        ["⏳ زمان‌سنجی کنکورها"],
        ["📅 برنامه مطالعاتی پیشرفته"],
        ["📊 آمار مطالعه حرفه‌ای"],
        ["👑 پنل مدیریت"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# منوی آزمون‌ها به‌صورت داینامیک از exam_data
def exams_menu():
    rows = []
    keys = list(EXAMS_1405.keys())
    for i in range(0, len(keys), 2):
        row = []
        for j in range(2):
            if i + j < len(keys):
                key = keys[i + j]
                label = EXAMS_1405[key]["name"]
                row.append(InlineKeyboardButton(f"🎓 {label}", callback_data=f"exam_{key}"))
        rows.append(row)
    rows.append([
        InlineKeyboardButton("🔄 بروزرسانی همه", callback_data="refresh_all"),
        InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
    ])
    return InlineKeyboardMarkup(rows)

# دکمه‌های زمان‌سنجی برای هر آزمون
def countdown_actions(exam_key=None):
    keyboard = []
    if exam_key:
        keyboard.append([InlineKeyboardButton("🔄 بروزرسانی", callback_data=f"refresh_{exam_key}")])
    keyboard.append([InlineKeyboardButton("📋 همه کنکورها", callback_data="show_all_exams")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")])
    return InlineKeyboardMarkup(keyboard)

# منوی برنامه مطالعاتی
def study_plan_menu():
    keyboard = [
        [
            InlineKeyboardButton("📝 ایجاد برنامه", callback_data="create_plan"),
            InlineKeyboardButton("📊 مشاهده برنامه", callback_data="view_plan")
        ],
        [
            InlineKeyboardButton("✏️ ویرایش برنامه", callback_data="edit_plan"),
            InlineKeyboardButton("📈 پیشرفت", callback_data="progress")
        ],
        [
            InlineKeyboardButton("🔄 بروزرسانی", callback_data="refresh_plan"),
            InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# منوی آمار مطالعه
def stats_menu():
    keyboard = [
        [
            InlineKeyboardButton("⏱️ ثبت مطالعه", callback_data="log_study"),
            InlineKeyboardButton("📊 آمار روزانه", callback_data="daily_stats")
        ],
        [
            InlineKeyboardButton("📈 آمار هفتگی", callback_data="weekly_stats"),
            InlineKeyboardButton("🏆 لیدربرد", callback_data="leaderboard")
        ],
        [
            InlineKeyboardButton("📋 گزارش کامل", callback_data="full_report"),
            InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# منوی مدیریت با دکمه‌های حساس
def admin_menu():
    keyboard = [
        [
            InlineKeyboardButton("📊 آمار ربات", callback_data="admin_stats"),
            InlineKeyboardButton("👥 کاربران", callback_data="admin_users")
        ],
        [
            InlineKeyboardButton("📢 ارسال همگانی", callback_data="admin_broadcast"),
            InlineKeyboardButton("⚙️ تنظیمات", callback_data="admin_settings")
        ],
        [
            InlineKeyboardButton("🔄 بروزرسانی", callback_data="admin_refresh"),
            InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# دکمه‌های تأیید و لغو برای عملیات حساس
def confirm_cancel_menu(confirm_callback, cancel_callback="back_to_main"):
    keyboard = [
        [
            InlineKeyboardButton("✅ تأیید", callback_data=confirm_callback),
            InlineKeyboardButton("❌ لغو", callback_data=cancel_callback)
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
