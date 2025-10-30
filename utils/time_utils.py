"""
ابزارهای کار با زمان و تاریخ
"""
from datetime import datetime, timedelta
from typing import Tuple, Dict, Any, List

def gregorian_to_jalali(gy, gm, gd):
    """
    تبدیل تاریخ میلادی به شمسی
    منبع: https://jdf.scr.ir/
    """
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    if gm > 2:
        gy2 = gy + 1
    else:
        gy2 = gy
    days = 355666 + (365 * gy) + ((gy2 + 3) // 4) - ((gy2 + 99) // 100) + ((gy2 + 399) // 400) + gd + g_d_m[gm - 1]
    jy = -1595 + (33 * (days // 12053))
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        jm = 1 + (days // 31)
        jd = 1 + (days % 31)
    else:
        jm = 7 + ((days - 186) // 30)
        jd = 1 + ((days - 186) % 30)
    return jy, jm, jd

def get_current_persian_datetime():
    """
    دریافت تاریخ و زمان فعلی به صورت شمسی
    """
    now = datetime.now()
    year, month, day = gregorian_to_jalali(now.year, now.month, now.day)
    
    # نام ماه‌های شمسی
    persian_months = {
        1: "فروردین", 2: "اردیبهشت", 3: "خرداد", 
        4: "تیر", 5: "مرداد", 6: "شهریور",
        7: "مهر", 8: "آبان", 9: "آذر", 
        10: "دی", 11: "بهمن", 12: "اسفند"
    }
    
    weekday = get_persian_weekday(now)
    month_name = persian_months.get(month, "نامشخص")
    
    return {
        'year': year,
        'month': month,
        'month_name': month_name,
        'day': day,
        'weekday': weekday,
        'hour': now.hour,
        'minute': now.minute,
        'second': now.second,
        'full_date': f"{weekday} {day} {month_name} {year}",
        'full_time': f"{now.hour:02d}:{now.minute:02d}:{now.second:02d}"
    }

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

def get_persian_weekday(date: datetime) -> str:
    """
    تبدیل روز هفته به فارسی
    """
    weekdays = {
        0: "دوشنبه",
        1: "سه‌شنبه", 
        2: "چهارشنبه",
        3: "پنجشنبه",
        4: "جمعه",
        5: "شنبه",
        6: "یکشنبه"
    }
    return weekdays[date.weekday()]

def format_exam_dates(dates: List[datetime]) -> str:
    """
    فرمت‌بندی تاریخ‌های آزمون به صورت کامل
    """
    if not dates:
        return "تاریخ تعیین نشده"
    
    result = []
    for date in dates:
        weekday = get_persian_weekday(date)
        # تبدیل تاریخ میلادی به شمسی
        jy, jm, jd = gregorian_to_jalali(date.year, date.month, date.day)
        persian_months = {
            1: "فروردین", 2: "اردیبهشت", 3: "خرداد", 4: "تیر",
            5: "مرداد", 6: "شهریور", 7: "مهر", 8: "آبان", 
            9: "آذر", 10: "دی", 11: "بهمن", 12: "اسفند"
        }
        month_name = persian_months.get(jm, "نامشخص")
        
        result.append(f"📅 {weekday} {jd} {month_name} {jy} - ساعت {date.strftime('%H:%M')}")
    
    return "\n".join(result)

def calculate_multiple_dates_countdown(dates: List[datetime]) -> List[Dict[str, Any]]:
    """
    محاسبه زمان باقی‌مانده برای چندین تاریخ
    """
    now = datetime.now()
    result = []
    
    for date in dates:
        if date <= now:
            result.append({
                'date': date,
                'status': 'passed',
                'countdown': '✅ برگزار شده',
                'days_remaining': 0
            })
        else:
            delta = date - now
            countdown_text, days_remaining = format_time_remaining(date)
            result.append({
                'date': date,
                'status': 'upcoming', 
                'countdown': countdown_text,
                'days_remaining': days_remaining
            })
    
    return result
