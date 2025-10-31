"""
سیستم زمان‌بندی پیشرفته برای ریمایندرهای ادمین
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import pytz

from reminder.reminder_database import reminder_db
from utils.time_utils import get_current_persian_datetime

logger = logging.getLogger(__name__)
TEHRAN_TIMEZONE = pytz.timezone('Asia/Tehran')

class AdvancedReminderScheduler:
    def __init__(self, bot):
        self.bot = bot
        self.is_running = False
        self.check_interval = 60  # چک هر ۱ دقیقه برای دقت بیشتر
        
    async def start_scheduler(self):
        """شروع سیستم زمان‌بندی ریمایندرهای پیشرفته"""
        if self.is_running:
            return
            
        self.is_running = True
        logger.info("🚀 سیستم ریمایندرهای پیشرفته شروع به کار کرد")
        
        while self.is_running:
            try:
                await self.check_and_send_advanced_reminders()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"خطا در سیستم ریمایندرهای پیشرفته: {e}")
                await asyncio.sleep(30)
                
    async def stop_scheduler(self):
        """توقف سیستم زمان‌بندی"""
        self.is_running = False
        logger.info("🛑 سیستم ریمایندرهای پیشرفته متوقف شد")
        
    async def check_and_send_advanced_reminders(self):
        """چک و ارسال ریمایندرهای پیشرفته"""
        try:
            now = datetime.now(TEHRAN_TIMEZONE)
            current_time = now.strftime("%H:%M")
            current_date = now.strftime("%Y-%m-%d")
            current_weekday = now.weekday()  # 0=شنبه, 6=جمعه
            
            # دریافت ریمایندرهای پیشرفته فعال
            advanced_reminders = reminder_db.get_admin_advanced_reminders()
            active_reminders = [r for r in advanced_reminders if r['is_active']]
            
            for reminder in active_reminders:
                await self.check_advanced_reminder_for_now(reminder, now, current_time, current_date, current_weekday)
                
        except Exception as e:
            logger.error(f"خطا در چک ریمایندرهای پیشرفته: {e}")

    async def check_advanced_reminder_for_now(self, reminder: Dict[str, Any], now: datetime, 
                                            current_time: str, current_date: str, current_weekday: int):
        """بررسی آیا این ریمایندر پیشرفته باید الان ارسال شود"""
        try:
            # بررسی تاریخ
            if not (reminder['start_date'] <= current_date <= reminder['end_date']):
                return
                
            # بررسی روز هفته
            if current_weekday not in reminder['days_of_week']:
                return
                
            # بررسی زمان
            if not (reminder['start_time'] <= current_time <= reminder['end_time']):
                return
            
            # اگر همه شرایط برقرار بود، ریمایندر رو ارسال کن
            await self.send_advanced_reminder_with_repeats(reminder, now)
            
        except Exception as e:
            logger.error(f"خطا در بررسی ریمایندر پیشرفته {reminder['id']}: {e}")

    async def send_advanced_reminder_with_repeats(self, reminder: Dict[str, Any], start_time: datetime):
        """ارسال ریمایندر پیشرفته با قابلیت تکرار"""
        try:
            repeat_count = reminder['repeat_count']
            repeat_interval = reminder['repeat_interval']
            
            if repeat_count == 0:
                logger.info(f"📝 ریمایندر پیشرفته {reminder['id']} فقط ثبت شده (بدون ارسال)")
                return
                
            elif repeat_count == 1:
                # ارسال یکبار
                await self.send_single_advanced_reminder(reminder, start_time)
                
            else:
                # ارسال با تکرار
                for i in range(repeat_count):
                    send_time = start_time + timedelta(seconds=repeat_interval * i)
                    
                    if i > 0:
                        # محاسبه زمان باقی‌مانده تا ارسال بعدی
                        wait_time = (send_time - datetime.now(TEHRAN_TIMEZONE)).total_seconds()
                        if wait_time > 0:
                            await asyncio.sleep(wait_time)
                    
                    await self.send_single_advanced_reminder(reminder, send_time, i + 1, repeat_count)
            
            logger.info(f"✅ ریمایندر پیشرفته {reminder['id']} با {repeat_count} تکرار ارسال شد")
            
        except Exception as e:
            logger.error(f"خطا در ارسال ریمایندر پیشرفته {reminder['id']}: {e}")

    async def send_single_advanced_reminder(self, reminder: Dict[str, Any], send_time: datetime, 
                                          current_repeat: int = 1, total_repeats: int = 1):
        """ارسال یک نمونه از ریمایندر پیشرفته"""
        try:
            # دریافت همه کاربران فعال ربات - با کوئری مستقیم
            from database import Database
            db = Database()
            
            # استفاده از کوئری مستقیم به جای تابع get_active_users
            active_users = db.execute_query("""
                SELECT user_id, username, first_name, last_name 
                FROM users 
                WHERE is_active = 1
            """, fetch_all=True)
            
            if not active_users:
                logger.info(f"⚠️ هیچ کاربر فعالی برای ریمایندر پیشرفته {reminder['id']} پیدا نشد")
                return
            
            message = await self.create_advanced_reminder_message(reminder, current_repeat, total_repeats)
            successful_sends = 0
            
            for user in active_users:
                try:
                    await self.bot.send_message(
                        chat_id=user['user_id'],
                        text=message,
                        parse_mode="HTML"
                    )
                    successful_sends += 1
                    
                    # وقفه کوتاه برای جلوگیری از محدودیت تلگرام
                    await asyncio.sleep(0.1)  # افزایش زمان برای امنیت بیشتر
                    
                except Exception as e:
                    logger.error(f"❌ خطا در ارسال ریمایندر پیشرفته به کاربر {user['user_id']}: {e}")
            
            # ثبت لاگ
            reminder_db.log_reminder_sent(
                user_id=0,  # 0 برای ریمایندرهای عمومی ادمین
                reminder_id=reminder['id'],
                reminder_type='admin_advanced',
                status='sent',
                delivery_time_ms=int((datetime.now(TEHRAN_TIMEZONE) - send_time).total_seconds() * 1000)
            )
            
            # به‌روزرسانی تعداد ارسال‌ها
            self.update_advanced_reminder_sent_count(reminder['id'])
            
            logger.info(f"✅ ریمایندر پیشرفته {reminder['id']} (تکرار {current_repeat}/{total_repeats}) به {successful_sends} کاربر ارسال شد")
            
        except Exception as e:
            logger.error(f"خطا در ارسال تکی ریمایندر پیشرفته: {e}")

    def update_advanced_reminder_sent_count(self, reminder_id: int):
        """به‌روزرسانی تعداد ارسال‌های ریمایندر پیشرفته"""
        try:
            query = """
            UPDATE advanced_reminders 
            SET total_sent = total_sent + 1, 
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """
            reminder_db.execute_query(query, (reminder_id,))
        except Exception as e:
            logger.error(f"خطا در به‌روزرسانی تعداد ارسال‌های ریمایندر {reminder_id}: {e}")

    async def create_advanced_reminder_message(self, reminder: Dict[str, Any], 
                                             current_repeat: int = 1, total_repeats: int = 1) -> str:
        """ایجاد پیام ریمایندر پیشرفته"""
        current_time = get_current_persian_datetime()
        
        repeat_info = ""
        if total_repeats > 1:
            repeat_info = f"\n🔄 تکرار: {current_repeat} از {total_repeats}"
        
        message = (
            f"🤖 <b>یادآوری پیشرفته</b>\n\n"
            f"📝 <b>{reminder['title']}</b>\n\n"
            f"{reminder['message']}\n\n"
            f"⏰ <b>زمان ارسال:</b> {current_time['full_time']}"
            f"{repeat_info}\n\n"
            f"💪 <b>موفق باشید!</b>"
        )
        
        return message

    async def send_test_advanced_reminder(self, admin_id: int, reminder_data: Dict[str, Any]):
        """ارسال تست ریمایندر پیشرفته به ادمین"""
        try:
            test_message = await self.create_test_advanced_reminder_message(reminder_data)
            
            await self.bot.send_message(
                chat_id=admin_id,
                text=test_message,
                parse_mode="HTML"
            )
            
            logger.info(f"✅ تست ریمایندر پیشرفته به ادمین {admin_id} ارسال شد")
            
        except Exception as e:
            logger.error(f"خطا در ارسال تست ریمایندر پیشرفته: {e}")
            raise

    async def create_test_advanced_reminder_message(self, reminder_data: Dict[str, Any]) -> str:
        """ایجاد پیام تست ریمایندر پیشرفته"""
        current_time = get_current_persian_datetime()
        
        day_mapping = {
            0: "شنبه", 1: "یکشنبه", 2: "دوشنبه",
            3: "سه‌شنبه", 4: "چهارشنبه", 5: "پنجشنبه", 6: "جمعه"
        }
        
        days_text = "، ".join([day_mapping[day] for day in reminder_data.get('selected_days', [])])
        
        repeat_count = reminder_data.get('repeat_count', 1)
        repeat_interval = reminder_data.get('repeat_interval', 0)
        
        if repeat_count == 0:
            repeat_text = "فقط ثبت (بدون ارسال)"
        elif repeat_count == 1:
            repeat_text = "ارسال یکبار"
        else:
            repeat_text = f"ارسال {repeat_count} بار با فاصله {repeat_interval} ثانیه"
        
        message = (
            f"🧪 <b>تست ریمایندر پیشرفته</b>\n\n"
            f"📝 <b>عنوان:</b> {reminder_data.get('title', 'تست')}\n"
            f"📄 <b>متن:</b> {reminder_data.get('message', 'این یک پیام تست است')}\n\n"
            f"⏰ <b>ساعت شروع:</b> {reminder_data.get('start_time', '14:00')}\n"
            f"📅 <b>تاریخ شروع:</b> {reminder_data.get('start_date', '1404-01-01')}\n"
            f"⏰ <b>ساعت پایان:</b> {reminder_data.get('end_time', '23:59')}\n"
            f"📅 <b>تاریخ پایان:</b> {reminder_data.get('end_date', '1404-12-29')}\n"
            f"📆 <b>روزهای هفته:</b> {days_text}\n"
            f"🔢 <b>تکرار:</b> {repeat_text}\n\n"
            f"🕒 <b>زمان تست:</b> {current_time['full_time']}\n\n"
            f"✅ <b>این یک پیام تست است!</b>"
        )
        
        return message

# ایجاد instance اصلی
advanced_reminder_scheduler = None

def init_advanced_reminder_scheduler(bot):
    """مقداردهی اولیه سیستم ریمایندرهای پیشرفته"""
    global advanced_reminder_scheduler
    advanced_reminder_scheduler = AdvancedReminderScheduler(bot)
    return advanced_reminder_scheduler
