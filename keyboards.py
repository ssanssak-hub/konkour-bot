from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    """منوی اصلی"""
    keyboard = [
        ["⏳ زمان‌سنجی کنکورها"],
        ["📅 برنامه مطالعاتی پیشرفته"],
        ["📊 آمار مطالعه حرفه‌ای"],
        ["👑 پنل مدیریت"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def exams_menu():
    """منوی کنکورها"""
    keyboard = [
        [
            InlineKeyboardButton("🔬 علوم تجربی", callback_data="exam_علوم_تجربی"),
            InlineKeyboardButton("📚 علوم انسانی", callback_data="exam_علوم_انسانی")
        ],
        [
            InlineKeyboardButton("🧮 ریاضی فنی", callback_data="exam_ریاضی_فنی"),
            InlineKeyboardButton("🎨 هنر", callback_data="exam_هنر")
        ],
        [
            InlineKeyboardButton("🌍 زبان خارجه", callback_data="exam_زبان_خارجه"),
            InlineKeyboardButton("🏫 فرهنگیان", callback_data="exam_فرهنگیان")
        ],
        [
            InlineKeyboardButton("🔄 بروزرسانی همه", callback_data="refresh_all"),
            InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def countdown_actions(exam_key=None):
    """دکمه‌های زمان‌سنجی"""
    keyboard = []
    if exam_key:
        keyboard.append([InlineKeyboardButton("🔄 بروزرسانی", callback_data=f"refresh_{exam_key}")])
    keyboard.append([InlineKeyboardButton("📋 همه کنکورها", callback_data="show_all_exams")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")])
    return InlineKeyboardMarkup(keyboard)

def study_plan_menu():
    """منوی برنامه مطالعاتی پیشرفته"""
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

def stats_menu():
    """منوی آمار مطالعه حرفه‌ای"""
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

def admin_menu():
    """منوی پنل مدیریت"""
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
