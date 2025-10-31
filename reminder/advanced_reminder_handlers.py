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

async def process_start_date(message: types.Message, state: FSMContext):
    """پردازش تاریخ شروع"""
    if message.text == "🔙 بازگشت":
        await state.set_state(AdvancedReminderStates.waiting_for_start_time)
        await message.answer(
            "لطفاً ساعت شروع را وارد کنید:",
            reply_markup=create_start_time_menu()
        )
        return
    
    if message.text == "📅 امروز":
        current_date = get_current_persian_datetime()
        await state.update_data(start_date=current_date['date'])
    else:
        # اعتبارسنجی فرمت تاریخ
        try:
            date_str = message.text.strip()
            # تبدیل تاریخ شمسی به میلادی برای ذخیره در دیتابیس
            gregorian_date = persian_to_gregorian_string(date_str)
            await state.update_data(start_date=date_str)  # ذخیره شمسی برای نمایش
        except Exception as e:
            await message.answer(
                "❌ فرمت تاریخ نامعتبر!\n\n"
                "لطفاً تاریخ را به فرمت YYYY-MM-DD وارد کنید:\n"
                "💡 <i>مثال: 1404-01-15</i>",
                reply_markup=create_start_date_menu()
            )
            return
    
    await state.set_state(AdvancedReminderStates.waiting_for_end_time)
    
    await message.answer(
        "⏰ <b>ساعت پایان</b>\n\n"
        "لطفاً ساعت پایان را به فرمت HH:MM وارد کنید:\n\n"
        "💡 <i>مثال: 18:00 یا 22:30</i>\n"
        "⏰ یا برای بدون پایان: بدون پایان\n\n"
        "یا برای بازگشت: 🔙 بازگشت",
        reply_markup=create_end_time_menu(),
        parse_mode="HTML"
    )

async def process_end_time(message: types.Message, state: FSMContext):
    """پردازش ساعت پایان"""
    if message.text == "🔙 بازگشت":
        await state.set_state(AdvancedReminderStates.waiting_for_start_date)
        await message.answer(
            "لطفاً تاریخ شروع را وارد کنید:",
            reply_markup=create_start_date_menu()
        )
        return
    
    if message.text == "⏰ بدون پایان":
        await state.update_data(end_time="23:59")
    else:
        # اعتبارسنجی فرمت زمان
        try:
            time_str = message.text.strip()
            datetime.strptime(time_str, "%H:%M")
            await state.update_data(end_time=time_str)
        except ValueError:
            await message.answer(
                "❌ فرمت زمان نامعتبر!\n\n"
                "لطفاً زمان را به فرمت HH:MM وارد کنید:\n"
                "💡 <i>مثال: 18:00 یا 22:30</i>",
                reply_markup=create_end_time_menu()
            )
            return
    
    await state.set_state(AdvancedReminderStates.waiting_for_end_date)
    
    await message.answer(
        "📅 <b>تاریخ پایان</b>\n\n"
        "لطفاً تاریخ پایان را به فرمت YYYY-MM-DD وارد کنید:\n\n"
        "💡 <i>مثال: 1404-12-29</i>\n"
        "📅 یا برای بدون تاریخ پایان: بدون تاریخ پایان\n\n"
        "یا برای بازگشت: 🔙 بازگشت",
        reply_markup=create_end_date_menu(),
        parse_mode="HTML"
    )

