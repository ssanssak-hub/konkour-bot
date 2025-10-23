from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from database.operations import database
import jdatetime
from datetime import datetime, timedelta

async def statistics_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # دریافت آمار کاربر
    user_stats = database.get_user_statistics(user_id)
    daily_time = database.get_daily_study_time(user_id)
    weekly_time = database.get_weekly_study_time(user_id)
    monthly_time = database.get_monthly_study_time(user_id)
    
    attendance_stats = database.get_user_attendance_stats(user_id, 30)
    
    message_text = (
        "📊 آمار و گزارش جامع\n\n"
        f"⏰ مطالعه امروز: {daily_time:.1f} ساعت\n"
        f"📅 مطالعه این هفته: {weekly_time:.1f} ساعت\n"
        f"🗓️ مطالعه این ماه: {monthly_time:.1f} ساعت\n"
        f"📚 کل مطالعه ۳۰ روزه: {user_stats.get('study_time', {}).get('total_30_days', 0):.1f} ساعت\n\n"
        f"✅ تعداد حضور: {attendance_stats.get('attendance_days', 0)} روز\n"
        f"🎯 نرخ موفقیت اهداف: {user_stats.get('plans', {}).get('completion_rate', 0):.1f}%\n"
        f"📈 میانگین جلسات: {user_stats.get('sessions', {}).get('average_duration', 0):.1f} ساعت\n\n"
        f"📅 تاریخ امروز: {jdatetime.datetime.now().strftime('%Y/%m/%d')}"
    )
    
    # تحلیل عملکرد
    analysis = ""
    total_30_days = user_stats.get('study_time', {}).get('total_30_days', 0)
    if total_30_days > 100:
        analysis = "🎉 عملکرد فوق‌العاده! ادامه بده"
    elif total_30_days > 50:
        analysis = "✅ خوب پیش می‌ری! می‌تونی بهتر هم باشی"
    elif total_30_days > 20:
        analysis = "📈 در مسیر درستی! بیشتر تلاش کن"
    else:
        analysis = "💪 نیاز به تلاش بیشتر داری! شروع کن"
    
    message_text += f"\n\n{analysis}"
    
    keyboard = [
        [InlineKeyboardButton("📈 پیشرفت روزانه", callback_data="daily_progress")],
        [InlineKeyboardButton("📆 پیشرفت هفتگی", callback_data="weekly_progress")],
        [InlineKeyboardButton("🗓️ پیشرفت ماهانه", callback_data="monthly_progress")],
        [InlineKeyboardButton("🏆 مقایسه با برترین‌ها", callback_data="compare_top")],
        [InlineKeyboardButton("📋 گزارش کامل", callback_data="full_report")],
        [InlineKeyboardButton("🔄 بروزرسانی آمار", callback_data="statistics")],
        [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message_text, reply_markup=reply_markup)

async def show_daily_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # آمار ۷ روز اخیر
    days = []
    study_times = []
    
    for i in range(7):
        date = (jdatetime.datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        study_time = database.get_daily_study_time(user_id, date)
        days.append(date[5:])  # فقط ماه و روز
        study_times.append(study_time)
    
    days.reverse()
    study_times.reverse()
    
    # ایجاد نمودار متنی ساده
    chart_text = "📈 نمودار مطالعه ۷ روز اخیر:\n\n"
    max_time = max(study_times) if study_times else 1
    
    for i, (day, time) in enumerate(zip(days, study_times)):
        bar_length = int((time / max_time) * 20) if max_time > 0 else 0
        bar = "█" * bar_length
        chart_text += f"{day}: {bar} {time:.1f}h\n"
    
    today_time = study_times[-1] if study_times else 0
    yesterday_time = study_times[-2] if len(study_times) > 1 else 0
    
    if yesterday_time > 0:
        change = ((today_time - yesterday_time) / yesterday_time) * 100
        trend = "📈 افزایش" if change > 0 else "📉 کاهش" if change < 0 else "➡️ بدون تغییر"
        chart_text += f"\n{today_time:.1f} ساعت\n{trend} {abs(change):.1f}% نسبت به دیروز"
    
    # توصیه روزانه
    recommendation = ""
    if today_time >= 6:
        recommendation = "🎉 امروز عالی بود! فردا هم ادامه بده"
    elif today_time >= 3:
        recommendation = "✅ خوب بود. سعی کن فردا بیشتر مطالعه کنی"
    elif today_time >= 1:
        recommendation = "💪 شروع خوبی بود. فردا بیشتر تلاش کن"
    else:
        recommendation = "🔴 فردا حتماً مطالعه رو شروع کن"
    
    chart_text += f"\n\n{recommendation}"
    
    keyboard = [
        [InlineKeyboardButton("📆 پیشرفت هفتگی", callback_data="weekly_progress")],
        [InlineKeyboardButton("🔙 بازگشت به آمار", callback_data="statistics")],
        [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(chart_text, reply_markup=reply_markup)

async def show_weekly_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # آمار ۴ هفته اخیر (شبیه‌سازی)
    weeks = ["هفته ۴", "هفته ۳", "هفته ۲", "هفته ۱"]
    study_times = []
    
    # محاسبه مطالعه هفتگی (شبیه‌سازی)
    for i in range(4):
        # در نسخه واقعی، این مقدار از دیتابیس محاسبه می‌شود
        base_time = database.get_weekly_study_time(user_id)
        study_time = max(base_time - i * 5, 0)  # شبیه‌سازی داده
        study_times.append(study_time)
    
    chart_text = "📆 نمودار مطالعه ۴ هفته اخیر:\n\n"
    max_time = max(study_times) if study_times else 1
    
    for week, time in zip(weeks, study_times):
        bar_length = int((time / max_time) * 20) if max_time > 0 else 0
        bar = "█" * bar_length
        chart_text += f"{week}: {bar} {time:.1f}h\n"
    
    # تحلیل پیشرفت
    if len(study_times) >= 2:
        current_week = study_times[-1]
        last_week = study_times[-2]
        
        if last_week > 0:
            change = ((current_week - last_week) / last_week) * 100
            
            if change > 20:
                analysis = "🎉 پیشرفت فوق‌العاده! روندت عالیه"
            elif change > 0:
                analysis = "✅ در مسیر پیشرفت قرار داری"
            elif change > -10:
                analysis = "⚠️ ثابت موندی، نیاز به تلاش بیشتر"
            else:
                analysis = "🔴 افت داشتی، برنامه‌ات رو بررسی کن"
            
            chart_text += f"\n{analysis}\nتغییر: {change:+.1f}%"
    
    keyboard = [
        [InlineKeyboardButton("📈 پیشرفت روزانه", callback_data="daily_progress")],
        [InlineKeyboardButton("🔙 بازگشت به آمار", callback_data="statistics")],
        [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(chart_text, reply_markup=reply_markup)

async def compare_with_top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # دریافت آمار کاربر
    user_weekly_time = database.get_weekly_study_time(user_id)
    user_monthly_time = database.get_monthly_study_time(user_id)
    
    # نمونه‌سازی داده‌های ۲۰ کاربر برتر
    top_users = [
        {"name": "کاربر برتر ۱", "study_time": 48.5, "progress": 98},
        {"name": "کاربر برتر ۲", "study_time": 45.0, "progress": 95},
        {"name": "کاربر برتر ۳", "study_time": 42.5, "progress": 92},
        {"name": "کاربر برتر ۴", "study_time": 40.0, "progress": 90},
        {"name": "کاربر برتر ۵", "study_time": 38.5, "progress": 88},
    ]
    
    # محاسبه رتبه کاربر (شبیه‌سازی)
    user_rank = 6 if user_weekly_time < 35 else 3
    
    message_text = "🏆 مقایسه با برترین‌ها\n\n"
    message_text += f"🔸 رتبه شما: {user_rank}\n"
    message_text += f"🔸 مطالعه هفتگی شما: {user_weekly_time:.1f} ساعت\n"
    message_text += f"🔸 مطالعه ماهانه شما: {user_monthly_time:.1f} ساعت\n\n"
    
    message_text += "📊 ۵ کاربر برتر:\n"
    for i, user in enumerate(top_users, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        message_text += f"{medal} {user['name']}: {user['study_time']} ساعت ({user['progress']}%)\n"
    
    # توصیه‌ها
    advice = ""
    if user_weekly_time < 20:
        advice = "💡 برای رسیدن به رتبه‌های برتر، حداقل ۲۵ ساعت در هفته مطالعه نیاز داری."
    elif user_weekly_time < 30:
        advice = "✅ خوب پیش می‌ری! با ۵-۱۰ ساعت مطالعه بیشتر می‌تونی بین برترین‌ها باشی."
    else:
        advice = "🎉 عالی! شما در بین برترین‌ها هستید. همین روال رو ادامه بده."
    
    message_text += f"\n{advice}"
    
    keyboard = [
        [InlineKeyboardButton("📈 پیشرفت شخصی", callback_data="statistics")],
        [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message_text, reply_markup=reply_markup)

async def show_full_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # جمع‌آوری تمام آمار
    user_stats = database.get_user_statistics(user_id)
    attendance_stats = database.get_user_attendance_stats(user_id, 30)
    study_by_subject = database.study_repo.get_study_time_by_subject(user_id, 30)
    
    report_text = (
        "📋 گزارش کامل عملکرد\n\n"
        f"⏰ آمار مطالعه:\n"
        f"• امروز: {database.get_daily_study_time(user_id):.1f} ساعت\n"
        f"• این هفته: {database.get_weekly_study_time(user_id):.1f} ساعت\n"
        f"• این ماه: {database.get_monthly_study_time(user_id):.1f} ساعت\n"
        f"• ۳۰ روزه: {user_stats.get('study_time', {}).get('total_30_days', 0):.1f} ساعت\n\n"
        
        f"📅 آمار کمی:\n"
        f"• تعداد جلسات: {user_stats.get('sessions', {}).get('total', 0)} جلسه\n"
        f"• میانگین هر جلسه: {user_stats.get('sessions', {}).get('average_duration', 0):.1f} ساعت\n"
        f"• روزهای حضور: {attendance_stats.get('attendance_days', 0)} روز\n"
        f"• نرخ حضور: {attendance_stats.get('attendance_rate', 0):.1f}%\n\n"
    )
    
    if study_by_subject:
        report_text += "🎯 مطالعه بر اساس درس:\n"
        for subject, time in list(study_by_subject.items())[:5]:
            percentage = (time / user_stats.get('study_time', {}).get('total_30_days', 1)) * 100
            report_text += f"• {subject}: {time:.1f} ساعت ({percentage:.1f}%)\n"
    
    # تحلیل نهایی
    total_study = user_stats.get('study_time', {}).get('total_30_days', 0)
    if total_study >= 100:
        final_analysis = "🎉 عملکرد استثنایی! شما واقعاً الهام‌بخش هستید"
    elif total_study >= 60:
        final_analysis = "✅ عملکرد بسیار خوب! در مسیر موفقیت قرار داری"
    elif total_study >= 30:
        final_analysis = "📈 عملکرد قابل قبول! می‌تونی بهتر هم باشی"
    else:
        final_analysis = "💪 نیاز به تلاش بیشتر داری! از امروز شروع کن"
    
    report_text += f"\n{final_analysis}"
    
    keyboard = [
        [InlineKeyboardButton("🔄 بروزرسانی گزارش", callback_data="full_report")],
        [InlineKeyboardButton("🔙 بازگشت به آمار", callback_data="statistics")],
        [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(report_text, reply_markup=reply_markup)

def setup_statistics_handlers(application):
    application.add_handler(CallbackQueryHandler(statistics_menu, pattern="^statistics$"))
    application.add_handler(CallbackQueryHandler(show_daily_progress, pattern="^daily_progress$"))
    application.add_handler(CallbackQueryHandler(show_weekly_progress, pattern="^weekly_progress$"))
    application.add_handler(CallbackQueryHandler(compare_with_top, pattern="^compare_top$"))
    application.add_handler(CallbackQueryHandler(show_full_report, pattern="^full_report$"))
    application.add_handler(CallbackQueryHandler(show_weekly_progress, pattern="^monthly_progress$"))
