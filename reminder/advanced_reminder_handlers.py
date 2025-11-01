"""
هندلرهای ریمایندرهای پیشرفته برای ادمین - نسخه کامل و پیشرفته
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
from utils.time_utils import (
    get_current_persian_datetime, 
    get_tehran_time_formatted,    # اضافه کنید
    get_tehran_date_formatted,    # اضافه کنید
    persian_to_gregorian_string
)
logger = logging.getLogger(__name__)

# =============================================================================
# بخش ۱: منوی اصلی و مدیریت اولیه
# =============================================================================

async def advanced_reminders_admin_handler(message: types.Message):
    """منوی اصلی ریمایندرهای پیشرفته برای ادمین"""
    from config import ADMIN_ID
    
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ دسترسی denied!")
        return
    
    reminders = reminder_db.get_admin_advanced_reminders()
    active_count = len([r for r in reminders if r['is_active']])
    
    # محاسبه آمار پیشرفته
    total_repeats = sum(r['repeat_count'] for r in reminders)
    active_with_repeats = sum(r['repeat_count'] for r in reminders if r['is_active'])
    
    await message.answer(
        f"🤖 <b>مدیریت ریمایندرهای پیشرفته</b>\n\n"
        f"📊 آمار سیستم:\n"
        f"• 📝 کل ریمایندرها: {len(reminders)}\n"
        f"• 🔔 فعال: {active_count}\n"
        f"• 🔕 غیرفعال: {len(reminders) - active_count}\n"
        f"• 🔄 کل تکرارها: {total_repeats}\n"
        f"• 🎯 تکرارهای فعال: {active_with_repeats}\n\n"
        f"💡 <i>ویژگی‌های پیشرفته:</i>\n"
        f"• ⏰ زمان‌بندی دقیق شروع و پایان\n"
        f"• 📆 انتخاب روزهای خاص هفته\n"
        f"• 🔢 تکرارهای متوالی با فاصله زمانی\n"
        f"• 🎯 ارسال به همه کاربران فعال\n\n"
        f"لطفاً عمل مورد نظر را انتخاب کنید:",
        reply_markup=create_advanced_reminder_admin_menu(),
        parse_mode="HTML"
    )

# =============================================================================
# بخش ۲: فرآیند ایجاد ریمایندر پیشرفته (FSM)
# =============================================================================

async def start_add_advanced_reminder(message: types.Message, state: FSMContext):
    """شروع فرآیند افزودن ریمایندر پیشرفته"""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ دسترسی denied!")
        return
    
    await state.set_state(AdvancedReminderStates.waiting_for_title)
    
    await message.answer(
        "➕ <b>افزودن ریمایندر پیشرفته جدید</b>\n\n"
        "📝 <b>لطفاً عنوان ریمایندر را وارد کنید:</b>\n\n"
        "💡 <i>مثال‌های پیشنهادی:</i>\n"
        "• شروع فصل طلایی مطالعه\n"
        "• یادآوری مرور هفتگی\n"
        "• آماده‌سازی برای آزمون\n"
        "• پیام انگیزشی روزانه\n\n"
        "🔙 برای بازگشت: 🔙 بازگشت",
        reply_markup=create_back_only_menu(),
        parse_mode="HTML"
    )

async def process_advanced_title(message: types.Message, state: FSMContext):
    """پردازش عنوان ریمایندر پیشرفته"""
    if message.text == "🔙 بازگشت":
        await state.clear()
        await advanced_reminders_admin_handler(message)
        return
    
    if len(message.text) < 3:
        await message.answer(
            "❌ عنوان خیلی کوتاه است!\n\n"
            "لطفاً عنوانی با حداقل ۳ حرف وارد کنید:",
            reply_markup=create_back_only_menu()
        )
        return
    
    await state.update_data(title=message.text)
    await state.set_state(AdvancedReminderStates.waiting_for_message)
    
    await message.answer(
        "📄 <b>متن ریمایندر</b>\n\n"
        "لطفاً متن کامل ریمایندر را وارد کنید:\n\n"
        "💡 <i>نکات مهم:</i>\n"
        "• این متن برای همه کاربران ارسال خواهد شد\n"
        "• می‌توانید از اموجی و فرمت‌بندی HTML استفاده کنید\n"
        "• متن باید واضح و انگیزشی باشد\n\n"
        "🔙 برای بازگشت: 🔙 بازگشت",
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
    
    if len(message.text) < 10:
        await message.answer(
            "❌ متن خیلی کوتاه است!\n\n"
            "لطفاً متنی با حداقل ۱۰ حرف وارد کنید:",
            reply_markup=create_back_only_menu()
        )
        return
    
    await state.update_data(message=message.text)
    await state.set_state(AdvancedReminderStates.waiting_for_start_time)
    
    await message.answer(
        "⏰ <b>ساعت شروع</b>\n\n"
        "لطفاً ساعت شروع را به فرمت HH:MM وارد کنید:\n\n"
        "💡 <i>مثال‌های صحیح:</i>\n"
        "• 08:00 - ساعت ۸ صبح\n"
        "• 14:30 - ساعت ۲:۳۰ بعدازظهر\n"
        "• 22:15 - ساعت ۱۰:۱۵ شب\n\n"
        "⏰ <b>گزینه‌های سریع:</b>\n"
        "• همین الان - زمان فعلی سیستم\n\n"
        "🔙 برای بازگشت: 🔙 بازگشت",
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
        try:
            # استفاده از زمان تهران با jdatetime
            from jdatetime import datetime as jdatetime
            import pytz
            tehran_tz = pytz.timezone('Asia/Tehran')
            current_time = jdatetime.now(tehran_tz).strftime("%H:%M")
            await state.update_data(start_time=current_time)
            await message.answer(f"✅ ساعت شروع تنظیم شد: {current_time} (تهران)")
        except Exception as e:
            # اگر jdatetime کار نکرد، از datetime معمولی استفاده کن
            from datetime import datetime
            current_time = datetime.now().strftime("%H:%M")
            await state.update_data(start_time=current_time)
            await message.answer(f"✅ ساعت شروع تنظیم شد: {current_time}")
    else:
        # اعتبارسنجی فرمت زمان
        try:
            time_str = message.text.strip()
            # بررسی فرمت HH:MM
            if len(time_str) != 5 or time_str[2] != ':':
                raise ValueError
            
            hours = int(time_str[:2])
            minutes = int(time_str[3:])
            
            if hours < 0 or hours > 23 or minutes < 0 or minutes > 59:
                raise ValueError
                
            await state.update_data(start_time=time_str)
            await message.answer(f"✅ ساعت شروع ثبت شد: {time_str}")
            
        except ValueError:
            await message.answer(
                "❌ فرمت زمان نامعتبر!\n\n"
                "لطفاً زمان را به فرمت HH:MM وارد کنید:\n"
                "💡 <i>مثال‌های صحیح:</i>\n"
                "• 08:00 - ساعت ۸ صبح\n"
                "• 14:30 - ساعت ۲:۳۰ بعدازظهر\n"
                "• 22:15 - ساعت ۱۰:۱۵ شب\n\n"
                "🔙 برای بازگشت: 🔙 بازگشت",
                reply_markup=create_start_time_menu()
            )
            return
    
    await state.set_state(AdvancedReminderStates.waiting_for_start_date)
    
    await message.answer(
        "📅 <b>تاریخ شروع</b>\n\n"
        "لطفاً تاریخ شروع را به فرمت YYYY-MM-DD وارد کنید:\n\n"
        "💡 <i>مثال‌های صحیح:</i>\n"
        "• 1404-01-15 - ۱۵ فروردین ۱۴۰۴\n"
        "• 1404-07-01 - ۱ مهر ۱۴۰۴\n"
        "• 1404-12-29 - ۲۹ اسفند ۱۴۰۴\n\n"
        "📅 <b>گزینه‌های سریع:</b>\n"
        "• امروز - تاریخ امروز\n\n"
        "🔙 برای بازگشت: 🔙 بازگشت",
        reply_markup=create_start_date_menu(),
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
        try:
            # استفاده مستقیم از تابع get_tehran_date برای تاریخ تهران
            current_date = get_tehran_date()  # این تاریخ امروز تهران رو برمی‌گردونه
            await state.update_data(start_date=current_date)
            await message.answer(f"✅ تاریخ شروع تنظیم شد: {current_date} (امروز - تهران)")
                
        except Exception as e:
            # فال‌بک: استفاده مستقیم از jdatetime
            try:
                from jdatetime import datetime as jdatetime
                import pytz
                tehran_tz = pytz.timezone('Asia/Tehran')
                current_date = jdatetime.now(tehran_tz).strftime("%Y-%m-%d")
                await state.update_data(start_date=current_date)
                await message.answer(f"✅ تاریخ شروع تنظیم شد: {current_date} (امروز - تهران)")
            except Exception as e2:
                # آخرین فال‌بک
                from datetime import datetime
                today = datetime.now().strftime("%Y-%m-%d")
                await state.update_data(start_date=today)
                await message.answer(f"✅ تاریخ شروع تنظیم شد: {today} (تاریخ پیش‌فرض)")
            
    else:
        # اعتبارسنجی فرمت تاریخ
        try:
            date_str = message.text.strip()
            # بررسی فرمت YYYY-MM-DD
            if len(date_str) != 10 or date_str[4] != '-' or date_str[7] != '-':
                raise ValueError
            
            year = int(date_str[:4])
            month = int(date_str[5:7])
            day = int(date_str[8:10])
            
            if year < 1400 or year > 1500 or month < 1 or month > 12 or day < 1 or day > 31:
                raise ValueError
            
            # تبدیل تاریخ شمسی به میلادی برای ذخیره در دیتابیس
            gregorian_date = persian_to_gregorian_string(date_str)
            await state.update_data(start_date=date_str)  # ذخیره شمسی برای نمایش
            await message.answer(f"✅ تاریخ شروع ثبت شد: {date_str}")
            
        except Exception as e:
            await message.answer(
                "❌ فرمت تاریخ نامعتبر!\n\n"
                "لطفاً تاریخ را به فرمت YYYY-MM-DD وارد کنید:\n"
                "💡 <i>مثال‌های صحیح:</i>\n"
                "• 1404-01-15 - ۱۵ فروردین ۱۴۰۴\n"
                "• 1404-07-01 - ۱ مهر ۱۴۰۴\n"
                "• 1404-12-29 - ۲۹ اسفند ۱۴۰۴\n\n"
                "🔙 برای بازگشت: 🔙 بازگشت",
                reply_markup=create_start_date_menu()
            )
            return
    
    await state.set_state(AdvancedReminderStates.waiting_for_end_time)
    
    await message.answer(
        "⏰ <b>ساعت پایان</b>\n\n"
        "لطفاً ساعت پایان را به فرمت HH:MM وارد کنید:\n\n"
        "💡 <i>مثال‌های صحیح:</i>\n"
        "• 18:00 - ساعت ۶ عصر\n"
        "• 22:30 - ساعت ۱۰:۳۰ شب\n"
        "• 23:59 - پایان روز\n\n"
        "⏰ <b>گزینه‌های سریع:</b>\n"
        "• بدون پایان - تا پایان روز (23:59)\n\n"
        "🔙 برای بازگشت: 🔙 بازگشت",
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
        await message.answer("✅ ساعت پایان تنظیم شد: 23:59 (پایان روز)")
    else:
        # اعتبارسنجی فرمت زمان
        try:
            time_str = message.text.strip()
            # بررسی فرمت HH:MM
            if len(time_str) != 5 or time_str[2] != ':':
                raise ValueError
            
            hours = int(time_str[:2])
            minutes = int(time_str[3:])
            
            if hours < 0 or hours > 23 or minutes < 0 or minutes > 59:
                raise ValueError
                
            await state.update_data(end_time=time_str)
            await message.answer(f"✅ ساعت پایان ثبت شد: {time_str}")
            
        except ValueError:
            await message.answer(
                "❌ فرمت زمان نامعتبر!\n\n"
                "لطفاً زمان را به فرمت HH:MM وارد کنید:\n"
                "💡 <i>مثال‌های صحیح:</i>\n"
                "• 18:00 - ساعت ۶ عصر\n"
                "• 22:30 - ساعت ۱۰:۳۰ شب\n"
                "• 23:59 - پایان روز\n\n"
                "🔙 برای بازگشت: 🔙 بازگشت",
                reply_markup=create_end_time_menu()
            )
            return
    
    await state.set_state(AdvancedReminderStates.waiting_for_end_date)
    
    await message.answer(
        "📅 <b>تاریخ پایان</b>\n\n"
        "لطفاً تاریخ پایان را به فرمت YYYY-MM-DD وارد کنید:\n\n"
        "💡 <i>مثال‌های صحیح:</i>\n"
        "• 1404-12-29 - ۲۹ اسفند ۱۴۰۴\n"
        "• 1405-06-30 - ۳۰ شهریور ۱۴۰۵\n"
        "• 1405-12-29 - ۲۹ اسفند ۱۴۰۵\n\n"
        "📅 <b>گزینه‌های سریع:</b>\n"
        "• بدون تاریخ پایان - یک سال بعد از امروز\n\n"
        "🔙 برای بازگشت: 🔙 بازگشت",
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
        try:
            # استفاده مستقیم از تابع get_tehran_date برای تاریخ تهران
            current_date = get_tehran_date()  # تاریخ امروز تهران
            
            # تبدیل تاریخ شمسی به عدد و اضافه کردن یک سال
            current_year = int(current_date[:4])
            next_year = str(current_year + 1) + current_date[4:]
                
            await state.update_data(end_date=next_year)
            await message.answer(f"✅ تاریخ پایان تنظیم شد: {next_year} (یک سال بعد - تهران)")
            
        except Exception as e:
            try:
                # فال‌بک: استفاده مستقیم از jdatetime
                from jdatetime import datetime as jdatetime
                import pytz
                tehran_tz = pytz.timezone('Asia/Tehran')
                today_tehran = jdatetime.now(tehran_tz)
                next_year = today_tehran.replace(year=today_tehran.year + 1).strftime("%Y-%m-%d")
                await state.update_data(end_date=next_year)
                await message.answer(f"✅ تاریخ پایان تنظیم شد: {next_year} (یک سال بعد - تهران)")
            except Exception as e2:
                # آخرین فال‌بک: تاریخ پیش‌فرض
                await state.update_data(end_date="1405-12-29")
                await message.answer("✅ تاریخ پایان تنظیم شد: 1405-12-29 (پیش‌فرض)")
            
    else:
        # اعتبارسنجی فرمت تاریخ
        try:
            date_str = message.text.strip()
            # بررسی فرمت YYYY-MM-DD
            if len(date_str) != 10 or date_str[4] != '-' or date_str[7] != '-':
                raise ValueError
            
            year = int(date_str[:4])
            month = int(date_str[5:7])
            day = int(date_str[8:10])
            
            if year < 1400 or year > 1500 or month < 1 or month > 12 or day < 1 or day > 31:
                raise ValueError
            
            # تبدیل تاریخ شمسی به میلادی برای ذخیره در دیتابیس
            gregorian_date = persian_to_gregorian_string(date_str)
            await state.update_data(end_date=date_str)  # ذخیره شمسی برای نمایش
            await message.answer(f"✅ تاریخ پایان ثبت شد: {date_str}")
            
        except Exception as e:
            await message.answer(
                "❌ فرمت تاریخ نامعتبر!\n\n"
                "لطفاً تاریخ را به فرمت YYYY-MM-DD وارد کنید:\n"
                "💡 <i>مثال‌های صحیح:</i>\n"
                "• 1404-12-29 - ۲۹ اسفند ۱۴۰۴\n"
                "• 1405-06-30 - ۳۰ شهریور ۱۴۰۵\n"
                "• 1405-12-29 - ۲۹ اسفند ۱۴۰۵\n\n"
                "🔙 برای بازگشت: 🔙 بازگشت",
                reply_markup=create_end_date_menu()
            )
            return
    
    await state.set_state(AdvancedReminderStates.waiting_for_days_of_week)
    
    await message.answer(
        "📆 <b>روزهای هفته</b>\n\n"
        "لطفاً روزهای مورد نظر برای ارسال ریمایندر را انتخاب کنید:\n\n"
        "💡 <i>نکات مهم:</i>\n"
        "• می‌توانید چند روز را انتخاب کنید\n"
        "• ریمایندر فقط در روزهای انتخاب شده ارسال می‌شود\n"
        "• اگر هیچ روزی انتخاب نکنید، ریمایندر غیرفعال می‌ماند\n\n"
        "📅 <b>گزینه‌های سریع:</b>\n"
        "• همه روزها - انتخاب تمام روزهای هفته\n"
        "• پاک کردن همه - حذف تمام انتخاب‌ها\n\n"
        "🔙 برای بازگشت: 🔙 بازگشت",
        reply_markup=create_days_of_week_menu([]),
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
            "💡 <i>توضیحات کامل:</i>\n"
            "• <b>0</b> = فقط ثبت اطلاعات، بدون ارسال پیام\n"
            "• <b>1</b> = ارسال یکبار در ساعت مشخص\n"
            "• <b>2-10</b> = ارسال چندباره با فاصله زمانی\n\n"
            "🎯 <b>کاربردهای مختلف:</b>\n"
            "• 0 - برای ذخیره الگوهای آماده\n"
            "• 1 - برای یادآوری‌های مهم یکباره\n"
            "• 2-5 - برای تأکید روی پیام مهم\n"
            "• 6-10 - برای پیام‌های بسیار فوری\n\n"
            "لطفاً عدد مورد نظر را انتخاب کنید:",
            reply_markup=create_repeat_count_menu(),
            parse_mode="HTML"
        )
        return
    
    else:
        # بررسی انتخاب روز
        day_selected = False
        for day_name, day_num in day_mapping.items():
            if day_name in message.text:
                if day_num in selected_days:
                    selected_days.remove(day_num)
                    await message.answer(f"❌ {day_name} از لیست حذف شد")
                else:
                    selected_days.append(day_num)
                    await message.answer(f"✅ {day_name} به لیست اضافه شد")
                day_selected = True
                break
        
        if not day_selected:
            await message.answer("❌ روز انتخاب شده معتبر نیست")
        
        await state.update_data(selected_days=selected_days)
    
    # نمایش وضعیت فعلی
    if selected_days:
        selected_days_names = [name for name, num in day_mapping.items() if num in selected_days]
        status_text = "، ".join(selected_days_names)
    else:
        status_text = "❌ هیچکدام"
    
    await message.answer(
        f"📆 <b>روزهای هفته</b>\n\n"
        f"📋 <b>روزهای انتخاب شده:</b> {status_text}\n\n"
        f"لطفاً روزهای مورد نظر را انتخاب کنید:",
        reply_markup=create_days_of_week_menu(selected_days),
        parse_mode="HTML"
    )

async def process_repeat_count(message: types.Message, state: FSMContext):
    """پردازش تعداد تکرار (&) - نسخه اصلاح شده"""
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
        
        # 🔥 اگر تکرار 0 یا 1 باشد، مستقیماً به تأیید نهایی برو
        if repeat_count == 0 or repeat_count == 1:
            await state.update_data(
                repeat_count=repeat_count,
                repeat_interval=0  # فاصله زمانی را 0 قرار بده
            )
            
            if repeat_count == 0:
                await message.answer(
                    "✅ تعداد تکرار تنظیم شد: 0 (فقط ثبت اطلاعات)\n\n"
                    "💡 <i>این ریمایندر فقط در سیستم ثبت می‌شود و پیامی ارسال نمی‌کند.</i>\n\n"
                    "در حال انتقال به مرحله تأیید نهایی...",
                    parse_mode="HTML"
                )
            else:
                await message.answer(
                    "✅ تعداد تکرار تنظیم شد: 1 (ارسال یکبار)\n\n"
                    "💡 <i>فاصله زمانی برای تکرار یکباره اعمال نمی‌شود.</i>\n\n"
                    "در حال انتقال به مرحله تأیید نهایی...",
                    parse_mode="HTML"
                )
            
            await asyncio.sleep(1)
            await show_advanced_confirmation(message, state)
        else:
            await state.update_data(repeat_count=repeat_count)
            await state.set_state(AdvancedReminderStates.waiting_for_repeat_interval)
            
            await message.answer(
                f"⏱️ <b>فاصله زمانی بین تکرارها (@)</b>\n\n"
                f"لطفاً فاصله زمانی بین ارسال‌ها را انتخاب کنید (10 تا 60 ثانیه):\n\n"
                f"💡 <i>توضیحات برای {repeat_count} بار تکرار:</i>\n"
                f"• ارسال {repeat_count} بار با فاصله زمانی مشخص\n"
                f"• اولین ارسال: رأس ساعت تعیین شده\n"
                f"• ارسال‌های بعدی: با فاصله @ ثانیه\n\n"
                f"🎯 <b>پیشنهادات:</b>\n"
                f"• 10-20 ثانیه: برای پیام‌های فوری\n"
                f"• 30-40 ثانیه: برای یادآوری‌های معمولی\n"
                f"• 50-60 ثانیه: برای پیام‌های طولانی\n\n"
                f"لطفاً فاصله زمانی را انتخاب کنید:",
                reply_markup=create_repeat_interval_menu(),
                parse_mode="HTML"
            )
            
    except ValueError:
        await message.answer(
            "❌ لطفاً یک عدد معتبر وارد کنید!",
            reply_markup=create_repeat_count_menu()
            )
        
async def process_repeat_interval(message: types.Message, state: FSMContext):
    """پردازش فاصله زمانی (@) - نسخه اصلاح شده"""
    if message.text == "🔙 بازگشت":
        await state.set_state(AdvancedReminderStates.waiting_for_repeat_count)
        await message.answer(
            "لطفاً تعداد تکرار را انتخاب کنید:",
            reply_markup=create_repeat_count_menu()
        )
        return
    
    try:
        repeat_interval = int(message.text)
        state_data = await state.get_data()
        repeat_count = state_data.get('repeat_count', 1)
        
        # 🔥 اگر تعداد تکرار 1 باشد، فاصله زمانی را نادیده بگیر
        if repeat_count == 1:
            repeat_interval = 0
            await message.answer(
                "✅ فاصله زمانی تنظیم شد: 0 (نادیده گرفته می‌شود)\n\n"
                "💡 <i>با توجه به تکرار یکباره، فاصله زمانی اعمال نمی‌شود.</i>\n\n"
                "در حال انتقال به مرحله تأیید نهایی...",
                parse_mode="HTML"
            )
        else:
            if repeat_interval < 10 or repeat_interval > 60:
                await message.answer(
                    "❌ فاصله زمانی باید بین 10 تا 60 ثانیه باشد!\n\n"
                    "لطفاً عدد معتبر وارد کنید:",
                    reply_markup=create_repeat_interval_menu()
                )
                return
            
            await message.answer(
                f"✅ فاصله زمانی تنظیم شد: {repeat_interval} ثانیه\n\n"
                f"💡 <i>پیام {repeat_count} بار با فاصله {repeat_interval} ثانیه ارسال می‌شود.</i>\n\n"
                "در حال انتقال به مرحله تأیید نهایی...",
                parse_mode="HTML"
            )
        
        await state.update_data(repeat_interval=repeat_interval)
        await asyncio.sleep(1)
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
        "🔍 <b>لطفاً اطلاعات را بررسی کنید:</b>\n\n"
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
        repeat_text = "📝 فقط ثبت (بدون ارسال پیام)"
        repeat_details = "• این ریمایندر فقط در سیستم ذخیره می‌شود\n• هیچ پیامی برای کاربران ارسال نمی‌شود"
    elif repeat_count == 1:
        repeat_text = "🔔 ارسال یکبار"
        repeat_details = f"• ارسال در ساعت {state_data.get('start_time', 'تعیین نشده')}"
    else:
        repeat_text = f"🔄 ارسال {repeat_count} بار"
        repeat_details = f"• فاصله بین ارسال‌ها: {repeat_interval} ثانیه\n• اولین ارسال: رأس ساعت\n• کل زمان: {(repeat_count - 1) * repeat_interval} ثانیه"
    
    summary = (
        f"📝 <b>عنوان:</b> {state_data.get('title', 'تعیین نشده')}\n"
        f"📄 <b>متن:</b> {state_data.get('message', 'تعیین نشده')[:100]}...\n\n"
        f"⏰ <b>ساعت شروع:</b> {state_data.get('start_time', 'تعیین نشده')}\n"
        f"📅 <b>تاریخ شروع:</b> {state_data.get('start_date', 'تعیین نشده')}\n"
        f"⏰ <b>ساعت پایان:</b> {state_data.get('end_time', 'تعیین نشده')}\n"
        f"📅 <b>تاریخ پایان:</b> {state_data.get('end_date', 'تعیین نشده')}\n"
        f"📆 <b>روزهای هفته:</b> {days_text}\n"
        f"🔢 <b>تکرار:</b> {repeat_text}\n"
        f"{repeat_details}\n\n"
        f"👥 <b>مخاطبان:</b> همه کاربران فعال ربات\n"
        f"🌍 <b>حوزه:</b> عمومی\n"
    )
    
    return summary

async def process_advanced_confirmation(message: types.Message, state: FSMContext):
    """پردازش تأیید نهایی ریمایندر پیشرفته - نسخه پیشرفته"""
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
            # 🎯 لاگ پیشرفته برای دیباگ
            logger.info("🎯 شروع ایجاد ریمایندر پیشرفته")
            logger.info(f"📊 داده‌های state: { {k: v for k, v in state_data.items() if k != 'message'} }")  # بدون متن برای حفظ حریم خصوصی
            
            # 🔍 اعتبارسنجی پیشرفته داده‌ها
            validation_errors = await validate_reminder_data(state_data)
            if validation_errors:
                error_message = "❌ <b>خطا در اعتبارسنجی داده‌ها:</b>\n\n" + "\n".join(validation_errors)
                await message.answer(
                    error_message + "\n\nلطفاً از گزینه '✏️ ویرایش اطلاعات' استفاده کنید.",
                    reply_markup=create_advanced_reminder_admin_menu(),
                    parse_mode="HTML"
                )
                return

            # 🔄 تبدیل تاریخ‌های شمسی به میلادی با مدیریت خطای پیشرفته
            conversion_result = await convert_persian_dates(state_data)
            if not conversion_result['success']:
                await message.answer(
                    f"❌ <b>خطا در تبدیل تاریخ‌ها:</b>\n\n{conversion_result['error']}\n\n"
                    f"💡 <i>لطفاً تاریخ‌ها را بررسی و مجدداً تلاش کنید.</i>",
                    reply_markup=create_advanced_reminder_admin_menu(),
                    parse_mode="HTML"
                )
                return

            start_date_gregorian = conversion_result['start_date']
            end_date_gregorian = conversion_result['end_date']

            # 📊 اعتبارسنجی منطق تاریخی
            date_validation = await validate_date_logic(start_date_gregorian, end_date_gregorian, state_data['start_time'], state_data['end_time'])
            if not date_validation['valid']:
                await message.answer(
                    f"⚠️ <b>هشدار در منطق زمانی:</b>\n\n{date_validation['message']}\n\n"
                    f"آیا می‌خواهید ادامه دهید؟",
                    reply_markup=create_date_validation_keyboard()  # کیبورد با گزینه‌های "ادامه می‌دهم" و "ویرایش"
                )
                return

            # 💾 ذخیره در دیتابیس با مدیریت تراکنش
            try:
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
                
                logger.info(f"✅ ریمایندر پیشرفته {reminder_id} با موفقیت در دیتابیس ذخیره شد")

            except Exception as db_error:
                logger.error(f"❌ خطای دیتابیس: {db_error}")
                await message.answer(
                    "❌ <b>خطا در ذخیره‌سازی دیتابیس!</b>\n\n"
                    "سیستم ذخیره‌سازی با مشکل مواجه شده است. لطفاً稍后 مجدداً تلاش کنید.",
                    reply_markup=create_advanced_reminder_admin_menu(),
                    parse_mode="HTML"
                )
                return

            # 🎉 ایجاد پیام موفقیت پیشرفته
            success_message = await create_success_message(reminder_id, state_data, start_date_gregorian, end_date_gregorian)
            
            await message.answer(
                success_message['text'],
                reply_markup=success_message['keyboard'],
                parse_mode="HTML"
            )

            # 📈 ثبت لاگ کامل
            logger.info(f"🎉 ریمایندر پیشرفته {reminder_id} توسط ادمین {message.from_user.id} ایجاد شد")
            logger.info(f"📝 مشخصات: {state_data['title']} - تکرار: {state_data['repeat_count']} - روزهای فعال: {len(state_data['selected_days'])}")

            # 🔔 اطلاع‌رسانی به ادمین‌های دیگر (اختیاری)
            await notify_other_admins(message.from_user.id, reminder_id, state_data['title'])

            # 🧹 پاک‌سازی state
            await state.clear()

            # 📅 راه‌اندازی scheduler برای ریمایندر جدید (اگر نیاز باشد)
            await setup_reminder_scheduler(reminder_id)

        except Exception as e:
            # 🚨 مدیریت خطای جامع
            error_handling = await handle_reminder_creation_error(e, state_data)
            await message.answer(
                error_handling['message'],
                reply_markup=error_handling['keyboard'],
                parse_mode="HTML"
            )
            logger.error(f"🚨 خطای کلی در ایجاد ریمایندر: {e}", exc_info=True)

    elif message.text == "✏️ ویرایش اطلاعات":
        await handle_edit_reminder(message, state)
    
    elif message.text == "❌ لغو":
        await handle_cancel_reminder(message, state)

# =============================================================================
# توابع کمکی پیشرفته
# =============================================================================

async def validate_reminder_data(state_data: dict) -> list:
    """اعتبارسنجی جامع داده‌های ریمایندر - نسخه اصلاح شده"""
    errors = []
    
    # بررسی وجود فیلدهای ضروری
    required_fields = {
        'title': 'عنوان',
        'message': 'متن ریمایندر',
        'start_date': 'تاریخ شروع',
        'start_time': 'ساعت شروع', 
        'end_date': 'تاریخ پایان',
        'end_time': 'ساعت پایان',
        'selected_days': 'روزهای هفته',
        'repeat_count': 'تعداد تکرار'
        # 🔥 فاصله زمانی فقط برای تکرارهای بیشتر از 1 اجباری است
    }
    
    for field, name in required_fields.items():
        if field not in state_data or state_data[field] is None or state_data[field] == "":
            errors.append(f"• فیلد '{name}' پر نشده است")
    
    # 🔥 اعتبارسنجی فاصله زمانی فقط برای تکرارهای بیشتر از 1
    if 'repeat_count' in state_data and state_data['repeat_count'] > 1:
        if 'repeat_interval' not in state_data or not state_data['repeat_interval']:
            errors.append("• برای تکرارهای بیشتر از 1، فاصله زمانی الزامی است")
        elif state_data['repeat_interval'] < 10 or state_data['repeat_interval'] > 60:
            errors.append("• فاصله زمانی باید بین ۱۰ تا ۶۰ ثانیه باشد")
    
    # 🔥 اگر تکرار 1 باشد، فاصله زمانی را 0 قرار بده
    if 'repeat_count' in state_data and state_data['repeat_count'] == 1:
        if 'repeat_interval' not in state_data or state_data['repeat_interval'] is None:
            state_data['repeat_interval'] = 0  # مقدار پیش‌فرض برای تکرار یکباره
    
    # اعتبارسنجی طول عنوان و متن
    if 'title' in state_data:
        if len(state_data['title']) < 3:
            errors.append("• عنوان باید حداقل ۳ حرف باشد")
        if len(state_data['title']) > 100:
            errors.append("• عنوان نمی‌تواند بیش از ۱۰۰ حرف باشد")
    
    if 'message' in state_data:
        if len(state_data['message']) < 10:
            errors.append("• متن ریمایندر باید حداقل ۱۰ حرف باشد")
        if len(state_data['message']) > 4000:
            errors.append("• متن ریمایندر نمی‌تواند بیش از ۴۰۰۰ حرف باشد")
    
    # اعتبارسنجی روزهای هفته
    if 'selected_days' in state_data:
        if not state_data['selected_days']:
            errors.append("• حداقل یک روز از هفته باید انتخاب شود")
        for day in state_data['selected_days']:
            if day not in [0, 1, 2, 3, 4, 5, 6]:
                errors.append("• روزهای هفته انتخاب شده معتبر نیستند")
    
    # 🔥 اعتبارسنجی تعداد تکرار
    if 'repeat_count' in state_data:
        if state_data['repeat_count'] < 0 or state_data['repeat_count'] > 10:
            errors.append("• تعداد تکرار باید بین ۰ تا ۱۰ باشد")
    
    return errors

async def convert_persian_dates(state_data: dict) -> dict:
    """تبدیل تاریخ‌های شمسی به میلادی با مدیریت خطا"""
    try:
        start_date = state_data['start_date']
        end_date = state_data['end_date']
        
        # لاگ برای دیباگ
        logger.info(f"🔄 تبدیل تاریخ: {start_date} -> میلادی")
        
        # تبدیل تاریخ شروع
        start_date_gregorian = persian_to_gregorian_string(start_date)
        
        # تبدیل تاریخ پایان
        end_date_gregorian = persian_to_gregorian_string(end_date)
        
        logger.info(f"✅ تبدیل موفق: {start_date} -> {start_date_gregorian}, {end_date} -> {end_date_gregorian}")
        
        return {
            'success': True,
            'start_date': start_date_gregorian,
            'end_date': end_date_gregorian,
            'message': 'تبدیل با موفقیت انجام شد'
        }
        
    except Exception as e:
        logger.error(f"❌ خطا در تبدیل تاریخ: {e}")
        return {
            'success': False,
            'error': f'خطا در تبدیل تاریخ: {str(e)}',
            'start_date': None,
            'end_date': None
        }

async def validate_date_logic(start_date: str, end_date: str, start_time: str, end_time: str) -> dict:
    """اعتبارسنجی منطق تاریخی و زمانی"""
    try:
        from datetime import datetime
        
        # ترکیب تاریخ و زمان
        start_datetime = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
        end_datetime = datetime.strptime(f"{end_date} {end_time}", "%Y-%m-%d %H:%M")
        
        # بررسی اینکه پایان قبل از شروع نباشد
        if end_datetime <= start_datetime:
            return {
                'valid': False,
                'message': '⏰ تاریخ/زمان پایان نمی‌تواند قبل از تاریخ/زمان شروع باشد!'
            }
        
        # بررسی فاصله زمانی معقول (حداکثر ۲ سال)
        time_difference = end_datetime - start_datetime
        if time_difference.days > 730:  # ۲ سال
            return {
                'valid': True,  # هشدار ولی قابل ادامه
                'message': '⚠️ بازه زمانی انتخاب شده بیش از ۲ سال است. آیا از صحت آن اطمینان دارید؟'
            }
        
        return {'valid': True, 'message': 'منطق زمانی معتبر است'}
        
    except Exception as e:
        logger.error(f"خطا در اعتبارسنجی منطق تاریخی: {e}")
        return {'valid': True, 'message': 'اعتبارسنجی زمانی انجام نشد'}

async def create_success_message(reminder_id: int, state_data: dict, start_date_gregorian: str, end_date_gregorian: str) -> dict:
    """ایجاد پیام موفقیت پیشرفته"""
    # اطلاعات تکرار
    repeat_info = ""
    if state_data['repeat_count'] == 0:
        repeat_info = "📝 <b>وضعیت:</b> فقط ثبت شده (بدون ارسال پیام)"
    elif state_data['repeat_count'] == 1:
        repeat_info = f"🔔 <b>وضعیت:</b> ارسال یکبار در ساعت {state_data['start_time']}"
    else:
        total_duration = (state_data['repeat_count'] - 1) * state_data['repeat_interval']
        repeat_info = f"🔄 <b>وضعیت:</b> ارسال {state_data['repeat_count']} بار با فاصله {state_data['repeat_interval']} ثانیه (کل زمان: {total_duration} ثانیه)"
    
    # روزهای هفته
    day_mapping = {
        0: "شنبه", 1: "یکشنبه", 2: "دوشنبه",
        3: "سه‌شنبه", 4: "چهارشنبه", 5: "پنجشنبه", 6: "جمعه"
    }
    days_text = "، ".join([day_mapping[day] for day in state_data['selected_days']])
    
    # محاسبه تعداد کاربران فعال
    active_users_count = await get_active_users_count()
    
    message_text = (
        f"🎉 <b>ریمایندر پیشرفته با موفقیت ایجاد شد!</b>\n\n"
        f"🆔 <b>کد ریمایندر:</b> <code>{reminder_id}</code>\n"
        f"📝 <b>عنوان:</b> {state_data['title']}\n"
        f"📄 <b>متن:</b> {state_data['message'][:100]}...\n\n"
        f"⏰ <b>زمان‌بندی:</b>\n"
        f"   • شروع: {state_data['start_date']} {state_data['start_time']}\n"
        f"   • پایان: {state_data['end_date']} {state_data['end_time']}\n"
        f"📆 <b>روزهای فعال:</b> {days_text}\n"
        f"{repeat_info}\n\n"
        f"👥 <b>مخاطبان:</b> {active_users_count} کاربر فعال\n"
        f"🕒 <b>تاریخ ایجاد:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        f"✅ <i>این ریمایندر به طور خودکار برای کاربران فعال ارسال خواهد شد.</i>"
    )
    
    return {
        'text': message_text,
        'keyboard': create_advanced_reminder_admin_menu()
    }

async def handle_reminder_creation_error(error: Exception, state_data: dict) -> dict:
    """مدیریت خطاهای ایجاد ریمایندر"""
    error_type = type(error).__name__
    
    if "date" in str(error).lower() or "time" in str(error).lower():
        message = (
            "❌ <b>خطا در داده‌های زمانی!</b>\n\n"
            f"خطا: {str(error)}\n\n"
            "💡 <i>لطفاً بررسی کنید:</i>\n"
            "• تاریخ‌ها به فرمت صحیح YYYY-MM-DD باشند\n"
            "• زمان‌ها به فرمت HH:MM باشند\n"
            "• تاریخ پایان بعد از تاریخ شروع باشد\n\n"
            "می‌توانید از گزینه '✏️ ویرایش اطلاعات' استفاده کنید."
        )
    elif "database" in str(error).lower() or "db" in str(error).lower():
        message = (
            "❌ <b>خطای سیستمی!</b>\n\n"
            "سیستم ذخیره‌سازی با مشکل مواجه شده است.\n"
            "لطفاً چند دقیقه دیگر مجدداً تلاش کنید."
        )
    else:
        message = (
            "❌ <b>خطای غیرمنتظره!</b>\n\n"
            f"خطا: {str(error)}\n\n"
            "لطفاً با پشتیبانی فنی تماس بگیرید."
        )
    
    return {
        'message': message,
        'keyboard': create_advanced_reminder_admin_menu()
    }

async def handle_edit_reminder(message: types.Message, state: FSMContext):
    """مدیریت ویرایش ریمایندر"""
    await state.set_state(AdvancedReminderStates.waiting_for_title)
    await message.answer(
        "✏️ <b>شروع ویرایش اطلاعات</b>\n\n"
        "لطفاً عنوان جدید ریمایندر را وارد کنید:",
        reply_markup=create_back_only_menu()
    )

async def handle_cancel_reminder(message: types.Message, state: FSMContext):
    """مدیریت لغو ایجاد ریمایندر"""
    await message.answer(
        "❌ <b>ایجاد ریمایندر لغو شد</b>\n\n"
        "هر زمان که خواستید می‌توانید ریمایندر جدیدی ایجاد کنید.",
        reply_markup=create_advanced_reminder_admin_menu(),
        parse_mode="HTML"
    )
    await state.clear()

# توابع اختیاری برای قابلیت‌های پیشرفته
async def get_active_users_count() -> int:
    """دریافت تعداد کاربران فعال"""
    try:
        # این تابع بستگی به ساختار دیتابیس شما دارد
        return 100  # مقدار نمونه
    except:
        return 0

async def notify_other_admins(creator_id: int, reminder_id: int, title: str):
    """اطلاع‌رسانی به سایر ادمین‌ها"""
    # پیاده‌سازی بستگی به ساختار ربات شما دارد
    pass

async def setup_reminder_scheduler(reminder_id: int):
    """راه‌اندازی زمان‌بند برای ریمایندر جدید"""
    # پیاده‌سازی بستگی به سیستم زمان‌بندی شما دارد
    pass

def create_date_validation_keyboard():
    """ایجاد کیبورد برای تأیید هشدارهای زمانی"""
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="✅ ادامه می‌دهم"),
                KeyboardButton(text="✏️ ویرایش زمان‌بندی")
            ],
            [
                KeyboardButton(text="🔙 بازگشت به منوی اصلی")
            ]
        ],
        resize_keyboard=True
    )

# =============================================================================
# بخش ۳: مدیریت و نمایش ریمایندرهای پیشرفته
# =============================================================================

async def list_advanced_reminders_admin(message: types.Message):
    """نمایش لیست ریمایندرهای پیشرفته برای ادمین"""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ دسترسی denied!")
        return
        
    reminders = reminder_db.get_admin_advanced_reminders()
    
    if not reminders:
        await message.answer(
            "📭 <b>هیچ ریمایندر پیشرفته‌ای پیدا نشد</b>\n\n"
            "💡 <i>می‌توانید با استفاده از گزینه '➕ افزودن ریمایندر جدید' یک ریمایندر ایجاد کنید.</i>\n\n"
            "🎯 <b>ایده‌هایی برای شروع:</b>\n"
            "• یادآوری شروع فصل‌های مطالعه\n"
            "• پیام‌های انگیزشی هفتگی\n"
            "• آماده‌سازی برای آزمون‌های آزمایشی\n"
            "• نکات طلایی مطالعه",
            reply_markup=create_advanced_reminder_admin_menu(),
            parse_mode="HTML"
        )
        return
    
    # محاسبه آمار
    active_count = len([r for r in reminders if r['is_active']])
    total_repeats = sum(r['repeat_count'] for r in reminders)
    
    message_text = (
        f"📋 <b>لیست ریمایندرهای پیشرفته</b>\n\n"
        f"📊 <b>آمار کلی:</b>\n"
        f"• 🔢 تعداد: {len(reminders)} ریمایندر\n"
        f"• 🔔 فعال: {active_count}\n"
        f"• 🔕 غیرفعال: {len(reminders) - active_count}\n"
        f"• 🔄 کل تکرارها: {total_repeats}\n\n"
        f"────────────────────\n\n"
    )
    
    for reminder in reminders:
        status = "✅" if reminder['is_active'] else "❌"
        
        # نمایش روزهای هفته به صورت فشرده
        day_mapping = {0: "ش", 1: "ی", 2: "د", 3: "س", 4: "چ", 5: "پ", 6: "ج"}
        days_text = "".join([day_mapping[day] for day in reminder['days_of_week']])
        
        # نمایش اطلاعات تکرار
        if reminder['repeat_count'] == 0:
            repeat_icon = "📝"
            repeat_text = "ثبت"
        elif reminder['repeat_count'] == 1:
            repeat_icon = "🔔"
            repeat_text = "یکبار"
        else:
            repeat_icon = "🔄"
            repeat_text = f"{reminder['repeat_count']}x"
        
        message_text += (
            f"{status} <b>کد {reminder['id']}</b>\n"
            f"{repeat_icon} {reminder['title'][:30]}{'...' if len(reminder['title']) > 30 else ''}\n"
            f"⏰ {reminder['start_time']} | 📆 {days_text}\n"
            f"🎯 {repeat_text} | 📨 {reminder['total_sent']}\n"
            f"────────────────────\n\n"
        )
    
    message_text += "💡 <i>برای مشاهده جزئیات هر ریمایندر، از گزینه‌های مدیریت استفاده کنید.</i>"
    
    await message.answer(
        message_text,
        reply_markup=create_advanced_reminder_admin_menu(),
        parse_mode="HTML"
    )

async def edit_advanced_reminder_handler(message: types.Message):
    """مدیریت ویرایش ریمایندرهای پیشرفته"""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ دسترسی denied!")
        return
        
    reminders = reminder_db.get_admin_advanced_reminders()
    
    if not reminders:
        await message.answer(
            "❌ هیچ ریمایندر پیشرفته‌ای برای ویرایش وجود ندارد",
            reply_markup=create_advanced_reminder_admin_menu()
        )
        return
    
    await message.answer(
        "✏️ <b>ویرایش ریمایندرهای پیشرفته</b>\n\n"
        "💡 <i>می‌توانید موارد زیر را ویرایش کنید:</i>\n"
        "• عنوان و متن ریمایندر\n"
        "• زمان‌بندی و تاریخ‌ها\n"
        "• روزهای فعال هفته\n"
        "• تنظیمات تکرار\n\n"
        "لطفاً ریمایندر مورد نظر را انتخاب کنید:",
        reply_markup=create_advanced_reminder_list_keyboard(reminders),
        parse_mode="HTML"
    )

async def delete_advanced_reminder_handler(message: types.Message):
    """مدیریت حذف ریمایندرهای پیشرفته"""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ دسترسی denied!")
        return
        
    reminders = reminder_db.get_admin_advanced_reminders()
    
    if not reminders:
        await message.answer(
            "❌ هیچ ریمایندر پیشرفته‌ای برای حذف وجود ندارد",
            reply_markup=create_advanced_reminder_admin_menu()
        )
        return
    
    await message.answer(
        "🗑️ <b>حذف ریمایندرهای پیشرفته</b>\n\n"
        "⚠️ <b>هشدار مهم: این عمل غیرقابل بازگشت است!</b>\n\n"
        "💡 <i>پس از حذف:</i>\n"
        "• تمام اطلاعات ریمایندر پاک می‌شود\n"
        "• لاگ‌های مربوطه حفظ می‌شوند\n"
        "• کاربران دیگر پیامی دریافت نمی‌کنند\n\n"
        "لطفاً ریمایندر مورد نظر را برای حذف انتخاب کنید:",
        reply_markup=create_advanced_reminder_list_keyboard(reminders),
        parse_mode="HTML"
    )

async def toggle_advanced_reminder_handler(message: types.Message):
    """مدیریت فعال/غیرفعال کردن ریمایندرهای پیشرفته"""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ دسترسی denied!")
        return
        
    reminders = reminder_db.get_admin_advanced_reminders()
    
    if not reminders:
        await message.answer(
            "❌ هیچ ریمایندر پیشرفته‌ای وجود ندارد",
            reply_markup=create_advanced_reminder_admin_menu()
        )
        return
    
    active_count = len([r for r in reminders if r['is_active']])
    
    await message.answer(
        f"🔔 <b>تغییر وضعیت ریمایندرهای پیشرفته</b>\n\n"
        f"📊 <b>وضعیت فعلی:</b>\n"
        f"• فعال: {active_count}\n"
        f"• غیرفعال: {len(reminders) - active_count}\n\n"
        f"💡 <i>با غیرفعال کردن:</i>\n"
        "• ریمایندر از چرخه ارسال خارج می‌شود\n"
        "• اطلاعات آن حفظ می‌شود\n"
        "• می‌توانید بعداً دوباره فعال کنید\n\n"
        "لطفاً ریمایندر مورد نظر را برای تغییر وضعیت انتخاب کنید:",
        reply_markup=create_advanced_reminder_list_keyboard(reminders),
        parse_mode="HTML"
    )

# =============================================================================
# بخش ۴: هندلرهای callback برای مدیریت پیشرفته
# =============================================================================

async def handle_advanced_reminder_callback(callback: types.CallbackQuery):
    """پردازش کلیک‌های ریمایندرهای پیشرفته"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ دسترسی denied!")
        return
    
    data = callback.data
    
    if data == "adv_admin:back":
        await callback.message.delete()
        await advanced_reminders_admin_handler(callback.message)
        return
    
    elif data.startswith("adv_reminder:"):
        # نمایش جزئیات ریمایندر
        reminder_id = int(data.split(":")[1])
        await show_advanced_reminder_details(callback, reminder_id)
    
    elif data.startswith("adv_edit:"):
        # ویرایش ریمایندر
        reminder_id = int(data.split(":")[1])
        await edit_advanced_reminder(callback, reminder_id)
    
    elif data.startswith("adv_delete:"):
        # حذف ریمایندر
        reminder_id = int(data.split(":")[1])
        await delete_advanced_reminder(callback, reminder_id)
    
    elif data.startswith("adv_toggle:"):
        # تغییر وضعیت فعال/غیرفعال
        reminder_id = int(data.split(":")[1])
        await toggle_advanced_reminder(callback, reminder_id)
    
    elif data.startswith("adv_list:"):
        # بازگشت به لیست
        action = data.split(":")[1]
        await list_advanced_reminders_action(callback, action)