async def process_end_date(message: types.Message, state: FSMContext):
    """پردازش تاریخ پایان"""
    if message.text == "🔙 بازگشت":
        await state.set_state(AdvancedReminderStates.waiting_for_end_time)
        await message.answer(
            "لطفاً ساعت پایان را وارد کنید:",
            reply_markup=create_end_time_menu()
        )
        return
    
    if message.text == "📅 بدون تاریخ پایان":
        # تاریخ پایان رو ۱ سال بعد قرار می‌دیم
        current_date = get_current_persian_datetime()
        next_year = str(int(current_date['date'][:4]) + 1) + current_date['date'][4:]
        await state.update_data(end_date=next_year)
    else:
        # اعتبارسنجی فرمت تاریخ
        try:
            date_str = message.text.strip()
            # تبدیل تاریخ شمسی به میلادی برای ذخیره در دیتابیس
            gregorian_date = persian_to_gregorian_string(date_str)
            await state.update_data(end_date=date_str)  # ذخیره شمسی برای نمایش
        except Exception as e:
            await message.answer(
                "❌ فرمت تاریخ نامعتبر!\n\n"
                "لطفاً تاریخ را به فرمت YYYY-MM-DD وارد کنید:\n"
                "💡 <i>مثال: 1404-12-29</i>",
                reply_markup=create_end_date_menu()
            )
            return
    
    await state.set_state(AdvancedReminderStates.waiting_for_days_of_week)
    await state.update_data(selected_days=[])
    
    await message.answer(
        "📆 <b>روزهای هفته</b>\n\n"
        "لطفاً روزهای هفته مورد نظر را انتخاب کنید:\n\n"
        "💡 <i>ریمایندر در روزهای انتخاب شده ارسال خواهد شد</i>\n\n"
        "روزهای انتخاب شده: ❌ هیچکدام",
        reply_markup=create_days_of_week_menu(),
        parse_mode="HTML"
    )

async def process_days_of_week(message: types.Message, state: FSMContext):
    """پردازش انتخاب روزهای هفته"""
    state_data = await state.get_data()
    selected_days = state_data.get('selected_days', [])
    
    day_mapping = {
        "شنبه": 0, "یکشنبه": 1, "دوشنبه": 2,
        "سه‌شنبه": 3, "چهارشنبه": 4, "پنجشنبه": 5, "جمعه": 6
    }
    
    if message.text == "🔙 بازگشت":
        await state.set_state(AdvancedReminderStates.waiting_for_end_date)
        await message.answer(
            "لطفاً تاریخ پایان را وارد کنید:",
            reply_markup=create_end_date_menu()
        )
        return
    
    elif message.text == "✅ همه روزها":
        selected_days = [0, 1, 2, 3, 4, 5, 6]
        await state.update_data(selected_days=selected_days)
        await message.answer("✅ همه روزهای هفته انتخاب شدند")
        
    elif message.text == "🗑️ پاک کردن همه":
        selected_days = []
        await state.update_data(selected_days=selected_days)
        await message.answer("🗑️ همه روزها پاک شدند")
        
    elif message.text == "➡️ ادامه":
        if not selected_days:
            await message.answer("❌ لطفاً حداقل یک روز از هفته را انتخاب کنید")
            return
        
        await state.set_state(AdvancedReminderStates.waiting_for_repeat_count)
        
        await message.answer(
            "🔢 <b>تعداد تکرار (&)</b>\n\n"
            "لطفاً تعداد دفعات تکرار پیام را انتخاب کنید (0 تا 10):\n\n"
            "💡 <i>توضیحات:\n"
            "• 0 = فقط ثبت، بدون ارسال\n"
            "• 1 = ارسال یکبار\n"  
            "• 2-10 = ارسال چندباره با فاصله زمانی</i>\n\n"
            "یا برای بازگشت: 🔙 بازگشت",
            reply_markup=create_repeat_count_menu(),
            parse_mode="HTML"
        )
        return
    
    else:
        # بررسی انتخاب روز
        for day_name, day_num in day_mapping.items():
            if day_name in message.text:
                if day_num in selected_days:
                    selected_days.remove(day_num)
                    await message.answer(f"❌ {day_name} حذف شد")
                else:
                    selected_days.append(day_num)
                    await message.answer(f"✅ {day_name} اضافه شد")
                break
        
        await state.update_data(selected_days=selected_days)
    
    # نمایش وضعیت فعلی
    if selected_days:
        selected_days_names = [name for name, num in day_mapping.items() if num in selected_days]
        status_text = "، ".join(selected_days_names)
    else:
        status_text = "❌ هیچکدام"
    
    await message.answer(
        f"📆 <b>روزهای هفته</b>\n\n"
        f"روزهای انتخاب شده: {status_text}\n\n"
        f"لطفاً روزهای مورد نظر را انتخاب کنید:",
        reply_markup=create_days_of_week_menu(selected_days),
        parse_mode="HTML"
    )

