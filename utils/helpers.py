import jdatetime
from datetime import datetime, timedelta
import config

def convert_to_jalali(gregorian_date):
    """تبدیل تاریخ میلادی به شمسی"""
    jalali_date = jdatetime.datetime.fromgregorian(datetime=gregorian_date)
    return jalali_date

def get_remaining_time(target_date_str):
    """محاسبه زمان باقی‌مانده تا تاریخ هدف"""
    target_date = jdatetime.datetime.strptime(target_date_str, "%Y-%m-%d %H:%M:%S")
    now = jdatetime.datetime.now()
    
    remaining = target_date - now
    
    weeks = remaining.days // 7
    days = remaining.days % 7
    hours = remaining.seconds // 3600
    minutes = (remaining.seconds % 3600) // 60
    seconds = remaining.seconds % 60
    
    return {
        'weeks': weeks,
        'days': days,
        'hours': hours,
        'minutes': minutes,
        'seconds': seconds,
        'total_days': remaining.days
    }

def format_remaining_time(remaining_dict):
    """قالب‌بندی زمان باقی‌مانده"""
    return (
        f"{remaining_dict['weeks']} هفته, {remaining_dict['days']} روز\n"
        f"{remaining_dict['hours']:02d}:{remaining_dict['minutes']:02d}:{remaining_dict['seconds']:02d}"
    )

def validate_time_format(time_str):
    """اعتبارسنجی فرمت زمان"""
    try:
        hours, minutes = map(int, time_str.split(':'))
        return 0 <= hours <= 23 and 0 <= minutes <= 59
    except:
        return False

def get_exam_dates(exam_name):
    """دریافت تاریخ‌های کنکور"""
    dates = config.EXAMS.get(exam_name)
    if isinstance(dates, list):
        return dates
    else:
        return [dates]

def calculate_study_progress(completed_hours, target_hours):
    """محاسبه پیشرفت مطالعه"""
    if target_hours == 0:
        return 0
    return min((completed_hours / target_hours) * 100, 100)

def get_progress_emoji(percentage):
    """دریافت ایموجی مناسب برای پیشرفت"""
    if percentage >= 90:
        return "🎉"
    elif percentage >= 75:
        return "✅"
    elif percentage >= 50:
        return "📈"
    elif percentage >= 25:
        return "⚠️"
    else:
        return "🔴"
