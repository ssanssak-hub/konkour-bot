# اضافه کردن این توابع به time_utils.py


def get_tehran_time_formatted() -> str:
    """دریافت زمان فعلی تهران به فرمت HH:MM"""
    try:
        from jdatetime import datetime as jdatetime
        import pytz
        tehran_tz = pytz.timezone('Asia/Tehran')
        return jdatetime.now(tehran_tz).strftime("%H:%M")
    except ImportError:
        # فال‌بک در صورت عدم وجود jdatetime
        from datetime import datetime
        return datetime.now().strftime("%H:%M")

def get_tehran_date_formatted() -> str:
    """دریافت تاریخ امروز تهران به فرمت شمسی خوانا"""
    try:
        from jdatetime import datetime as jdatetime
        import pytz
        tehran_tz = pytz.timezone('Asia/Tehran')
        return jdatetime.now(tehran_tz).strftime("%Y/%m/%d")
    except ImportError:
        # فال‌بک در صورت عدم وجود jdatetime
        from datetime import datetime
        return datetime.now().strftime("%Y/%m/%d")