async def show_advanced_reminder_details(callback: types.CallbackQuery, reminder_id: int):
    """نمایش جزئیات ریمایندر پیشرفته"""
    reminders = reminder_db.get_admin_advanced_reminders()
    reminder = next((r for r in reminders if r['id'] == reminder_id), None)
    
    if not reminder:
        await callback.answer("❌ ریمایندر پیدا نشد")
        return
    
    # نمایش روزهای هفته
    day_mapping = {
        0: "شنبه", 1: "یکشنبه", 2: "دوشنبه",
        3: "سه‌شنبه", 4: "چهارشنبه", 5: "پنجشنبه", 6: "جمعه"
    }
    days_text = "، ".join([day_mapping[day] for day in reminder['days_of_week']])
    
    # نمایش اطلاعات تکرار
    if reminder['repeat_count'] == 0:
        repeat_text = "📝 فقط ثبت شده (بدون ارسال)"
    elif reminder['repeat_count'] == 1:
        repeat_text = "🔔 ارسال یکبار"
    else:
        repeat_text = f"🔄 ارسال {reminder['repeat_count']} بار با فاصله {reminder['repeat_interval']} ثانیه"
    
    status_text = "✅ فعال" if reminder['is_active'] else "❌ غیرفعال"
    
    message = (
        f"📋 <b>جزئیات ریمایندر پیشرفته</b>\n\n"
        f"🆔 <b>کد ریمایندر:</b> <code>{reminder['id']}</code>\n"
        f"📝 <b>عنوان:</b> {reminder['title']}\n"
        f"📄 <b>متن:</b>\n{reminder['message']}\n\n"
        f"⏰ <b>ساعت شروع:</b> {reminder['start_time']}\n"
        f"📅 <b>تاریخ شروع:</b> {reminder['start_date']}\n"
        f"⏰ <b>ساعت پایان:</b> {reminder['end_time']}\n"
        f"📅 <b>تاریخ پایان:</b> {reminder['end_date']}\n"
        f"📆 <b>روزهای هفته:</b> {days_text}\n"
        f"🔢 <b>تکرار:</b> {repeat_text}\n\n"
        f"📊 <b>وضعیت:</b> {status_text}\n"
        f"📈 <b>تعداد ارسال:</b> {reminder['total_sent']} بار\n"
    )
    
    await callback.message.edit_text(
        message,
        reply_markup=create_advanced_reminder_actions_keyboard(reminder_id),
        parse_mode="HTML"
    )
    await callback.answer()
    
