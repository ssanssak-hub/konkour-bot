"""
ابزارهای کار با زمان و تاریخ - نسخه کامل و اصلاح شده
"""
import logging
from datetime import datetime, timedelta
from typing import Tuple, Dict, Any, List
from jdatetime import datetime as jdatetime
import pytz

logger = logging.getLogger(__name__)

# تنظیم تایم‌زون تهران
TEHRAN_TIMEZONE = pytz.timezone('Asia/Tehran')

def get_current_tehran_datetime():
    """دریافت datetime فعلی با تایم‌زون تهران"""
    return datetime.now(TEHRAN_TIMEZONE)
    
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

def jalali_to_gregorian(jy, jm, jd):
    """
    تبدیل تاریخ شمسی به میلادی
    منبع: https://jdf.scr.ir/
    """
    jy += 1595
    days = -355668 + (365 * jy) + ((jy // 33) * 8) + (((jy % 33) + 3) // 4) + jd
    if jm < 7:
        days += (jm - 1) * 31
    else:
        days += ((jm - 7) * 30) + 186
    gy = 400 * (days // 146097)
    days %= 146097
    if days > 36524:
        gy += 100 * ((days - 1) // 36524)
        days = (days - 1) % 36524
        if days >= 365:
            days += 1
    gy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        gy += ((days - 1) // 365)
        days = (days - 1) % 365
    gd = days + 1
    if (gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0):
        kab = 29
    else:
        kab = 28
    sal_a = [0, 31, kab, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    gm = 0
    while gm < 13:
        v = sal_a[gm]
        if gd <= v:
            break
        gd -= v
        gm += 1
    return gy, gm, gd

def parse_persian_date(date_str: str) -> tuple:
    """تبدیل رشته تاریخ شمسی به اعداد - پشتیبانی از / و -"""
    # پشتیبانی از هر دو جداکننده
    if '/' in date_str:
        separator = '/'
    elif '-' in date_str:
        separator = '-'
    else:
        raise ValueError("فرمت تاریخ نامعتبر")
    
    parts = date_str.split(separator)
    if len(parts) != 3:
        raise ValueError("فرمت تاریخ نامعتبر")
    
    return int(parts[0]), int(parts[1]), int(parts[2])
    
def persian_to_gregorian_string(persian_date: str) -> str:
    """تبدیل تاریخ شمسی به رشته میلادی YYYY-MM-DD"""
    # پشتیبانی از هر دو فرمت / و -
    if '/' in persian_date:
        jy, jm, jd = parse_persian_date(persian_date)
    elif '-' in persian_date:
        parts = persian_date.split('-')
        if len(parts) != 3:
            raise ValueError("فرمت تاریخ نامعتبر")
        jy, jm, jd = int(parts[0]), int(parts[1]), int(parts[2])
    else:
        raise ValueError("فرمت تاریخ نامعتبر")
    
    gy, gm, gd = jalali_to_gregorian(jy, jm, jd)
    return f"{gy}-{gm:02d}-{gd:02d}"

def format_gregorian_date_for_display(gregorian_date: str) -> str:
    """تبدیل تاریخ میلادی به شمسی برای نمایش به کاربر"""
    year, month, day = map(int, gregorian_date.split('-'))
    jy, jm, jd = gregorian_to_jalali(year, month, day)
    persian_months = {
        1: "فروردین", 2: "اردیبهشت", 3: "خرداد", 4: "تیر",
        5: "مرداد", 6: "شهریور", 7: "مهر", 8: "آبان", 
        9: "آذر", 10: "دی", 11: "بهمن", 12: "اسفند"
    }
    return f"{jd} {persian_months.get(jm, '')} {jy}"

def get_current_persian_datetime():
    """دریافت تاریخ و زمان فعلی تهران به صورت شمسی"""
    tehran_tz = pytz.timezone('Asia/Tehran')
    now_tehran = jdatetime.now(tehran_tz)
    
    # نام ماه‌های شمسی
    persian_months = {
        1: "فروردین", 2: "اردیبهشت", 3: "خرداد", 
        4: "تیر", 5: "مرداد", 6: "شهریور",
        7: "مهر", 8: "آبان", 9: "آذر", 
        10: "دی", 11: "بهمن", 12: "اسفند"
    }
    
    # نام روزهای هفته
    persian_weekdays = {
        0: "شنبه", 1: "یکشنبه", 2: "دوشنبه",
        3: "سه‌شنبه", 4: "چهارشنبه", 5: "پنجشنبه", 6: "جمعه"
    }
    
    weekday_name = persian_weekdays.get(now_tehran.weekday(), "نامشخص")
    month_name = persian_months.get(now_tehran.month, "نامشخص")
    
    return {
        'year': now_tehran.year,
        'month': now_tehran.month,
        'month_name': month_name,
        'day': now_tehran.day,
        'weekday': weekday_name,
        'hour': now_tehran.hour,
        'minute': now_tehran.minute,
        'second': now_tehran.second,
        'date': now_tehran.strftime("%Y-%m-%d"),  # فرمت YYYY-MM-DD
        'time': now_tehran.strftime("%H:%M"),     # فرمت HH:MM
        'full_date': f"{weekday_name} {now_tehran.day} {month_name} {now_tehran.year}",
        'full_time': f"{now_tehran.hour:02d}:{now_tehran.minute:02d}:{now_tehran.second:02d}",
        'timezone': 'تهران'
    }
    
def get_tehran_time():
    """دریافت زمان فعلی تهران به فرمت HH:MM"""
    return get_current_persian_datetime()['time']

def get_tehran_date():
    """دریافت تاریخ امروز تهران به فرمت YYYY-MM-DD"""
    return get_current_persian_datetime()['date']
    
def get_tehran_time_formatted():
    """دریافت زمان فعلی تهران به فرمت HH:MM"""
    current = get_current_persian_datetime()
    return f"{current['hour']:02d}:{current['minute']:02d}"

def get_tehran_date_formatted():
    """دریافت تاریخ امروز تهران به فرمت YYYY-MM-DD"""
    current = get_current_persian_datetime()
    return f"{current['year']}-{current['month']:02d}-{current['day']:02d}"

def format_time_remaining(target_date) -> Tuple[str, int]:
    """
    فرمت‌بندی زمان باقی‌مانده به صورت دقیق و بازگشت تعداد کل روزها
    """
    try:
        now = get_current_tehran_datetime()
        
        # اگر target_date رشته هست، تبدیل به datetime کن
        if isinstance(target_date, str):
            # فرض بر این که فرمت تاریخ: "2024-06-14 08:00:00"
            target_date = datetime.strptime(target_date, "%Y-%m-%d %H:%M:%S")
            target_date = TEHRAN_TIMEZONE.localize(target_date)
        elif hasattr(target_date, 'tzinfo'):
            # اگر target_date از نوع datetime هست
            if target_date.tzinfo is None:
                target_date = TEHRAN_TIMEZONE.localize(target_date)
            else:
                target_date = target_date.astimezone(TEHRAN_TIMEZONE)
        
        # اگر هنوز target_date رشته هست (خطای قبلی)
        if isinstance(target_date, str):
            logger.error(f"target_date هنوز رشته است: {target_date}")
            return "خطا در فرمت تاریخ", 0
        
        # اطمینان از اینکه target_date هم در تایم‌زون تهران باشد
        if target_date.tzinfo is None:
            target_date = TEHRAN_TIMEZONE.localize(target_date)
        else:
            target_date = target_date.astimezone(TEHRAN_TIMEZONE)
        
        if target_date <= now:
            return "✅ برگزار شده", 0
        
        delta = target_date - now
        total_seconds = int(delta.total_seconds())
        total_days = delta.days
        
        # محاسبه اجزای زمان
        days = total_days
        hours = (total_seconds % (24 * 3600)) // 3600
        minutes = (total_seconds % 3600) // 60
        
        if days > 30:
            countdown_text = f"{days} روز"
        elif days > 0:
            countdown_text = f"{days} روز و {hours} ساعت"
        elif hours > 0:
            countdown_text = f"{hours} ساعت و {minutes} دقیقه"
        else:
            countdown_text = f"{minutes} دقیقه"
        
        time_text = f"⏳ {countdown_text} باقی مانده"
        return time_text, total_days
        
    except Exception as e:
        logger.error(f"خطا در format_time_remaining: {e}, target_date: {target_date}")
        return "خطا در محاسبه زمان", 0

def format_time_remaining_detailed(target_date) -> str:
    """
    فرمت‌بندی ساده زمان باقی‌مانده
    """
    try:
        time_text, _ = format_time_remaining(target_date)
        return time_text
    except Exception as e:
        logger.error(f"خطا در format_time_remaining_detailed: {e}")
        return "خطا در محاسبه"

def format_study_time(minutes: int) -> str:
    """
    فرمت‌بندی زمان مطالعه به صورت خوانا
    """
    try:
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
    except Exception as e:
        logger.error(f"خطا در format_study_time: {e}")
        return "0 دقیقه"

def get_persian_weekday(date: datetime) -> str:
    """
    تبدیل روز هفته به فارسی
    """
    try:
        weekdays = {
            0: "دوشنبه",
            1: "سه‌شنبه", 
            2: "چهارشنبه",
            3: "پنجشنبه",
            4: "جمعه",
            5: "شنبه",
            6: "یکشنبه"
        }
        return weekdays.get(date.weekday(), "نامشخص")
    except Exception as e:
        logger.error(f"خطا در get_persian_weekday: {e}")
        return "نامشخص"

def format_exam_dates(dates: List[datetime]) -> str:
    """
    فرمت‌بندی تاریخ‌های آزمون به صورت کامل با تایم‌زون تهران
    """
    if not dates:
        return "تاریخ تعیین نشده"
    
    result = []
    for date in dates:
        try:
            # تبدیل به تایم‌زون تهران
            if date.tzinfo is None:
                date = TEHRAN_TIMEZONE.localize(date)
            else:
                date = date.astimezone(TEHRAN_TIMEZONE)
                
            weekday = get_persian_weekday(date)
            # تبدیل تاریخ میلادی به شمسی
            jy, jm, jd = gregorian_to_jalali(date.year, date.month, date.day)
            persian_months = {
                1: "فروردین", 2: "اردیبهشت", 3: "خرداد", 4: "تیر",
                5: "مرداد", 6: "شهریور", 7: "مهر", 8: "آبان", 
                9: "آذر", 10: "دی", 11: "بهمن", 12: "اسفند"
            }
            month_name = persian_months.get(jm, "نامشخص")
            
            result.append(f"📅 {weekday} {jd} {month_name} {jy} - ساعت {date.strftime('%H:%M')} به وقت تهران")
        except Exception as e:
            logger.error(f"خطا در format_exam_dates برای تاریخ {date}: {e}")
            result.append(f"📅 خطا در نمایش تاریخ")
    
    return "\n".join(result)

def calculate_multiple_dates_countdown(exam_dates: Dict[str, Any]) -> List[Tuple[str, str, int]]:
    """
    محاسبه countdown برای چندین تاریخ - نسخه اصلاح شده
    """
    try:
        now = get_current_tehran_datetime()
        
        countdowns = []
        for exam_name, date_value in exam_dates.items():
            try:
                target_date = None
                
                # تبدیل تاریخ به datetime
                if isinstance(date_value, str):
                    # اگر تاریخ به صورت رشته هست
                    target_date = datetime.strptime(date_value, "%Y-%m-%d %H:%M:%S")
                    target_date = TEHRAN_TIMEZONE.localize(target_date)
                elif isinstance(date_value, datetime):
                    # اگر از قبل datetime هست
                    target_date = date_value
                    if target_date.tzinfo is None:
                        target_date = TEHRAN_TIMEZONE.localize(target_date)
                    else:
                        target_date = target_date.astimezone(TEHRAN_TIMEZONE)
                else:
                    countdowns.append((exam_name, "❌ فرمت تاریخ نامعتبر", 0))
                    continue
                
                # محاسبه زمان باقی‌مانده
                if target_date <= now:
                    countdowns.append((exam_name, "✅ گذشته", 0))
                else:
                    time_left = target_date - now
                    days = time_left.days
                    hours = time_left.seconds // 3600
                    minutes = (time_left.seconds % 3600) // 60
                    
                    if days > 30:
                        countdown_text = f"{days} روز"
                    elif days > 0:
                        countdown_text = f"{days} روز و {hours} ساعت"
                    else:
                        countdown_text = f"{hours} ساعت و {minutes} دقیقه"
                    
                    countdowns.append((exam_name, f"⏳ {countdown_text}", days))
                    
            except Exception as e:
                logger.error(f"خطا در پردازش تاریخ {exam_name}: {e}")
                countdowns.append((exam_name, "❌ خطا در تاریخ", 0))
        
        # مرتب کردن بر اساس روزهای باقی‌مانده (کمترین به بیشترین)
        countdowns.sort(key=lambda x: x[2])
        return countdowns
        
    except Exception as e:
        logger.error(f"خطای کلی در calculate_multiple_dates_countdown: {e}")
        return [("خطا", "❌ سیستم موقتاً недоступен", 0)]
        
def create_datetime_with_tehran_timezone(year, month, day, hour=0, minute=0, second=0):
    """
    ایجاد تاریخ با تایم‌زون تهران
    """
    try:
        naive_dt = datetime(year, month, day, hour, minute, second)
        return TEHRAN_TIMEZONE.localize(naive_dt)
    except Exception as e:
        logger.error(f"خطا در create_datetime_with_tehran_timezone: {e}")
        return None

def is_valid_exam_date(date_value) -> bool:
    """
    بررسی معتبر بودن تاریخ کنکور
    """
    try:
        if isinstance(date_value, str):
            # بررسی فرمت رشته
            datetime.strptime(date_value, "%Y-%m-%d %H:%M:%S")
            return True
        elif isinstance(date_value, datetime):
            return True
        else:
            return False
    except:
        return False

def get_exam_date_display(exam_name: str, date_value) -> str:
    """
    نمایش فرمت شده تاریخ کنکور
    """
    try:
        if isinstance(date_value, str):
            date_obj = datetime.strptime(date_value, "%Y-%m-%d %H:%M:%S")
        elif isinstance(date_value, datetime):
            date_obj = date_value
        else:
            return f"{exam_name}: تاریخ نامعتبر"
        
        # تبدیل به شمسی
        jy, jm, jd = gregorian_to_jalali(date_obj.year, date_obj.month, date_obj.day)
        persian_months = {
            1: "فروردین", 2: "اردیبهشت", 3: "خرداد", 4: "تیر",
            5: "مرداد", 6: "شهریور", 7: "مهر", 8: "آبان", 
            9: "آذر", 10: "دی", 11: "بهمن", 12: "اسفند"
        }
        month_name = persian_months.get(jm, "نامشخص")
        
        return f"{exam_name}: {jd} {month_name} {jy} - ساعت {date_obj.strftime('%H:%M')}"
    except Exception as e:
        logger.error(f"خطا در get_exam_date_display: {e}")
        return f"{exam_name}: خطا در نمایش تاریخ"
