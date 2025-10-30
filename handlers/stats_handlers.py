"""
هندلرهای آمار و گزارشات
"""
import logging
from aiogram import types, F
from aiogram.fsm.context import FSMContext

from keyboards import create_stats_keyboard, back_button_menu
from utils import get_motivational_quote, format_study_time, calculate_streak
from database import Database

logger = logging.getLogger(__name__)
db = Database()

async def stats_callback_handler(callback: types.CallbackQuery):
    """هندلر اصلی برای callback_dataهای stats"""
    data = callback.data
    
    if data == "stats:today":
        await today_stats_handler(callback)
    elif data == "stats:weekly":
        await weekly_stats_handler(callback)
    elif data == "stats:monthly":
        await monthly_stats_handler(callback)
    elif data == "stats:full":
        await full_stats_handler(callback)
    elif data == "stats:refresh":
        await refresh_stats_handler(callback)
    elif data == "stats:back":
        await back_to_stats_handler(callback)
    else:
        await callback.answer("⚠️ این قابلیت به زودی اضافه می‌شود")

async def today_stats_handler(callback: types.CallbackQuery):
    """نمایش آمار امروز"""
    from handlers.study_handlers import today_stats_handler
    await today_stats_handler(callback)

async def weekly_stats_handler(callback: types.CallbackQuery):
    """نمایش آمار هفته جاری"""
    from handlers.study_handlers import weekly_stats_handler
    await weekly_stats_handler(callback)

async def monthly_stats_handler(callback: types.CallbackQuery):
    """نمایش آمار ماه جاری"""
    monthly_stats = db.get_monthly_stats(callback.from_user.id)
    total_monthly = sum(day['total_minutes'] for day in monthly_stats)
    
    await callback.message.edit_text(
        f"📈 <b>آمار مطالعه ماه جاری</b>\n\n"
        f"🕒 کل زمان مطالعه: {format_study_time(total_monthly)}\n"
        f"📊 میانگین روزانه: {total_monthly // 30 if monthly_stats else 0} دقیقه\n"
        f"📅 روزهای مطالعه: {len([d for d in monthly_stats if d['total_minutes'] > 0])} روز\n\n"
        f"💪 {get_motivational_quote()}",
        reply_markup=create_stats_keyboard(),
        parse_mode="HTML"
    )

async def full_stats_handler(callback: types.CallbackQuery):
    """نمایش آمار کامل"""
    user_stats = db.get_user_progress(callback.from_user.id)
    today_stats = db.get_today_study_stats(callback.from_user.id)
    weekly_stats = db.get_weekly_stats(callback.from_user.id)
    
    total_weekly = sum(day['total_minutes'] for day in weekly_stats)
    study_days = [day['date'] for day in weekly_stats if day['total_minutes'] > 0]
    current_streak = calculate_streak(study_days)
    
    await callback.message.edit_text(
        f"📊 <b>گزارش کامل آمار مطالعه</b>\n\n"
        f"📅 <b>امروز:</b>\n"
        f"• 🕒 زمان: {today_stats['total_minutes']} دقیقه\n"
        f"• 📖 جلسات: {today_stats['sessions_count']} جلسه\n\n"
        f"📅 <b>هفته جاری:</b>\n"
        f"• 🕒 کل زمان: {format_study_time(total_weekly)}\n"
        f"• 📊 میانگین روزانه: {total_weekly // 7 if weekly_stats else 0} دقیقه\n"
        f"• 🔥 Streak: {current_streak} روز\n\n"
        f"📊 <b>کلی:</b>\n"
        f"• 🕒 کل زمان: {user_stats['total_hours']} ساعت\n"
        f"• 📖 کل جلسات: {user_stats['total_sessions']} جلسه\n"
        f"• 📅 روزهای فعال: {user_stats['active_days']} روز\n\n"
        f"🎯 {get_motivational_quote()}",
        reply_markup=create_stats_keyboard(),
        parse_mode="HTML"
    )

async def refresh_stats_handler(callback: types.CallbackQuery):
    """بروزرسانی آمار"""
    await callback.answer("🔄 آمار بروزرسانی شد")
    await stats_handler(callback.message)

async def back_to_stats_handler(callback: types.CallbackQuery):
    """بازگشت به منوی آمار"""
    from handlers.menu_handlers import stats_handler
    await stats_handler(callback.message)