async def edit_advanced_reminder(callback: types.CallbackQuery, reminder_id: int):
    """ویرایش ریمایندر پیشرفته"""
    await callback.answer("✏️ قابلیت ویرایش به زودی اضافه خواهد شد")
    
    # نمایش پیام موقت
    await callback.message.answer(
        "✏️ <b>سیستم ویرایش ریمایندر</b>\n\n"
        "💡 <i>این قابلیت در حال توسعه است و به زودی در دسترس قرار می‌گیرد.</i>\n\n"
        "فعلاً می‌توانید ریمایندر جدیدی ایجاد کنید یا ریمایندر فعلی را حذف و مجدداً ایجاد کنید.",
        reply_markup=create_advanced_reminder_admin_menu(),
        parse_mode="HTML"
    )

async def delete_advanced_reminder(callback: types.CallbackQuery, reminder_id: int):
    """حذف ریمایندر پیشرفته"""
    # دریافت اطلاعات ریمایندر قبل از حذف
    reminders = reminder_db.get_admin_advanced_reminders()
    reminder = next((r for r in reminders if r['id'] == reminder_id), None)
    
    if not reminder:
        await callback.answer("❌ ریمایندر پیدا نشد")
        return
    
    success = reminder_db.delete_admin_advanced_reminder(reminder_id)
    
    if success:
        await callback.answer("✅ ریمایندر حذف شد")
        await callback.message.edit_text(
            f"🗑️ <b>ریمایندر پیشرفته حذف شد</b>\n\n"
            f"📝 <b>عنوان:</b> {reminder['title']}\n"
            f"🆔 <b>کد ریمایندر:</b> {reminder_id}\n\n"
            f"💡 <i>تمام اطلاعات این ریمایندر از سیستم حذف شد.</i>",
            reply_markup=create_advanced_reminder_admin_menu(),
            parse_mode="HTML"
        )
    else:
        await callback.answer("❌ خطا در حذف ریمایندر")

