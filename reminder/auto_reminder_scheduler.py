"""
سیستم زمان‌بندی برای ارسال ریمایندرهای خودکار
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import pytz

from reminder.auto_reminder_system import auto_reminder_system
from exam_data import EXAMS_1405
from utils.time_utils import get_current_persian_datetime

logger = logging.getLogger(__name__)
TEHRAN_TIMEZONE = pytz.timezone('Asia/Tehran')

class AutoReminderScheduler:
    def __init__(self, bot):
        self.bot = bot
        self.is_running = False
        self.check_interval = 3600  # چک هر ۱ ساعت
        
    async def start_scheduler(self):
        """شروع سیستم زمان‌بندی ریمایندرهای خودکار"""
        if self.is_running:
            return
            
        self.is_running = True
        logger.info("🚀 سیستم ریمایندرهای خودکار شروع به کار کرد")
        
        while self.is_running:
            try:
                await self.check_and_send_auto_reminders()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"خطا در سیستم ریمایندرهای خودکار: {e}")
                await asyncio.sleep(60)
                
    async def stop_scheduler(self):
        """توقف سیستم زمان‌بندی"""
        self.is_running = False
        logger.info("🛑 سیستم ریمایندرهای خودکار متوقف شد")
        
    async def check_and_send_auto_reminders(self):
        """چک و ارسال ریمایندرهای خودکار"""
        try:
            now = datetime.now(TEHRAN_TIMEZONE)
            current_date = now.strftime("%Y-%m-%d")
            
            logger.info(f"🔍 چک ریمایندرهای خودکار - تاریخ: {current_date}")
            
            # دریافت ریمایندرهای خودکار فعال
            auto_reminders = auto_reminder_system.get_active_auto_reminders()
            
            for reminder in auto_reminders:
                await self.check_reminder_for_today(reminder, now)
                
        except Exception as e:
            logger.error(f"خطا در چک ریمایندرهای خودکار: {e}")

    async def check_reminder_for_today(self, reminder: Dict[str, Any], now: datetime):
        """بررسی آیا این ریمایندر باید امروز ارسال شود"""
        try:
            # محاسبه تاریخ هدف برای هر کنکور
            for exam_key in reminder['exam_keys']:
                if exam_key in EXAMS_1405:
                    exam = EXAMS_1405[exam_key]
                    target_date = await self.calculate_target_date(exam, reminder['days_before_exam'])
                    
                    if target_date and target_date.strftime("%Y-%m-%d") == now.strftime("%Y-%m-%d"):
                        # امروز روز ارساله
                        await self.send_auto_reminder_to_users(reminder, exam)
                        
        except Exception as e:
            logger.error(f"خطا در بررسی ریمایندر {reminder['id']}: {e}")

    async def calculate_target_date(self, exam: Dict[str, Any], days_before: int) -> datetime:
        """محاسبه تاریخ هدف برای ارسال ریمایندر"""
        try:
            dates = exam["date"] if isinstance(exam["date"], list) else [exam["date"]]
            
            for date_tuple in dates:
                if len(date_tuple) == 3:
                    exam_date = datetime(date_tuple[0], date_tuple[1], date_tuple[2])
                    exam_date = TEHRAN_TIMEZONE.localize(exam_date)
                    
                    # تاریخ هدف = تاریخ کنکور - days_before
                    target_date = exam_date - timedelta(days=days_before)
                    return target_date
                    
        except Exception as e:
            logger.error(f"خطا در محاسبه تاریخ هدف: {e}")
        
        return None

    async def send_auto_reminder_to_users(self, reminder: Dict[str, Any], exam: Dict[str, Any]):
        """ارسال ریمایندر خودکار به کاربران"""
        try:
            # دریافت کاربرانی که این ریمایندر برایشان فعال است
            user_ids = auto_reminder_system.get_users_for_auto_reminder(reminder['id'])
            
            if not user_ids:
                logger.info(f"⚠️ هیچ کاربر فعالی برای ریمایندر {reminder['id']} پیدا نشد")
                return
            
            message = await self.create_auto_reminder_message(reminder, exam)
            successful_sends = 0
            
            for user_id in user_ids:
                try:
                    await self.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode="HTML"
                    )
                    successful_sends += 1
                    
                    # وقفه کوتاه برای جلوگیری از محدودیت تلگرام
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"❌ خطا در ارسال ریمایندر به کاربر {user_id}: {e}")
            
            logger.info(f"✅ ریمایندر خودکار {reminder['id']} به {successful_sends} کاربر ارسال شد")
            
        except Exception as e:
            logger.error(f"خطا در ارسال ریمایندر خودکار: {e}")

    async def create_auto_reminder_message(self, reminder: Dict[str, Any], exam: Dict[str, Any]) -> str:
        """ایجاد پیام ریمایندر خودکار"""
        current_time = get_current_persian_datetime()
        
        message = (
            f"🤖 <b>یادآوری خودکار</b>\n\n"
            f"📝 <b>{reminder['title']}</b>\n\n"
            f"{reminder['message']}\n\n"
            f"🎯 <b>کنکور:</b> {exam['name']}\n"
            f"📅 <b>تاریخ کنکور:</b> {exam['persian_date']}\n"
            f"⏰ <b>این یادآوری:</b> {reminder['days_before_exam']} روز قبل از کنکور\n\n"
            f"🕒 <i>زمان ارسال: {current_time['full_time']}</i>\n"
            f"💪 <b>موفق باشید!</b>"
        )
        
        return message

# ایجاد instance اصلی
auto_reminder_scheduler = None

def init_auto_reminder_scheduler(bot):
    """مقداردهی اولیه سیستم ریمایندرهای خودکار"""
    global auto_reminder_scheduler
    auto_reminder_scheduler = AutoReminderScheduler(bot)
    return auto_reminder_scheduler
