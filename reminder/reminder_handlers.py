"""
هندلرهای سیستم ریمایندر
"""
import logging
from datetime import datetime, timedelta
from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from reminder.reminder_keyboards import (
    create_reminder_main_menu,
    create_exam_selection_menu,      # به جای create_exam_selection_keyboard
    create_days_selection_menu,      # به جای create_days_of_week_keyboard  
    create_time_selection_menu,      # به جای create_time_selection_keyboard
    create_repetition_type_menu,     # به جای create_repetition_type_keyboard
    create_confirmation_menu,        # به جای create_confirmation_keyboard
    create_management_menu,          # به جای create_management_keyboard
    create_back_only_menu,
    remove_menu
)

from reminder.reminder_database import reminder_db

logger = logging.getLogger(__name__)

# حالت‌های FSM برای ریمایندر کنکور
class ExamReminderStates(StatesGroup):
    selecting_exams = State()
    selecting_days = State()
    selecting_times = State()
    selecting_start_date = State()
    selecting_end_date = State()
    confirmation = State()

# حالت‌های FSM برای ریمایندر شخصی
class PersonalReminderStates(StatesGroup):
    entering_title = State()
    entering_message = State()
    selecting_repetition = State()
    selecting_days = State()
    selecting_time = State()
    selecting_start_date = State()
    selecting_end_date = State()
    confirmation = State()

# هندلر اصلی منوی ریمایندر
# تغییر از callback به message handler
async def reminder_main_handler(message: types.Message):
    """منوی اصلی ریمایندر"""
    await message.answer(
        "📅 <b>سیستم مدیریت یادآوری‌ها</b>\n\n"
        "لطفاً نوع یادآوری مورد نظر را انتخاب کنید:",
        reply_markup=create_reminder_main_menu(),
        parse_mode="HTML"
    )


# --- هندلرهای ریمایندر کنکور ---
async def start_exam_reminder(message: types.Message, state: FSMContext):
    """شروع ایجاد ریمایندر کنکور"""
    await state.set_state(ExamReminderStates.selecting_exams)
    await message.answer(
        "🎯 <b>یادآوری کنکورها</b>\n\n"
        "لطفاً کنکورهای مورد نظر را انتخاب کنید:",
        reply_markup=create_exam_selection_menu(),
        parse_mode="HTML"
    )


async def process_exam_selection(callback: types.CallbackQuery, state: FSMContext):
    """پردازش انتخاب کنکورها"""
    data = callback.data
    
    if data == "reminder_exams:all":
        # انتخاب همه کنکورها
        await state.update_data(selected_exams=[
            "علوم_انسانی", "ریاضی_فنی", "علوم_تجربی", 
            "هنر", "زبان_خارجه", "فرهنگیان"
        ])
        await callback.answer("✅ همه کنکورها انتخاب شدند")
    
    elif data == "reminder_exams:continue":
        # ادامه به مرحله بعد
        state_data = await state.get_data()
        selected_exams = state_data.get('selected_exams', [])
        
        if not selected_exams:
            await callback.answer("❌ لطفاً حداقل یک کنکور انتخاب کنید")
            return
        
        await state.set_state(ExamReminderStates.selecting_days)
        await callback.message.edit_text(
            "🗓️ <b>انتخاب روزهای هفته</b>\n\n"
            "لطفاً روزهایی که می‌خواهید یادآوری دریافت کنید را انتخاب کنید:",
            reply_markup=create_days_of_week_keyboard(),
            parse_mode="HTML"
        )
    
    elif data.startswith("reminder_exam:"):
        # انتخاب/لغو انتخاب یک کنکور
        exam_key = data.replace("reminder_exam:", "")
        state_data = await state.get_data()
        selected_exams = state_data.get('selected_exams', [])
        
        if exam_key in selected_exams:
            selected_exams.remove(exam_key)
            await callback.answer("❌ حذف شد")
        else:
            selected_exams.append(exam_key)
            await callback.answer("✅ اضافه شد")
        
        await state.update_data(selected_exams=selected_exams)
        
        # آپدیت کیبورد
        await callback.message.edit_reply_markup(
            reply_markup=create_exam_selection_keyboard(selected_exams)
        )

