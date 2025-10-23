from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
import jdatetime
from datetime import datetime
import config
from database.operations import database

def calculate_time_remaining(target_date):
    """محاسبه زمان باقی‌مانده"""
    now = jdatetime.datetime.now()
    
    if isinstance(target_date, str):
        target_date = jdatetime.datetime.strptime(target_date, "%Y-%m-%d %H:%M:%S")
    
    remaining = target_date - now
    
    weeks = remaining.days // 7
    days = remaining.days % 7
    hours = remaining.seconds // 3600
    minutes = (remaining.seconds % 3600) // 60
    seconds = remaining.seconds % 60
    
    return weeks, days, hours, minutes, seconds, remaining.days

async def countdown_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = []
    for exam_name in config.Config.get_all_exam_names():
        exam_emoji = config.Config.get_exam_emoji(exam_name)
        keyboard.append([InlineKeyboardButton(f"{exam_emoji} {exam_name}", callback_data=f"countdown_{exam_name}")])
    
    keyboard.append([InlineKeyboardButton("🔄 بروزرسانی همه", callback_data="refresh_all")])
    keyboard.append([InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🎯 انتخاب کنکور برای نمایش زمان باقی‌مانده\n\n"
        "لطفاً کنکور مورد نظر خود را انتخاب کنید:",
        reply_markup=reply_markup
    )

async def show_countdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    exam_name = query.data.replace("countdown_", "")
    
    if exam_name == "refresh_all":
        await countdown_menu(update, context)
        return
    
    exam_data = config.Config.EXAMS.get(exam_name)
    
    if not exam_data:
        await query.answer("❌ کنکور یافت نشد")
        return
    
    if exam_name == "فرهنگیان":
        dates = exam_data["date"]
        message_text = f"⏰ زمان باقی‌مانده تا کنکور {exam_name}:\n\n"
        
        for i, date_str in enumerate(dates, 1):
            target_date = jdatetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            weeks, days, hours, minutes, seconds, total_days = calculate_time_remaining(target_date)
            
            message_text += (
                f"📅 تاریخ {i}: {date_str}\n"
                f"⏳ زمان باقی‌مانده:\n"
                f"   {weeks} هفته, {days} روز\n"
                f"   {hours:02d}:{minutes:02d}:{seconds:02d}\n"
                f"   📊 مجموع: {total_days} روز\n\n"
            )
    else:
        date_str = exam_data["date"]
        target_date = jdatetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        weeks, days, hours, minutes, seconds, total_days = calculate_time_remaining(target_date)
        
        # دریافت توصیه مطالعه
        recommendation = config.Config.get_study_recommendation(total_days)
        
        message_text = (
            f"⏰ زمان باقی‌مانده تا کنکور {exam_name}:\n\n"
            f"📅 تاریخ: {date_str}\n"
            f"⏳ زمان باقی‌مانده:\n"
            f"   {weeks} هفته, {days} روز\n"
            f"   {hours:02d}:{minutes:02d}:{seconds:02d}\n"
            f"   📊 مجموع: {total_days} روز\n\n"
            f"💡 {recommendation}"
        )
    
    keyboard = [
        [InlineKeyboardButton("🔄 بروزرسانی", callback_data=f"countdown_{exam_name}")],
        [InlineKeyboardButton("📊 همه کنکورها", callback_data="countdown")],
        [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message_text, reply_markup=reply_markup)

def setup_countdown_handlers(application):
    application.add_handler(CallbackQueryHandler(countdown_menu, pattern="^countdown$"))
    application.add_handler(CallbackQueryHandler(show_countdown, pattern="^countdown_"))
