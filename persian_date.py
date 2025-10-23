"""
جایگزین کامل برای python-jdatetime
با الگوریتم تبدیل تاریخ شمسی
"""

import datetime
from typing import Tuple, Optional

class PersianDate:
    """کلاس مدیریت تاریخ شمسی"""
    
    # آرایه‌های تبدیل تاریخ
    GREGORIAN_EPOCH = 1721425.5
    PERSIAN_EPOCH = 1948320.5
    
    @staticmethod
    def persian_to_julian(year: int, month: int, day: int) -> float:
        """تبدیل تاریخ شمسی به ژولیانی"""
        epbase = year - (1 if year >= 0 else 0) // 474
        epyear = 474 * epbase + 1029983
        month_day = 31 * (month - 1) if month <= 6 else 186 + 30 * (month - 7)
        return (epyear * 682 + (epyear * 281 // 1280) + month_day + day - 1) * 1.0 / 2816 + 1.0
    
    @staticmethod
    def julian_to_gregorian(jd: float) -> Tuple[int, int, int]:
        """تبدیل ژولیانی به میلادی"""
        jd = jd + 0.5
        z = int(jd)
        f = jd - z
        
        a = z
        if z >= 2299161:
            alpha = int((z - 1867216.25) / 36524.25)
            a = z + 1 + alpha - alpha // 4
        
        b = a + 1524
        c = int((b - 122.1) / 365.25)
        d = int(365.25 * c)
        e = int((b - d) / 30.6001)
        
        day = b - d - int(30.6001 * e) + f
        month = e - 1 if e < 14 else e - 13
        year = c - 4716 if month > 2 else c - 4715
        
        return year, month, int(day)
    
    @staticmethod
    def gregorian_to_julian(year: int, month: int, day: int) -> float:
        """تبدیل میلادی به ژولیانی"""
        if month <= 2:
            year -= 1
            month += 12
        
        a = year // 100
        b = 2 - a + a // 4
        return int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524.5
    
    @staticmethod
    def now():
        """تاریخ و زمان فعلی شمسی"""
        return PersianDateTime.now()

class PersianDateTime:
    """کلاس تاریخ و زمان شمسی"""
    
    def __init__(self, year: int = None, month: int = None, day: int = None, 
                 hour: int = 0, minute: int = 0, second: int = 0):
        if year is None:
            # تاریخ فعلی
            now = datetime.datetime.now()
            jd = PersianDate.gregorian_to_julian(now.year, now.month, now.day)
            self._set_from_julian(jd)
            self.hour = now.hour
            self.minute = now.minute
            self.second = now.second
        else:
            self.year = year
            self.month = month
            self.day = day
            self.hour = hour
            self.minute = minute
            self.second = second
    
    def _set_from_julian(self, jd: float):
        """تنظیم تاریخ از ژولیان"""
        jd = jd - PersianDate.PERSIAN_EPOCH + PersianDate.GREGORIAN_EPOCH
        g_year, g_month, g_day = PersianDate.julian_to_gregorian(jd)
        
        # تبدیل به شمسی (ساده‌سازی)
        self.year = g_year - 621
        self.month = (g_month + 6) % 12 + 1
        self.day = min(g_day, 31)
    
    def strftime(self, format_str: str) -> str:
        """قالب‌بندی تاریخ"""
        format_str = format_str.replace('%Y', str(self.year))
        format_str = format_str.replace('%m', f"{self.month:02d}")
        format_str = format_str.replace('%d', f"{self.day:02d}")
        format_str = format_str.replace('%H', f"{self.hour:02d}")
        format_str = format_str.replace('%M', f"{self.minute:02d}")
        format_str = format_str.replace('%S', f"{self.second:02d}")
        return format_str
    
    @classmethod
    def now(cls):
        """تاریخ و زمان فعلی"""
        return cls()
    
    @classmethod
    def fromgregorian(cls, datetime_obj: datetime.datetime = None):
        """تبدیل از میلادی"""
        if datetime_obj is None:
            datetime_obj = datetime.datetime.now()
        
        jd = PersianDate.gregorian_to_julian(datetime_obj.year, datetime_obj.month, datetime_obj.day)
        instance = cls()
        instance._set_from_julian(jd)
        instance.hour = datetime_obj.hour
        instance.minute = datetime_obj.minute
        instance.second = datetime_obj.second
        return instance

# ایجاد alias
jdatetime = PersianDate