async def process_repeat_count(message: types.Message, state: FSMContext):
    """پردازش تعداد تکرار (&)"""
    if message.text == "🔙 بازگشت":
        await state.set_state(AdvancedReminderStates.waiting_for_days_of_week)
        state_data = await state.get_data()
        selected_days = state_data.get('selected_days', [])
        
        await message.answer(
            "لطفاً روزهای هفته مورد نظر را انتخاب کنید:",
            reply_markup=create_days_of_week_menu(selected_days)
        )
        return
    
    try:
        repeat_count = int(message.text)
        if repeat_count < 0 or repeat_count > 10:
            await message.answer(
                "❌ تعداد تکرار باید بین 0 تا 10 باشد!\n\n"
                "لطفاً عدد معتبر وارد کنید:",
                reply_markup=create_repeat_count_menu()
            )
            return
        
        await state.update_data(repeat_count=repeat_count)
        
        if repeat_count == 0:
            # اگر تعداد تکرار 0 باشد، از کاربر فاصله زمانی نمی‌پرسیم
            await state.update_data(repeat_interval=0)
            await show_advanced_confirmation(message, state)
        else:
            await state.set_state(AdvancedReminderStates.waiting_for_repeat_interval)
            
            explanation = ""
            if repeat_count == 1:
                explanation = "• ارسال یکبار در ساعت مشخص (فاصله زمانی نادیده گرفته می‌شود)"
            else:
                explanation = f"• ارسال {repeat_count} بار با فاصله زمانی مشخص"
            
            await message.answer(
                f"⏱️ <b>فاصله زمانی بین تکرارها (@)</b>\n\n"
                f"لطفاً فاصله زمانی بین ارسال‌ها را انتخاب کنید (10 تا 60 ثانیه):\n\n"
                f"💡 <i>توضیحات:\n"
                f"{explanation}</i>\n\n"
                f"یا برای بازگشت: 🔙 بازگشت",
                reply_markup=create_repeat_interval_menu(),
                parse_mode="HTML"
            )
            
    except ValueError:
        await message.answer(
            "❌ لطفاً یک عدد معتبر وارد کنید!",
            reply_markup=create_repeat_count_menu()
        )

async def process_repeat_interval(message: types.Message, state: FSMContext):
    """پردازش فاصله زمانی (@)"""
    if message.text == "🔙 بازگشت":
        await state.set_state(AdvancedReminderStates.waiting_for_repeat_count)
        await message.answer(
            "لطفاً تعداد تکرار را انتخاب کنید:",
            reply_markup=create_repeat_count_menu()
        )
        return
    
    try:
        repeat_interval = int(message.text)
        if repeat_interval < 10 or repeat_interval > 60:
            await message.answer(
                "❌ فاصله زمانی باید بین 10 تا 60 ثانیه باشد!\n\n"
                "لطفاً عدد معتبر وارد کنید:",
                reply_markup=create_repeat_interval_menu()
            )
            return
        
        state_data = await state.get_data()
        repeat_count = state_data.get('repeat_count', 1)
        
        # اگر تعداد تکرار 1 باشد، فاصله زمانی رو نادیده می‌گیریم
        if repeat_count == 1:
            repeat_interval = 0
        
        await state.update_data(repeat_interval=repeat_interval)
        await show_advanced_confirmation(message, state)
        
    except ValueError:
        await message.answer(
            "❌ لطفاً یک عدد معتبر وارد کنید!",
            reply_markup=create_repeat_interval_menu()
        )

async def show_advanced_confirmation(message: types.Message, state: FSMContext):
    """نمایش خلاصه و تأیید نهایی"""
    state_data = await state.get_data()
    
    summary = await create_advanced_reminder_summary(state_data)
    
    await state.set_state(AdvancedReminderStates.waiting_for_confirmation)
    
    await message.answer(
        f"✅ <b>خلاصه ریمایندر پیشرفته</b>\n\n{summary}\n\n"
        "آیا مایل به ایجاد این ریمایندر هستید؟",
        reply_markup=create_confirmation_menu(),
        parse_mode="HTML"
    )

