"""
هندلرهای منوی اصلی
"""
import logging
from aiogram import types, F

from keyboards import (
    exams_menu, study_plan_menu, stats_menu, admin_menu,
    create_study_plan_keyboard, create_stats_keyboard
)
from utils import (
    get_study_tips, calculate_study_progress, format_study_time,
    calculate_streak, get_motivational_quote
)
from database import Database

logger = logging.getLogger(__name__)
db = Database()

async def exams_menu_handler(message: types.Message):
    """هندلر منوی زمان‌سنجی کنکورها"""
    logger.info(f"⏰ کاربر {message.from_user.id} منوی کنکورها را انتخاب کرد")
    await message.answer("🎯 انتخاب کنکور مورد نظر:", reply_markup=exams_menu())

async def study_plan_handler(message: types.Message):
    """هندلر منوی برنامه مطالعاتی"""
    logger.info(f"📅 کاربر {message.from_user.id} منوی برنامه مطالعاتی را انتخاب کرد")
    
    user_stats = db.get_user_progress(message.from_user.id)
    progress = calculate_study_progress(user_stats['total_minutes'])
    
    await message.answer(
        f"📅 <b>برنامه مطالعاتی پیشرفته</b>\n\n"
        f"📊 آمار کلی شما:\n"
        f"• 🕒 کل زمان مطالعه: {user_stats['total_hours']} ساعت\n"
        f"• 📖 تعداد جلسات: {user_stats['total_sessions']} جلسه\n"
        f"• 📅 روزهای فعال: {user_stats['active_days']} روز\n"
        f"• 📈 پیشرفت کلی: {progress['percentage']}%\n"
        f"{progress['progress_bar']}\n\n"
        f"💡 <b>نکته طلایی:</b>\n{get_study_tips()}\n\n"
        f"از گزینه‌های زیر استفاده کنید:",
        reply_markup=create_study_plan_keyboard(),
        parse_mode="HTML"
    )

async def stats_handler(message: types.Message):
    """هندلر منوی آمار مطالعه"""
    logger.info(f"📊 کاربر {message.from_user.id} منوی آمار مطالعه را انتخاب کرد")
    
    today_stats = db.get_today_study_stats(message.from_user.id)
    weekly_stats = db.get_weekly_stats(message.from_user.id)
    user_stats = db.get_user_progress(message.from_user.id)
    
    total_weekly = sum(day['total_minutes'] for day in weekly_stats)
    study_days = [day['date'] for day in weekly_stats if day['total_minutes'] > 0]
    current_streak = calculate_streak(study_days)
    
    await message.answer(
        f"📊 <b>آمار مطالعه حرفه‌ای</b>\n\n"
        f"📈 <b>امروز:</b>\n"
        f"• 🕒 زمان مطالعه: {today_stats['total_minutes']} دقیقه\n"
        f"• 📖 جلسات: {today_stats['sessions_count']} جلسه\n"
        f"• 📚 دروس: {today_stats['subjects']}\n\n"
        f"📅 <b>هفته جاری:</b>\n"
        f"• 🕒 کل زمان: {format_study_time(total_weekly)}\n"
        f"• 📊 میانگین روزانه: {total_weekly // 7 if weekly_stats else 0} دقیقه\n"
        f"• 🔥 streak فعلی: {current_streak} روز\n\n"
        f"📊 <b>کلی:</b>\n"
        f"• 🕒 کل زمان: {user_stats['total_hours']} ساعت\n"
        f"• 📖 کل جلسات: {user_stats['total_sessions']} جلسه\n\n"
        f"برای مشاهده جزئیات بیشتر از گزینه‌های زیر استفاده کنید:",
        reply_markup=create_stats_keyboard(),
        parse_mode="HTML"
    )

async def admin_handler(message: types.Message):
    """هندلر منوی مدیریت"""
    from config import ADMIN_ID
    
    user = message.from_user
    logger.info(f"👑 کاربر {user.first_name} منوی مدیریت را انتخاب کرد")
    
    if user.id != ADMIN_ID:
        await message.answer("❌ دسترسی denied!")
        return
        
    channels = db.get_mandatory_channels()
    channel_count = len(channels)
    
    await message.answer(
        f"👑 <b>پنل مدیریت</b>\n\n"
        f"📊 آمار سیستم:\n"
        f"• 👥 کانال‌های اجباری: {channel_count} کانال\n"
        f"• ⚙️ سیستم عضویت اجباری: {'فعال' if channel_count > 0 else 'غیرفعال'}\n\n"
        f"از گزینه‌های زیر برای مدیریت استفاده کنید:",
        reply_markup=admin_menu(),
        parse_mode="HTML"
    )
