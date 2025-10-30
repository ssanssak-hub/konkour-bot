"""
مدیریت ریمایندرهای خودکار برای ادمین
"""
import logging
from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from reminder.auto_reminder_system import auto_reminder_system
from reminder.reminder_keyboards import create_auto_reminders_admin_menu, create_back_only_menu
from exam_data import EXAMS_1405

logger = logging.getLogger(__name__)

# حالت‌های FSM برای مدیریت ریمایندرهای خودکار
class AutoReminderAdminStates(StatesGroup):
    adding_title = State()
    adding_message = State()
    adding_days = State()
    selecting_exams = State()
    confirmation = State()
    editing_reminder = State()
    deleting_reminder = State()

async def auto_reminders_admin_handler(message: types.Message):
    """منوی مدیریت ریمایندرهای خودکار برای ادمین"""
    from config import ADMIN_ID
    
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ دسترسی denied!")
        return
        
    auto_reminders = auto_reminder_system.get_all_auto_reminders()
    active_count = len([r for r in auto_reminders if r['is_active']])
    
    await message.answer(
        f"🤖 <b>مدیریت ریمایندرهای خودکار</b>\n\n"
        f"📊 آمار سیستم:\n"
        f"• 📝 کل ریمایندرها: {len(auto_reminders)}\n"
        f"• 🔔 فعال: {active_count}\n"
        f"• 🔕 غیرفعال: {len(auto_reminders) - active_count}\n\n"
        f"لطفاً عمل مورد نظر را انتخاب کنید:",
        reply_markup=create_auto_reminders_admin_menu(),
        parse_mode="HTML"
    )

async def list_auto_reminders_admin(message: types.Message):
    """نمایش لیست ریمایندرهای خودکار برای ادمین"""
    auto_reminders = auto_reminder_system.get_all_auto_reminders()
    
    if not auto_reminders:
        await message.answer(
            "📭 <b>هیچ ریمایندر خودکاری پیدا نشد</b>",
            reply_markup=create_auto_reminders_admin_menu(),
            parse_mode="HTML"
        )
        return
    
    message_text = "📋 <b>لیست ریمایندرهای خودکار</b>\n\n"
    
    for reminder in auto_reminders:
        status = "✅" if reminder['is_active'] else "❌"
        exam_names = [EXAMS_1405[key]['name'] for key in reminder['exam_keys'] if key in EXAMS_1405]
        message_text += (
            f"{status} <b>کد {reminder['id']}</b>\n"
            f"📝 {reminder['title']}\n"
            f"⏰ {reminder['days_before_exam']} روز قبل از کنکور\n"
            f"🎯 {', '.join(exam_names)}\n"
            f"📅 ایجاد شده در: {reminder['created_at'][:10]}\n"
            f"────────────────────\n\n"
        )
    
    await message.answer(
        message_text,
        reply_markup=create_auto_reminders_admin_menu(),
        parse_mode="HTML"
    )

async def start_add_auto_reminder(message: types.Message, state: FSMContext):
    """شروع افزودن ریمایندر خودکار جدید"""
    from config import ADMIN_ID
    
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ دسترسی denied!")
        return
        
    await state.set_state(AutoReminderAdminStates.adding_title)
    
    await message.answer(
        "➕ <b>افزودن ریمایندر خودکار جدید</b>\n\n"
        "لطفاً عنوان ریمایندر را وارد کنید:\n\n"
        "💡 <i>مثال: شروع فصل طلایی</i>\n\n"
        "یا برای بازگشت: 🔙 بازگشت",
        reply_markup=create_back_only_menu(),
        parse_mode="HTML"
    )

async def process_add_title(message: types.Message, state: FSMContext):
    """پردازش عنوان ریمایندر خودکار"""
    if message.text == "🔙 بازگشت":
        await state.clear()
        await auto_reminders_admin_handler(message)
        return
    
    await state.update_data(title=message.text)
    await state.set_state(AutoReminderAdminStates.adding_message)
    
    await message.answer(
        "📄 <b>متن ریمایندر</b>\n\n"
        "لطفاً متن کامل ریمایندر را وارد کنید:\n\n"
        "💡 <i>این متن برای کاربران ارسال خواهد شد</i>\n\n"
        "یا برای بازگشت: 🔙 بازگشت",
        reply_markup=create_back_only_menu(),
        parse_mode="HTML"
    )