async def create_advanced_reminder_summary(state_data: dict) -> str:
    """ایجاد خلاصه ریمایندر پیشرفته"""
    day_mapping = {
        0: "شنبه", 1: "یکشنبه", 2: "دوشنبه",
        3: "سه‌شنبه", 4: "چهارشنبه", 5: "پنجشنبه", 6: "جمعه"
    }
    
    selected_days = state_data.get('selected_days', [])
    days_text = "، ".join([day_mapping[day] for day in selected_days]) if selected_days else "هیچکدام"
    
    repeat_count = state_data.get('repeat_count', 1)
    repeat_interval = state_data.get('repeat_interval', 0)
    
    if repeat_count == 0:
        repeat_text = "فقط ثبت (بدون ارسال)"
    elif repeat_count == 1:
        repeat_text = "ارسال یکبار"
    else:
        repeat_text = f"ارسال {repeat_count} بار با فاصله {repeat_interval} ثانیه"
    
    summary = (
        f"📝 <b>عنوان:</b> {state_data.get('title', 'تعیین نشده')}\n"
        f"📄 <b>متن:</b> {state_data.get('message', 'تعیین نشده')}\n"
        f"⏰ <b>ساعت شروع:</b> {state_data.get('start_time', 'تعیین نشده')}\n"
        f"📅 <b>تاریخ شروع:</b> {state_data.get('start_date', 'تعیین نشده')}\n"
        f"⏰ <b>ساعت پایان:</b> {state_data.get('end_time', 'تعیین نشده')}\n"
        f"📅 <b>تاریخ پایان:</b> {state_data.get('end_date', 'تعیین نشده')}\n"
        f"📆 <b>روزهای هفته:</b> {days_text}\n"
        f"🔢 <b>تکرار:</b> {repeat_text}\n"
    )
    
    return summary

async def process_advanced_confirmation(message: types.Message, state: FSMContext):
    """پردازش تأیید نهایی ریمایندر پیشرفته"""
    if message.text == "🔙 بازگشت":
        await state.set_state(AdvancedReminderStates.waiting_for_repeat_interval)
        await message.answer(
            "لطفاً فاصله زمانی را انتخاب کنید:",
            reply_markup=create_repeat_interval_menu()
        )
        return
    
    if message.text == "✅ تأیید و ایجاد":
        state_data = await state.get_data()
        
        try:
            # تبدیل تاریخ‌های شمسی به میلادی برای ذخیره
            start_date_gregorian = persian_to_gregorian_string(state_data['start_date'])
            end_date_gregorian = persian_to_gregorian_string(state_data['end_date'])
            
            # ذخیره در دیتابیس
            reminder_id = reminder_db.add_admin_advanced_reminder(
                admin_id=message.from_user.id,
                title=state_data['title'],
                message=state_data['message'],
                start_time=state_data['start_time'],
                start_date=start_date_gregorian,
                end_time=state_data['end_time'],
                end_date=end_date_gregorian,
                days_of_week=state_data['selected_days'],
                repeat_count=state_data['repeat_count'],
                repeat_interval=state_data['repeat_interval']
            )
            
            await message.answer(
                "🎉 <b>ریمایندر پیشرفته با موفقیت ایجاد شد!</b>\n\n"
                f"📝 کد ریمایندر: <code>{reminder_id}</code>\n"
                f"📝 عنوان: {state_data['title']}\n"
                f"⏰ زمان‌بندی: از {state_data['start_date']} {state_data['start_time']} "
                f"تا {state_data['end_date']} {state_data['end_time']}\n\n"
                "✅ این ریمایندر در زمان‌های مشخص شده ارسال خواهد شد.",
                reply_markup=create_advanced_reminder_admin_menu(),
                parse_mode="HTML"
            )
            
            logger.info(f"✅ ریمایندر پیشرفته {reminder_id} توسط ادمین {message.from_user.id} ایجاد شد")
            
        except Exception as e:
            await message.answer(
                "❌ <b>خطا در ایجاد ریمایندر!</b>\n\n"
                "لطفاً مجدداً تلاش کنید.",
                reply_markup=create_advanced_reminder_admin_menu(),
                parse_mode="HTML"
            )
            logger.error(f"خطا در ایجاد ریمایندر پیشرفته: {e}")
        
        await state.clear()
    
    elif message.text == "✏️ ویرایش اطلاعات":
        await state.set_state(AdvancedReminderStates.waiting_for_title)
        await message.answer(
            "لطفاً عنوان ریمایندر را وارد کنید:",
            reply_markup=create_back_only_menu()
        )
    
    elif message.text == "❌ لغو":
        await message.answer(
            "❌ <b>ایجاد ریمایندر لغو شد</b>",
            reply_markup=create_advanced_reminder_admin_menu(),
            parse_mode="HTML"
        )
        await state.clear()
