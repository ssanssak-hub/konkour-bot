"""
سیستم زمان‌بندی و ارسال ریمایندرها - نسخه کامل با تاریخ میلادی
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pytz
import time

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
        self.last_check = None
        self.stats = {
            'total_checks': 0,
            'total_reminders_sent': 0,
            'last_successful_check': None,
            'errors': 0
        }
        
    async def start_scheduler(self):
        """شروع سیستم زمان‌بندی"""
        if self.is_running:
            logger.warning("⚠️ سیستم ریمایندر در حال اجراست")
            return
            
        self.is_running = True
        logger.info("🚀 سیستم ریمایندر شروع به کار کرد")
        
        # بارگذاری اولیه ریمایندرهای فعال
        active_reminders = reminder_db.get_active_exam_reminders()
        logger.info(f"📥 {len(active_reminders)} ریمایندر فعال بارگذاری شد")
        
        while self.is_running:
            try:
                await self.check_and_send_reminders()
                self.stats['total_checks'] += 1
                self.stats['last_successful_check'] = datetime.now(TEHRAN_TIMEZONE)
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                self.stats['errors'] += 1
                logger.error(f"خطا در سیستم ریمایندر: {e}")
                await asyncio.sleep(10)  # وقفه کوتاه در صورت خطا
                
    async def stop_scheduler(self):
        """توقف سیستم زمان‌بندی"""
        self.is_running = False
        logger.info("🛑 سیستم ریمایندر متوقف شد")
        
    async def check_and_send_reminders(self):
        """چک و ارسال ریمایندرهای due"""
        try:
            now = datetime.now(TEHRAN_TIMEZONE)
            current_time_str = now.strftime("%H:%M")
            current_date_str = now.strftime("%Y-%m-%d")  # میلادی
            current_weekday = now.weekday()  # 0=Monday, 6=Sunday
            
            self.last_check = now
            
            logger.debug(f"🔍 چک ریمایندرها - زمان: {current_time_str} - تاریخ میلادی: {current_date_str} - روز هفته: {current_weekday}")
            
            # دریافت ریمایندرهای due از دیتابیس - با تاریخ میلادی
            due_reminders = reminder_db.get_due_reminders(
                current_date_str, 
                current_time_str, 
                current_weekday
            )
            
            if due_reminders:
                logger.info(f"📤 پیدا شد {len(due_reminders)} ریمایندر برای ارسال")
                
                # ارسال موازی ریمایندرها
                tasks = []
                for reminder in due_reminders:
                    task = asyncio.create_task(self.send_reminder(reminder))
                    tasks.append(task)
                
                # منتظر تمام شدن همه ارسال‌ها بمان
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # بررسی نتایج
                successful_sends = 0
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        logger.error(f"❌ خطا در ارسال ریمایندر {due_reminders[i]['id']}: {result}")
                    else:
                        successful_sends += 1
                
                self.stats['total_reminders_sent'] += successful_sends
                logger.info(f"✅ {successful_sends} ریمایندر با موفقیت ارسال شد")
                
            else:
                logger.debug("✅ هیچ ریمایندری برای ارسال پیدا نشد")
                
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"خطا در چک ریمایندرها: {e}")

    async def send_reminder(self, reminder: Dict[str, Any]):
        """ارسال ریمایندر"""
        start_time = time.time()
        
        try:
            user_id = reminder['user_id']
            
            if reminder['reminder_type'] == 'exam':
                success = await self.send_exam_reminder(reminder)
            elif reminder['reminder_type'] == 'personal':
                success = await self.send_personal_reminder(reminder)
            else:
                logger.warning(f"⚠️ نوع ریمایندر نامعتبر: {reminder['reminder_type']}")
                success = False
            
            delivery_time = int((time.time() - start_time) * 1000)  # میلی‌ثانیه
            
            if success:
                # ثبت لاگ ارسال موفق
                reminder_db.log_reminder_sent(
                    user_id, reminder['id'], reminder['reminder_type'],
                    status='sent', delivery_time_ms=delivery_time
                )
                logger.info(f"✅ ریمایندر {reminder['id']} برای کاربر {user_id} ارسال شد ({delivery_time}ms)")
            else:
                # ثبت لاگ ارسال ناموفق
                reminder_db.log_reminder_sent(
                    user_id, reminder['id'], reminder['reminder_type'],
                    status='failed', error_message='ارسال ناموفق',
                    delivery_time_ms=delivery_time
                )
                logger.warning(f"❌ ارسال ریمایندر {reminder['id']} برای کاربر {user_id} ناموفق بود")
            
            return success
            
        except Exception as e:
            delivery_time = int((time.time() - start_time) * 1000)
            reminder_db.log_reminder_sent(
                reminder['user_id'], reminder['id'], reminder['reminder_type'],
                status='failed', error_message=str(e),
                delivery_time_ms=delivery_time
            )
            logger.error(f"❌ خطا در ارسال ریمایندر {reminder['id']}: {e}")
            return False

    async def send_exam_reminder(self, reminder: Dict[str, Any]) -> bool:
        """ارسال ریمایندر کنکور"""
        try:
            user_id = reminder['user_id']
            sent_count = 0
            
            for exam_key in reminder['exam_keys']:
                if exam_key in EXAMS_1405:
                    exam = EXAMS_1405[exam_key]
                    message = await self.create_exam_reminder_message(exam)
                    
                    await self.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode="HTML"
                    )
                    sent_count += 1
                    
                    logger.debug(f"🎯 ریمایندر کنکور {exam['name']} برای کاربر {user_id} ارسال شد")
            
            return sent_count > 0
            
        except Exception as e:
            logger.error(f"خطا در ارسال ریمایندر کنکور: {e}")
            return False

    async def send_personal_reminder(self, reminder: Dict[str, Any]) -> bool:
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
            
            logger.debug(f"📝 ریمایندر شخصی برای کاربر {user_id} ارسال شد")
            return True
            
        except Exception as e:
            logger.error(f"خطا در ارسال ریمایندر شخصی: {e}")
            return False

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
            return True
            
        except Exception as e:
            logger.error(f"خطا در ارسال ریمایندر تستی: {e}")
            return False

    async def send_bulk_reminders(self, user_ids: List[int], message: str):
        """ارسال ریمایندر به چند کاربر"""
        successful_sends = 0
        failed_sends = 0
        
        for user_id in user_ids:
            try:
                await self.bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode="HTML"
                )
                successful_sends += 1
                logger.debug(f"✅ ریمایندر گروهی برای کاربر {user_id} ارسال شد")
                
                # وقفه کوتاه برای جلوگیری از محدودیت تلگرام
                await asyncio.sleep(0.1)
                
            except Exception as e:
                failed_sends += 1
                logger.error(f"❌ خطا در ارسال ریمایندر گروهی به کاربر {user_id}: {e}")
        
        logger.info(f"📤 ارسال گروهی کامل: {successful_sends} موفق, {failed_sends} ناموفق")
        return successful_sends, failed_sends

    def get_scheduler_stats(self) -> Dict[str, Any]:
        """دریافت آمار سیستم زمان‌بندی"""
        db_stats = reminder_db.get_reminder_stats()
        
        stats = {
            'scheduler_running': self.is_running,
            'total_checks': self.stats['total_checks'],
            'total_reminders_sent': self.stats['total_reminders_sent'],
            'errors': self.stats['errors'],
            'last_check': self.last_check,
            'last_successful_check': self.stats['last_successful_check'],
            'check_interval': self.check_interval
        }
        
        # ترکیب با آمار دیتابیس
        stats.update(db_stats)
        return stats

    async def health_check(self) -> Dict[str, Any]:
        """بررسی سلامت سیستم"""
        try:
            # تست اتصال به دیتابیس
            test_reminders = reminder_db.get_active_exam_reminders()
            db_healthy = True
            
            # تست ارسال (اگر ربات متصل است)
            bot_healthy = await self.bot.get_me()
            
            return {
                'status': 'healthy',
                'database': 'connected' if db_healthy else 'disconnected',
                'bot': 'connected' if bot_healthy else 'disconnected',
                'active_reminders': len(test_reminders),
                'scheduler_running': self.is_running,
                'last_check': self.last_check
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'scheduler_running': self.is_running
            }

# ایجاد instance اصلی
reminder_scheduler = None

def init_reminder_scheduler(bot):
    """مقداردهی اولیه سیستم ریمایندر"""
    global reminder_scheduler
    reminder_scheduler = ReminderScheduler(bot)
    return reminder_scheduler
