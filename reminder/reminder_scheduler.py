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
                await asyncio.sleep(10)
                
    async def stop_scheduler(self):
        """توقف سیستم زمان‌بندی"""
        self.is_running = False
        logger.info("🛑 سیستم ریمایندر متوقف شد")
        
    async def check_and_send_reminders(self):
        """چک و ارسال ریمایندرهای due"""
        try:
            now = datetime.now(TEHRAN_TIMEZONE)
            current_time_str = now.strftime("%H:%M")
            current_date_str = now.strftime("%Y-%m-%d")
            current_weekday = now.weekday()
            
            logger.info(f"🔍 چک ریمایندرها - زمان: {current_time_str} - روز: {current_weekday}")
            
            # دریافت ریمایندرهای due از دیتابیس
            due_reminders = reminder_db.get_due_reminders(
                current_date_str, 
                current_time_str, 
                current_weekday
            )
            
            if due_reminders:
                logger.info(f"📤 پیدا شد {len(due_reminders)} ریمایندر برای ارسال")
                for reminder in due_reminders:
                    await self.send_reminder(reminder)
            else:
                logger.debug("✅ هیچ ریمایندری برای ارسال پیدا نشد")
                
        except Exception as e:
            logger.error(f"خطا در چک ریمایندرها: {e}")

    async def send_reminder(self, reminder: Dict[str, Any]):
        """ارسال ریمایندر"""
        try:
            user_id = reminder['user_id']
            
            if reminder['reminder_type'] == 'exam':
                await self.send_exam_reminder(reminder)
            elif reminder['reminder_type'] == 'personal':
                await self.send_personal_reminder(reminder)
                
            # ثبت لاگ ارسال
            reminder_db.log_reminder_sent(user_id, reminder['id'], reminder['reminder_type'])
            
            logger.info(f"✅ ریمایندر برای کاربر {user_id} ارسال شد")
            
        except Exception as e:
            logger.error(f"❌ خطا در ارسال ریمایندر: {e}")

    async def send_exam_reminder(self, reminder: Dict[str, Any]):
        """ارسال ریمایندر کنکور"""
        try:
            user_id = reminder['user_id']
            
            for exam_key in reminder['exam_keys']:
                if exam_key in EXAMS_1405:
                    exam = EXAMS_1405[exam_key]
                    message = await self.create_exam_reminder_message(exam)
                    
                    await self.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode="HTML"
                    )
                    
                    logger.info(f"🎯 ریمایندر کنکور {exam['name']} برای کاربر {user_id} ارسال شد")
                    
        except Exception as e:
            logger.error(f"خطا در ارسال ریمایندر کنکور: {e}")

    async def send_personal_reminder(self, reminder: Dict[str, Any]):
        """ارسال ریمایندر شخصی"""
        try:
            user_id = reminder['user_id']
            
            message = (
                f"⏰ <b>یادآوری شخصی</b>\n\n"
                f"📝 {reminder['title']}\n\n"
                f"📄 {reminder['message']}\n\n"
                f"🕒 <i>زمان یادآوری: {datetime.now(TEHRAN_TIMEZONE).strftime('%H:%M')}</i>\n"
                f"💪 <b>موفق باشید!</b>"
            )
            
            await self.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode="HTML"
            )
            
            logger.info(f"📝 ریمایندر شخصی برای کاربر {user_id} ارسال شد")
            
        except Exception as e:
            logger.error(f"خطا در ارسال ریمایندر شخصی: {e}")

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

    async def send_test_reminder_now(self, user_id: int):
        """ارسال ریمایندر تستی فوری"""
        try:
            test_exam = EXAMS_1405["ریاضی_فنی"]
            message = await self.create_exam_reminder_message(test_exam)
            
            await self.bot.send_message(
                chat_id=user_id,
                text=f"🧪 <b>تست سیستم ریمایندر</b>\n\n{message}",
                parse_mode="HTML"
            )
            
            logger.info(f"🧪 ریمایندر تستی برای کاربر {user_id} ارسال شد")
            
        except Exception as e:
            logger.error(f"خطا در ارسال ریمایندر تستی: {e}")

# ایجاد instance اصلی
reminder_scheduler = None

def init_reminder_scheduler(bot):
    """مقداردهی اولیه سیستم ریمایندر"""
    global reminder_scheduler
    reminder_scheduler = ReminderScheduler(bot)
    return reminder_scheduler
