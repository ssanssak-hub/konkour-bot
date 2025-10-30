import logging
import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی
load_dotenv()

# ایمپورت سیستم مقاوم‌سازی از پوشه utils
from utils.error_handlers import register_error_handlers
from utils.health_monitor import health_monitor

# ایمپورت سیستم ریمایندر
from reminder import setup_reminder_system
from reminder.reminder_handlers import (
    ExamReminderStates, PersonalReminderStates, ManagementStates
)

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# کش global
_CACHE = {}

# ایجاد ربات و دیسپچر
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8381121739:AAFB2YBMomBh9xhoI3Qn0VVuGaGlpea9fx8")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ثبت هندلرهای خطا
register_error_handlers(dp)

# --- راه‌اندازی سیستم ریمایندر ---
reminder_scheduler = setup_reminder_system(bot)

# --- ایمپورت هندلرهای اصلی ---
@dp.message(CommandStart())
async def start_wrapper(message: types.Message):
    from handlers.main_handlers import start_handler
    await start_handler(message, bot)

@dp.message(Command("test"))
async def test_wrapper(message: types.Message):
    from handlers.main_handlers import test_handler
    await test_handler(message)

@dp.message(Command("stats"))
async def stats_wrapper(message: types.Message):
    from handlers.main_handlers import stats_command_handler
    await stats_command_handler(message)

# --- هندلرهای منو ---
@dp.message(F.text == "⏳ زمان‌سنجی کنکورها")
async def exams_wrapper(message: types.Message):
    from handlers.menu_handlers import exams_menu_handler
    await exams_menu_handler(message)

@dp.message(F.text == "📅 برنامه مطالعاتی پیشرفته")
async def study_wrapper(message: types.Message):
    from handlers.menu_handlers import study_plan_handler
    await study_plan_handler(message)

@dp.message(F.text == "📊 آمار مطالعه حرفه‌ای")
async def stats_menu_wrapper(message: types.Message):
    from handlers.menu_handlers import stats_handler
    await stats_handler(message)

@dp.message(F.text == "🔔 مدیریت یادآوری‌ها")
async def reminders_wrapper(message: types.Message):
    from reminder.reminder_handlers import reminder_main_handler
    await reminder_main_handler(message)

@dp.message(F.text == "👑 پنل مدیریت")
async def admin_wrapper(message: types.Message):
    from handlers.menu_handlers import admin_handler
    await admin_handler(message)

# --- هندلرهای کنکور ---
@dp.callback_query(F.data.startswith("exam:"))
async def exam_wrapper(callback: types.CallbackQuery):
    from handlers.exam_handlers import exam_callback_handler
    await exam_callback_handler(callback)

@dp.callback_query(F.data == "exams:all")
async def all_exams_wrapper(callback: types.CallbackQuery):
    from handlers.exam_handlers import all_exams_handler
    await all_exams_handler(callback)

@dp.callback_query(F.data.startswith("refresh:"))
async def refresh_exam_wrapper(callback: types.CallbackQuery):
    from handlers.exam_handlers import refresh_exam_handler
    await refresh_exam_handler(callback)

@dp.callback_query(F.data == "exams:refresh")
async def refresh_all_wrapper(callback: types.CallbackQuery):
    from handlers.exam_handlers import refresh_all_exams_handler
    await refresh_all_exams_handler(callback)

@dp.callback_query(F.data == "exams:next")
async def next_exam_wrapper(callback: types.CallbackQuery):
    from handlers.exam_handlers import next_exam_handler
    await next_exam_handler(callback)

@dp.callback_query(F.data.startswith("details:"))
async def details_wrapper(callback: types.CallbackQuery):
    from handlers.exam_handlers import exam_details_handler
    await exam_details_handler(callback)

# --- هندلرهای بازگشت ---
@dp.callback_query(F.data == "main:back")
async def back_main_wrapper(callback: types.CallbackQuery):
    from handlers.back_handlers import back_to_main_handler
    await back_to_main_handler(callback)

# --- هندلرهای برنامه مطالعاتی ---
@dp.callback_query(F.data.startswith("study:"))
async def study_wrapper(callback: types.CallbackQuery, state: FSMContext):
    from handlers.study_handlers import study_callback_handler
    await study_callback_handler(callback, state)

# --- هندلرهای آمار ---
@dp.callback_query(F.data.startswith("stats:"))
async def stats_wrapper(callback: types.CallbackQuery):
    from handlers.stats_handlers import stats_callback_handler
    await stats_callback_handler(callback)

# --- هندلرهای مدیریت ---
@dp.callback_query(F.data.startswith("admin:"))
async def admin_wrapper(callback: types.CallbackQuery, state: FSMContext):
    from handlers.admin_handlers import admin_callback_handler
    await admin_callback_handler(callback, state)

# --- هندلرهای منوی ریمایندر ---
@dp.message(F.text == "⏰ یادآوری کنکورها")
async def reminder_exam_start_wrapper(message: types.Message, state: FSMContext):
    from reminder.reminder_handlers import start_exam_reminder
    await start_exam_reminder(message, state)

@dp.message(F.text == "📝 یادآوری شخصی")
async def reminder_personal_wrapper(message: types.Message, state: FSMContext):
    from reminder.reminder_handlers import start_personal_reminder
    await start_personal_reminder(message, state)

@dp.message(F.text == "🤖 یادآوری خودکار")
async def reminder_auto_wrapper(message: types.Message):
    from reminder.reminder_handlers import start_auto_reminders
    await start_auto_reminders(message)

