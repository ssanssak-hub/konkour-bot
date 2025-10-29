"""
ابزارهای کمکی برای ربات
"""
import asyncio
from datetime import datetime, timedelta
from typing import Tuple
from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database import Database

db = Database()

async def check_user_membership(bot: Bot, user_id: int) -> bool:
    """
    بررسی عضویت کاربر در تمام کانال‌های اجباری
    """
    channels = db.get_mandatory_channels()
    
    if not channels:
        return True  # اگر کانال اجباری وجود ندارد
    
    for channel in channels:
        try:
            member = await bot.get_chat_member(channel['channel_id'], user_id)
            is_member = member.status in ['member', 'administrator', 'creator']
            db.update_channel_membership(user_id, channel['channel_id'], is_member)
            
            if not is_member:
                return False
        except Exception as e:
            print(f"خطا در بررسی عضویت: {e}")
            return False
    
    return True

def format_time_remaining(target_date: datetime) -> str:
    """
    فرمت‌بندی زمان باقی‌مانده به صورت دقیق (هفته، روز، ساعت، دقیقه، ثانیه)
    """
    now = datetime.now()
    
    if target_date <= now:
        return "✅ برگزار شده"
    
    delta = target_date - now
    total_seconds = int(delta.total_seconds())
    
    # محاسبه اجزای زمان
    weeks = total_seconds // (7 * 24 * 3600)
    days = (total_seconds % (7 * 24 * 3600)) // (24 * 3600)
    hours = (total_seconds % (24 * 3600)) // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    parts = []
    
    if weeks > 0:
        parts.append(f"{weeks} هفته")
    if days > 0:
        parts.append(f"{days} روز")
    if hours > 0:
        parts.append(f"{hours} ساعت")
    if minutes > 0:
        parts.append(f"{minutes} دقیقه")
    if seconds > 0:
        parts.append(f"{seconds} ثانیه")
    
    if not parts:
        return "⏳ کمتر از ۱ ثانیه باقی مانده"
    
    return "⏳ " + " و ".join(parts) + " باقی مانده"

def create_membership_keyboard() -> InlineKeyboardMarkup:
    """
    ایجاد کیبورد برای عضویت در کانال‌ها
    """
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

def get_subject_emoji(subject: str) -> str:
    """
    دریافت ایموجی مناسب برای هر درس
    """
    emoji_map = {
        "ریاضی": "📐",
        "فیزیک": "⚡", 
        "شیمی": "🧪",
        "زیست": "🔬",
        "ادبیات": "📖",
        "عربی": "🕌",
        "دینی": "📿",
        "زبان": "🔠",
        "هنر": "🎨",
        "تاریخ": "📜",
        "جغرافیا": "🗺️",
        "فلسفه": "💭",
        "اقتصاد": "💹",
        "جامعه": "👥"
    }
    return emoji_map.get(subject, "📚")
