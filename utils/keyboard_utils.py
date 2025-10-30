"""
ابزارهای ایجاد کیبوردهای اینلاین
"""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def create_study_plan_keyboard() -> InlineKeyboardMarkup:
    """
    ایجاد کیبورد پیشرفته برای برنامه مطالعاتی
    """
    keyboard = [
        [
            InlineKeyboardButton(text="📝 برنامه روزانه", callback_data="daily_plan"),
            InlineKeyboardButton(text="📅 برنامه هفتگی", callback_data="weekly_plan")
        ],
        [
            InlineKeyboardButton(text="⏱️ ثبت مطالعه", callback_data="log_study"),
            InlineKeyboardButton(text="✅ ثبت پیشرفت", callback_data="log_progress")
        ],
        [
            InlineKeyboardButton(text="📊 آمار پیشرفت", callback_data="view_progress"),
            InlineKeyboardButton(text="🎯 تعیین هدف", callback_data="set_goal")
        ],
        [
            InlineKeyboardButton(text="📋 گزارش کامل", callback_data="full_report"),
            InlineKeyboardButton(text="🔄 بروزرسانی", callback_data="refresh_plan")
        ],
        [
            InlineKeyboardButton(text="🏠 منوی اصلی", callback_data="back_to_main")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def create_stats_keyboard() -> InlineKeyboardMarkup:
    """
    ایجاد کیبورد پیشرفته برای آمار مطالعه
    """
    keyboard = [
        [
            InlineKeyboardButton(text="📊 امروز", callback_data="today_stats"),
            InlineKeyboardButton(text="📅 هفته", callback_data="weekly_stats"),
            InlineKeyboardButton(text="📈 ماه", callback_data="monthly_stats")
        ],
        [
            InlineKeyboardButton(text="📋 گزارش کامل", callback_data="full_report"),
            InlineKeyboardButton(text="📉 نمودارها", callback_data="charts")
        ],
        [
            InlineKeyboardButton(text="🏆 رکوردها", callback_data="records"),
            InlineKeyboardButton(text="🎯 اهداف", callback_data="goals")
        ],
        [
            InlineKeyboardButton(text="⏱️ ثبت مطالعه", callback_data="log_study"),
            InlineKeyboardButton(text="📤 خروجی", callback_data="export_stats")
        ],
        [
            InlineKeyboardButton(text="🔄 بروزرسانی", callback_data="refresh_stats"),
            InlineKeyboardButton(text="🏠 منوی اصلی", callback_data="back_to_main")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