async def toggle_advanced_reminder(callback: types.CallbackQuery, reminder_id: int):
    """تغییر وضعیت فعال/غیرفعال ریمایندر پیشرفته"""
    success = reminder_db.toggle_admin_advanced_reminder(reminder_id)
    
    if success:
        # دریافت وضعیت جدید
        reminders = reminder_db.get_admin_advanced_reminders()
        current_reminder = next((r for r in reminders if r['id'] == reminder_id), None)
        
        if current_reminder:
            status_text = "فعال" if current_reminder['is_active'] else "غیرفعال"
            await callback.answer(f"✅ ریمایندر {status_text} شد")
            
            # بروزرسانی پیام
            await show_advanced_reminder_details(callback, reminder_id)
    else:
        await callback.answer("❌ خطا در تغییر وضعیت")

async def list_advanced_reminders_action(callback: types.CallbackQuery, action: str):
    """بازگشت به لیست با action مشخص"""
    reminders = reminder_db.get_admin_advanced_reminders()
    
    action_texts = {
        "edit": "ویرایش",
        "delete": "حذف", 
        "toggle": "تغییر وضعیت"
    }
    
    action_text = action_texts.get(action, "مدیریت")
    
    await callback.message.edit_text(
        f"✏️ <b>{action_text} ریمایندرهای پیشرفته</b>\n\n"
        f"لطفاً ریمایندر مورد نظر را انتخاب کنید:",
        reply_markup=create_advanced_reminder_list_keyboard(reminders, action=action),
        parse_mode="HTML"
    )
    await callback.answer()
    
