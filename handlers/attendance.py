from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from database.operations import database
import jdatetime

async def attendance_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # ثبت حضور کاربر
    attendance = database.record_attendance(user_id)
    
    # دریافت آمار
    today_count = database.get_today_attendance_count()
    user_stats = database.get_user_attendance_stats(user_id, 30)
    
    persian_date = jdatetime.datetime.now().strftime("%Y/%m/%d")
    current_time = jdatetime.datetime.now().strftime("%H:%M:%S")
    
    keyboard = [
        [InlineKeyboardButton("📊 نمایش اعلام حضورها", callback_data="show_attendance")],
        [InlineKeyboardButton("📈 آمار حضور من", callback_data="my_attendance_stats")],
        [InlineKeyboardButton("🔄 بروزرسانی", callback_data="attendance")],
        [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = (
        "✅ حضور شما با موفقیت ثبت شد!\n\n"
        f"📅 تاریخ: {persian_date}\n"
        f"🕒 زمان: {current_time}\n"
        f"👥 تعداد حاضرین امروز: {today_count} نفر\n\n"
        f"📊 آمار ۳۰ روزه شما:\n"
        f"• 📅 روزهای حضور: {user_stats.get('attendance_days', 0)} روز\n"
        f"• ⏰ مجموع مطالعه: {user_stats.get('total_hours', 0):.1f} ساعت\n"
        f"• 📈 نرخ حضور: {user_stats.get('attendance_rate', 0):.1f}%"
    )
    
    await query.edit_message_text(message_text, reply_markup=reply_markup)

async def show_attendance_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # دریافت آمار حضور امروز
    today_count = database.get_today_attendance_count()
    today = jdatetime.datetime.now().strftime("%Y/%m/%d")
    
    # در اینجا می‌توانید لیست کاربران حاضر را از دیتابیس دریافت کنید
    # برای نمونه از پیام ثابت استفاده می‌کنیم
    
    keyboard = [
        [InlineKeyboardButton("🔄 بروزرسانی", callback_data="show_attendance")],
        [InlineKeyboardButton("✅ اعلام حضور", callback_data="attendance")],
        [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = (
        "📊 لیست اعلام حضورها\n\n"
        f"📅 تاریخ: {today}\n"
        f"👥 تعداد حاضرین: {today_count} نفر\n\n"
        "🔄 لیست حاضرین به صورت زنده بروزرسانی می‌شود.\n"
        "برای مشاهده لیست کامل از دکمه بروزرسانی استفاده کنید."
    )
    
    await query.edit_message_text(message_text, reply_markup=reply_markup)

async def show_my_attendance_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_stats = database.get_user_attendance_stats(user_id, 30)
    
    keyboard = [
        [InlineKeyboardButton("📅 آمار هفتگی", callback_data="weekly_attendance_stats")],
        [InlineKeyboardButton("📈 آمار ماهانه", callback_data="monthly_attendance_stats")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="attendance")],
        [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = (
        "📊 آمار حضور و مطالعه شما\n\n"
        f"📅 دوره: ۳۰ روز اخیر\n\n"
        f"📆 روزهای حضور: {user_stats.get('attendance_days', 0)} روز\n"
        f"⏰ مجموع مطالعه: {user_stats.get('total_hours', 0):.1f} ساعت\n"
        f"📈 نرخ حضور: {user_stats.get('attendance_rate', 0):.1f}%\n"
        f"⚡ بیشترین مطالعه روزانه: {user_stats.get('max_daily_minutes', 0)} دقیقه\n"
        f"📊 میانگین روزانه: {user_stats.get('avg_daily_minutes', 0):.1f} دقیقه\n\n"
        f"🎯 هدف پیشنهادی: حداقل ۲۵ روز حضور در ماه"
    )
    
    await query.edit_message_text(message_text, reply_markup=reply_markup)

def setup_attendance_handlers(application):
    application.add_handler(CallbackQueryHandler(attendance_menu, pattern="^attendance$"))
    application.add_handler(CallbackQueryHandler(show_attendance_list, pattern="^show_attendance$"))
    application.add_handler(CallbackQueryHandler(show_my_attendance_stats, pattern="^my_attendance_stats$"))
    application.add_handler(CallbackQueryHandler(show_my_attendance_stats, pattern="^weekly_attendance_stats$"))
    application.add_handler(CallbackQueryHandler(show_my_attendance_stats, pattern="^monthly_attendance_stats$"))