async def process_add_message(message: types.Message, state: FSMContext):
    """پردازش متن ریمایندر خودکار"""
    if message.text == "🔙 بازگشت":
        await state.set_state(AutoReminderAdminStates.adding_title)
        await message.answer(
            "لطفاً عنوان ریمایندر را وارد کنید:",
            reply_markup=create_back_only_menu()
        )
        return
    
    await state.update_data(message=message.text)
    await state.set_state(AutoReminderAdminStates.adding_days)
    
    await message.answer(
        "⏰ <b>تعداد روزهای قبل از کنکور</b>\n\n"
        "لطفاً تعداد روزهای قبل از کنکور را وارد کنید:\n\n"
        "💡 <i>مثال: برای یادآوری ۷ روز قبل، عدد ۷ را وارد کنید</i>\n\n"
        "یا برای بازگشت: 🔙 بازگشت",
        reply_markup=create_back_only_menu(),
        parse_mode="HTML"
    )

# ادامۀ توابع برای ادمین...
async def process_add_days(message: types.Message, state: FSMContext):
    """پردازش تعداد روزهای قبل از کنکور"""
    if message.text == "🔙 بازگشت":
        await state.set_state(AutoReminderAdminStates.adding_message)
        await message.answer(
            "لطفاً متن ریمایندر را وارد کنید:",
            reply_markup=create_back_only_menu()
        )
        return
    
    try:
        days = int(message.text)
        if days < 1 or days > 365:
            await message.answer(
                "❌ تعداد روز نامعتبر!\n\n"
                "لطفاً عددی بین ۱ تا ۳۶۵ وارد کنید:",
                reply_markup=create_back_only_menu()
            )
            return
        
        await state.update_data(days_before_exam=days, selected_exams=[])
        await state.set_state(AutoReminderAdminStates.selecting_exams)
        
        await message.answer(
            "🎯 <b>انتخاب کنکورها</b>\n\n"
            "لطفاً کنکورهای مورد نظر را انتخاب کنید:\n\n"
            "💡 <i>این ریمایندر برای کنکورهای انتخاب شده ارسال خواهد شد</i>",
            reply_markup=create_exam_selection_menu(),  # از reminder_keyboards استفاده کن
            parse_mode="HTML"
        )
        
    except ValueError:
        await message.answer(
            "❌ لطفاً یک عدد معتبر وارد کنید!",
            reply_markup=create_back_only_menu()
        )

async def process_admin_exam_selection(message: types.Message, state: FSMContext):
    """پردازش انتخاب کنکورها توسط ادمین"""
    text = message.text
    
    if text == "✅ انتخاب همه":
        await state.update_data(selected_exams=list(EXAMS_1405.keys()))
        await message.answer("✅ همه کنکورها انتخاب شدند")
        
    elif text == "➡️ ادامه":
        state_data = await state.get_data()
        selected_exams = state_data.get('selected_exams', [])
        
        if not selected_exams:
            await message.answer("❌ لطفاً حداقل یک کنکور انتخاب کنید")
            return
        
        await state.set_state(AutoReminderAdminStates.confirmation)
        
        # نمایش خلاصه
        summary = await create_auto_reminder_summary(state_data)
        
        await message.answer(
            f"✅ <b>خلاصه ریمایندر خودکار</b>\n\n{summary}\n\n"
            "آیا مایل به ایجاد این ریمایندر هستید؟",
            reply_markup=create_confirmation_menu(),  # از reminder_keyboards استفاده کن
            parse_mode="HTML"
        )
    
    elif text == "🔙 بازگشت":
        await state.set_state(AutoReminderAdminStates.adding_days)
        await message.answer(
            "لطفاً تعداد روزهای قبل از کنکور را وارد کنید:",
            reply_markup=create_back_only_menu()
        )
    
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

