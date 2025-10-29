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
    await callback.message.edit_text(
        "🏠 منوی اصلی:",
        reply_markup=main_menu()
    )

async def back_to_stats_handler(callback: types.CallbackQuery):
    """بازگشت به آمار"""
    from handlers.menu_handlers import stats_handler
    await stats_handler(callback.message)

async def back_to_study_handler(callback: types.CallbackQuery):
    """بازگشت به برنامه مطالعاتی"""
    from handlers.menu_handlers import study_plan_handler
    await study_plan_handler(callback.message)

async def back_to_admin_handler(callback: types.CallbackQuery):
    """بازگشت به مدیریت"""
    from handlers.menu_handlers import admin_handler
    await admin_handler(callback.message)
