"""
هندلرهای مربوط به کنکورها و زمان‌سنجی - نسخه کامل اصلاح شده
"""
import logging
import random
from datetime import datetime
from aiogram import types, F

from config import MOTIVATIONAL_MESSAGES
from exam_data import EXAMS_1405
from keyboards import exam_actions_menu
from utils.time_utils import (
    format_time_remaining, get_study_tips, 
    get_current_tehran_datetime, create_datetime_with_tehran_timezone,
    calculate_multiple_dates_countdown, format_exam_dates
)

logger = logging.getLogger(__name__)

def get_next_exam():
    """پیدا کردن نزدیک‌ترین آزمون آینده"""
    try:
        now = get_current_tehran_datetime()
        next_exam = None
        min_days = float('inf')
        
        for exam_key, exam in EXAMS_1405.items():
            dates = exam["date"] if isinstance(exam["date"], list) else [exam["date"]]
            
            # تبدیل تاریخ‌ها به datetime با تایم‌زون تهران
            exam_dates = []
            for date_tuple in dates:
                time_parts = exam["time"].split(":")
                hour = int(time_parts[0])
                minute = int(time_parts[1]) if len(time_parts) > 1 else 0
                
                if len(date_tuple) == 3:
                    exam_date = create_datetime_with_tehran_timezone(
                        date_tuple[0], date_tuple[1], date_tuple[2], hour, minute, 0
                    )
                    exam_dates.append(exam_date)
            
            # پیدا کردن نزدیک‌ترین تاریخ آینده
            for exam_date in exam_dates:
                if exam_date > now:
                    days_until = (exam_date - now).days
                    if days_until < min_days:
                        min_days = days_until
                        next_exam = {
                            'key': exam_key,
                            'name': exam['name'],
                            'persian_date': exam['persian_date'],
                            'time': exam['time'],
                            'date': exam_date
                        }
        
        return next_exam
    except Exception as e:
        logger.error(f"خطا در پیدا کردن آزمون بعدی: {e}")
        return None

def format_time_remaining_detailed(target_date):
    """فرمت‌بندی دقیق زمان باقی‌مانده با جزئیات کامل"""
    try:
        now = get_current_tehran_datetime()
        
        # اطمینان از اینکه target_date در تایم‌زون تهران باشد
        if target_date.tzinfo is None:
            from utils.time_utils import TEHRAN_TIMEZONE
            target_date = TEHRAN_TIMEZONE.localize(target_date)
        else:
            target_date = target_date.astimezone(get_current_tehran_datetime().tzinfo)
        
        if target_date <= now:
            return {
                'total_days': 0,
                'weeks': 0,
                'days': 0,
                'hours': 0,
                'minutes': 0,
                'seconds': 0,
                'total_seconds': 0
            }
        
        delta = target_date - now
        total_seconds = int(delta.total_seconds())
        total_days = delta.days
        
        # محاسبه جزئیات زمان
        weeks = total_days // 7
        days = total_days % 7
        hours = (total_seconds % (24 * 3600)) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        return {
            'total_days': total_days,
            'weeks': weeks,
            'days': days,
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds,
            'total_seconds': total_seconds
        }
    except Exception as e:
        logger.error(f"خطا در format_time_remaining_detailed: {e}")
        return {
            'total_days': 0,
            'weeks': 0,
            'days': 0,
            'hours': 0,
            'minutes': 0,
            'seconds': 0,
            'total_seconds': 0
        }