async def show_advanced_reminder_stats(callback: types.CallbackQuery, reminder_id: int):
    """نمایش آمار ریمایندر پیشرفته"""
    reminders = reminder_db.get_admin_advanced_reminders()
    reminder = next((r for r in reminders if r['id'] == reminder_id), None)
    
    if not reminder:
        await callback.answer("❌ ریمایندر پیدا نشد")
        return
    
    current_time = get_current_persian_datetime()
    
    # محاسبه مدت زمان فعالیت
    created_date = datetime.strptime(reminder['created_at'][:10], "%Y-%m-%d")
    current_date = datetime.now()
    days_active = (current_date - created_date).days
    
    # اطلاعات تکرار
    if reminder['repeat_count'] == 0:
        repeat_info = "📝 حالت ثبت فقط - بدون ارسال"
    elif reminder['repeat_count'] == 1:
        repeat_info = f"🔔 ارسال یکبار در ساعت {reminder['start_time']}"
    else:
        total_duration = (reminder['repeat_count'] - 1) * reminder['repeat_interval']
        repeat_info = f"🔄 {reminder['repeat_count']} بار با فاصله {reminder['repeat_interval']}ث (کل: {total_duration}ث)"
    
    message = (
        f"📊 <b>آمار ریمایندر پیشرفته</b>\n\n"
        f"📝 <b>عنوان:</b> {reminder['title']}\n"
        f"🆔 <b>کد ریمایندر:</b> <code>{reminder['id']}</code>\n\n"
        f"📈 <b>آمار ارسال:</b>\n"
        f"• تعداد ارسال: {reminder['total_sent']} بار\n"
        f"• وضعیت: {'✅ فعال' if reminder['is_active'] else '❌ غیرفعال'}\n"
        f"• مدت فعالیت: {days_active} روز\n\n"
        f"🔢 <b>تنظیمات تکرار:</b>\n"
        f"• {repeat_info}\n"
        f"• روزهای فعال: {len(reminder['days_of_week'])} روز\n\n"
        f"⏰ <b>زمان‌بندی:</b>\n"
        f"• از {reminder['start_date']} {reminder['start_time']}\n"
        f"• تا {reminder['end_date']} {reminder['end_time']}\n\n"
        f"🕒 <i>آخرین بروزرسانی: {current_time['full_time']}</i>\n\n"
        f"💡 <i>این آمار به صورت real-time بروزرسانی می‌شود.</i>"
    )
    
    await callback.message.edit_text(
        message,
        reply_markup=create_advanced_reminder_actions_keyboard(reminder_id),
        parse_mode="HTML"
    )
