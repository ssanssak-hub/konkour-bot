"""
هندلرهای سیستم ریمایندر با کیبورد ساده
"""
import logging
from datetime import datetime
from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from reminder.reminder_keyboards import (
    create_reminder_main_menu,
    create_exam_selection_menu,
    create_days_selection_menu,
    create_time_selection_menu,
    create_repetition_type_menu,
    create_confirmation_menu,
    create_management_menu,
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

# --- هندلرهای اصلی ریمایندر ---
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
        "لطفاً کنکورهای مورد نظر را انتخاب کنید:\n\n"
        "💡 می‌توانید چند کنکور انتخاب کنید",
        reply_markup=create_exam_selection_menu(),
        parse_mode="HTML"
    )

async def process_exam_selection(message: types.Message, state: FSMContext):
    """پردازش انتخاب کنکورها"""
    text = message.text
    
    if text == "✅ انتخاب همه":
        await state.update_data(selected_exams=[
            "علوم_انسانی", "ریاضی_فنی", "علوم_تجربی", 
            "هنر", "زبان_خارجه", "فرهنگیان"
        ])
        await message.answer("✅ همه کنکورها انتخاب شدند")
        
    elif text == "➡️ ادامه":
        state_data = await state.get_data()
        selected_exams = state_data.get('selected_exams', [])
        
        if not selected_exams:
            await message.answer("❌ لطفاً حداقل یک کنکور انتخاب کنید")
            return
        
        await state.set_state(ExamReminderStates.selecting_days)
        await message.answer(
            "🗓️ <b>انتخاب روزهای هفته</b>\n\n"
            "لطفاً روزهایی که می‌خواهید یادآوری دریافت کنید را انتخاب کنید:",
            reply_markup=create_days_selection_menu(),
            parse_mode="HTML"
        )
    
    elif text == "🔙 بازگشت":
        await state.clear()
        await reminder_main_handler(message)
    
    else:
        # پردازش انتخاب کنکور خاص
        exam_map = {
            "🎯 علوم انسانی": "علوم_انسانی",
            "📐 ریاضی و فنی": "ریاضی_فنی", 
            "🔬 علوم تجربی": "علوم_تجربی",
            "🎨 هنر": "هنر",
            "🔠 زبان خارجه": "زبان_خارجه",
            "👨‍🏫 فرهنگیان": "فرهنگیان"
        }
        
        if text in exam_map:
            state_data = await state.get_data()
            selected_exams = state_data.get('selected_exams', [])
            exam_key = exam_map[text]
            
            if exam_key in selected_exams:
                selected_exams.remove(exam_key)
                await message.answer(f"❌ {text} حذف شد")
            else:
                selected_exams.append(exam_key)
                await message.answer(f"✅ {text} اضافه شد")
            
            await state.update_data(selected_exams=selected_exams)

async def process_days_selection(message: types.Message, state: FSMContext):
    """پردازش انتخاب روزهای هفته"""
    text = message.text
    
    if text == "✅ همه روزها":
        await state.update_data(selected_days=[0, 1, 2, 3, 4, 5, 6])
        await message.answer("✅ همه روزها انتخاب شدند")
        
    elif text == "🗑️ پاک کردن":
        await state.update_data(selected_days=[])
        await message.answer("🗑️ همه روزها پاک شد")
        
    elif text == "➡️ ادامه":
        state_data = await state.get_data()
        selected_days = state_data.get('selected_days', [])
        
        if not selected_days:
            await message.answer("❌ لطفاً حداقل یک روز انتخاب کنید")
            return
        
        await state.set_state(ExamReminderStates.selecting_times)
        await message.answer(
            "🕐 <b>انتخاب ساعات یادآوری</b>\n\n"
            "لطفاً ساعات مورد نظر را انتخاب کنید:",
            reply_markup=create_time_selection_menu(),
            parse_mode="HTML"
        )
    
    elif text == "🔙 بازگشت":
        await state.set_state(ExamReminderStates.selecting_exams)
        await start_exam_reminder(message, state)
    
    else:
        # پردازش انتخاب روز خاص
        days_map = {
            "شنبه": 0, "یکشنبه": 1, "دوشنبه": 2,
            "سه‌شنبه": 3, "چهارشنبه": 4, "پنجشنبه": 5, "جمعه": 6
        }
        
        if text in days_map:
            state_data = await state.get_data()
            selected_days = state_data.get('selected_days', [])
            day_index = days_map[text]
            
            if day_index in selected_days:
                selected_days.remove(day_index)
                await message.answer(f"❌ {text} حذف شد")
            else:
                selected_days.append(day_index)
                await message.answer(f"✅ {text} اضافه شد")
            
            await state.update_data(selected_days=selected_days)