@dp.message(F.text == "📋 مدیریت یادآوری")
async def reminder_manage_wrapper(message: types.Message):
    from reminder.reminder_handlers import manage_reminders_handler
    await manage_reminders_handler(message)

@dp.message(F.text == "🏠 منوی اصلی")
async def reminder_main_menu_wrapper(message: types.Message, state: FSMContext):
    await state.clear()
    from handlers.main_handlers import start_handler
    await start_handler(message, bot)

# --- هندلرهای مدیریت یادآوری ---
@dp.message(F.text == "📋 مشاهده همه")
async def view_all_reminders_wrapper(message: types.Message):
    from reminder.reminder_handlers import view_all_reminders
    await view_all_reminders(message)

@dp.message(F.text == "📊 آمار")
async def stats_reminders_wrapper(message: types.Message):
    from reminder.reminder_handlers import manage_reminders_handler
    await manage_reminders_handler(message)

@dp.message(F.text == "🔔 فعال")
async def activate_reminders_wrapper(message: types.Message):
    await message.answer("🔄 به زودی: فعال کردن یادآوری‌ها")

@dp.message(F.text == "🔕 غیرفعال")
async def deactivate_reminders_wrapper(message: types.Message):
    await message.answer("🔄 به زودی: غیرفعال کردن یادآوری‌ها")

@dp.message(F.text == "✏️ ویرایش")
async def edit_reminders_wrapper(message: types.Message):
    await message.answer("🔄 به زودی: ویرایش یادآوری‌ها")

@dp.message(F.text == "🗑️ حذف")
async def delete_reminders_wrapper(message: types.Message):
    await message.answer("🔄 به زودی: حذف یادآوری‌ها")

# --- هندلرهای یادآوری خودکار ---
@dp.message(F.text == "📋 لیست یادآوری‌ها")
async def list_auto_reminders_wrapper(message: types.Message):
    from reminder.reminder_handlers import list_auto_reminders
    await list_auto_reminders(message)

@dp.message(F.text == "✅ فعال کردن")
async def enable_auto_reminders_wrapper(message: types.Message):
    await message.answer("✅ یادآوری خودکار فعال شد")

@dp.message(F.text == "❌ غیرفعال کردن")
async def disable_auto_reminders_wrapper(message: types.Message):
    await message.answer("❌ یادآوری خودکار غیرفعال شد")

@dp.message(Command("test_reminder"))
async def test_reminder_wrapper(message: types.Message):
    """تست سیستم ریمایندر"""
    try:
        await reminder_scheduler.send_test_reminder_now(message.from_user.id)
        await message.answer("✅ ریمایندر تستی ارسال شد!")
    except Exception as e:
        await message.answer(f"❌ خطا در ارسال ریمایندر: {e}")
        
# --- هندلرهای state برای ریمایندر کنکور ---
@dp.message(ExamReminderStates.selecting_exams)
async def exam_reminder_exams_wrapper(message: types.Message, state: FSMContext):
    from reminder.reminder_handlers import process_exam_selection
    await process_exam_selection(message, state)

@dp.message(ExamReminderStates.selecting_days)
async def exam_reminder_days_wrapper(message: types.Message, state: FSMContext):
    from reminder.reminder_handlers import process_days_selection
    await process_days_selection(message, state)

@dp.message(ExamReminderStates.entering_time)
async def exam_reminder_time_wrapper(message: types.Message, state: FSMContext):
    from reminder.reminder_handlers import process_time_input
    await process_time_input(message, state)

@dp.message(ExamReminderStates.entering_start_date)
async def exam_reminder_start_date_wrapper(message: types.Message, state: FSMContext):
    from reminder.reminder_handlers import process_start_date
    await process_start_date(message, state)

@dp.message(ExamReminderStates.entering_end_date)
async def exam_reminder_end_date_wrapper(message: types.Message, state: FSMContext):
    from reminder.reminder_handlers import process_end_date
    await process_end_date(message, state)

@dp.message(ExamReminderStates.confirmation)
async def exam_reminder_confirmation_wrapper(message: types.Message, state: FSMContext):
    from reminder.reminder_handlers import process_confirmation
    await process_confirmation(message, state)

# --- هندلرهای state برای ریمایندر شخصی ---
@dp.message(PersonalReminderStates.entering_title)
async def personal_reminder_title_wrapper(message: types.Message, state: FSMContext):
    from reminder.reminder_handlers import process_personal_title
    await process_personal_title(message, state)

@dp.message(PersonalReminderStates.entering_message)
async def personal_reminder_message_wrapper(message: types.Message, state: FSMContext):
    from reminder.reminder_handlers import process_personal_message
    await process_personal_message(message, state)

# --- هندلر عمومی بازگشت ---
@dp.message(F.text == "🔙 بازگشت")
async def back_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.clear()
    from reminder.reminder_handlers import reminder_main_handler
    await reminder_main_handler(message)

# --- هندلر دیباگ ---
@dp.message()
async def debug_all_messages(message: types.Message):
    """هندلر دیباگ برای لاگ تمام پیام‌ها"""
    logger.info(f"📩 پیام دریافت شد: user_id={message.from_user.id}, text='{message.text}'")

async def main():
    """تابع اصلی با Polling"""
    # حذف وب‌هوک قبلی
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("🗑️ وب‌هوک حذف شد + پیام‌های pending پاک شد")
    
    # شروع سیستم ریمایندر در event loop اصلی
    asyncio.create_task(reminder_scheduler.start_scheduler())
    logger.info("🚀 سیستم ریمایندر شروع به کار کرد")
    
    logger.info("🔄 شروع Polling روی Railway...")
    
    # شروع دریافت پیام‌ها
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