async def process_admin_confirmation(message: types.Message, state: FSMContext):
    """پردازش تأیید نهایی ریمایندر خودکار"""
    text = message.text
    
    if text == "✅ تأیید و ایجاد":
        state_data = await state.get_data()
        
        try:
            # ذخیره در دیتابیس
            reminder_id = auto_reminder_system.add_auto_reminder(
                title=state_data['title'],
                message=state_data['message'],
                days_before_exam=state_data['days_before_exam'],
                exam_keys=state_data['selected_exams'],
                admin_id=message.from_user.id,
                is_global=True
            )
            
            await message.answer(
                "🎉 <b>ریمایندر خودکار با موفقیت ایجاد شد!</b>\n\n"
                f"📝 کد ریمایندر: <code>{reminder_id}</code>\n"
                f"📝 عنوان: {state_data['title']}\n"
                f"⏰ ارسال: {state_data['days_before_exam']} روز قبل از کنکور\n\n"
                "این ریمایندر برای همه کاربران فعال خواهد بود.",
                reply_markup=create_auto_reminders_admin_menu(),
                parse_mode="HTML"
            )
            
            logger.info(f"✅ ریمایندر خودکار {reminder_id} توسط ادمین {message.from_user.id} ایجاد شد")
            
        except Exception as e:
            await message.answer(
                "❌ <b>خطا در ایجاد ریمایندر!</b>\n\n"
                "لطفاً مجدداً تلاش کنید.",
                reply_markup=create_auto_reminders_admin_menu(),
                parse_mode="HTML"
            )
            logger.error(f"خطا در ایجاد ریمایندر خودکار: {e}")
        
        await state.clear()
    
    elif text == "✏️ ویرایش":
        await state.set_state(AutoReminderAdminStates.adding_title)
        await message.answer(
            "لطفاً عنوان ریمایندر را وارد کنید:",
            reply_markup=create_back_only_menu()
        )
    
    elif text == "❌ لغو":
        await message.answer(
            "❌ <b>ایجاد ریمایندر لغو شد</b>",
            reply_markup=create_auto_reminders_admin_menu(),
            parse_mode="HTML"
        )
        await state.clear()

