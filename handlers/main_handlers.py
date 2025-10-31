"""
هندلرهای منوی اصلی
"""
import logging
from aiogram import Bot, types, F
from aiogram.filters import Command, CommandStart

from config import MOTIVATIONAL_MESSAGES, ADMIN_ID
from keyboards import main_menu
from utils import check_user_membership, create_membership_keyboard
from database import Database

# ایمپورت ماژول‌های ریمایندر
from reminder.reminder_keyboards import create_reminder_main_menu
from reminder.auto_reminder_admin import auto_reminders_admin_handler
from reminder.auto_reminder_handlers import user_auto_reminders_list

logger = logging.getLogger(__name__)
db = Database()

async def start_handler(message: types.Message, bot: Bot):
    """هندلر دستور /start"""
    user = message.from_user
    logger.info(f"🎯 دریافت /start از {user.first_name} ({user.id})")
    
    # اصلاح: استفاده از user.id به جای user_id
    db.add_user(user.id, user.username or "", user.first_name, user.last_name or "")
    
    # بررسی عضویت
    is_member = await check_user_membership(bot, user.id)
    
    if not is_member:
        channels = db.get_mandatory_channels()
        if channels:
            channel_list = "\n".join([f"• {ch['channel_title']}" for ch in channels])
            
            await message.answer(
                f"👋 سلام {user.first_name} عزیز!\n\n"
                f"🚫 <b>برای استفاده از ربات باید در کانال‌های زیر عضو باشید:</b>\n\n"
                f"{channel_list}\n\n"
                f"پس از عضویت، دکمه '✅ بررسی عضویت' را بزنید.",
                reply_markup=create_membership_keyboard(),
                parse_mode="HTML"
            )
            return
    
    welcome = f"""
👋 سلام {user.first_name} عزیز!
به ربات کنکور ۱۴۰۵ خوش آمدی! 🎯

📚 <b>امکانات ربات:</b>
• ⏳ شمارش معکوس کنکورها
• 📅 برنامه مطالعاتی پیشرفته  
• 📊 آمار مطالعه حرفه‌ای
• 💫 پیام‌های انگیزشی
• 🎯 نکات طلایی مطالعه

از منوی زیر یکی از گزینه‌ها رو انتخاب کن:
"""
    await message.answer(welcome, reply_markup=main_menu(), parse_mode="HTML")

async def test_handler(message: types.Message):
    """هندلر دستور /test"""
    logger.info(f"🧪 دریافت /test از {message.from_user.id}")
    await message.answer("✅ ربات با aiogram + webhook کار می‌کند! تست موفق.")

async def stats_command_handler(message: types.Message):
    """دستور سریع برای مشاهده آمار"""
    from utils import calculate_study_progress
    user_stats = db.get_user_progress(message.from_user.id)
    progress = calculate_study_progress(user_stats['total_minutes'])
    
    await message.answer(
        f"📊 <b>آمار سریع شما</b>\n\n"
        f"🕒 کل زمان مطالعه: {user_stats['total_hours']} ساعت\n"
        f"📖 تعداد جلسات: {user_stats['total_sessions']} جلسه\n"
        f"📅 روزهای فعال: {user_stats['active_days']} روز\n"
        f"📈 پیشرفت کلی: {progress['percentage']}%\n"
        f"{progress['progress_bar']}\n\n"
        f"💪 {MOTIVATIONAL_MESSAGES[0]}",
        parse_mode="HTML"
    )

async def handle_reminder_management(message: types.Message):
    """هندلر منوی مدیریت یادآوری‌ها"""
    if message.from_user.id == ADMIN_ID:
        # نمایش منوی ادمین برای ریمایندرهای خودکار
        await auto_reminders_admin_handler(message)
    else:
        # نمایش منوی کاربر عادی
        await message.answer(
            "🔔 <b>مدیریت یادآوری‌ها</b>\n\n"
            "لطفاً گزینه مورد نظر را انتخاب کنید:",
            reply_markup=create_reminder_main_menu(),
            parse_mode="HTML"
        )

async def handle_auto_reminders(message: types.Message):
    """هندلر منوی یادآوری خودکار"""
    if message.from_user.id == ADMIN_ID:
        # نمایش منوی ادمین
        await auto_reminders_admin_handler(message)
    else:
        # نمایش منوی کاربر عادی
        await user_auto_reminders_list(message)

async def handle_exam_timing(message: types.Message):
    """هندلر منوی زمان‌سنجی کنکورها"""
    from handlers.exam_handlers import exam_menu_handler
    await exam_menu_handler(message)

async def handle_study_plan(message: types.Message):
    """هندلر منوی برنامه مطالعاتی"""
    from handlers.study_handlers import study_plan_menu_handler
    await study_plan_menu_handler(message)

async def handle_study_stats(message: types.Message):
    """هندلر منوی آمار مطالعه"""
    from handlers.stats_handlers import stats_menu_handler
    await stats_menu_handler(message)

async def handle_admin_panel(message: types.Message):
    """هندلر منوی پنل مدیریت"""
    if message.from_user.id == ADMIN_ID:
        from handlers.admin_handlers import admin_menu_handler
        await admin_menu_handler(message)
    else:
        await message.answer("❌ دسترسی denied!")

async def unknown_handler(message: types.Message):
    """هندلر پیام‌های ناشناخته"""
    logger.info(f"📝 پیام ناشناخته از {message.from_user.id}: {message.text}")
    await message.answer(
        "🤔 متوجه نشدم!\n\nلطفاً از دکمه‌های منو استفاده کنید:",
        reply_markup=main_menu()
    )

async def handle_back_to_main(message: types.Message):
    """هندلر بازگشت به منوی اصلی"""
    await message.answer(
        "🏠 <b>منوی اصلی</b>\n\n"
        "لطفاً گزینه مورد نظر را انتخاب کنید:",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )
