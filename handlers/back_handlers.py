"""
هندلرهای بازگشت
"""
import logging
from aiogram import types, F

from keyboards import main_menu

logger = logging.getLogger(__name__)

async def back_to_main_handler(callback: types.CallbackQuery):
    """بازگشت به منوی اصلی"""
    logger.info(f"🏠 کاربر {callback.from_user.id} به منوی اصلی بازگشت")
    
    # ابتدا پیام فعلی رو پاک کن
    await callback.message.delete()
    
    # سپس پیام جدید با منوی اصلی ارسال کن
    await callback.message.answer(
        "🏠 <b>منوی اصلی</b>\n\n"
        "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

async def back_to_stats_handler(callback: types.CallbackQuery):
    """بازگشت به آمار"""
    from handlers.menu_handlers import stats_handler
    await callback.message.delete()
    await stats_handler(callback.message)

async def back_to_study_handler(callback: types.CallbackQuery):
    """بازگشت به برنامه مطالعاتی"""
    from handlers.menu_handlers import study_plan_handler
    await callback.message.delete()
    await study_plan_handler(callback.message)

async def back_to_admin_handler(callback: types.CallbackQuery):
    """بازگشت به مدیریت"""
    from handlers.menu_handlers import admin_handler
    await callback.message.delete()
    await admin_handler(callback.message)
