"""
هندلرهای مدیریت
"""
import logging
from aiogram import types, F
from aiogram.fsm.context import FSMContext

from keyboards import admin_menu, back_button_menu
from database import Database

logger = logging.getLogger(__name__)
db = Database()

async def admin_channels_handler(callback: types.CallbackQuery):
    """مدیریت کانال‌های اجباری"""
    channels = db.get_mandatory_channels()
    
    if not channels:
        message = "👑 <b>مدیریت کانال‌های اجباری</b>\n\n❌ هیچ کانال اجباری تعریف نشده است."
    else:
        message = "👑 <b>مدیریت کانال‌های اجباری</b>\n\n📋 کانال‌های فعلی:\n"
        for i, channel in enumerate(channels, 1):
            message += f"{i}. {channel['channel_title']} (@{channel['channel_username']})\n"
    
    keyboard = [
        [types.InlineKeyboardButton(text="➕ افزودن کانال", callback_data="admin:add_channel")],
        [types.InlineKeyboardButton(text="🗑️ حذف کانال", callback_data="admin:remove_channel")],
        [types.InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin:back")]
    ]
    
    await callback.message.edit_text(
        message,
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode="HTML"
    )

async def admin_add_channel_handler(callback: types.CallbackQuery, state: FSMContext, bot):
    """شروع فرآیند افزودن کانال اجباری"""
    await callback.message.edit_text(
        "👑 <b>افزودن کانال اجباری</b>\n\n"
        "لطفاً اطلاعات کانال را به فرمت زیر ارسال کنید:\n"
        "<code>آیدی_عددی @username عنوان_کانال</code>\n\n"
        "مثال:\n"
        "<code>-1001234567890 @konkour_channel کانال کنکور ۱۴۰۵</code>\n\n"
        "❕ توجه: ربات باید در کانال ادمین باشد.",
        reply_markup=back_button_menu("🔙 بازگشت", "admin:channels"),
        parse_mode="HTML"
    )
    
    await state.set_state("waiting_for_channel_info")

async def process_channel_info(message: types.Message, state: FSMContext, bot):
    """پردازش اطلاعات کانال وارد شده"""
    try:
        parts = message.text.split()
        if len(parts) < 3:
            await message.answer("❌ فرمت وارد شده صحیح نیست. لطفاً دوباره尝试 کنید:")
            return
        
        channel_id = int(parts[0])
        channel_username = parts[1].lstrip('@')
        channel_title = ' '.join(parts[2:])
        
        # بررسی اینکه ربات در کانال ادمین است
        try:
            chat_member = await bot.get_chat_member(channel_id, bot.id)
            if chat_member.status not in ['administrator', 'creator']:
                await message.answer(
                    "❌ ربات باید در کانال ادمین باشد. لطفاً ابتدا ربات را ادمین کنید.",
                    reply_markup=back_button_menu("🔙 بازگشت", "admin:channels")
                )
                await state.clear()
                return
        except Exception as e:
            await message.answer(
                f"❌ خطا در بررسی وضعیت ربات: {e}",
                reply_markup=back_button_menu("🔙 بازگشت", "admin:channels")
            )
            await state.clear()
            return
        
        # ذخیره کانال در دیتابیس
        db.add_mandatory_channel(
            channel_id=channel_id,
            channel_username=channel_username,
            channel_title=channel_title,
            admin_id=message.from_user.id
        )
        
        await state.clear()
        
        await message.answer(
            f"✅ <b>کانال با موفقیت اضافه شد!</b>\n\n"
            f"📢 عنوان: {channel_title}\n"
            f"🔗 آیدی: {channel_id}\n"
            f"👤 یوزرنیم: @{channel_username}\n\n"
            f"از این پس کاربران برای استفاده از ربات باید در این کانال عضو باشند.",
            reply_markup=admin_menu(),
            parse_mode="HTML"
        )
        
    except ValueError:
        await message.answer("❌ آیدی کانال باید عددی باشد. لطفاً دوباره尝试 کنید:")
    except Exception as e:
        await message.answer(f"❌ خطا: {e}")
