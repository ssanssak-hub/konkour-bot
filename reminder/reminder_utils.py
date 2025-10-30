"""
ابزارها و توابع کمکی سیستم ریمایندر
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import re
import pytz

logger = logging.getLogger(__name__)

# تنظیم تایم‌زون تهران
TEHRAN_TIMEZONE = pytz.timezone('Asia/Tehran')

class ReminderValidator:
    """کلاس اعتبارسنجی داده‌های ریمایندر"""
    
    @staticmethod
    def validate_time_format(time_str: str) -> bool:
        """اعتبارسنجی فرمت زمان"""
        pattern = r'^([۰-۹]{1,2}):([۰-۹]{2})$'
        if re.match(pattern, time_str):
            return True
        
        # چک فرمت انگلیسی
        pattern_en = r'^([0-9]{1,2}):([0-9]{2})$'
        return bool(re.match(pattern_en, time_str))
    
    @staticmethod
    def validate_persian_date(date_str: str) -> bool:
        """اعتبارسنجی تاریخ شمسی"""
        pattern = r'^۱[۰-۴]|[۱-۹][۰-۹]?$'  # الگوی ساده‌شده
        return bool(re.match(pattern, date_str))
    
    @staticmethod
    def validate_days_of_week(days: List[int]) -> bool:
        """اعتبارسنجی روزهای هفته"""
        if not days:
            return False
        return all(0 <= day <= 6 for day in days)
    
    @staticmethod
    def validate_exam_keys(exam_keys: List[str], valid_exams: List[str]) -> bool:
        """اعتبارسنجی کلیدهای کنکور"""
        if not exam_keys:
            return False
        return all(exam in valid_exams for exam in exam_keys)

class ReminderFormatter:
    """کلاس فرمت‌بندی داده‌های ریمایندر"""
    
    @staticmethod
    def format_days_of_week(days: List[int]) -> str:
        """فرمت‌بندی روزهای هفته به فارسی"""
        days_map = {
            0: "شنبه", 1: "یکشنبه", 2: "دوشنبه", 
            3: "سه‌شنبه", 4: "چهارشنبه", 5: "پنجشنبه", 6: "جمعه"
        }
        
        if len(days) == 7:
            return "همه روزهای هفته"
        
        persian_days = [days_map[day] for day in sorted(days)]
        return "، ".join(persian_days)
    
    @staticmethod
    def format_times(times: List[str]) -> str:
        """فرمت‌بندی ساعات"""
        if not times:
            return "تعیین نشده"
        return "، ".join(times)
    
    @staticmethod
    def format_exams(exam_keys: List[str], exams_data: Dict) -> str:
        """فرمت‌بندی نام کنکورها"""
        exam_names = []
        for key in exam_keys:
            if key in exams_data:
                exam_names.append(exams_data[key]["name"])
        return "، ".join(exam_names) if exam_names else "تعیین نشده"
    
    @staticmethod
    def create_reminder_summary(reminder_data: Dict[str, Any], reminder_type: str) -> str:
        """ایجاد خلاصه ریمایندر"""
        if reminder_type == "exam":
            return ReminderFormatter._create_exam_reminder_summary(reminder_data)
        elif reminder_type == "personal":
            return ReminderFormatter._create_personal_reminder_summary(reminder_data)
        else:
            return "خلاصه نامعتبر"
    
    @staticmethod
    def _create_exam_reminder_summary(reminder_data: Dict[str, Any]) -> str:
        """خلاصه ریمایندر کنکور"""
        from exam_data import EXAMS_1405
        
        days_text = ReminderFormatter.format_days_of_week(reminder_data.get('selected_days', []))
        times_text = ReminderFormatter.format_times(reminder_data.get('selected_times', []))
        exams_text = ReminderFormatter.format_exams(reminder_data.get('selected_exams', []), EXAMS_1405)
        
        summary = (
            f"🎯 <b>کنکورها:</b> {exams_text}\n"
            f"🗓️ <b>روزها:</b> {days_text}\n"
            f"🕐 <b>ساعات:</b> {times_text}\n"
            f"📅 <b>شروع:</b> {reminder_data.get('start_date', 'تعیین نشده')}\n"
            f"📅 <b>پایان:</b> {reminder_data.get('end_date', 'تعیین نشده')}\n"
        )
        
        return summary
    
    @staticmethod
    def _create_personal_reminder_summary(reminder_data: Dict[str, Any]) -> str:
        """خلاصه ریمایندر شخصی"""
        repetition_map = {
            "once": "یکبار",
            "daily": "روزانه",
            "weekly": "هفتگی",
            "monthly": "ماهانه",
            "custom": "سفارشی"
        }
        
        repetition_text = repetition_map.get(reminder_data.get('repetition_type', ''), 'نامشخص')
        days_text = ReminderFormatter.format_days_of_week(reminder_data.get('days_of_week', []))
        
        summary = (
            f"📝 <b>عنوان:</b> {reminder_data.get('title', 'تعیین نشده')}\n"
            f"📄 <b>متن:</b> {reminder_data.get('message', 'تعیین نشده')}\n"
            f"🔁 <b>تکرار:</b> {repetition_text}\n"
            f"🗓️ <b>روزها:</b> {days_text}\n"
            f"🕐 <b>ساعت:</b> {reminder_data.get('specific_time', 'تعیین نشده')}\n"
            f"📅 <b>شروع:</b> {reminder_data.get('start_date', 'تعیین نشده')}\n"
        )
        
        if reminder_data.get('end_date'):
            summary += f"📅 <b>پایان:</b> {reminder_data['end_date']}\n"
        
        return summary

class TimeConverter:
    """کلاس تبدیل زمان‌ها"""
    
    @staticmethod
    def persian_to_english_time(persian_time: str) -> str:
        """تبدیل زمان فارسی به انگلیسی"""
        persian_to_english = {
            '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
            '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'
        }
        
        english_time = ''.join(persian_to_english.get(char, char) for char in persian_time)
        return english_time
    
    @staticmethod
    def english_to_persian_time(english_time: str) -> str:
        """تبدیل زمان انگلیسی به فارسی"""
        english_to_persian = {
            '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
            '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'
        }
        
        persian_time = ''.join(english_to_persian.get(char, char) for char in english_time)
        return persian_time

class ReminderAnalyzer:
    """کلاس تحلیل و آمار ریمایندرها"""
    
    @staticmethod
    def calculate_reminder_stats(reminders: List[Dict[str, Any]]) -> Dict[str, Any]:
        """محاسبه آمار ریمایندرها"""
        total = len(reminders)
        active = len([r for r in reminders if r.get('is_active', False)])
        inactive = total - active
        
        # گروه‌بندی بر اساس نوع
        exam_count = len([r for r in reminders if 'exam_keys' in r])
        personal_count = len([r for r in reminders if 'title' in r])
        
        return {
            'total': total,
            'active': active,
            'inactive': inactive,
            'exam_count': exam_count,
            'personal_count': personal_count,
            'active_percentage': (active / total * 100) if total > 0 else 0
        }

def setup_reminder_system(bot):
    """راه‌اندازی کامل سیستم ریمایندر"""
    from reminder.reminder_scheduler import init_reminder_scheduler
    
    # مقداردهی اولیه سیستم زمان‌بندی
    scheduler = init_reminder_scheduler(bot)
    
    logger.info("✅ سیستم ریمایندر راه‌اندازی شد")
    return scheduler

# ایجاد instance‌های全局
validator = ReminderValidator()
formatter = ReminderFormatter()
time_converter = TimeConverter()
analyzer = ReminderAnalyzer()
