"""
هندلرهای برنامه مطالعاتی و آمار
"""
import logging
from datetime import datetime
from aiogram import types, F
from aiogram.fsm.context import FSMContext

from keyboards import study_subjects_menu, create_stats_keyboard, back_button_menu
from utils import get_motivational_quote, format_study_time
from database import Database

logger = logging.getLogger(__name__)
db = Database()

async def study_callback_handler(callback: types.CallbackQuery, state: FSMContext):
    """هندلر اصلی برای callback_dataهای study"""
    data = callback.data
    
    if data == "study:log":
        await log_study_handler(callback, state)
    elif data.startswith("study:subject:"):
        await log_subject_handler(callback, state)
    elif data in ["study:daily", "study:weekly", "study:monthly"]:
        await callback.answer("⚠️ این قابلیت به زودی اضافه می‌شود")
    else:
        await callback.answer("⚠️ دستور نامعتبر")

async def today_stats_handler(callback: types.CallbackQuery):
    """نمایش آمار امروز"""
    today_stats = db.get_today_study_stats(callback.from_user.id)
    
    await callback.message.edit_text(
        f"📊 <b>آمار مطالعه امروز</b>\n\n"
        f"📅 تاریخ: {datetime.now().strftime('%Y-%m-%d')}\n\n"
        f"• 🕒 زمان مطالعه: {today_stats['total_minutes']} دقیقه\n"
        f"• 📖 تعداد جلسات: {today_stats['sessions_count']} جلسه\n"
        f"• 📚 دروس مطالعه شده: {today_stats['subjects']}\n\n"
        f"💪 {get_motivational_quote()}",
        reply_markup=create_stats_keyboard(),
        parse_mode="HTML"
    )

async def weekly_stats_handler(callback: types.CallbackQuery):
    """نمایش آمار هفته جاری"""
    from utils import calculate_streak
    
    weekly_stats = db.get_weekly_stats(callback.from_user.id)
    total_weekly = sum(day['total_minutes'] for day in weekly_stats)
    
    stats_text = "📅 <b>آمار مطالعه هفته جاری</b>\n\n"
    
    for day in weekly_stats:
        stats_text += f"• {day['date']}: {day['total_minutes']} دقیقه ({day['sessions_count']} جلسه)\n"
    
    study_days = [day['date'] for day in weekly_stats if day['total_minutes'] > 0]
    current_streak = calculate_streak(study_days)
    
    stats_text += f"\n📊 <b>جمع کل:</b> {format_study_time(total_weekly)}\n"
    stats_text += f"📈 <b>میانگین روزانه:</b> {total_weekly // 7 if weekly_stats else 0} دقیقه\n"
    stats_text += f"🔥 <b>Streak فعلی:</b> {current_streak} روز\n\n"
    stats_text += f"🎯 {get_motivational_quote()}"
    
    await callback.message.edit_text(
        stats_text,
        reply_markup=create_stats_keyboard(),
        parse_mode="HTML"
    )

async def log_study_handler(callback: types.CallbackQuery, state: FSMContext):
    """شروع فرآیند ثبت جلسه مطالعه"""
    await callback.message.edit_text(
        "⏱️ <b>ثبت جلسه مطالعه</b>\n\n"
        "لطفاً درس مورد نظر را انتخاب کنید:",
        reply_markup=study_subjects_menu(),
        parse_mode="HTML"
    )

async def log_subject_handler(callback: types.CallbackQuery, state: FSMContext):
    """ذخیره درس انتخاب شده و درخواست مدت زمان"""
    subject_data = callback.data.replace("study:subject:", "")
    
    subject_map = {
        "math": "ریاضی", "physics": "فیزیک", "chemistry": "شیمی", 
        "biology": "زیست", "literature": "ادبیات", "arabic": "عربی",
        "religion": "دینی", "english": "زبان"
    }
    
    subject_name = subject_map.get(subject_data, "نامشخص")
    
    await state.update_data(subject=subject_data, subject_name=subject_name)
    await state.set_state("waiting_for_duration")
    
    await callback.message.edit_text(
        f"⏱️ <b>ثبت مطالعه {subject_name}</b>\n\n"
        f"مدت زمان مطالعه را به دقیقه وارد کنید:\n"
        f"مثال: <code>120</code> (برای ۲ ساعت)",
        reply_markup=back_button_menu("🔙 بازگشت به انتخاب درس", "study:log"),
        parse_mode="HTML"
    )

async def process_study_duration(message: types.Message, state: FSMContext):
    """پردازش مدت زمان مطالعه"""
    try:
        duration = int(message.text)
        if duration <= 0 or duration > 1440:  # حداکثر 24 ساعت
            await message.answer("❌ لطفاً یک عدد معتبر بین 1 تا 1440 وارد کنید:")
            return
        
        data = await state.get_data()
        subject = data.get('subject')
        subject_name = data.get('subject_name')
        
        # ذخیره در دیتابیس
        db.add_study_session(
            user_id=message.from_user.id,
            subject=subject,
            topic=f"جلسه مطالعه {subject_name}",
            duration_minutes=duration
        )
        
        await state.clear()
        
        # نمایش نتیجه
        user_stats = db.get_today_study_stats(message.from_user.id)
        
        await message.answer(
            f"✅ <b>جلسه مطالعه ثبت شد!</b>\n\n"
            f"📚 درس: {subject_name}\n"
            f"⏰ مدت: {duration} دقیقه\n"
            f"📅 تاریخ: {datetime.now().strftime('%Y-%m-%d')}\n\n"
            f"📊 <b>آمار امروز:</b>\n"
            f"• 🕒 کل زمان: {user_stats['total_minutes']} دقیقه\n"
            f"• 📖 جلسات: {user_stats['sessions_count']} جلسه\n\n"
            f"🎯 {get_motivational_quote()}",
            reply_markup=create_stats_keyboard(),
            parse_mode="HTML"
        )
        
    except ValueError:
        await message.answer("❌ لطفاً یک عدد معتبر وارد کنید:")