async def process_days_selection(callback: types.CallbackQuery, state: FSMContext):
    """پردازش انتخاب روزهای هفته"""
    data = callback.data
    
    if data == "reminder_days:all":
        # انتخاب همه روزها
        await state.update_data(selected_days=[0, 1, 2, 3, 4, 5, 6])
        await callback.answer("✅ همه روزها انتخاب شدند")
    
    elif data == "reminder_days:clear":
        # پاک کردن همه
        await state.update_data(selected_days=[])
        await callback.answer("🗑️ همه روزها پاک شد")
    
    elif data == "reminder_days:continue":
        # ادامه به مرحله بعد
        state_data = await state.get_data()
        selected_days = state_data.get('selected_days', [])
        
        if not selected_days:
            await callback.answer("❌ لطفاً حداقل یک روز انتخاب کنید")
            return
        
        await state.set_state(ExamReminderStates.selecting_times)
        await callback.message.edit_text(
            "🕐 <b>انتخاب ساعات یادآوری</b>\n\n"
            "لطفاً ساعات مورد نظر را انتخاب کنید:",
            reply_markup=create_time_selection_keyboard(),
            parse_mode="HTML"
        )
    
    elif data.startswith("reminder_day:"):
        # انتخاب/لغو انتخاب یک روز
        day_index = int(data.replace("reminder_day:", ""))
        state_data = await state.get_data()
        selected_days = state_data.get('selected_days', [])
        
        if day_index in selected_days:
            selected_days.remove(day_index)
            await callback.answer("❌ حذف شد")
        else:
            selected_days.append(day_index)
            await callback.answer("✅ اضافه شد")
        
        await state.update_data(selected_days=selected_days)
        
        # آپدیت کیبورد
        await callback.message.edit_reply_markup(
            reply_markup=create_days_of_week_keyboard(selected_days)
        )

async def process_times_selection(callback: types.CallbackQuery, state: FSMContext):
    """پردازش انتخاب ساعات"""
    data = callback.data
    
    if data == "reminder_times:all":
        # انتخاب همه ساعات
        await state.update_data(selected_times=[
            "۰۸:۰۰", "۱۰:۰۰", "۱۲:۰۰", "۱۴:۰۰",
            "۱۶:۰۰", "۱۸:۰۰", "۲۰:۰۰", "۲۲:۰۰"
        ])
        await callback.answer("✅ همه ساعات انتخاب شدند")
    
    elif data == "reminder_times:clear":
        # پاک کردن همه
        await state.update_data(selected_times=[])
        await callback.answer("🗑️ همه ساعات پاک شد")
    
    elif data == "reminder_times:continue":
        # ادامه به مرحله بعد
        state_data = await state.get_data()
        selected_times = state_data.get('selected_times', [])
        
        if not selected_times:
            await callback.answer("❌ لطفاً حداقل یک ساعت انتخاب کنید")
            return
        
        await state.set_state(ExamReminderStates.selecting_start_date)
        await callback.message.edit_text(
            "📅 <b>تاریخ شروع</b>\n\n"
            "لطفاً تاریخ شروع یادآوری را وارد کنید:\n"
            "مثال: <code>1404/08/15</code>",
            parse_mode="HTML"
        )
    
    elif data.startswith("reminder_time:"):
        # انتخاب/لغو انتخاب یک ساعت
        time_str = data.replace("reminder_time:", "")
        state_data = await state.get_data()
        selected_times = state_data.get('selected_times', [])
        
        if time_str in selected_times:
            selected_times.remove(time_str)
            await callback.answer("❌ حذف شد")
        else:
            selected_times.append(time_str)
            await callback.answer("✅ اضافه شد")
        
        await state.update_data(selected_times=selected_times)
        
        # آپدیت کیبورد
        await callback.message.edit_reply_markup(
            reply_markup=create_time_selection_keyboard(selected_times)
        )

async def process_start_date(message: types.Message, state: FSMContext):
    """پردازش تاریخ شروع"""
    # TODO: اضافه کردن منطق اعتبارسنجی تاریخ
    start_date = message.text
    
    await state.update_data(start_date=start_date)
    await state.set_state(ExamReminderStates.selecting_end_date)
    
    await message.answer(
        "📅 <b>تاریخ پایان</b>\n\n"
        "لطفاً تاریخ پایان یادآوری را وارد کنید:\n"
        "مثال: <code>1405/04/11</code>\n"
        "یا بنویسید: <code>همیشه</code>",
        parse_mode="HTML"
    )

async def process_end_date(message: types.Message, state: FSMContext):
    """پردازش تاریخ پایان"""
    end_date = message.text
    
    if end_date.lower() == "همیشه":
        end_date = "1405/12/29"  # پایان سال 1405
    
    await state.update_data(end_date=end_date)
    await state.set_state(ExamReminderStates.confirmation)
    
    # نمایش خلاصه و تأیید نهایی
    state_data = await state.get_data()
    
    summary = create_reminder_summary(state_data)
    await message.answer(
        f"✅ <b>خلاصه یادآوری</b>\n\n{summary}\n\n"
        "آیا مایل به ایجاد این یادآوری هستید؟",
        reply_markup=create_confirmation_keyboard(),
        parse_mode="HTML"
    )

