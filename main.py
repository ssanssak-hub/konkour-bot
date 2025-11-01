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
from reminder.auto_reminder_scheduler import init_auto_reminder_scheduler
from reminder.auto_reminder_admin import AutoReminderAdminStates

# 🔥 ایمپورت سیستم ریمایندر پیشرفته
from reminder.advanced_reminder_states import AdvancedReminderStates
from reminder.advanced_reminder_scheduler import init_advanced_reminder_scheduler
from reminder.advanced_reminder_handlers import (
    advanced_reminders_admin_handler,
    start_add_advanced_reminder,
    list_advanced_reminders_admin,
    edit_advanced_reminder_handler,
    delete_advanced_reminder_handler,
    toggle_advanced_reminder_handler,
    handle_advanced_reminder_callback
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
    from handlers.main_handlers import handle_reminder_management
    await handle_reminder_management(message)

@dp.message(F.text == "👑 پنل مدیریت")
async def admin_panel_wrapper(message: types.Message):  # ✅ تغییر نام
    from handlers.main_handlers import handle_admin_panel
    await handle_admin_panel(message)

@dp.message(F.text == "🏠 منوی اصلی")
async def main_menu_wrapper(message: types.Message):
    from handlers.main_handlers import handle_back_to_main
    await handle_back_to_main(message)

# =============================================================================
# هندلرهای منوی اصلی - اضافه کردن این بخش
# =============================================================================

@dp.message(F.text == "🔔 یادآوری‌ها")
async def handle_reminders_submenu(message: types.Message):
    """هندلر منوی زیرمجموعه یادآوری‌ها"""
    from keyboards import reminders_submenu
    
    menu = reminders_submenu(user_id=message.from_user.id)
    
    await message.answer(
        "🔔 <b>منوی یادآوری‌ها</b>\n\n"
        "لطفاً نوع یادآوری مورد نظر را انتخاب کنید:",
        reply_markup=menu,
        parse_mode="HTML"
    )

@dp.message(F.text == "⏳ زمان‌سنجی کنکورها")
async def handle_exam_timing(message: types.Message):
    """هندلر منوی زمان‌سنجی کنکورها"""
    from handlers.main_handlers import handle_exam_timing
    await handle_exam_timing(message)

@dp.message(F.text == "📅 برنامه مطالعاتی پیشرفته")
async def handle_study_plan(message: types.Message):
    """هندلر منوی برنامه مطالعاتی"""
    from handlers.main_handlers import handle_study_plan
    await handle_study_plan(message)

@dp.message(F.text == "📊 آمار مطالعه حرفه‌ای")
async def handle_study_stats(message: types.Message):
    """هندلر منوی آمار مطالعه"""
    from handlers.main_handlers import handle_study_stats
    await handle_study_stats(message)

@dp.message(F.text == "🤖 ریمایندرهای پیشرفته")
async def handle_advanced_reminders_submenu(message: types.Message):
    """هندلر منوی ریمایندرهای پیشرفته - فقط برای ادمین"""
    from config import ADMIN_ID
    
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ دسترسی denied!")
        return
    
    await advanced_reminders_admin_handler(message)

# =============================================================================
# هندلرهای بازگشت
# =============================================================================

@dp.message(F.text == "🔙 بازگشت به یادآوری‌ها")
async def handle_back_to_reminders(message: types.Message):
    """هندلر بازگشت به منوی یادآوری‌ها"""
    from keyboards import reminders_submenu
    
    menu = reminders_submenu(user_id=message.from_user.id)
    
    await message.answer(
        "🔔 <b>منوی یادآوری‌ها</b>\n\n"
        "لطفاً نوع یادآوری مورد نظر را انتخاب کنید:",
        reply_markup=menu,
        parse_mode="HTML"
    )

@dp.message(F.text == "🔙 بازگشت به مدیریت")
async def back_to_management_wrapper(message: types.Message):
    """هندلر بازگشت به منوی اصلی مدیریت"""
    from handlers.main_handlers import handle_admin_panel
    await handle_admin_panel(message)

# --- هندلرهای جدید برای ریمایندرهای پیشرفته ادمین ---
@dp.message(F.text == "🤖 ریمایندرهای پیشرفته")
async def advanced_reminders_wrapper(message: types.Message):
    await advanced_reminders_admin_handler(message)

@dp.message(F.text == "📋 لیست ریمایندرهای پیشرفته")
async def list_advanced_reminders_wrapper(message: types.Message):
    await list_advanced_reminders_admin(message)

@dp.message(F.text == "➕ افزودن ریمایندر جدید")
async def add_advanced_reminder_wrapper(message: types.Message, state: FSMContext):
    await start_add_advanced_reminder(message, state)

@dp.message(F.text == "✏️ ویرایش ریمایندر")
async def edit_advanced_reminder_wrapper(message: types.Message):
    await edit_advanced_reminder_handler(message)

@dp.message(F.text == "🗑️ حذف ریمایندر")
async def delete_advanced_reminder_wrapper(message: types.Message):
    await delete_advanced_reminder_handler(message)

@dp.message(F.text == "🔔 فعال/غیرفعال")
async def toggle_advanced_reminder_wrapper(message: types.Message):
    await toggle_advanced_reminder_handler(message)

# --- هندلرهای state برای ریمایندرهای پیشرفته ---
@dp.message(AdvancedReminderStates.waiting_for_title)
async def advanced_title_wrapper(message: types.Message, state: FSMContext):
    from reminder.advanced_reminder_handlers import process_advanced_title
    await process_advanced_title(message, state)

@dp.message(AdvancedReminderStates.waiting_for_message)
async def advanced_message_wrapper(message: types.Message, state: FSMContext):
    from reminder.advanced_reminder_handlers import process_advanced_message
    await process_advanced_message(message, state)

@dp.message(AdvancedReminderStates.waiting_for_start_time)
async def advanced_start_time_wrapper(message: types.Message, state: FSMContext):
    from reminder.advanced_reminder_handlers import process_start_time
    await process_start_time(message, state)

@dp.message(AdvancedReminderStates.waiting_for_start_date)
async def advanced_start_date_wrapper(message: types.Message, state: FSMContext):
    from reminder.advanced_reminder_handlers import process_start_date
    await process_start_date(message, state)

@dp.message(AdvancedReminderStates.waiting_for_end_time)
async def advanced_end_time_wrapper(message: types.Message, state: FSMContext):
    from reminder.advanced_reminder_handlers import process_end_time
    await process_end_time(message, state)

@dp.message(AdvancedReminderStates.waiting_for_end_date)
async def advanced_end_date_wrapper(message: types.Message, state: FSMContext):
    from reminder.advanced_reminder_handlers import process_end_date
    await process_end_date(message, state)

@dp.message(AdvancedReminderStates.waiting_for_days_of_week)
async def advanced_days_of_week_wrapper(message: types.Message, state: FSMContext):
    from reminder.advanced_reminder_handlers import process_days_of_week
    await process_days_of_week(message, state)

@dp.message(AdvancedReminderStates.waiting_for_repeat_count)
async def advanced_repeat_count_wrapper(message: types.Message, state: FSMContext):
    from reminder.advanced_reminder_handlers import process_repeat_count
    await process_repeat_count(message, state)

@dp.message(AdvancedReminderStates.waiting_for_repeat_interval)
async def advanced_repeat_interval_wrapper(message: types.Message, state: FSMContext):
    from reminder.advanced_reminder_handlers import process_repeat_interval
    await process_repeat_interval(message, state)

@dp.message(AdvancedReminderStates.waiting_for_confirmation)
async def advanced_confirmation_wrapper(message: types.Message, state: FSMContext):
    from reminder.advanced_reminder_handlers import process_advanced_confirmation
    await process_advanced_confirmation(message, state)

# --- هندلرهای callback برای ریمایندرهای پیشرفته ---
@dp.callback_query(F.data.startswith("adv_"))
async def advanced_reminder_callback_wrapper(callback: types.CallbackQuery):
    await handle_advanced_reminder_callback(callback)

@dp.callback_query(F.data == "adv_admin:back")
async def advanced_admin_back_wrapper(callback: types.CallbackQuery):
    await handle_advanced_reminder_callback(callback)

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
async def handle_admin_callbacks(callback: types.CallbackQuery, state: FSMContext):  # ✅ تغییر نام
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
    from handlers.main_handlers import handle_auto_reminders
    await handle_auto_reminders(message)

@dp.message(F.text == "📋 مدیریت یادآوری")
async def reminder_manage_wrapper(message: types.Message):
    from reminder.reminder_handlers import manage_reminders_handler
    await manage_reminders_handler(message)

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
    from reminder.reminder_handlers import toggle_reminder_status
    await toggle_reminder_status(message)

@dp.message(F.text == "🔕 غیرفعال")
async def deactivate_reminders_wrapper(message: types.Message):
    from reminder.reminder_handlers import toggle_reminder_status
    await toggle_reminder_status(message)
    
@dp.message(F.text == "✏️ ویرایش")
async def edit_reminders_wrapper(message: types.Message):
    from reminder.reminder_handlers import edit_reminder_handler
    await edit_reminder_handler(message)

@dp.message(F.text == "🗑️ حذف")
async def delete_reminders_wrapper(message: types.Message):
    from reminder.reminder_handlers import delete_reminder_handler
    await delete_reminder_handler(message)

# --- هندلرهای callback برای مدیریت ---
@dp.callback_query(F.data.startswith("manage_"))
async def manage_reminder_callback_wrapper(callback: types.CallbackQuery):
    from reminder.reminder_handlers import handle_reminder_management_callback
    await handle_reminder_management_callback(callback)

# --- هندلرهای یادآوری خودکار برای کاربران عادی ---
@dp.message(F.text == "📋 لیست یادآوری‌ها")
async def list_auto_reminders_wrapper(message: types.Message):
    from reminder.auto_reminder_handlers import user_auto_reminders_list
    await user_auto_reminders_list(message)

@dp.message(F.text == "✅ فعال کردن")
async def enable_auto_reminders_wrapper(message: types.Message):
    from reminder.auto_reminder_handlers import toggle_user_auto_reminder
    await toggle_user_auto_reminder(message)

@dp.message(F.text == "❌ غیرفعال کردن")
async def disable_auto_reminders_wrapper(message: types.Message):
    from reminder.auto_reminder_handlers import toggle_user_auto_reminder
    await toggle_user_auto_reminder(message)

@dp.message(Command("test_reminder"))
async def test_reminder_wrapper(message: types.Message):
    """تست سیستم ریمایندر"""
    try:
        await reminder_scheduler.send_test_reminder_now(message.from_user.id)
        await message.answer("✅ ریمایندر تستی ارسال شد!")
    except Exception as e:
        await message.answer(f"❌ خطا در ارسال ریمایندر: {e}")

@dp.message(Command("test_advanced_reminder"))
async def test_advanced_reminder_wrapper(message: types.Message, state: FSMContext):
    """تست سیستم ریمایندر پیشرفته"""
    from config import ADMIN_ID
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ دسترسی denied!")
        return
    
    try:
        # ایجاد یک ریمایندر تستی
        test_data = {
            'title': 'تست ریمایندر پیشرفته',
            'message': 'این یک پیام تست برای ریمایندر پیشرفته است!',
            'start_time': '14:00',
            'start_date': '1404-01-01',
            'end_time': '23:59', 
            'end_date': '1404-12-29',
            'selected_days': [0, 1, 2, 3, 4, 5, 6],
            'repeat_count': 3,
            'repeat_interval': 10
        }
        
        await advanced_reminder_scheduler.send_test_advanced_reminder(message.from_user.id, test_data)
        await message.answer("✅ ریمایندر پیشرفته تستی ارسال شد!")
    except Exception as e:
        await message.answer(f"❌ خطا در ارسال ریمایندر پیشرفته: {e}")

# --- هندلرهای callback برای کاربران عادی ---
@dp.callback_query(F.data.startswith("auto_toggle:"))
async def auto_user_toggle_wrapper(callback: types.CallbackQuery):
    from reminder.auto_reminder_handlers import handle_auto_reminder_user_callback
    await handle_auto_reminder_user_callback(callback)

@dp.callback_query(F.data == "auto_user:back")
async def auto_user_back_wrapper(callback: types.CallbackQuery):
    from reminder.auto_reminder_handlers import handle_auto_reminder_user_callback
    await handle_auto_reminder_user_callback(callback)

# --- هندلرهای مدیریت ریمایندر خودکار برای ادمین ---
@dp.message(F.text == "📋 لیست ریمایندرها")
async def list_auto_reminders_admin_wrapper(message: types.Message):
    from reminder.auto_reminder_admin import list_auto_reminders_admin
    await list_auto_reminders_admin(message)

@dp.message(F.text == "➕ افزودن جدید")
async def add_auto_reminder_wrapper(message: types.Message, state: FSMContext):
    from reminder.auto_reminder_admin import start_add_auto_reminder
    await start_add_auto_reminder(message, state)

@dp.message(F.text == "🗑️ حذف")
async def delete_auto_reminder_wrapper(message: types.Message):
    from reminder.auto_reminder_admin import delete_auto_reminder_handler
    await delete_auto_reminder_handler(message)

@dp.message(F.text == "🔔 فعال کردن")
async def enable_auto_admin_wrapper(message: types.Message):
    from reminder.auto_reminder_admin import toggle_auto_reminder_status
    await toggle_auto_reminder_status(message)

@dp.message(F.text == "🔕 غیرفعال کردن")
async def disable_auto_admin_wrapper(message: types.Message):
    from reminder.auto_reminder_admin import toggle_auto_reminder_status
    await toggle_auto_reminder_status(message)

# --- هندلرهای state برای ادمین ---
@dp.message(AutoReminderAdminStates.adding_title)
async def auto_admin_title_wrapper(message: types.Message, state: FSMContext):
    from reminder.auto_reminder_admin import process_add_title
    await process_add_title(message, state)

@dp.message(AutoReminderAdminStates.adding_message)
async def auto_admin_message_wrapper(message: types.Message, state: FSMContext):
    from reminder.auto_reminder_admin import process_add_message
    await process_add_message(message, state)

@dp.message(AutoReminderAdminStates.adding_days)
async def auto_admin_days_wrapper(message: types.Message, state: FSMContext):
    from reminder.auto_reminder_admin import process_add_days
    await process_add_days(message, state)

@dp.message(AutoReminderAdminStates.selecting_exams)
async def auto_admin_exams_wrapper(message: types.Message, state: FSMContext):
    from reminder.auto_reminder_admin import process_admin_exam_selection
    await process_admin_exam_selection(message, state)

@dp.message(AutoReminderAdminStates.confirmation)
async def auto_admin_confirmation_wrapper(message: types.Message, state: FSMContext):
    from reminder.auto_reminder_admin import process_admin_confirmation
    await process_admin_confirmation(message, state)

# --- هندلرهای callback برای ادمین ---
@dp.callback_query(F.data.startswith("auto_admin_"))
async def auto_admin_callback_wrapper(callback: types.CallbackQuery):
    from reminder.auto_reminder_admin import handle_auto_reminder_admin_callback
    await handle_auto_reminder_admin_callback(callback)

@dp.callback_query(F.data == "auto_admin:back")
async def auto_admin_back_wrapper(callback: types.CallbackQuery):
    from reminder.auto_reminder_admin import handle_auto_reminder_admin_callback
    await handle_auto_reminder_admin_callback(callback)

# --- هندلر callback برای ریمایندرهای خودکار ---
@dp.callback_query(F.data.startswith("auto_"))
async def auto_reminder_callback_wrapper(callback: types.CallbackQuery):
    from config import ADMIN_ID
    
    if callback.from_user.id == ADMIN_ID:
        from reminder.auto_reminder_admin import handle_auto_reminder_admin_callback
        await handle_auto_reminder_admin_callback(callback)
    else:
        from reminder.auto_reminder_handlers import handle_auto_reminder_user_callback
        await handle_auto_reminder_user_callback(callback)

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

@dp.message(PersonalReminderStates.selecting_repetition)
async def personal_reminder_repetition_wrapper(message: types.Message, state: FSMContext):
    from reminder.reminder_handlers import process_repetition_selection
    await process_repetition_selection(message, state)

@dp.message(PersonalReminderStates.selecting_days)
async def personal_reminder_days_wrapper(message: types.Message, state: FSMContext):
    from reminder.reminder_handlers import process_personal_days_selection
    await process_personal_days_selection(message, state)

@dp.message(PersonalReminderStates.entering_time)
async def personal_reminder_time_wrapper(message: types.Message, state: FSMContext):
    from reminder.reminder_handlers import process_personal_time_input
    await process_personal_time_input(message, state)

@dp.message(PersonalReminderStates.entering_start_date)
async def personal_reminder_start_date_wrapper(message: types.Message, state: FSMContext):
    from reminder.reminder_handlers import process_personal_start_date
    await process_personal_start_date(message, state)

@dp.message(PersonalReminderStates.confirmation)
async def personal_reminder_confirmation_wrapper(message: types.Message, state: FSMContext):
    from reminder.reminder_handlers import process_personal_confirmation
    await process_personal_confirmation(message, state)

@dp.message(PersonalReminderStates.entering_custom_interval)
async def personal_reminder_custom_interval_wrapper(message: types.Message, state: FSMContext):
    from reminder.reminder_handlers import process_personal_custom_interval
    await process_personal_custom_interval(message, state)

# --- هندلر عمومی بازگشت ---
@dp.message(F.text == "🔙 بازگشت")
async def back_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.clear()
    from handlers.main_handlers import handle_back_to_main
    await handle_back_to_main(message)

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

    # --- راه‌اندازی سیستم‌های زمان‌بندی ---
    auto_reminder_scheduler = init_auto_reminder_scheduler(bot)
    asyncio.create_task(auto_reminder_scheduler.start_scheduler())
    logger.info("🚀 سیستم ریمایندرهای خودکار شروع به کار کرد")
    
    # 🔥 راه‌اندازی سیستم ریمایندرهای پیشرفته
    advanced_reminder_scheduler = init_advanced_reminder_scheduler(bot)
    asyncio.create_task(advanced_reminder_scheduler.start_scheduler())
    logger.info("🚀 سیستم ریمایندرهای پیشرفته شروع به کار کرد")
    
    logger.info("🔄 شروع Polling روی Railway...")
    
    # شروع دریافت پیام‌ها
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
