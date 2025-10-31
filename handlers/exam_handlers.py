"""
هندلرهای مربوط به کنکورها و زمان‌سنجی - نسخه اصلاح شده
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
    
    # دریافت تاریخ و زمان فعلی تهران به صورت شمسی
    from utils.time_utils import get_current_persian_datetime, calculate_multiple_dates_countdown, format_exam_dates, create_datetime_with_tehran_timezone
    current_time = get_current_persian_datetime()
    
    # تبدیل تاریخ‌های آزمون به datetime با تایم‌زون تهران و ساعت صحیح
    dates = exam["date"] if isinstance(exam["date"], list) else [exam["date"]]
    exam_dates = []
    
    for date_tuple in dates:
        # استخراج ساعت از زمان آزمون
        time_parts = exam["time"].split(":")
        hour = int(time_parts[0])
        minute = int(time_parts[1]) if len(time_parts) > 1 else 0
        
        if len(date_tuple) == 3:  # (year, month, day)
            exam_dates.append(create_datetime_with_tehran_timezone(
                date_tuple[0], date_tuple[1], date_tuple[2], hour, minute, 0
            ))
        else:  # اگر ساعت هم در تاریخ باشد
            exam_dates.append(create_datetime_with_tehran_timezone(*date_tuple))
    
    # محاسبه زمان باقی‌مانده برای همه تاریخ‌ها
    exam_dates_dict = {exam['name']: date for date in exam_dates}
    countdowns = calculate_multiple_dates_countdown(exam_dates_dict)
    
    # ساخت پیام
    message = f"🕒 <b>زمان فعلی تهران:</b> {current_time['full_date']}\n"
    message += f"⏰ <b>ساعت:</b> {current_time['full_time']}\n\n"
    
    message += f"📘 <b>{exam['name']}</b>\n"
    message += f"🕐 <b>ساعت برگزاری:</b> {exam['time']} به وقت تهران\n\n"
    
    # نمایش تاریخ‌های برگزاری به شمسی با تایم‌زون تهران
    message += f"🗓️ <b>تاریخ‌های برگزاری:</b>\n"
    message += format_exam_dates(exam_dates)
    message += "\n\n"
    
    # نمایش زمان باقی‌مانده برای هر تاریخ - اصلاح شده
    if len(countdowns) > 1:
        message += f"⏳ <b>زمان باقی‌مانده:</b>\n"
        for i, countdown in enumerate(countdowns, 1):
            # countdown یک تاپل هست: (نام آزمون, متن وضعیت, روزهای باقی‌مانده)
            if isinstance(countdown, tuple) and len(countdown) >= 3:
                exam_name, status_text, days_remaining = countdown
                if 'گذشته' in status_text or '✅' in status_text:
                    message += f"{i}. ✅ برگزار شده\n"
                else:
                    message += f"{i}. {status_text} ({days_remaining} روز)\n"
            else:
                message += f"{i}. ❌ خطا در محاسبه\n"
    else:
        # برای آزمون‌های تک‌روزه
        if countdowns and isinstance(countdowns[0], tuple) and len(countdowns[0]) >= 3:
            countdown = countdowns[0]
            status_text = countdown[1]
            days_remaining = countdown[2]
            
            if 'گذشته' in status_text or '✅' in status_text:
                message += f"⏳ <b>وضعیت:</b> ✅ برگزار شده\n"
            else:
                message += f"⏳ <b>زمان باقی‌مانده:</b> {status_text}\n"
                message += f"📆 <b>تعداد روزهای باقی‌مانده:</b> {days_remaining} روز\n"
        else:
            message += f"⏳ <b>وضعیت:</b> ❌ خطا در محاسبه زمان\n"
    
    message += f"\n🎯 {random.choice(MOTIVATIONAL_MESSAGES)}"
    
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
        # استفاده از time_utils برای محاسبه صحیح
        from utils.time_utils import get_current_tehran_datetime, create_datetime_with_tehran_timezone
        
        now = get_current_tehran_datetime()
        dates = exam["date"] if isinstance(exam["date"], list) else [exam["date"]]
        
        # تبدیل تاریخ‌ها به datetime با تایم‌زون تهران
        exam_dates = []
        for date_tuple in dates:
            time_parts = exam["time"].split(":")
            hour = int(time_parts[0])
            minute = int(time_parts[1]) if len(time_parts) > 1 else 0
            
            if len(date_tuple) == 3:
                exam_dates.append(create_datetime_with_tehran_timezone(
                    date_tuple[0], date_tuple[1], date_tuple[2], hour, minute, 0
                ))
        
        # پیدا کردن تاریخ‌های آینده
        future_dates = [d for d in exam_dates if d > now]
        
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
    """هندلر دکمه بروزرسانی - بدون تغییر callback.data"""
    exam_key = callback.data.replace("refresh:", "")
    
    if exam_key in EXAMS_1405:
        # استفاده از time_utils برای محاسبه صحیح
        from utils.time_utils import get_current_tehran_datetime, create_datetime_with_tehran_timezone
        
        exam = EXAMS_1405[exam_key]
        now = get_current_tehran_datetime()
        
        dates = exam["date"] if isinstance(exam["date"], list) else [exam["date"]]
        
        # تبدیل تاریخ‌ها به datetime با تایم‌زون تهران
        exam_dates = []
        for date_tuple in dates:
            time_parts = exam["time"].split(":")
            hour = int(time_parts[0])
            minute = int(time_parts[1]) if len(time_parts) > 1 else 0
            
            if len(date_tuple) == 3:
                exam_dates.append(create_datetime_with_tehran_timezone(
                    date_tuple[0], date_tuple[1], date_tuple[2], hour, minute, 0
                ))
        
        # پیدا کردن تاریخ‌های آینده
        future_dates = [d for d in exam_dates if d > now]
        
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

🔄 اطلاعات بروزرسانی شد
🎯 {random.choice(MOTIVATIONAL_MESSAGES)}
"""
        await callback.message.edit_text(
            message, 
            reply_markup=exam_actions_menu(exam_key), 
            parse_mode="HTML"
        )
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
        # استفاده از time_utils برای محاسبه صحیح
        from utils.time_utils import get_current_tehran_datetime, create_datetime_with_tehran_timezone
        
        exam = next_exam
        now = get_current_tehran_datetime()
        
        # تبدیل تاریخ آزمون به datetime با تایم‌زون تهران
        dates = exam["date"] if isinstance(exam["date"], list) else [exam["date"]]
        time_parts = exam["time"].split(":")
        hour = int(time_parts[0])
        minute = int(time_parts[1]) if len(time_parts) > 1 else 0
        
        if len(dates[0]) == 3:
            target = create_datetime_with_tehran_timezone(
                dates[0][0], dates[0][1], dates[0][2], hour, minute, 0
            )
        else:
            target = create_datetime_with_tehran_timezone(*dates[0])
        
        countdown, total_days = format_time_remaining(target)
        
        message = f"""
🎯 <b>نزدیک‌ترین آزمون: {exam['name']}</b>
📅 تاریخ: {exam['persian_date']}
🕒 ساعت: {exam['time']}

{countdown}
📆 تعداد کل روزهای باقی‌مانده: {total_days} روز

💫 این نزدیک‌ترین آزمون به زمان حال است!
"""
        await callback.message.edit_text(
            message,
            reply_markup=exam_actions_menu(next_exam['key']),
            parse_mode="HTML"
        )
        await callback.answer("🎯 نزدیک‌ترین آزمون نمایش داده شد")
    else:
        await callback.answer("❌ هیچ آزمون آینده‌ای پیدا نشد", show_alert=True)

async def exam_details_handler(callback: types.CallbackQuery):
    """هندلر دکمه جزئیات بیشتر"""
    exam_key = callback.data.replace("details:", "")
    
    if exam_key not in EXAMS_1405:
        await callback.answer("❌ آزمون یافت نشد")
        return
    
    # استفاده از time_utils برای محاسبه صحیح
    from utils.time_utils import get_current_tehran_datetime, create_datetime_with_tehran_timezone
    
    exam = EXAMS_1405[exam_key]
    now = get_current_tehran_datetime()
    dates = exam["date"] if isinstance(exam["date"], list) else [exam["date"]]
    
    # تبدیل تاریخ‌ها به datetime با تایم‌زون تهران
    exam_dates = []
    for date_tuple in dates:
        time_parts = exam["time"].split(":")
        hour = int(time_parts[0])
        minute = int(time_parts[1]) if len(time_parts) > 1 else 0
        
        if len(date_tuple) == 3:
            exam_dates.append(create_datetime_with_tehran_timezone(
                date_tuple[0], date_tuple[1], date_tuple[2], hour, minute, 0
            ))
    
    # پیدا کردن تاریخ‌های آینده
    future_dates = [d for d in exam_dates if d > now]
    
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
