"""
هندلرهای سیستم ریمایندر - نسخه کامل با تاریخ میلادی
"""
import logging
from datetime import datetime, timedelta
from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton  # 🔥 این خط رو اضافه کن

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
from reminder.reminder_utils import validator, formatter, analyzer
from utils.time_utils import get_current_persian_datetime, format_gregorian_date_for_display
from exam_data import EXAMS_1405

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
    entering_custom_interval = State()
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
    user_stats = reminder_db.get_reminder_stats(message.from_user.id)
    
    await message.answer(
        "📅 <b>سیستم مدیریت یادآوری‌ها</b>\n\n"
        f"📊 آمار شما:\n"
        f"• 📝 کل یادآوری‌ها: {user_stats.get('user_total_reminders', 0)}\n"
        f"• 📤 ارسال شده: {user_stats.get('user_total_sent', 0)}\n\n"
        "لطفاً نوع یادآوری مورد نظر را انتخاب کنید:",
        reply_markup=create_reminder_main_menu(),
        parse_mode="HTML"
    )

# --- هندلرهای ریمایندر کنکور ---
async def start_exam_reminder(message: types.Message, state: FSMContext):
    """شروع ایجاد ریمایندر کنکور"""
    await state.set_state(ExamReminderStates.selecting_exams)
    await state.update_data(selected_exams=[])
    
    await message.answer(
        "🎯 <b>یادآوری کنکورها</b>\n\n"
        "لطفاً کنکورهای مورد نظر را انتخاب کنید:\n\n"
        "💡 <i>می‌توانید چندین کنکور انتخاب کنید</i>",
        reply_markup=create_exam_selection_menu(),
        parse_mode="HTML"
    )

