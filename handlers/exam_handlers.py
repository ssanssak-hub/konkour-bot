"""
هندلرهای مربوط به کنکورها و زمان‌سنجی
"""
import logging
import random
from datetime import datetime
from aiogram import types, F

from config import MOTIVATIONAL_MESSAGES
from exam_data import EXAMS_1405
from keyboards import exam_actions_menu
from utils import (
    format_time_remaining, format_time_remaining_detailed, 
    get_study_tips, get_next_exam
)

logger = logging.getLogger(__name__)

async def exam_callback_handler(callback: types.CallbackQuery):
    """هندلر کلیک روی کنکور خاص"""
    exam_key = callback.data.replace("exam:", "")
    logger.info(f"🔘 کلیک روی کنکور: {exam_key}")
    
    if exam_key not in EXAMS_1405:
        await callback.answer("❌ آزمون یافت نشد")
        return
    
    exam = EXAMS_1405[exam_key]
    now = datetime.now()
    
    dates = exam["date"] if isinstance(exam["date"], list) else [exam["date"]]
    future_dates = [datetime(*d) for d in dates if datetime(*d) > now]
    
    if not future_dates:
        countdown = "✅ برگزار شده"
        total_days = 0
    else:
        target = min(future_dates)
        countdown, total_days = format_time_remaining(target)
    
    message = f"""
📘 <b>{exam['name']}</b>
📅 تاریخ: {exam['persian_date']}
🕒 ساعت: {exam['time']}

{countdown}
📆 تعداد کل روزهای باقی‌مانده: {total_days} روز

🎯 {random.choice(MOTIVATIONAL_MESSAGES)}
"""
    await callback.message.edit_text(
        message, 
        reply_markup=exam_actions_menu(exam_key), 
        parse_mode="HTML"
    )

async def all_exams_handler(callback: types.CallbackQuery):
    """هندلر نمایش همه کنکورها"""
    logger.info(f"📋 کاربر {callback.from_user.id} همه کنکورها را انتخاب کرد")
    
    message = "⏳ <b>زمان باقی‌مانده تا کنکورهای ۱۴۰۵</b>\n\n"
    
    for exam_key, exam in EXAMS_1405.items():
        now = datetime.now()
        dates = exam["date"] if isinstance(exam["date"], list) else [exam["date"]]
        future_dates = [datetime(*d) for d in dates if datetime(*d) > now]
        
        message += f"🎯 <b>{exam['name']}</b>\n"
        message += f"📅 {exam['persian_date']} - 🕒 {exam['time']}\n"
        
        if future_dates:
            target = min(future_dates)
            countdown, total_days = format_time_remaining(target)
            message += f"{countdown}\n"
            message += f"📆 کل روزهای باقی‌مانده: {total_days} روز\n"
        else:
            message += "✅ برگزار شده\n"
        
        message += "─" * 30 + "\n\n"
    
    message += f"💫 <i>{random.choice(MOTIVATIONAL_MESSAGES)}</i>"
    
    await callback.message.edit_text(
        message, 
        reply_markup=exam_actions_menu(), 
        parse_mode="HTML"
    )

async def refresh_exam_handler(callback: types.CallbackQuery):
    """هندلر دکمه بروزرسانی"""
    exam_key = callback.data.replace("refresh:", "")
    
    if exam_key in EXAMS_1405:
        # بروزرسانی آزمون خاص
        callback.data = f"exam:{exam_key}"
        await exam_callback_handler(callback)
        await callback.answer("🔄 اطلاعات بروزرسانی شد")
    else:
        await callback.answer("❌ آزمون یافت نشد")

async def refresh_all_exams_handler(callback: types.CallbackQuery):
    """هندلر بروزرسانی همه آزمون‌ها"""
    await all_exams_handler(callback)
    await callback.answer("🔄 همه اطلاعات بروزرسانی شد")

async def next_exam_handler(callback: types.CallbackQuery):
    """هندلر دکمه آزمون بعدی"""
    next_exam = get_next_exam()
    
    if next_exam:
        # استفاده از هندلر موجود
        callback.data = f"exam:{next_exam['key']}"
        await exam_callback_handler(callback)
        await callback.answer("🎯 نزدیک‌ترین آزمون نمایش داده شد")
    else:
        await callback.answer("❌ هیچ آزمون آینده‌ای پیدا نشد", show_alert=True)

async def exam_details_handler(callback: types.CallbackQuery):
    """هندلر دکمه جزئیات بیشتر"""
    exam_key = callback.data.replace("details:", "")
    
    if exam_key not in EXAMS_1405:
        await callback.answer("❌ آزمون یافت نشد")
        return
    
    exam = EXAMS_1405[exam_key]
    now = datetime.now()
    dates = exam["date"] if isinstance(exam["date"], list) else [exam["date"]]
    future_dates = [datetime(*d) for d in dates if datetime(*d) > now]
    
    if future_dates:
        target = min(future_dates)
        time_details = format_time_remaining_detailed(target)
        
        message = f"""
📘 <b>جزئیات کامل {exam['name']}</b>

📅 تاریخ: {exam['persian_date']}
🕒 ساعت: {exam['time']}

⏳ <b>زمان باقی‌مانده:</b>
• 📆 کل روزها: {time_details['total_days']} روز
• 🗓️ هفته: {time_details['weeks']} هفته
• 📅 روز: {time_details['days']} روز  
• 🕒 ساعت: {time_details['hours']} ساعت
• ⏰ دقیقه: {time_details['minutes']} دقیقه
• ⏱️ ثانیه: {time_details['seconds']} ثانیه

📊 <b>اطلاعات آماری:</b>
• 📈 کل ثانیه‌ها: {time_details['total_seconds']:,} ثانیه

💡 <b>نکته مطالعاتی:</b>
{get_study_tips()}
"""
    else:
        message = f"""
📘 <b>جزئیات کامل {exam['name']}</b>

📅 تاریخ: {exam['persian_date']}
🕒 ساعت: {exam['time']}

✅ این آزمون برگزار شده است.

🎯 {random.choice(MOTIVATIONAL_MESSAGES)}
"""
    
    await callback.message.edit_text(
        message,
        reply_markup=exam_actions_menu(exam_key),
        parse_mode="HTML"
    )
