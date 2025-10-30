"""
ابزارهای مربوط به مطالعه و برنامه‌ریزی
"""
import random
from datetime import datetime
from typing import List, Dict, Any
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

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