async def process_exam_selection(message: types.Message, state: FSMContext):
    """پردازش انتخاب کنکورها"""
    text = message.text
    
    if text == "✅ انتخاب همه":
        await state.update_data(selected_exams=list(EXAMS_1405.keys()))
        await message.answer(
            "✅ همه کنکورها انتخاب شدند\n\n"
            "برای ادامه روی '➡️ ادامه' کلیک کنید",
            reply_markup=create_exam_selection_menu()
        )
        
    elif text == "➡️ ادامه":
        state_data = await state.get_data()
        selected_exams = state_data.get('selected_exams', [])
        
        if not selected_exams:
            await message.answer(
                "❌ لطفاً حداقل یک کنکور انتخاب کنید",
                reply_markup=create_exam_selection_menu()
            )
            return
        
        await state.set_state(ExamReminderStates.selecting_days)
        await state.update_data(selected_days=[])
        
        await message.answer(
            "🗓️ <b>انتخاب روزهای هفته</b>\n\n"
            "لطفاً روزهایی که می‌خواهید یادآوری دریافت کنید را انتخاب کنید:\n\n"
            "💡 <i>می‌توانید چندین روز انتخاب کنید</i>",
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
                action_text = f"❌ {text} حذف شد"
            else:
                selected_exams.append(exam_key)
                action_text = f"✅ {text} اضافه شد"
            
            await state.update_data(selected_exams=selected_exams)
            
            # نمایش وضعیت فعلی
            current_count = len(selected_exams)
            await message.answer(
                f"{action_text}\n\n"
                f"📋 انتخاب‌های فعلی: {current_count} کنکور\n"
                f"برای ادامه روی '➡️ ادامه' کلیک کنید"
            )

async def process_days_selection(message: types.Message, state: FSMContext):
    """پردازش انتخاب روزهای هفته"""
    text = message.text
    
    if text == "✅ همه روزها":
        await state.update_data(selected_days=[0, 1, 2, 3, 4, 5, 6])
        await message.answer(
            "✅ همه روزهای هفته انتخاب شدند\n\n"
            "برای ادامه روی '➡️ ادامه' کلیک کنید",
            reply_markup=create_days_selection_menu()
        )
        
    elif text == "🗑️ پاک کردن":
        await state.update_data(selected_days=[])
        await message.answer(
            "🗑️ همه روزها پاک شد\n\n"
            "لطفاً روزهای مورد نظر را انتخاب کنید"
        )
        
    elif text == "➡️ ادامه":
        state_data = await state.get_data()
        selected_days = state_data.get('selected_days', [])
        
        if not selected_days:
            await message.answer(
                "❌ لطفاً حداقل یک روز انتخاب کنید",
                reply_markup=create_days_selection_menu()
            )
            return
        
        await state.set_state(ExamReminderStates.entering_time)
        current_time = get_current_persian_datetime()
        
        await message.answer(
            "🕐 <b>ورود ساعت یادآوری</b>\n\n"
            f"⏰ زمان فعلی: {current_time['full_time']}\n\n"
            "⚠️ <b>توجه: فقط از اعداد انگلیسی استفاده کنید</b>\n\n"
            "لطفاً ساعت دلخواه را به فرمت زیر وارد کنید:\n"
            "• مثال: <code>08:30</code>\n"
            "• مثال: <code>14:45</code>\n\n"
            "💡 <i>ساعت باید بین 00:00 تا 23:59 باشد</i>\n\n"
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
                action_text = f"❌ {text} حذف شد"
            else:
                selected_days.append(day_index)
                action_text = f"✅ {text} اضافه شد"
            
            await state.update_data(selected_days=selected_days)
            
            # نمایش وضعیت فعلی
            current_days = [day for day in days_map if days_map[day] in selected_days]
            days_text = "، ".join(current_days) if current_days else "هیچ روزی"
            
            await message.answer(
                f"{action_text}\n\n"
                f"📋 روزهای انتخاب شده: {days_text}\n"
                f"برای ادامه روی '➡️ ادامه' کلیک کنید"
            )

async def process_time_input(message: types.Message, state: FSMContext):
    """پردازش ورود ساعت با اعتبارسنجی پیشرفته"""
    if message.text == "🔙 بازگشت":
        await state.set_state(ExamReminderStates.selecting_days)
        await message.answer(
            "🗓️ انتخاب روزهای هفته:",
            reply_markup=create_days_selection_menu()
        )
        return
    
    time_str = message.text
    
    # تبدیل اعداد فارسی به انگلیسی
    persian_to_english = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
    time_str = time_str.translate(persian_to_english)
    
    # اعتبارسنجی فرمت زمان
    import re
    time_pattern = re.compile(r'^([0-1]?[0-9]|2[0-3]):([0-5][0-9])$')
    
    if not time_pattern.match(time_str):
        await message.answer(
            "❌ <b>فرمت زمان نامعتبر!</b>\n\n"
            "⚠️ <b>لطفاً فقط از اعداد انگلیسی استفاده کنید:</b>\n"
            "• ✅ صحیح: <code>08:30</code>, <code>14:45</code>, <code>9:05</code>\n"
            "• ❌ غلط: <code>۰۸:۳۰</code>, <code>۸:۳۰</code>, <code>24:70</code>\n\n"
            "📝 فرمت صحیح: <b>HH:MM</b>\n"
            "• ساعت: 00 تا 23\n"
            "• دقیقه: 00 تا 59\n\n"
            "لطفاً مجدداً وارد کنید:",
            parse_mode="HTML",
            reply_markup=create_time_input_menu()
        )
        return
    
    # زمان معتبر است
    await state.update_data(specific_time=time_str)
    await state.set_state(ExamReminderStates.entering_start_date)
    
    current_date = get_current_persian_datetime()
    await message.answer(
        "📅 <b>تاریخ شروع یادآوری</b>\n\n"
        f"📆 تاریخ امروز: {current_date['full_date']}\n\n"
        "⚠️ <b>توجه: فقط از اعداد انگلیسی استفاده کنید</b>\n"
        "لطفاً تاریخ شروع را به فرمت زیر وارد کنید:\n"
        "• مثال: <code>1404/08/15</code>\n\n"
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
        # اعتبارسنجی ساده تاریخ
        if not validator.validate_persian_date(start_date.replace('/', '')):
            await message.answer(
                "❌ فرمت تاریخ نامعتبر!\n\n"
                "لطفاً تاریخ را به فرمت <code>1404/08/15</code> وارد کنید:",
                parse_mode="HTML",
                reply_markup=create_date_input_menu()
            )
            return
    
    await state.update_data(start_date=start_date)
    await state.set_state(ExamReminderStates.entering_end_date)
    
    await message.answer(
        "📅 <b>تاریخ پایان یادآوری</b>\n\n"
        "⚠️ <b>توجه: فقط از اعداد انگلیسی استفاده کنید</b>\n\n"
        "لطفاً تاریخ پایان را به فرمت زیر وارد کنید:\n"
        "• مثال: <code>1405/04/11</code>\n"
        "• یا بنویسید: <code>همیشه</code>\n\n"
        "💡 <i>یادآوری تا این تاریخ ادامه خواهد یافت</i>\n\n"
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
        end_date = "1405/12/29"  # پایان سال 1405
        await message.answer(f"✅ تاریخ پایان: {end_date} (همیشه)")
    else:
        # اعتبارسنجی ساده تاریخ
        if not validator.validate_persian_date(end_date.replace('/', '')):
            await message.answer(
                "❌ فرمت تاریخ نامعتبر!\n\n"
                "لطفاً تاریخ را به فرمت <code>1405/04/11</code> وارد کنید\n"
                "یا بنویسید <code>همیشه</code>:",
                parse_mode="HTML",
                reply_markup=create_back_only_menu()
            )
            return
    
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
        
        try:
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
                f"⏰ اولین یادآوری: امروز ساعت {state_data['specific_time']}\n\n"
                "می‌توانید یادآوری‌های خود را از بخش مدیریت مشاهده کنید.\n\n"
                "💡 <i>کاربر گرامی یادآوری ثبت شده شما ممکن است با یک دقیقه تاخیر برای شما ارسال شود، لطفاً شکیبا باشید🎈</i>\n"
                "<i>از طرف سَنس | SanssAK</i>",
                reply_markup=create_reminder_main_menu(),
                parse_mode="HTML"
            )
            
            logger.info(f"✅ ریمایندر کنکور {reminder_id} برای کاربر {message.from_user.id} ایجاد شد")
            
        except Exception as e:
            await message.answer(
                "❌ <b>خطا در ایجاد یادآوری!</b>\n\n"
                "لطفاً مجدداً تلاش کنید.",
                reply_markup=create_reminder_main_menu(),
                parse_mode="HTML"
            )
            logger.error(f"خطا در ایجاد ریمایندر کنکور: {e}")
        
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
    await state.update_data(reminder_data={})
    
    await message.answer(
        "📝 <b>یادآوری شخصی</b>\n\n"
        "لطفاً عنوان یادآوری را وارد کنید:\n\n"
        "💡 <i>مثال: مرور فصل ۳ ریاضی</i>\n\n"
        "یا برای بازگشت: 🔙 بازگشت",
        reply_markup=create_back_only_menu(),
        parse_mode="HTML"
    )

async def process_personal_title(message: types.Message, state: FSMContext):
    """پردازش عنوان ریمایندر شخصی"""
    if message.text == "🔙 بازگشت":
        await state.clear()
        await reminder_main_handler(message)
        return
    
    if len(message.text) > 100:
        await message.answer(
            "❌ عنوان خیلی طولانی است!\n\n"
            "لطفاً عنوانی کوتاه‌تر (حداکثر ۱۰۰ کاراکتر) وارد کنید:",
            reply_markup=create_back_only_menu()
        )
        return
    
    await state.update_data(title=message.text)
    await state.set_state(PersonalReminderStates.entering_message)
    
    await message.answer(
        "📄 <b>متن یادآوری</b>\n\n"
        "لطفاً متن کامل یادآوری را وارد کنید:\n\n"
        "💡 <i>مثال: وقت مرور فصل ۳ ریاضی و حل تمرین‌های صفحه ۸۵</i>\n\n"
        "یا برای بازگشت: 🔙 بازگشت",
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
    
    if len(message.text) > 500:
        await message.answer(
            "❌ متن خیلی طولانی است!\n\n"
            "لطفاً متنی کوتاه‌تر (حداکثر ۵۰۰ کاراکتر) وارد کنید:",
            reply_markup=create_back_only_menu()
        )
        return
    
    await state.update_data(message=message.text)
    await state.set_state(PersonalReminderStates.selecting_repetition)
    
    await message.answer(
        "🔁 <b>نوع تکرار یادآوری</b>\n\n"
        "لطفاً نوع تکرار را انتخاب کنید:\n\n"
        "• 🔘 یکبار - فقط یکبار ارسال می‌شود\n"
        "• 🔄 روزانه - هر روز در ساعت مشخص\n"
        "• 📅 هفتگی - روزهای مشخص هفته\n"
        "• 🗓️ ماهانه - هر ماه در تاریخ مشخص\n"
        "• ⚙️ سفارشی - با فاصله روزهای مشخص\n\n"
        "یا برای بازگشت: 🔙 بازگشت",
        reply_markup=create_repetition_type_menu(),
        parse_mode="HTML"
    )
    
async def process_repetition_selection(message: types.Message, state: FSMContext):
    """پردازش انتخاب نوع تکرار"""
    if message.text == "🔙 بازگشت":
        await state.set_state(PersonalReminderStates.entering_message)
        await message.answer(
            "لطفاً متن یادآوری را وارد کنید:",
            reply_markup=create_back_only_menu()
        )
        return
    
    repetition_map = {
        "🔘 یکبار": "once",
        "🔄 روزانه": "daily", 
        "📅 هفتگی": "weekly",
        "🗓️ ماهانه": "monthly",
        "⚙️ سفارشی": "custom"
    }
    
    if message.text not in repetition_map:
        await message.answer(
            "❌ گزینه نامعتبر!\n\n"
            "لطفاً از گزینه‌های موجود انتخاب کنید:",
            reply_markup=create_repetition_type_menu()
        )
        return
    
    repetition_type = repetition_map[message.text]
    await state.update_data(repetition_type=repetition_type)
    
    if repetition_type == "weekly":
        await state.set_state(PersonalReminderStates.selecting_days)
        await state.update_data(days_of_week=[])
        
        await message.answer(
            "🗓️ <b>انتخاب روزهای هفته</b>\n\n"
            "لطفاً روزهایی که می‌خواهید یادآوری دریافت کنید را انتخاب کنید:",
            reply_markup=create_days_selection_menu(),
            parse_mode="HTML"
        )
    elif repetition_type == "custom":
        await state.set_state(PersonalReminderStates.entering_custom_interval)
        
        await message.answer(
            "⚙️ <b>فاصله تکرار سفارشی</b>\n\n"
            "لطفاً فاصله روزهای بین یادآوری‌ها را وارد کنید:\n\n"
            "💡 <i>مثال: برای یادآوری هر ۳ روز یکبار، عدد ۳ را وارد کنید</i>\n\n"
            "یا برای بازگشت: 🔙 بازگشت",
            reply_markup=create_back_only_menu(),
            parse_mode="HTML"
        )
    else:
        await state.set_state(PersonalReminderStates.entering_time)
        current_time = get_current_persian_datetime()
        
        await message.answer(
            "🕐 <b>ورود ساعت یادآوری</b>\n\n"
            f"⏰ زمان فعلی: {current_time['full_time']}\n\n"
            "⚠️ <b>توجه: فقط از اعداد انگلیسی استفاده کنید</b>\n\n"
            "لطفاً ساعت دلخواه را به فرمت HH:MM وارد کنید:",
            reply_markup=create_time_input_menu(),
            parse_mode="HTML"
        )

async def process_personal_days_selection(message: types.Message, state: FSMContext):
    """پردازش انتخاب روزهای هفته برای ریمایندر شخصی"""
    text = message.text
    
    if text == "✅ همه روزها":
        await state.update_data(days_of_week=[0, 1, 2, 3, 4, 5, 6])
        await message.answer(
            "✅ همه روزهای هفته انتخاب شدند\n\n"
            "برای ادامه روی '➡️ ادامه' کلیک کنید",
            reply_markup=create_days_selection_menu()
        )
        
    elif text == "🗑️ پاک کردن":
        await state.update_data(days_of_week=[])
        await message.answer(
            "🗑️ همه روزها پاک شد\n\n"
            "لطفاً روزهای مورد نظر را انتخاب کنید"
        )
        
    elif text == "➡️ ادامه":
        state_data = await state.get_data()
        selected_days = state_data.get('days_of_week', [])
        
        if not selected_days:
            await message.answer(
                "❌ لطفاً حداقل یک روز انتخاب کنید",
                reply_markup=create_days_selection_menu()
            )
            return
        
        await state.set_state(PersonalReminderStates.entering_time)
        current_time = get_current_persian_datetime()
        
        await message.answer(
            "🕐 <b>ورود ساعت یادآوری</b>\n\n"
            f"⏰ زمان فعلی: {current_time['full_time']}\n\n"
            "لطفاً ساعت دلخواه را به فرمت HH:MM وارد کنید:",
            reply_markup=create_time_input_menu(),
            parse_mode="HTML"
        )
    
    elif text == "🔙 بازگشت":
        await state.set_state(PersonalReminderStates.selecting_repetition)
        await message.answer(
            "لطفاً نوع تکرار را انتخاب کنید:",
            reply_markup=create_repetition_type_menu()
        )
    
    else:
        days_map = {
            "شنبه": 0, "یکشنبه": 1, "دوشنبه": 2,
            "سه‌شنبه": 3, "چهارشنبه": 4, "پنجشنبه": 5, "جمعه": 6
        }
        
        if text in days_map:
            state_data = await state.get_data()
            selected_days = state_data.get('days_of_week', [])
            day_index = days_map[text]
            
            if day_index in selected_days:
                selected_days.remove(day_index)
                action_text = f"❌ {text} حذف شد"
            else:
                selected_days.append(day_index)
                action_text = f"✅ {text} اضافه شد"
            
            await state.update_data(days_of_week=selected_days)
            
            # نمایش وضعیت فعلی
            current_days = [day for day in days_map if days_map[day] in selected_days]
            days_text = "، ".join(current_days) if current_days else "هیچ روزی"
            
            await message.answer(
                f"{action_text}\n\n"
                f"📋 روزهای انتخاب شده: {days_text}\n"
                f"برای ادامه روی '➡️ ادامه' کلیک کنید"
            )

async def process_personal_time_input(message: types.Message, state: FSMContext):
    """پردازش ورود ساعت برای ریمایندر شخصی"""
    if message.text == "🔙 بازگشت":
        state_data = await state.get_data()
        repetition_type = state_data.get('repetition_type')
        
        if repetition_type == "weekly":
            await state.set_state(PersonalReminderStates.selecting_days)
            await message.answer(
                "🗓️ انتخاب روزهای هفته:",
                reply_markup=create_days_selection_menu()
            )
        else:
            await state.set_state(PersonalReminderStates.selecting_repetition)
            await message.answer(
                "لطفاً نوع تکرار را انتخاب کنید:",
                reply_mekup=create_repetition_type_menu()
            )
        return
    
    time_str = message.text
    
    # تبدیل اعداد فارسی به انگلیسی
    persian_to_english = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
    time_str = time_str.translate(persian_to_english)
    
    # اعتبارسنجی فرمت زمان
    import re
    time_pattern = re.compile(r'^([0-1]?[0-9]|2[0-3]):([0-5][0-9])$')
    
    if not time_pattern.match(time_str):
        await message.answer(
            "❌ <b>فرمت زمان نامعتبر!</b>\n\n"
            "لطفاً ساعت را به فرمت HH:MM وارد کنید:\n"
            "• مثال: <code>08:30</code>\n"
            "• مثال: <code>14:45</code>\n\n"
            "لطفاً مجدداً وارد کنید:",
            parse_mode="HTML",
            reply_markup=create_time_input_menu()
        )
        return
    
    await state.update_data(specific_time=time_str)
    await state.set_state(PersonalReminderStates.entering_start_date)
    
    current_date = get_current_persian_datetime()
    await message.answer(
        "📅 <b>تاریخ شروع یادآوری</b>\n\n"
        f"📆 تاریخ امروز: {current_date['full_date']}\n\n"
        "لطفاً تاریخ شروع را به فرمت YYYY/MM/DD وارد کنید:\n"
        "• مثال: <code>1404/08/15</code>\n\n"
        "یا برای شروع از امروز: 📅 امروز\n"
        "یا برای بازگشت: 🔙 بازگشت",
        reply_markup=create_date_input_menu(),
        parse_mode="HTML"
    )

async def process_personal_start_date(message: types.Message, state: FSMContext):
    """پردازش تاریخ شروع برای ریمایندر شخصی"""
    if message.text == "🔙 بازگشت":
        await state.set_state(PersonalReminderStates.entering_time)
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
    await state.set_state(PersonalReminderStates.confirmation)
    
    # نمایش خلاصه و تأیید نهایی
    state_data = await state.get_data()
    summary = formatter.create_reminder_summary(state_data, "personal")
    
    await message.answer(
        f"✅ <b>خلاصه یادآوری شخصی</b>\n\n{summary}\n\n"
        "آیا مایل به ایجاد این یادآوری هستید؟",
        reply_markup=create_confirmation_menu(),
        parse_mode="HTML"
    )

async def process_personal_confirmation(message: types.Message, state: FSMContext):
    """پردازش تأیید نهایی ریمایندر شخصی"""
    text = message.text
    
    if text == "✅ تأیید و ایجاد":
        state_data = await state.get_data()
        
        try:
            # ذخیره در دیتابیس
            reminder_id = reminder_db.add_personal_reminder(
                user_id=message.from_user.id,
                title=state_data['title'],
                message=state_data['message'],
                repetition_type=state_data['repetition_type'],
                specific_time=state_data['specific_time'],
                start_date=state_data['start_date'],
                days_of_week=state_data.get('days_of_week', []),
                custom_days_interval=state_data.get('custom_days_interval'),
                end_date=state_data.get('end_date'),
                max_occurrences=state_data.get('max_occurrences')
            )
            
            await message.answer(
                "🎉 <b>یادآوری شخصی با موفقیت ایجاد شد!</b>\n\n"
                f"📝 کد یادآوری: <code>{reminder_id}</code>\n"
                f"⏰ اولین یادآوری: فردا ساعت {state_data['specific_time']}\n\n"
                "می‌توانید یادآوری‌های خود را از بخش مدیریت مشاهده کنید.",
                reply_markup=create_reminder_main_menu(),
                parse_mode="HTML"
            )
            
            logger.info(f"✅ ریمایندر شخصی {reminder_id} برای کاربر {message.from_user.id} ایجاد شد")
            
        except Exception as e:
            await message.answer(
                "❌ <b>خطا در ایجاد یادآوری!</b>\n\n"
                "لطفاً مجدداً تلاش کنید.",
                reply_markup=create_reminder_main_menu(),
                parse_mode="HTML"
            )
            logger.error(f"خطا در ایجاد ریمایندر شخصی: {e}")
        
        await state.clear()
    
    elif text == "✏️ ویرایش":
        await state.set_state(PersonalReminderStates.entering_title)
        await message.answer(
            "لطفاً عنوان یادآوری را وارد کنید:",
            reply_markup=create_back_only_menu()
        )
    
    elif text == "❌ لغو":
        await message.answer(
            "❌ <b>ایجاد یادآوری لغو شد</b>",
            reply_markup=create_reminder_main_menu(),
            parse_mode="HTML"
        )
        await state.clear()
    
    elif text == "🔙 بازگشت":
        await state.set_state(PersonalReminderStates.entering_start_date)
        await message.answer(
            "📅 لطفاً تاریخ شروع را وارد کنید:",
            reply_markup=create_date_input_menu()
        )

# --- هندلرهای یادآوری خودکار ---
async def start_auto_reminders(message: types.Message):
    """منوی یادآوری خودکار"""
    await message.answer(
        "🤖 <b>یادآوری خودکار</b>\n\n"
        "این سیستم به صورت خودکار در زمان‌های مهم یادآوری ارسال می‌کند.\n\n"
        "📋 <b>یادآوری‌های موجود:</b>\n"
        "• 📅 ۹۰ روز قبل از کنکور\n"
        "• 🗓️ ۳۰ روز قبل از کنکور\n"  
        "• 📊 ۱۵ روز قبل از کنکور\n"
        "• ⏰ ۷ روز قبل از کنکور\n"
        "• 🔔 ۳ روز قبل از کنکور\n"
        "• 🎯 ۱ روز قبل از کنکور\n\n"
        "💡 <i>این یادآوری‌ها برای همه کنکورها فعال می‌شوند</i>\n\n"
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
    
    stats = analyzer.calculate_reminder_stats(user_reminders + personal_reminders)
    
    await message.answer(
        f"📋 <b>مدیریت یادآوری‌ها</b>\n\n"
        f"📊 آمار شما:\n"
        f"• 📝 کل یادآوری‌ها: {total_count}\n"
        f"• 🔔 فعال: {active_count}\n"
        f"• 🔕 غیرفعال: {total_count - active_count}\n"
        f"• 🎯 کنکوری: {stats['exam_count']}\n"
        f"• 📝 شخصی: {stats['personal_count']}\n"
        f"• 📈 فعال: {stats['active_percentage']:.1f}%\n\n"
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
            exam_names = [EXAMS_1405[key]['name'] for key in reminder['exam_keys'] if key in EXAMS_1405]
            
            # تبدیل تاریخ‌های میلادی به شمسی برای نمایش
            start_date_persian = format_gregorian_date_for_display(reminder['start_date'])
            end_date_persian = format_gregorian_date_for_display(reminder['end_date'])
            
            message_text += f"{status} کد {reminder['id']}: {', '.join(exam_names)}\n"
            message_text += f"   ⏰ ساعت: {', '.join(reminder['specific_times'])}\n"
            message_text += f"   📅 از: {start_date_persian} تا: {end_date_persian}\n\n"
    
    if personal_reminders:
        message_text += "📝 <b>یادآوری‌های شخصی:</b>\n"
        for reminder in personal_reminders:
            status = "🔔" if reminder['is_active'] else "🔕"
            
            # تبدیل تاریخ‌های میلادی به شمسی برای نمایش
            start_date_persian = format_gregorian_date_for_display(reminder['start_date'])
            end_date_text = format_gregorian_date_for_display(reminder['end_date']) if reminder['end_date'] else "همیشه"
            
            message_text += f"{status} کد {reminder['id']}: {reminder['title']}\n"
            message_text += f"   ⏰ ساعت: {reminder['specific_time']}\n"
            message_text += f"   🔁 تکرار: {reminder['repetition_type']}\n"
            message_text += f"   📅 از: {start_date_persian} تا: {end_date_text}\n\n"
    
    # اضافه کردن دکمه‌های مدیریت
    await message.answer(
        message_text,
        reply_markup=create_management_menu(),
        parse_mode="HTML"
    )

async def process_personal_custom_interval(message: types.Message, state: FSMContext):
    """پردازش فاصله تکرار سفارشی"""
    if message.text == "🔙 بازگشت":
        await state.set_state(PersonalReminderStates.selecting_repetition)
        await message.answer(
            "لطفاً نوع تکرار را انتخاب کنید:",
            reply_markup=create_repetition_type_menu()
        )
        return
    
    try:
        interval = int(message.text)
        if interval < 1 or interval > 365:
            await message.answer(
                "❌ فاصله نامعتبر!\n\n"
                "لطفاً عددی بین ۱ تا ۳۶۵ وارد کنید:",
                reply_markup=create_back_only_menu()
            )
            return
        
        await state.update_data(custom_days_interval=interval)
        await state.set_state(PersonalReminderStates.entering_time)
        current_time = get_current_persian_datetime()
        
        await message.answer(
            "🕐 <b>ورود ساعت یادآوری</b>\n\n"
            f"⏰ زمان فعلی: {current_time['full_time']}\n\n"
            "لطفاً ساعت دلخواه را به فرمت HH:MM وارد کنید:",
            reply_markup=create_time_input_menu(),
            parse_mode="HTML"
        )
        
    except ValueError:
        await message.answer(
            "❌ لطفاً یک عدد معتبر وارد کنید!\n\n"
            "مثال: برای یادآوری هر ۳ روز یکبار، عدد ۳ را وارد کنید:",
            reply_markup=create_back_only_menu()
        )

async def edit_reminder_handler(message: types.Message):
    """ویرایش یادآوری - پیام راهنما"""
    await message.answer(
        "✏️ <b>ویرایش یادآوری</b>\n\n"
        "در حال حاضر ویرایش یادآوری از طریق حذف و ایجاد مجدد انجام می‌شود.\n\n"
        "💡 <i>می‌توانید یادآوری مورد نظر را حذف کرده و مجدداً ایجاد کنید.</i>\n\n"
        "برای حذف از منوی مدیریت استفاده کنید.",
        reply_markup=create_management_menu(),
        parse_mode="HTML"
    )

# --- هندلرهای مدیریت با عملکرد واقعی ---
async def toggle_reminder_status(message: types.Message):
    """تغییر وضعیت فعال/غیرفعال کردن یادآوری"""
    user_reminders = reminder_db.get_user_exam_reminders(message.from_user.id)
    personal_reminders = reminder_db.get_user_personal_reminders(message.from_user.id)
    all_reminders = user_reminders + personal_reminders
    
    if not all_reminders:
        await message.answer(
            "📭 <b>هیچ یادآوری‌ای برای مدیریت ندارید</b>",
            reply_markup=create_management_menu(),
            parse_mode="HTML"
        )
        return
    
    # ایجاد کیبورد اینلاین برای انتخاب ریمایندر
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = []
    for reminder in all_reminders:
        reminder_type = 'exam' if 'exam_keys' in reminder else 'personal'
        status_icon = "🔔" if reminder['is_active'] else "🔕"
        status_text = "غیرفعال کن" if reminder['is_active'] else "فعال کن"
        
        keyboard.append([
            InlineKeyboardButton(
                text=f"{status_icon} {reminder['id']} - {status_text}",
                callback_data=f"manage_toggle:{reminder_type}:{reminder['id']}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton(text="🔙 بازگشت", callback_data="manage:back")
    ])
    
    await message.answer(
        "🔔 <b>تغییر وضعیت یادآوری‌ها</b>\n\n"
        "لطفاً یادآوری مورد نظر را برای تغییر وضعیت انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode="HTML"
    )

async def delete_reminder_handler(message: types.Message):
    """حذف یادآوری"""
    user_reminders = reminder_db.get_user_exam_reminders(message.from_user.id)
    personal_reminders = reminder_db.get_user_personal_reminders(message.from_user.id)
    all_reminders = user_reminders + personal_reminders
    
    if not all_reminders:
        await message.answer(
            "📭 <b>هیچ یادآوری‌ای برای حذف ندارید</b>",
            reply_markup=create_management_menu(),
            parse_mode="HTML"
        )
        return
    
    # ایجاد کیبورد اینلاین برای انتخاب ریمایندر
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = []
    for reminder in all_reminders:
        reminder_type = 'exam' if 'exam_keys' in reminder else 'personal'
        title = ', '.join([EXAMS_1405[key]['name'] for key in reminder['exam_keys']]) if 'exam_keys' in reminder else reminder['title']
        
        keyboard.append([
            InlineKeyboardButton(
                text=f"🗑️ {reminder['id']} - {title}",
                callback_data=f"manage_delete:{reminder_type}:{reminder['id']}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton(text="🔙 بازگشت", callback_data="manage:back")
    ])
    
    await message.answer(
        "🗑️ <b>حذف یادآوری</b>\n\n"
        "⚠️ <b>توجه: این عمل غیرقابل بازگشت است!</b>\n\n"
        "لطفاً یادآوری مورد نظر را برای حذف انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode="HTML"
    )

# --- هندلرهای callback برای مدیریت ---
async def handle_reminder_management_callback(callback: types.CallbackQuery):
    """پردازش کلیک‌های مدیریت ریمایندر"""
    data = callback.data
    
    if data == "manage:back":
        try:
            # حذف پیام فعلی و نمایش منوی مدیریت
            await callback.message.delete()
        except:
            # اگر حذف پیام ممکن نبود، فقط منوی جدید نمایش بده
            pass
        
        await manage_reminders_handler(callback.message)
        return
    
    if data.startswith("manage_delete:"):
        _, reminder_type, reminder_id = data.split(":")
        reminder_id = int(reminder_id)
        
        success = reminder_db.delete_reminder(reminder_type, reminder_id)
        
        if success:
            await callback.answer("✅ یادآوری حذف شد")
            
            # به جای ویرایش پیام، پیام جدید بفرست
            await callback.message.edit_text(
                f"✅ <b>یادآوری حذف شد</b>\n\n"
                f"کد یادآوری: {reminder_id}\n\n"
                f"برای بازگشت به منوی مدیریت از دکمه زیر استفاده کنید:",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="🔙 بازگشت به مدیریت", callback_data="manage:back")
                ]]),
                parse_mode="HTML"
            )
        else:
            await callback.answer("❌ خطا در حذف یادآوری")
    
    elif data.startswith("manage_toggle:"):
        _, reminder_type, reminder_id = data.split(":")
        reminder_id = int(reminder_id)
        
        # دریافت وضعیت فعلی
        reminders = []
        if reminder_type == 'exam':
            reminders = reminder_db.get_user_exam_reminders(callback.from_user.id)
        else:
            reminders = reminder_db.get_user_personal_reminders(callback.from_user.id)
        
        current_reminder = next((r for r in reminders if r['id'] == reminder_id), None)
        if not current_reminder:
            await callback.answer("❌ یادآوری پیدا نشد")
            return
        
        new_status = not current_reminder['is_active']
        success = reminder_db.update_reminder_status(reminder_type, reminder_id, new_status)
        
        if success:
            status_text = "فعال" if new_status else "غیرفعال"
            await callback.answer(f"✅ یادآوری {status_text} شد")
            
            await callback.message.edit_text(
                f"✅ <b>وضعیت یادآوری تغییر کرد</b>\n\n"
                f"کد یادآوری: {reminder_id}\n"
                f"وضعیت جدید: {status_text}\n\n"
                f"برای بازگشت به منوی مدیریت از دکمه زیر استفاده کنید:",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="🔙 بازگشت به مدیریت", callback_data="manage:back")
                ]]),
                parse_mode="HTML"
            )
        else:
            await callback.answer("❌ خطا در تغییر وضعیت")
            