async def process_times_selection(message: types.Message, state: FSMContext):
    """پردازش انتخاب ساعات"""
    text = message.text
    
    if text == "✅ انتخاب همه":
        await state.update_data(selected_times=[
            "۸:۰۰", "۱۰:۰۰", "۱۲:۰۰", "۱۴:۰۰",
            "۱۶:۰۰", "۱۸:۰۰", "۲۰:۰۰", "۲۲:۰۰"
        ])
        await message.answer("✅ همه ساعات انتخاب شدند")
        
    elif text == "🗑️ پاک کردن":
        await state.update_data(selected_times=[])
        await message.answer("🗑️ همه ساعات پاک شد")
        
    elif text == "➡️ ادامه":
        state_data = await state.get_data()
        selected_times = state_data.get('selected_times', [])
        
        if not selected_times:
            await message.answer("❌ لطفاً حداقل یک ساعت انتخاب کنید")
            return
        
        await state.set_state(ExamReminderStates.selecting_start_date)
        await message.answer(
            "📅 <b>تاریخ شروع</b>\n\n"
            "لطفاً تاریخ شروع یادآوری را وارد کنید:\n"
            "مثال: <code>1404/08/15</code>\n\n"
            "یا برای بازگشت: 🔙 بازگشت",
            reply_markup=create_back_only_menu(),
            parse_mode="HTML"
        )
    
    elif text == "🔙 بازگشت":
        await state.set_state(ExamReminderStates.selecting_days)
        await message.answer(
            "🗓️ انتخاب روزهای هفته:",
            reply_markup=create_days_selection_menu()
        )
    
    elif text == "✏️ ساعت دلخواه":
        await message.answer(
            "⏰ لطفاً ساعت دلخواه را وارد کنید:\n"
            "مثال: <code>۰۹:۳۰</code>",
            reply_markup=create_back_only_menu()
        )
    
    else:
        # پردازش انتخاب ساعت خاص
        times = ["۸:۰۰", "۱۰:۰۰", "۱۲:۰۰", "۱۴:۰۰", "۱۶:۰۰", "۱۸:۰۰", "۲۰:۰۰", "۲۲:۰۰"]
        if text in times:
            state_data = await state.get_data()
            selected_times = state_data.get('selected_times', [])
            
            if text in selected_times:
                selected_times.remove(text)
                await message.answer(f"❌ {text} حذف شد")
            else:
                selected_times.append(text)
                await message.answer(f"✅ {text} اضافه شد")
            
            await state.update_data(selected_times=selected_times)

async def process_start_date(message: types.Message, state: FSMContext):
    """پردازش تاریخ شروع"""
    if message.text == "🔙 بازگشت":
        await state.set_state(ExamReminderStates.selecting_times)
        await message.answer(
            "🕐 انتخاب ساعات:",
            reply_markup=create_time_selection_menu()
        )
        return
    
    start_date = message.text
    await state.update_data(start_date=start_date)
    await state.set_state(ExamReminderStates.selecting_end_date)
    
    await message.answer(
        "📅 <b>تاریخ پایان</b>\n\n"
        "لطفاً تاریخ پایان یادآوری را وارد کنید:\n"
        "مثال: <code>1405/04/11</code>\n"
        "یا بنویسید: <code>همیشه</code>\n\n"
        "یا برای بازگشت: 🔙 بازگشت",
        reply_markup=create_back_only_menu(),
        parse_mode="HTML"
    )

async def process_end_date(message: types.Message, state: FSMContext):
    """پردازش تاریخ پایان"""
    if message.text == "🔙 بازگشت":
        await state.set_state(ExamReminderStates.selecting_start_date)
        await message.answer(
            "📅 لطفاً تاریخ شروع را وارد کنید:",
            reply_markup=create_back_only_menu()
        )
        return
    
    end_date = message.text
    if end_date.lower() == "همیشه":
        end_date = "1405/12/29"
    
    await state.update_data(end_date=end_date)
    await state.set_state(ExamReminderStates.confirmation)
    
    # نمایش خلاصه و تأیید نهایی
    state_data = await state.get_data()
    summary = create_reminder_summary(state_data)
    
    await message.answer(
        f"✅ <b>خلاصه یادآوری</b>\n\n{summary}\n\n"
        "آیا مایل به ایجاد این یادآوری هستید؟",
        reply_markup=create_confirmation_menu(),
        parse_mode="HTML"
    )

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

# --- هندلر مدیریت ---
async def manage_reminders_handler(message: types.Message):
    """منوی مدیریت ریمایندرها"""
    user_reminders = reminder_db.get_user_exam_reminders(message.from_user.id)
    personal_reminders = reminder_db.get_user_personal_reminders(message.from_user.id)
    
    total_count = len(user_reminders) + len(personal_reminders)
    active_count = len([r for r in user_reminders + personal_reminders if r['is_active']])
    
    await message.answer(
        f"📊 <b>مدیریت یادآوری‌ها</b>\n\n"
        f"📈 آمار شما:\n"
        f"• 📋 کل یادآوری‌ها: {total_count}\n"
        f"• 🔔 فعال: {active_count}\n"
        f"• 🔕 غیرفعال: {total_count - active_count}\n\n"
        f"لطفاً عمل مورد نظر را انتخاب کنید:",
        reply_markup=create_management_menu(),
        parse_mode="HTML"
    )
