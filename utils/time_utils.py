"""
ابزارهای کار با زمان و تاریخ
"""
from datetime import datetime, timedelta
from typing import Tuple, Dict, Any

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
