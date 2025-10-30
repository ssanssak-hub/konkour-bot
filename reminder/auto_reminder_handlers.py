"""
هندلرهای ریمایندر خودکار برای کاربران عادی
"""
import logging
from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from reminder.auto_reminder_system import auto_reminder_system
from reminder.reminder_keyboards import create_auto_reminders_user_menu, create_back_only_menu
from exam_data import EXAMS_1405

logger = logging.getLogger(__name__)

async def user_auto_reminders_list(message: types.Message):
    """لیست ریمایندرهای خودکار برای کاربران عادی"""
    auto_reminders = auto_reminder_system.get_active_auto_reminders()
    user_reminders = auto_reminder_system.get_user_auto_reminders(message.from_user.id)
    
    # ایجاد مپ برای وضعیت فعال بودن هر ریمایندر برای کاربر
    user_reminders_map = {ur['auto_reminder_id']: ur['is_active'] for ur in user_reminders}
    
    if not auto_reminders:
        await message.answer(
            "📭 <b>هیچ ریمایندر خودکار فعالی موجود نیست</b>",
            reply_markup=create_auto_reminders_user_menu(),
            parse_mode="HTML"
        )
        return
    
    message_text = "🤖 <b>ریمایندرهای خودکار</b>\n\n"
    message_text += "این ریمایندرها به صورت خودکار در زمان‌های مهم برای شما ارسال می‌شوند:\n\n"
    
    for reminder in auto_reminders:
        user_status = user_reminders_map.get(reminder['id'], True)  # پیش‌فرض فعال
        status_icon = "✅" if user_status else "❌"
        status_text = "فعال" if user_status else "غیرفعال"
        
        exam_names = [EXAMS_1405[key]['name'] for key in reminder['exam_keys'] if key in EXAMS_1405]
        
        message_text += (
            f"{status_icon} <b>{reminder['title']}</b>\n"
            f"⏰ {reminder['days_before_exam']} روز قبل از کنکور\n"
            f"📝 {reminder['message']}\n"
            f"🎯 برای: {', '.join(exam_names)}\n"
            f"🔔 وضعیت شما: {status_text}\n"
            f"────────────────────\n\n"
        )
    
    message_text += "💡 می‌توانید وضعیت هر ریمایندر را تغییر دهید."
    
    await message.answer(
        message_text,
        reply_markup=create_auto_reminders_user_menu(),
        parse_mode="HTML"
    )

async def toggle_user_auto_reminder(message: types.Message):
    """تغییر وضعیت ریمایندر خودکار برای کاربر"""
    auto_reminders = auto_reminder_system.get_active_auto_reminders()
    
    if not auto_reminders:
        await message.answer(
            "❌ هیچ ریمایندر خودکار فعالی موجود نیست",
            reply_markup=create_auto_reminders_user_menu()
        )
        return
    
    # ایجاد کیبورد برای انتخاب ریمایندر
    keyboard = []
    for reminder in auto_reminders:
        user_reminders = auto_reminder_system.get_user_auto_reminders(message.from_user.id)
        user_status = any(ur['auto_reminder_id'] == reminder['id'] and ur['is_active'] for ur in user_reminders)
        status_text = "🔔 غیرفعال کن" if user_status else "✅ فعال کن"
        
        keyboard.append([
            InlineKeyboardButton(
                text=f"{reminder['title']} - {status_text}",
                callback_data=f"auto_toggle:{reminder['id']}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton(text="🔙 بازگشت", callback_data="auto_user:back")
    ])
    
    await message.answer(
        "🔔 <b>مدیریت ریمایندرهای خودکار</b>\n\n"
        "لطفاً ریمایندر مورد نظر را برای تغییر وضعیت انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode="HTML"
    )

async def handle_auto_reminder_user_callback(callback: types.CallbackQuery):
    """پردازش کلیک‌های ریمایندر خودکار برای کاربران"""
    data = callback.data
    
    if data == "auto_user:back":
        await callback.message.delete()
        await user_auto_reminders_list(callback.message)
        return
    
    if data.startswith("auto_toggle:"):
        reminder_id = int(data.split(":")[1])
        
        success = auto_reminder_system.toggle_user_auto_reminder(callback.from_user.id, reminder_id)
        
        if success:
            # دریافت وضعیت جدید
            user_reminders = auto_reminder_system.get_user_auto_reminders(callback.from_user.id)
            user_status = any(ur['auto_reminder_id'] == reminder_id and ur['is_active'] for ur in user_reminders)
            status_text = "فعال" if user_status else "غیرفعال"
            
            await callback.answer(f"✅ ریمایندر {status_text} شد")
            
            # بروزرسانی پیام
            await callback.message.edit_reply_markup(
                reply_markup=await create_auto_reminders_user_keyboard(callback.from_user.id)
            )
        else:
            await callback.answer("❌ خطا در تغییر وضعیت")

async def create_auto_reminders_user_keyboard(user_id: int):
    """ایجاد کیبورد ریمایندرهای خودکار برای کاربر"""
    auto_reminders = auto_reminder_system.get_active_auto_reminders()
    user_reminders = auto_reminder_system.get_user_auto_reminders(user_id)
    user_reminders_map = {ur['auto_reminder_id']: ur['is_active'] for ur in user_reminders}
    
    keyboard = []
    for reminder in auto_reminders:
        user_status = user_reminders_map.get(reminder['id'], True)
        status_text = "🔔 غیرفعال کن" if user_status else "✅ فعال کن"
        
        keyboard.append([
            InlineKeyboardButton(
                text=f"{reminder['title']} - {status_text}",
                callback_data=f"auto_toggle:{reminder['id']}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton(text="🔙 بازگشت", callback_data="auto_user:back")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