async def exam_callback_handler(callback: types.CallbackQuery):
    """هندلر کلیک روی کنکور خاص"""
    exam_key = callback.data.replace("exam:", "")
    logger.info(f"🔘 کلیک روی کنکور: {exam_key}")
    
    if exam_key not in EXAMS_1405:
        await callback.answer("❌ آزمون یافت نشد")
        return
    
    exam = EXAMS_1405[exam_key]
    
    # دریافت تاریخ و زمان فعلی تهران به صورت شمسی
    from utils.time_utils import get_current_persian_datetime
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
                # محاسبه جزئیات زمان
                if exam_dates:
                    time_details = format_time_remaining_detailed(exam_dates[0])
                    message += f"⏳ <b>زمان باقی‌مانده:</b>\n"
                    message += f"• 🗓️ هفته: {time_details['weeks']} هفته\n"
                    message += f"• 📅 روز: {time_details['days']} روز\n"
                    message += f"• 🕒 ساعت: {time_details['hours']} ساعت\n"
                    message += f"• ⏰ دقیقه: {time_details['minutes']} دقیقه\n"
                    message += f"• ⏱️ ثانیه: {time_details['seconds']} ثانیه\n"
                    message += f"📆 <b>کل روزهای باقی‌مانده:</b> {time_details['total_days']} روز\n"
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
            
            # محاسبه جزئیات زمان
            time_details = format_time_remaining_detailed(target)
            
            message += f"⏳ {countdown}\n"
            message += f"📊 جزئیات: {time_details['weeks']}هفته {time_details['days']}روز {time_details['hours']}ساعت\n"
            message += f"📆 کل روزها: {total_days} روز\n"
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
            time_details = {'weeks': 0, 'days': 0, 'hours': 0, 'minutes': 0, 'seconds': 0, 'total_days': 0}
        else:
            target = min(future_dates)
            countdown, total_days = format_time_remaining(target)
            time_details = format_time_remaining_detailed(target)
        
        message = f"""
📘 <b>{exam['name']}</b>
📅 تاریخ: {exam['persian_date']}
🕒 ساعت: {exam['time']}

⏳ <b>زمان باقی‌مانده:</b>
{countdown}

📊 <b>جزئیات زمان:</b>
• 🗓️ هفته: {time_details['weeks']}
• 📅 روز: {time_details['days']}
• 🕒 ساعت: {time_details['hours']}
• ⏰ دقیقه: {time_details['minutes']}
• ⏱️ ثانیه: {time_details['seconds']}

📆 <b>کل روزهای باقی‌مانده:</b> {total_days} روز

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
        exam = next_exam
        now = get_current_tehran_datetime()
        target = exam['date']
        
        countdown, total_days = format_time_remaining(target)
        time_details = format_time_remaining_detailed(target)
        
        message = f"""
🎯 <b>نزدیک‌ترین آزمون: {exam['name']}</b>
📅 تاریخ: {exam['persian_date']}
🕒 ساعت: {exam['time']}

⏳ <b>زمان باقی‌مانده:</b>
{countdown}

📊 <b>جزئیات زمان:</b>
• 🗓️ هفته: {time_details['weeks']}
• 📅 روز: {time_details['days']}
• 🕒 ساعت: {time_details['hours']}
• ⏰ دقیقه: {time_details['minutes']}
• ⏱️ ثانیه: {time_details['seconds']}

📆 <b>کل روزهای باقی‌مانده:</b> {total_days} روز

💫 این نزدیک‌ترین آزمون به زمان حال است!
🎯 {random.choice(MOTIVATIONAL_MESSAGES)}
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
        countdown, total_days = format_time_remaining(target)
        
        message = f"""
📘 <b>جزئیات کامل {exam['name']}</b>

📅 تاریخ: {exam['persian_date']}
🕒 ساعت: {exam['time']}

⏳ <b>خلاصه زمان باقی‌مانده:</b>
{countdown}

📊 <b>جزئیات کامل زمان:</b>
• 🗓️ هفته: {time_details['weeks']} هفته
• 📅 روز: {time_details['days']} روز  
• 🕒 ساعت: {time_details['hours']} ساعت
• ⏰ دقیقه: {time_details['minutes']} دقیقه
• ⏱️ ثانیه: {time_details['seconds']} ثانیه

📈 <b>اطلاعات آماری:</b>
• 📆 کل روزهای باقی‌مانده: {total_days} روز
• ⏱️ کل ثانیه‌ها: {time_details['total_seconds']:,} ثانیه

💡 <b>نکته مطالعاتی:</b>
{get_study_tips()}

🎯 {random.choice(MOTIVATIONAL_MESSAGES)}
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
    await callback.answer("📊 جزئیات کامل نمایش داده شد")
