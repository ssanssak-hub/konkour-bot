"""
ابزارهای کمکی پیشرفته برای ربات کنکور
"""
import asyncio
import random
from datetime import datetime, timedelta
from typing import Tuple, List, Dict, Any
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

def format_time_remaining(target_date: datetime) -> Tuple[str, int]:
    """
    فرمت‌بندی زمان باقی‌مانده به صورت دقیق و بازگشت تعداد کل روزها
    """
    now = datetime.now()
    
    if target_date <= now:
        return "✅ برگزار شده", 0
    
    delta = target_date - now
    total_seconds = int(delta.total_seconds())
    total_days = delta.days
    
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
        return "⏳ کمتر از ۱ ثانیه باقی مانده", total_days
    
    time_text = "⏳ " + " و ".join(parts) + " باقی مانده"
    return time_text, total_days

def format_time_remaining_detailed(target_date: datetime) -> Dict[str, Any]:
    """
    محاسبه دقیق زمان باقی‌مانده و بازگشت تمام جزئیات
    """
    now = datetime.now()
    
    if target_date <= now:
        return {
            'weeks': 0, 'days': 0, 'hours': 0, 
            'minutes': 0, 'seconds': 0, 
            'total_seconds': 0, 'total_days': 0
        }
    
    delta = target_date - now
    total_seconds = int(delta.total_seconds())
    total_days = delta.days
    
    return {
        'weeks': total_seconds // (7 * 24 * 3600),
        'days': (total_seconds % (7 * 24 * 3600)) // (24 * 3600),
        'hours': (total_seconds % (24 * 3600)) // 3600,
        'minutes': (total_seconds % 3600) // 60,
        'seconds': total_seconds % 60,
        'total_seconds': total_seconds,
        'total_days': total_days
    }
    
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
        "جامعه": "👥",
        "روانشناسی": "🧠",
        "مدیریت": "📊"
    }
    return emoji_map.get(subject, "📚")

def get_study_tips() -> str:
    """
    دریافت نکات مطالعاتی تصادفی
    """
    tips = [
        "🎯 **نکته طلایی**: مطالعه فعال بهتر از مطالعه منفعل است! سوال بپرسید و خلاصه بنویسید.",
        "⏰ **مدیریت زمان**: از تکنیک پومودورو استفاده کنید (۲۵ دقیقه مطالعه، ۵ دقیقه استراحت).",
        "📝 **مرور هوشمند**: مطالب را در فواصل زمانی مشخص مرور کنید تا در حافظه بلندمدت ثبت شوند.",
        "💡 **یادگیری عمیق**: سعی کنید مفاهیم را به زبان خودتان توضیح دهید.",
        "📊 **برنامه‌ریزی**: برنامه هفتگی داشته باشید و به آن پایبند باشید.",
        "🔄 **تست زنی**: بعد از هر مبحث، تست زماندار بزنید.",
        "📈 **تحلیل آزمون**: بعد از هر آزمون،弱点های خود را شناسایی و برطرف کنید.",
        "🧘 **سلامت روان**: استراحت کافی داشته باشید و ورزش را فراموش نکنید.",
        "📚 **منابع استاندارد**: از منابع معتبر و استاندارد استفاده کنید.",
        "🎪 **تعادل**: بین مطالعه و تفریح تعادل برقرار کنید."
    ]
    return random.choice(tips)

def calculate_study_progress(total_study_minutes: int, target_minutes: int = 10000) -> Dict[str, Any]:
    """
    محاسبه پیشرفت مطالعه نسبت به هدف (۱۰۰۰۰ دقیقه = حدود ۱۶۷ ساعت)
    """
    if target_minutes <= 0:
        return {
            'percentage': 0,
            'remaining_minutes': 0,
            'remaining_hours': 0,
            'progress_bar': "░░░░░░░░░░"
        }
    
    percentage = min(100, (total_study_minutes / target_minutes) * 100)
    remaining_minutes = max(0, target_minutes - total_study_minutes)
    
    # ایجاد نوار پیشرفت
    progress_length = 10
    filled_length = int(progress_length * percentage / 100)
    progress_bar = "█" * filled_length + "░" * (progress_length - filled_length)
    
    return {
        'percentage': round(percentage, 1),
        'remaining_minutes': remaining_minutes,
        'remaining_hours': round(remaining_minutes / 60, 1),
        'progress_bar': progress_bar
    }

