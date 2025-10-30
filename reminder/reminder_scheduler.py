"""
سیستم زمان‌بندی و ارسال ریمایندرها
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import pytz

from reminder.reminder_database import reminder_db
from exam_data import EXAMS_1405
from utils.time_utils import get_current_persian_datetime, format_time_remaining

logger = logging.getLogger(__name__)

# تنظیم تایم‌زون تهران
TEHRAN_TIMEZONE = pytz.timezone('Asia/Tehran')

class ReminderScheduler:
    def __init__(self, bot):
        self.bot = bot
        self.is_running = False
        self.check_interval = 60  # چک هر ۱ دقیقه
        
    async def start_scheduler(self):
        """شروع سیستم زمان‌بندی"""
        if self.is_running:
            return
            
        self.is_running = True
        logger.info("🚀 سیستم ریمایندر شروع به کار کرد")
        
        while self.is_running:
            try:
                await self.check_and_send_reminders()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"خطا در سیستم ریمایندر: {e}")
                await asyncio.sleep(10)  # انتظار در صورت خطا
                
    async def stop_scheduler(self):
        """توقف سیستم زمان‌بندی"""
        self.is_running = False
        logger.info("🛑 سیستم ریمایندر متوقف شد")
        
    async def check_and_send_reminders(self):
        """چک و ارسال ریمایندرهای due"""
        now = datetime.now(TEHRAN_TIMEZONE)
        current_time_str = now.strftime("%H:%M")
        current_date_str = now.strftime("%Y-%m-%d")
        current_weekday = now.weekday()
        
        logger.debug(f"🔍 چک ریمایندرها - زمان: {current_time_str} - روز: {current_weekday}")
        
        # چک ریمایندرهای کنکور
        await self.check_exam_reminders(now, current_time_str, current_weekday)
        
        # چک ریمایندرهای شخصی
        await self.check_personal_reminders(now, current_time_str, current_weekday)
        
    async def check_exam_reminders(self, now: datetime, current_time_str: str, current_weekday: int):
        """چک ریمایندرهای کنکور"""
        # تبدیل زمان به فرمت فارسی برای تطابق
        persian_times_map = {
            "08:00": "۰۸:۰۰", "10:00": "۱۰:۰۰", "12:00": "۱۲:۰۰", "14:00": "۱۴:۰۰",
            "16:00": "۱۶:۰۰", "18:00": "۱۸:۰۰", "20:00": "۲۰:۰۰", "22:00": "۲۲:۰۰"
        }
        
        current_time_persian = persian_times_map.get(current_time_str, current_time_str)
        
        # دریافت همه ریمایندرهای فعال
        # TODO: این تابع رو در دیتابیس اضافه کنیم
        all_reminders = []  # برای تست
        
        for reminder in all_reminders:
            try:
                # چک فعال بودن
                if not reminder['is_active']:
                    continue
                    
                # چک روز هفته
                if current_weekday not in reminder['days_of_week']:
                    continue
                    
                # چک ساعت
                if current_time_persian not in reminder['specific_times']:
                    continue
                    
                # چک تاریخ (شروع و پایان)
                if not self.is_date_in_range(now, reminder['start_date'], reminder['end_date']):
                    continue
                    
                # ارسال ریمایندر
                await self.send_exam_reminder(reminder)
                
            except Exception as e:
                logger.error(f"خطا در پردازش ریمایندر {reminder['id']}: {e}")
                
    async def check_personal_reminders(self, now: datetime, current_time_str: str, current_weekday: int):
        """چک ریمایندرهای شخصی"""
        # TODO: پیاده‌سازی مشابه ریمایندرهای کنکور
        pass
        
    async def send_exam_reminder(self, reminder: Dict[str, Any]):
        """ارسال ریمایندر کنکور"""
        try:
            user_id = reminder['user_id']
            exam_keys = reminder['exam_keys']
            
            for exam_key in exam_keys:
                if exam_key in EXAMS_1405:
                    exam = EXAMS_1405[exam_key]
                    message = await self.create_exam_reminder_message(exam)
                    
                    await self.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode="HTML"
                    )
                    
                    # لاگ ارسال
                    self.log_reminder_sent(user_id, reminder['id'], 'exam')
                    
                    logger.info(f"📤 ریمایندر کنکور {exam['name']} برای کاربر {user_id} ارسال شد")
                    
        except Exception as e:
            logger.error(f"خطا در ارسال ریمایندر: {e}")
            
    async def create_exam_reminder_message(self, exam: Dict[str, Any]) -> str:
        """ایجاد پیام ریمایندر کنکور"""
        from datetime import datetime
        
        # اطلاعات زمان فعلی
        current_time = get_current_persian_datetime()
        
        # محاسبه زمان باقی‌مانده
        now = datetime.now(TEHRAN_TIMEZONE)
        dates = exam["date"] if isinstance(exam["date"], list) else [exam["date"]]
        exam_dates = [datetime(*d) for d in dates]
        
        future_dates = [d for d in exam_dates if d > now]
        
        if not future_dates:
            countdown_text = "✅ برگزار شده"
            total_days = 0
        else:
            target = min(future_dates)
            countdown_text, total_days = format_time_remaining(target)
        
        # ساخت پیام
        message = (
            f"⏰ <b>یادآوری کنکور</b>\n\n"
            f"📘 <b>{exam['name']}</b>\n"
            f"📅 تاریخ: {exam['persian_date']}\n"
            f"🕒 ساعت: {exam['time']}\n\n"
            f"{countdown_text}\n"
            f"📆 تعداد روزهای باقی‌مانده: {total_days} روز\n\n"
            f"🕒 <i>زمان یادآوری: {current_time['full_time']}</i>\n"
            f"💪 <b>موفق باشید!</b>"
        )
        
        return message
        
    def is_date_in_range(self, current_date: datetime, start_date: str, end_date: str) -> bool:
        """چک کردن قرار داشتن تاریخ در بازه"""
        # TODO: پیاده‌سازی منطق چک تاریخ شمسی
        # فعلاً True برمی‌گردانیم
        return True
        
    def log_reminder_sent(self, user_id: int, reminder_id: int, reminder_type: str):
        """ثبت لاگ ارسال ریمایندر"""
        # TODO: اضافه کردن به دیتابیس
        pass
        
    async def send_test_reminder(self, user_id: int):
        """ارسال ریمایندر تستی"""
        test_exam = EXAMS_1405["ریاضی_فنی"]
        message = await self.create_exam_reminder_message(test_exam)
        
        await self.bot.send_message(
            chat_id=user_id,
            text=message,
            parse_mode="HTML"
        )

# ایجاد instance اصلی
reminder_scheduler = None

def init_reminder_scheduler(bot):
    """مقداردهی اولیه سیستم ریمایندر"""
    global reminder_scheduler
    reminder_scheduler = ReminderScheduler(bot)
    return reminder_scheduler
