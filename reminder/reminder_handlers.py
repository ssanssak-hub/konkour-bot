"""
هندلرهای سیستم ریمایندر
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
    create_time_input_menu,
    create_date_input_menu,
    create_repetition_type_menu,
    create_confirmation_menu,
    create_management_menu,
    create_auto_reminders_menu,
    create_back_only_menu,
    remove_menu
)
from reminder.reminder_database import reminder_db
from utils.time_utils import get_current_persian_datetime

logger = logging.getLogger(__name__)

# حالت‌های FSM برای ریمایندر کنکور
class ExamReminderStates(StatesGroup):
    selecting_exams = State()
    selecting_days = State()
    entering_time = State()
    entering_start_date = State()
    entering_end_date = State()
    confirmation = State()

# حالت‌های FSM برای ریمایندر شخصی
class PersonalReminderStates(StatesGroup):
    entering_title = State()
    entering_message = State()
    selecting_repetition = State()
    selecting_days = State()
    entering_time = State()
    entering_start_date = State()
    entering_end_date = State()
    confirmation = State()

# حالت‌های FSM برای مدیریت
class ManagementStates(StatesGroup):
    viewing_reminders = State()
    editing_reminder = State()
    deleting_reminder = State()
    toggling_reminder = State()

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
        "لطفاً کنکورهای مورد نظر را انتخاب کنید:",
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
        
        await state.set_state(ExamReminderStates.entering_time)
        current_time = get_current_persian_datetime()
        await message.answer(
            "🕐 <b>ورود ساعت یادآوری</b>\n\n"
            f"⏰ زمان فعلی: {current_time['full_time']}\n\n"
            "لطفاً ساعت دلخواه را به فرمت زیر وارد کنید:\n"
            "مثال: <code>۰۸:۳۰</code> یا <code>14:45</code>\n\n"
            "یا برای بازگشت: 🔙 بازگشت",
            reply_markup=create_time_input_menu(),
            parse_mode="HTML"
        )
    
    elif text == "🔙 بازگشت":
        await state.set_state(ExamReminderStates.selecting_exams)
        await start_exam_reminder(message, state)
    
    else:
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

async def process_time_input(message: types.Message, state: FSMContext):
    """پردازش ورود ساعت"""
    if message.text == "🔙 بازگشت":
        await state.set_state(ExamReminderStates.selecting_days)
        await message.answer(
            "🗓️ انتخاب روزهای هفته:",
            reply_markup=create_days_selection_menu()
        )
        return
    
    time_str = message.text
    # اعتبارسنجی ساده فرمت زمان
    if not (len(time_str) in [4, 5] and ':' in time_str):
        await message.answer("❌ فرمت زمان نامعتبر! لطفاً به فرمت HH:MM وارد کنید")
        return
    
    await state.update_data(specific_time=time_str)
    await state.set_state(ExamReminderStates.entering_start_date)
    
    current_date = get_current_persian_datetime()
    await message.answer(
        "📅 <b>تاریخ شروع یادآوری</b>\n\n"
        f"📆 تاریخ امروز: {current_date['full_date']}\n\n"
        "لطفاً تاریخ شروع را به فرمت زیر وارد کنید:\n"
        "مثال: <code>1404/08/15</code>\n\n"
        "یا برای شروع از امروز: 📅 امروز\n"
        "یا برای بازگشت: 🔙 بازگشت",
        reply_markup=create_date_input_menu(),
        parse_mode="HTML"
    )

async def process_start_date(message: types.Message, state: FSMContext):
    """پردازش تاریخ شروع"""
    if message.text == "🔙 بازگشت":
        await state.set_state(ExamReminderStates.entering_time)
        await message.answer(
            "🕐 لطفاً ساعت را وارد کنید:",
            reply_markup=create_time_input_menu()
        )
        return
    
    if message.text == "📅 امروز":
        current_date = get_current_persian_datetime()
        start_date = f"{current_date['year']}/{current_date['month']:02d}/{current_date['day']:02d}"
        await message.answer(f"✅ تاریخ شروع: {start_date}")
    else:
        start_date = message.text
    
    await state.update_data(start_date=start_date)
    await state.set_state(ExamReminderStates.entering_end_date)
    
    await message.answer(
        "📅 <b>تاریخ پایان یادآوری</b>\n\n"
        "لطفاً تاریخ پایان را به فرمت زیر وارد کنید:\n"
        "مثال: <code>1405/04/11</code>\n"
        "یا بنویسید: <code>همیشه</code>\n\n"
        "یا برای بازگشت: 🔙 بازگشت",
        reply_markup=create_back_only_menu(),
        parse_mode="HTML"
    )

async def process_end_date(message: types.Message, state: FSMContext):
    """پردازش تاریخ پایان"""
    if message.text == "🔙 بازگشت":
        await state.set_state(ExamReminderStates.entering_start_date)
        await message.answer(
            "📅 لطفاً تاریخ شروع را وارد کنید:",
            reply_markup=create_date_input_menu()
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
        f"✅ <b>خلاصه یادآوری کنکور</b>\n\n{summary}\n\n"
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
            specific_times=[state_data['specific_time']],
            start_date=state_data['start_date'],
            end_date=state_data['end_date']
        )
        
        await message.answer(
            "🎉 <b>یادآوری کنکور با موفقیت ایجاد شد!</b>\n\n"
            f"📝 کد یادآوری: <code>{reminder_id}</code>\n"
            "می‌توانید یادآوری‌های خود را از بخش مدیریت مشاهده کنید.",
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
        await state.set_state(ExamReminderStates.entering_end_date)
        await message.answer(
            "📅 لطفاً تاریخ پایان را وارد کنید:",
            reply_markup=create_back_only_menu()
        )

# --- هندلرهای ریمایندر شخصی ---
async def start_personal_reminder(message: types.Message, state: FSMContext):
    """شروع ایجاد ریمایندر شخصی"""
    await state.set_state(PersonalReminderStates.entering_title)
    await message.answer(
        "📝 <b>یادآوری شخصی</b>\n\n"
        "لطفاً عنوان یادآوری را وارد کنید:\n\n"
        "مثال: <code>مرور فصل ۳ ریاضی</code>",
        reply_markup=create_back_only_menu(),
        parse_mode="HTML"
    )

async def process_personal_title(message: types.Message, state: FSMContext):
    """پردازش عنوان ریمایندر شخصی"""
    if message.text == "🔙 بازگشت":
        await state.clear()
        await reminder_main_handler(message)
        return
    
    await state.update_data(title=message.text)
    await state.set_state(PersonalReminderStates.entering_message)
    
    await message.answer(
        "📄 <b>متن یادآوری</b>\n\n"
        "لطفاً متن کامل یادآوری را وارد کنید:\n\n"
        "مثال: <code>وقت مرور فصل ۳ ریاضی و حل تمرین‌های صفحه ۸۵</code>",
        reply_markup=create_back_only_menu(),
        parse_mode="HTML"
    )

async def process_personal_message(message: types.Message, state: FSMContext):
    """پردازش متن ریمایندر شخصی"""
    if message.text == "🔙 بازگشت":
        await state.set_state(PersonalReminderStates.entering_title)
        await message.answer(
            "لطفاً عنوان یادآوری را وارد کنید:",
            reply_markup=create_back_only_menu()
        )
        return
    
    await state.update_data(message=message.text)
    await state.set_state(PersonalReminderStates.selecting_repetition)
    
    await message.answer(
        "🔁 <b>نوع تکرار یادآوری</b>\n\n"
        "لطفاً نوع تکرار را انتخاب کنید:",
        reply_markup=create_repetition_type_menu(),
        parse_mode="HTML"
    )

# --- هندلرهای یادآوری خودکار ---
async def start_auto_reminders(message: types.Message):
    """منوی یادآوری خودکار"""
    await message.answer(
        "🤖 <b>یادآوری خودکار</b>\n\n"
        "این سیستم به صورت خودکار در زمان‌های مهم یادآوری ارسال می‌کند.\n\n"
        "ویژگی‌ها:\n"
        "• 📅 ۹۰ روز قبل از کنکور\n"
        "• 🗓️ ۳۰ روز قبل از کنکور\n"
        "• 📊 ۱۵ روز قبل از کنکور\n"
        "• ⏰ ۷ روز قبل از کنکور\n"
        "• 🔔 ۳ روز قبل از کنکور\n"
        "• 🎯 ۱ روز قبل از کنکور\n\n"
        "لطفاً عمل مورد نظر را انتخاب کنید:",
        reply_markup=create_auto_reminders_menu(),
        parse_mode="HTML"
    )

async def list_auto_reminders(message: types.Message):
    """نمایش لیست یادآوری‌های خودکار"""
    auto_reminders = [
        {"days": 90, "title": "شروع فصل طلایی", "status": "✅ فعال"},
        {"days": 30, "title": "شروع جمع‌بندی", "status": "✅ فعال"},
        {"days": 15, "title": "دو هفته پایانی", "status": "✅ فعال"},
        {"days": 7, "title": "هفته آخر", "status": "❌ غیرفعال"},
        {"days": 3, "title": "آماده‌سازی نهایی", "status": "❌ غیرفعال"},
        {"days": 1, "title": "روز قبل کنکور", "status": "✅ فعال"},
    ]
    
    message_text = "📋 <b>لیست یادآوری‌های خودکار</b>\n\n"
    for reminder in auto_reminders:
        message_text += f"• {reminder['days']} روز قبل: {reminder['title']} - {reminder['status']}\n"
    
    message_text += "\n💡 می‌توانید وضعیت هر یادآوری را تغییر دهید."
    
    await message.answer(
        message_text,
        reply_markup=create_auto_reminders_menu(),
        parse_mode="HTML"
    )

# --- هندلرهای مدیریت یادآوری ---
async def manage_reminders_handler(message: types.Message):
    """منوی مدیریت یادآوری"""
    user_reminders = reminder_db.get_user_exam_reminders(message.from_user.id)
    personal_reminders = reminder_db.get_user_personal_reminders(message.from_user.id)
    
    total_count = len(user_reminders) + len(personal_reminders)
    active_count = len([r for r in user_reminders + personal_reminders if r['is_active']])
    
    await message.answer(
        f"📋 <b>مدیریت یادآوری‌ها</b>\n\n"
        f"📊 آمار شما:\n"
        f"• 📝 کل یادآوری‌ها: {total_count}\n"
        f"• 🔔 فعال: {active_count}\n"
        f"• 🔕 غیرفعال: {total_count - active_count}\n\n"
        f"لطفاً عمل مورد نظر را انتخاب کنید:",
        reply_markup=create_management_menu(),
        parse_mode="HTML"
    )

async def view_all_reminders(message: types.Message):
    """مشاهده همه یادآوری‌ها"""
    user_reminders = reminder_db.get_user_exam_reminders(message.from_user.id)
    personal_reminders = reminder_db.get_user_personal_reminders(message.from_user.id)
    
    if not user_reminders and not personal_reminders:
        await message.answer(
            "📭 <b>هیچ یادآوری‌ای پیدا نشد</b>\n\n"
            "می‌توانید از منوی اصلی یک یادآوری جدید ایجاد کنید.",
            reply_markup=create_management_menu(),
            parse_mode="HTML"
        )
        return
    
    message_text = "📋 <b>همه یادآوری‌های شما</b>\n\n"
    
    if user_reminders:
        message_text += "🎯 <b>یادآوری‌های کنکور:</b>\n"
        for reminder in user_reminders:
            status = "🔔" if reminder['is_active'] else "🔕"
            message_text += f"{status} کد {reminder['id']}: {', '.join(reminder['exam_keys'])}\n"
        message_text += "\n"
    
    if personal_reminders:
        message_text += "📝 <b>یادآوری‌های شخصی:</b>\n"
        for reminder in personal_reminders:
            status = "🔔" if reminder['is_active'] else "🔕"
            message_text += f"{status} کد {reminder['id']}: {reminder['title']}\n"
    
    await message.answer(
        message_text,
        reply_markup=create_management_menu(),
        parse_mode="HTML"
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
        f"🕐 <b>ساعت:</b> {state_data.get('specific_time', 'تعیین نشده')}\n"
        f"📅 <b>شروع:</b> {state_data.get('start_date', 'تعیین نشده')}\n"
        f"📅 <b>پایان:</b> {state_data.get('end_date', 'تعیین نشده')}\n"
    )
    
    return summary