def format_study_time(minutes: int) -> str:
    """
    فرمت‌بندی زمان مطالعه به صورت خوانا
    """
    if minutes < 60:
        return f"{minutes} دقیقه"
    elif minutes < 1440:  # کمتر از یک روز
        hours = minutes // 60
        mins = minutes % 60
        if mins > 0:
            return f"{hours} ساعت و {mins} دقیقه"
        else:
            return f"{hours} ساعت"
    else:
        days = minutes // 1440
        hours = (minutes % 1440) // 60
        if hours > 0:
            return f"{days} روز و {hours} ساعت"
        else:
            return f"{days} روز"

def get_motivational_quote() -> str:
    """
    دریافت جمله انگیزشی تصادفی
    """
    quotes = [
        "💪 **اراده**: بزرگ‌ترین کشف نسل ما این است که انسان با تغییر نگرش ذهنی‌اش می‌تواند زندگی‌اش را تغییر دهد.",
        "🚀 **تلاش**: موفقیت تصادفی نیست، حاصل پشتکار، یادگیری، مطالعه، قربانی کردن و最重要的是 عشق به کاری است که انجام می‌دهید.",
        "🌟 **امید**: بهترین راه برای پیش‌بینی آینده، ساختن آن است.",
        "🎯 **تمرکز**: روی اهدافتان تمرکز کنید، نه موانع.",
        "📚 **علم**: سرمایه‌گذاری روی دانش بهترین سود را دارد.",
        "⏰ **زمان**: زمان طلاست، اما نمی‌توانید آن را ذخیره کنید. فقط می‌توانید آن را wisely صرف کنید.",
        "💎 **اصالت**: مانند الماس باشید - کمیاب، باارزش و همیشه درخشنده.",
        "🌈 **پشتکار**: بعد از هر تاریکی، روشنایی می‌آید. پس هیچ‌گاه امیدت را از دست نده.",
        "🎓 **هدف**: آموزش قدرتمندترین سلاحی است که می‌توانید برای تغییر جهان از آن استفاده کنید.",
        "🔥 **اشتیاق**: اگر چیزی را به اندازه کافی دوست داشته باشید، برای به دست آوردنش تمام قوايت را به کار خواهی گرفت."
    ]
    return random.choice(quotes)

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

def calculate_streak(study_days: List[str]) -> int:
    """
    محاسبه streak (تعداد روزهای متوالی مطالعه)
    """
    if not study_days:
        return 0
    
    # تبدیل تاریخ‌ها به datetime و مرتب‌سازی
    dates = sorted([datetime.strptime(day, '%Y-%m-%d').date() for day in study_days])
    
    streak = 1
    current_date = dates[-1]
    
    for i in range(len(dates)-2, -1, -1):
        if (current_date - dates[i]).days == 1:
            streak += 1
            current_date = dates[i]
        else:
            break
    
    return streak

def get_next_exam() -> Dict[str, Any]:
    """
    پیدا کردن نزدیک‌ترین آزمون آینده
    """
    from exam_data import EXAMS_1405
    from datetime import datetime
    
    now = datetime.now()
    next_exam = None
    min_delta = None
    
    for exam_key, exam in EXAMS_1405.items():
        dates = exam["date"] if isinstance(exam["date"], list) else [exam["date"]]
        
        for date_tuple in dates:
            exam_date = datetime(*date_tuple)
            if exam_date > now:
                delta = exam_date - now
                if min_delta is None or delta < min_delta:
                    min_delta = delta
                    next_exam = {
                        'key': exam_key,
                        'name': exam['name'],
                        'date': exam_date,
                        'persian_date': exam['persian_date'],
                        'time': exam['time']
                    }
    
    return next_exam

def create_admin_stats_message() -> str:
    """
    ایجاد پیام آمار برای پنل مدیریت
    """
    # اینجا می‌توان آمار واقعی از دیتابیس گرفت
    return (
        "👑 <b>آمار مدیریتی ربات</b>\n\n"
        "📊 آمار کلی:\n"
        "• 👥 کاربران فعال: در حال بارگذاری...\n"
        "• 📚 جلسات مطالعه: در حال بارگذاری...\n"
        "• 🕒 زمان کل مطالعه: در حال بارگذاری...\n\n"
        "⚙️ سیستم عضویت اجباری:\n"
        "• 📢 کانال‌های فعال: در حال بارگذاری...\n"
        "• ✅ کاربران تأیید شده: در حال بارگذاری...\n"
        "• ❌ کاربران bloque شده: در حال بارگذاری..."
    )
