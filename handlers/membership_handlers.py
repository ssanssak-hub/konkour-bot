"""
هندلرهای عضویت اجباری
"""
import logging
from aiogram import types, F
from aiogram.fsm.context import FSMContext

from keyboards import create_membership_keyboard
from utils import check_user_membership

logger = logging.getLogger(__name__)

async def check_membership_handler(callback: types.CallbackQuery, bot):
    """بررسی عضویت کاربر"""
    user_id = callback.from_user.id
    is_member = await check_user_membership(bot, user_id)
    
    if is_member:
        await callback.message.edit_text(
            "✅ <b>تبریک! شما در تمام کانال‌ها عضو هستید.</b>\n\n"
            "اکنون می‌توانید از تمام امکانات ربات استفاده کنید.",
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[[
                types.InlineKeyboardButton(text="🏠 منوی اصلی", callback_data="main:back")
            ]]),
            parse_mode="HTML"
        )
    else:
        await callback.answer("❌ هنوز در برخی کانال‌ها عضو نیستید!", show_alert=True)
