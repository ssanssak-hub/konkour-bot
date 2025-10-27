from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    """منوی اصلی با دکمه‌های معمولی"""
    keyboard = [
        ["⏳ چند روز تا کنکور؟"],
        ["📅 برنامه مطالعاتی"],
        ["📊 آمار مطالعه"],
        ["ℹ️ راهنمای استفاده"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def countdown_actions():
    """دکمه‌های زیرمنوی زمان‌سنجی"""
    keyboard = [
        [InlineKeyboardButton("🔄 بروزرسانی", callback_data="refresh_countdown")],
        [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)