async def delete_auto_reminder_handler(message: types.Message):
    """حذف ریمایندر خودکار"""
    from config import ADMIN_ID
    
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ دسترسی denied!")
        return
        
    auto_reminders = auto_reminder_system.get_all_auto_reminders()
    
    if not auto_reminders:
        await message.answer(
            "📭 <b>هیچ ریمایندر خودکاری برای حذف وجود ندارد</b>",
            reply_markup=create_auto_reminders_admin_menu(),
            parse_mode="HTML"
        )
        return
    
    # ایجاد کیبورد برای انتخاب ریمایندر
    keyboard = []
    for reminder in auto_reminders:
        keyboard.append([
            InlineKeyboardButton(
                text=f"🗑️ {reminder['id']} - {reminder['title']}",
                callback_data=f"auto_admin_delete:{reminder['id']}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton(text="🔙 بازگشت", callback_data="auto_admin:back")
    ])
    
    await message.answer(
        "🗑️ <b>حذف ریمایندر خودکار</b>\n\n"
        "⚠️ <b>توجه: این عمل غیرقابل بازگشت است!</b>\n\n"
        "لطفاً ریمایندر مورد نظر را برای حذف انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode="HTML"
    )

async def toggle_auto_reminder_status(message: types.Message):
    """تغییر وضعیت فعال/غیرفعال ریمایندر خودکار"""
    from config import ADMIN_ID
    
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ دسترسی denied!")
        return
        
    auto_reminders = auto_reminder_system.get_all_auto_reminders()
    
    if not auto_reminders:
        await message.answer(
            "📭 <b>هیچ ریمایندر خودکاری وجود ندارد</b>",
            reply_markup=create_auto_reminders_admin_menu(),
            parse_mode="HTML"
        )
        return
    
    # ایجاد کیبورد برای انتخاب ریمایندر
    keyboard = []
    for reminder in auto_reminders:
        status_text = "🔕 غیرفعال کن" if reminder['is_active'] else "🔔 فعال کن"
        keyboard.append([
            InlineKeyboardButton(
                text=f"{reminder['title']} - {status_text}",
                callback_data=f"auto_admin_toggle:{reminder['id']}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton(text="🔙 بازگشت", callback_data="auto_admin:back")
    ])
    
    await message.answer(
        "🔔 <b>تغییر وضعیت ریمایندرهای خودکار</b>\n\n"
        "لطفاً ریمایندر مورد نظر را برای تغییر وضعیت انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode="HTML"
    )

async def handle_auto_reminder_admin_callback(callback: types.CallbackQuery):
    """پردازش کلیک‌های مدیریت ریمایندر خودکار برای ادمین"""
    from config import ADMIN_ID
    
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ دسترسی denied!")
        return
    
    data = callback.data
    
    if data == "auto_admin:back":
        await callback.message.delete()
        await auto_reminders_admin_handler(callback.message)
        return
    
    if data.startswith("auto_admin_delete:"):
        reminder_id = int(data.split(":")[1])
        
        success = auto_reminder_system.delete_auto_reminder(reminder_id)
        
        if success:
            await callback.answer("✅ ریمایندر حذف شد")
            await callback.message.edit_text(
                f"✅ <b>ریمایندر خودکار حذف شد</b>\n\n"
                f"کد ریمایندر: {reminder_id}\n\n"
                f"برای بازگشت به منوی مدیریت از دکمه زیر استفاده کنید:",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="🔙 بازگشت به مدیریت", callback_data="auto_admin:back")
                ]]),
                parse_mode="HTML"
            )
        else:
            await callback.answer("❌ خطا در حذف ریمایندر")
    
    elif data.startswith("auto_admin_toggle:"):
        reminder_id = int(data.split(":")[1])
        
        # دریافت وضعیت فعلی
        auto_reminders = auto_reminder_system.get_all_auto_reminders()
        current_reminder = next((r for r in auto_reminders if r['id'] == reminder_id), None)
        
        if not current_reminder:
            await callback.answer("❌ ریمایندر پیدا نشد")
            return
        
        new_status = not current_reminder['is_active']
        success = auto_reminder_system.update_auto_reminder(reminder_id, is_active=new_status)
        
        if success:
            status_text = "فعال" if new_status else "غیرفعال"
            await callback.answer(f"✅ ریمایندر {status_text} شد")
            await callback.message.edit_text(
                f"✅ <b>وضعیت ریمایندر تغییر کرد</b>\n\n"
                f"کد ریمایندر: {reminder_id}\n"
                f"وضعیت جدید: {status_text}\n\n"
                f"برای بازگشت به منوی مدیریت از دکمه زیر استفاده کنید:",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="🔙 بازگشت به مدیریت", callback_data="auto_admin:back")
                ]]),
                parse_mode="HTML"
            )
        else:
            await callback.answer("❌ خطا در تغییر وضعیت")

async def create_auto_reminder_summary(state_data: dict) -> str:
    """ایجاد خلاصه ریمایندر خودکار"""
    exam_names = [EXAMS_1405[key]['name'] for key in state_data.get('selected_exams', []) if key in EXAMS_1405]
    
    summary = (
        f"📝 <b>عنوان:</b> {state_data.get('title', 'تعیین نشده')}\n"
        f"📄 <b>متن:</b> {state_data.get('message', 'تعیین نشده')}\n"
        f"⏰ <b>ارسال:</b> {state_data.get('days_before_exam', 'تعیین نشده')} روز قبل از کنکور\n"
        f"🎯 <b>کنکورها:</b> {', '.join(exam_names) if exam_names else 'تعیین نشده'}\n"
        f"🌍 <b>دسترسی:</b> همه کاربران\n"
    )
    
    return summary
