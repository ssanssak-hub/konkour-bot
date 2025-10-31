"""
هندلرهای ریمایندرهای پیشرفته برای ادمین
"""
import logging
import asyncio
from datetime import datetime
from aiogram import types, F
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID
from reminder.reminder_database import reminder_db
from reminder.advanced_reminder_states import AdvancedReminderStates
from reminder.advanced_reminder_keyboards import (
    create_advanced_reminder_admin_menu,
    create_start_time_menu,
    create_start_date_menu,
    create_end_time_menu,
    create_end_date_menu,
    create_days_of_week_menu,
    create_repeat_count_menu,
    create_repeat_interval_menu,
    create_confirmation_menu,
    create_advanced_reminder_list_keyboard,
    create_advanced_reminder_actions_keyboard,
    create_back_only_menu
)
from utils.time_utils import get_current_persian_datetime, persian_to_gregorian_string

logger = logging.getLogger(__name__)

async def advanced_reminders_admin_handler(message: types.Message):
    """منوی اصلی ریمایندرهای پیشرفته برای ادمین"""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ دسترسی denied!")
        return
    
    reminders = reminder_db.get_admin_advanced_reminders()
    active_count = len([r for r in reminders if r['is_active']])
    
    await message.answer(
        f"🤖 <b>مدیریت ریمایندرهای پیشرفته</b>\n\n"
        f"📊 آمار سیستم:\n"
        f"• 📝 کل ریمایندرها: {len(reminders)}\n"
        f"• 🔔 فعال: {active_count}\n"
        f"• 🔕 غیرفعال: {len(reminders) - active_count}\n\n"
        f"💡 <i>این ریمایندرها قابلیت تکرار و زمان‌بندی پیشرفته دارند</i>\n\n"
        f"لطفاً عمل مورد نظر را انتخاب کنید:",
        reply_markup=create_advanced_reminder_admin_menu(),
        parse_mode="HTML"
    )

async def start_add_advanced_reminder(message: types.Message, state: FSMContext):
    """شروع فرآیند افزودن ریمایندر پیشرفته"""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ دسترسی denied!")
        return
    
    await state.set_state(AdvancedReminderStates.waiting_for_title)
    
    await message.answer(
        "➕ <b>افزودن ریمایندر پیشرفته جدید</b>\n\n"
        "لطفاً عنوان ریمایندر را وارد کنید:\n\n"
        "💡 <i>مثال: یادآوری مطالعه فصل ۱</i>\n\n"
        "یا برای بازگشت: 🔙 بازگشت",
        reply_markup=create_back_only_menu(),
        parse_mode="HTML"
    )

async def process_advanced_title(message: types.Message, state: FSMContext):
    """پردازش عنوان ریمایندر پیشرفته"""
    if message.text == "🔙 بازگشت":
        await state.clear()
        await advanced_reminders_admin_handler(message)
        return
    
    await state.update_data(title=message.text)
    await state.set_state(AdvancedReminderStates.waiting_for_message)
    
    await message.answer(
        "📄 <b>متن ریمایندر</b>\n\n"
        "لطفاً متن کامل ریمایندر را وارد کنید:\n\n"
        "💡 <i>این متن برای کاربران ارسال خواهد شد</i>\n\n"
        "یا برای بازگشت: 🔙 بازگشت",
        reply_markup=create_back_only_menu(),
        parse_mode="HTML"
    )

async def process_advanced_message(message: types.Message, state: FSMContext):
    """پردازش متن ریمایندر پیشرفته"""
    if message.text == "🔙 بازگشت":
        await state.set_state(AdvancedReminderStates.waiting_for_title)
        await message.answer(
            "لطفاً عنوان ریمایندر را وارد کنید:",
            reply_markup=create_back_only_menu()
        )
        return
    
    await state.update_data(message=message.text)
    await state.set_state(AdvancedReminderStates.waiting_for_start_time)
    
    await message.answer(
        "⏰ <b>ساعت شروع</b>\n\n"
        "لطفاً ساعت شروع را به فرمت HH:MM وارد کنید:\n\n"
        "💡 <i>مثال: 14:30 یا 08:00</i>\n"
        "⏰ یا برای زمان فعلی: همین الان\n\n"
        "یا برای بازگشت: 🔙 بازگشت",
        reply_markup=create_start_time_menu(),
        parse_mode="HTML"
    )

async def process_start_time(message: types.Message, state: FSMContext):
    """پردازش ساعت شروع"""
    if message.text == "🔙 بازگشت":
        await state.set_state(AdvancedReminderStates.waiting_for_message)
        await message.answer(
            "لطفاً متن ریمایندر را وارد کنید:",
            reply_markup=create_back_only_menu()
        )
        return
    
    if message.text == "⏰ همین الان":
        current_time = datetime.now().strftime("%H:%M")
        await state.update_data(start_time=current_time)
    else:
        # اعتبارسنجی فرمت زمان
        try:
            time_str = message.text.strip()
            datetime.strptime(time_str, "%H:%M")
            await state.update_data(start_time=time_str)
        except ValueError:
            await message.answer(
                "❌ فرمت زمان نامعتبر!\n\n"
                "لطفاً زمان را به فرمت HH:MM وارد کنید:\n"
                "💡 <i>مثال: 14:30 یا 08:00</i>",
                reply_markup=create_start_time_menu()
            )
            return
    
    await state.set_state(AdvancedReminderStates.waiting_for_start_date)
    
    await message.answer(
        "📅 <b>تاریخ شروع</b>\n\n"
        "لطفاً تاریخ شروع را به فرمت YYYY-MM-DD وارد کنید:\n\n"
        "💡 <i>مثال: 1404-01-15</i>\n"
        "📅 یا برای تاریخ امروز: امروز\n\n"
        "یا برای بازگشت: 🔙 بازگشت",
        reply_mmarkup=create_start_date_menu(),
        parse_mode="HTML"
    )

# ادامه هندلرها در پیام بعدی...