# --- توابع کمکی ---
def create_reminder_summary(state_data: dict) -> str:
    """ایجاد خلاصه ریمایندر"""
    days_map = {
        0: "شنبه", 1: "یکشنبه", 2: "دوشنبه", 
        3: "سه‌شنبه", 4: "چهارشنبه", 5: "پنجشنبه", 6: "جمعه"
    }
    
    selected_days = [days_map[day] for day in state_data.get('selected_days', [])]
    exam_names = [EXAMS_1405[key]['name'] for key in state_data.get('selected_exams', []) if key in EXAMS_1405]
    
    summary = (
        f"🎯 <b>کنکورها:</b> {', '.join(exam_names) if exam_names else 'تعیین نشده'}\n"
        f"🗓️ <b>روزها:</b> {', '.join(selected_days) if selected_days else 'همه روزها'}\n"
        f"🕐 <b>ساعت:</b> {state_data.get('specific_time', 'تعیین نشده')}\n"
        f"📅 <b>شروع:</b> {state_data.get('start_date', 'تعیین نشده')}\n"  # شمسی
        f"📅 <b>پایان:</b> {state_data.get('end_date', 'تعیین نشده')}\n"   # شمسی
    )
    
    return summary

async def process_reminder_management(message: types.Message):
    """پردازش دستورات مدیریت یادآوری"""
    text = message.text.lower()
    
    if text == "🔙 بازگشت":
        await manage_reminders_handler(message)
        return
    
    # پردازش دستورات
    if text.startswith('فعال') or text.startswith('غیرفعال'):
        parts = text.split()
        if len(parts) == 2 and parts[1].isdigit():
            reminder_id = int(parts[1])
            is_active = text.startswith('فعال')
            
            # تشخیص نوع ریمایندر و به‌روزرسانی
            success = reminder_db.update_reminder_status('exam', reminder_id, is_active)
            if not success:
                success = reminder_db.update_reminder_status('personal', reminder_id, is_active)
            
            if success:
                status_text = "فعال" if is_active else "غیرفعال"
                await message.answer(f"✅ یادآوری {reminder_id} {status_text} شد")
            else:
                await message.answer("❌ یادآوری پیدا نشد")
        else:
            await message.answer("❌ فرمت دستور نامعتبر! مثال: <code>فعال ۱۲۳</code>", parse_mode="HTML")
    
    elif text.startswith('حذف'):
        parts = text.split()
        if len(parts) == 2 and parts[1].isdigit():
            reminder_id = int(parts[1])
            
            # حذف ریمایندر
            success = reminder_db.delete_reminder('exam', reminder_id)
            if not success:
                success = reminder_db.delete_reminder('personal', reminder_id)
            
            if success:
                await message.answer(f"✅ یادآوری {reminder_id} حذف شد")
            else:
                await message.answer("❌ یادآوری پیدا نشد")
        else:
            await message.answer("❌ فرمت دستور نامعتبر! مثال: <code>حذف ۱۲۳</code>", parse_mode="HTML")
    
    else:
        await message.answer(
            "❌ دستور نامعتبر!\n\n"
            "لطفاً از فرمت‌های زیر استفاده کنید:\n"
            "• <code>فعال ۱۲۳</code>\n"
            "• <code>غیرفعال ۴۵۶</code>\n" 
            "• <code>حذف ۷۸۹</code>\n\n"
            "یا برای بازگشت: 🔙 بازگشت",
            parse_mode="HTML",
            reply_markup=create_back_only_menu()
        )