async def confirm_reminder_creation(callback: types.CallbackQuery, state: FSMContext):
    """تأیید نهایی ایجاد ریمایندر"""
    data = callback.data
    
    if data == "reminder_confirm:create":
        state_data = await state.get_data()
        
        # ذخیره در دیتابیس
        reminder_id = reminder_db.add_exam_reminder(
            user_id=callback.from_user.id,
            exam_keys=state_data['selected_exams'],
            days_of_week=state_data['selected_days'],
            specific_times=state_data['selected_times'],
            start_date=state_data['start_date'],
            end_date=state_data['end_date']
        )
        
        await callback.message.edit_text(
            "🎉 <b>یادآوری با موفقیت ایجاد شد!</b>\n\n"
            f"📝 کد یادآوری: <code>{reminder_id}</code>\n"
            "از منوی مدیریت می‌توانید یادآوری‌های خود را مشاهده و مدیریت کنید.",
            parse_mode="HTML"
        )
        
        await state.clear()
    
    elif data == "reminder_confirm:cancel":
        await callback.message.edit_text(
            "❌ <b>ایجاد یادآوری لغو شد</b>",
            parse_mode="HTML"
        )
        await state.clear()

async def process_confirmation(message: types.Message, state: FSMContext):
    """پردازش تأیید نهایی"""
    text = message.text
    
    if text == "✅ تأیید و ایجاد":
        state_data = await state.get_data()
        
        # ذخیره در دیتابیس
        reminder_id = reminder_db.add_exam_reminder(
            user_id=message.from_user.id,
            exam_keys=state_data['selected_exams'],
            days_of_week=state_data['selected_days'],
            specific_times=state_data['selected_times'],
            start_date=state_data['start_date'],
            end_date=state_data['end_date']
        )
        
        await message.answer(
            "🎉 <b>یادآوری با موفقیت ایجاد شد!</b>\n\n"
            f"📝 کد یادآوری: <code>{reminder_id}</code>\n"
            "از منوی مدیریت می‌توانید یادآوری‌های خود را مشاهده و مدیریت کنید.",
            reply_markup=create_reminder_main_menu(),
            parse_mode="HTML"
        )
        
        await state.clear()
    
    elif text == "✏️ ویرایش":
        await state.set_state(ExamReminderStates.selecting_exams)
        await start_exam_reminder(message, state)
    
    elif text == "❌ لغو":
        await message.answer(
            "❌ <b>ایجاد یادآوری لغو شد</b>",
            reply_markup=create_reminder_main_menu(),
            parse_mode="HTML"
        )
        await state.clear()
    
    elif text == "🔙 بازگشت":
        await state.set_state(ExamReminderStates.selecting_end_date)
        await message.answer(
            "📅 لطفاً تاریخ پایان را وارد کنید:",
            reply_markup=create_back_only_menu()
        )

# --- توابع کمکی ---
def create_reminder_summary(state_data: dict) -> str:
    """ایجاد خلاصه ریمایندر"""
    days_map = {
        0: "شنبه", 1: "یکشنبه", 2: "دوشنبه", 
        3: "سه‌شنبه", 4: "چهارشنبه", 5: "پنجشنبه", 6: "جمعه"
    }
    
    selected_days = [days_map[day] for day in state_data.get('selected_days', [])]
    
    summary = (
        f"🎯 <b>کنکورها:</b> {', '.join(state_data.get('selected_exams', []))}\n"
        f"🗓️ <b>روزها:</b> {', '.join(selected_days) if selected_days else 'همه روزها'}\n"
        f"🕐 <b>ساعات:</b> {', '.join(state_data.get('selected_times', []))}\n"
        f"📅 <b>شروع:</b> {state_data.get('start_date', 'تعیین نشده')}\n"
        f"📅 <b>پایان:</b> {state_data.get('end_date', 'تعیین نشده')}\n"
    )
    
    return summary

# هندلر مدیریت ریمایندرها
async def manage_reminders_handler(callback: types.CallbackQuery):
    """منوی مدیریت ریمایندرها"""
    user_reminders = reminder_db.get_user_exam_reminders(callback.from_user.id)
    personal_reminders = reminder_db.get_user_personal_reminders(callback.from_user.id)
    
    total_count = len(user_reminders) + len(personal_reminders)
    active_count = len([r for r in user_reminders + personal_reminders if r['is_active']])
    
    await callback.message.edit_text(
        f"📊 <b>مدیریت یادآوری‌ها</b>\n\n"
        f"📈 آمار شما:\n"
        f"• 📋 کل یادآوری‌ها: {total_count}\n"
        f"• 🔔 فعال: {active_count}\n"
        f"• 🔕 غیرفعال: {total_count - active_count}\n\n"
        f"لطفاً عمل مورد نظر را انتخاب کنید:",
        reply_markup=create_management_keyboard(),
        parse_mode="HTML"
    )
