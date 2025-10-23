from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters
from database.operations import database
from database.utils import db_manager
import config
import jdatetime

def is_admin(user_id):
    """بررسی اینکه کاربر ادمین است یا نه"""
    return user_id == config.Config.ADMIN_ID

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        await query.edit_message_text("❌ شما دسترسی به این بخش را ندارید.")
        return
    
    # دریافت آمار سیستم
    system_stats = database.get_system_statistics()
    db_info = db_manager.get_database_info()
    
    keyboard = [
        [InlineKeyboardButton("📊 آمار کلی کاربران", callback_data="admin_stats")],
        [InlineKeyboardButton("👥 مدیریت کاربران", callback_data="admin_manage_users")],
        [InlineKeyboardButton("📢 ارسال پیام همگانی", callback_data="admin_broadcast")],
        [InlineKeyboardButton("📨 ارسال پیام به کاربر", callback_data="admin_send_to_user")],
        [InlineKeyboardButton("📩 مدیریت پیام‌های کاربران", callback_data="admin_user_messages")],
        [InlineKeyboardButton("💾 مدیریت دیتابیس", callback_data="admin_database")],
        [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = (
        "🔧 پنل مدیریت پیشرفته\n\n"
        f"📊 آمار سیستم:\n"
        f"• 👥 کاربران کل: {system_stats.get('total_users', 0)}\n"
        f"• ✅ کاربران فعال: {system_stats.get('active_users', 0)}\n"
        f"• 📅 حضور امروز: {system_stats.get('today_attendance', 0)}\n"
        f"• 📩 پیام‌های pending: {system_stats.get('pending_messages', 0)}\n\n"
        f"💾 دیتابیس: {db_info.get('database_size', 'نامشخص')}\n"
        f"📅 آخرین بروزرسانی: {jdatetime.datetime.now().strftime('%Y/%m/%d %H:%M')}"
    )
    
    await query.edit_message_text(message_text, reply_markup=reply_markup)

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        await query.edit_message_text("❌ شما دسترسی به این بخش را ندارید.")
        return
    
    # جمع‌آوری آمار کامل
    system_stats = database.get_system_statistics()
    db_info = db_manager.get_database_info()
    
    # آمار حضور ۷ روز اخیر
    attendance_stats = database.attendance_repo.get_daily_attendance_stats(7)
    
    stats_text = (
        "📊 آمار کلی ربات\n\n"
        f"👥 **کاربران:**\n"
        f"• کل کاربران: {system_stats.get('total_users', 0)} نفر\n"
        f"• کاربران فعال: {system_stats.get('active_users', 0)} نفر\n"
        f"• کاربران غیرفعال: {system_stats.get('total_users', 0) - system_stats.get('active_users', 0)} نفر\n\n"
        
        f"📈 **فعالیت‌ها:**\n"
        f"• حضور و غیاب امروز: {system_stats.get('today_attendance', 0)} بار\n"
        f"• کل جلسات مطالعه: {system_stats.get('total_study_sessions', 0)} جلسه\n"
        f"• کل یادآوری‌ها: {system_stats.get('total_reminders', 0)} یادآوری\n"
        f"• پیام‌های pending: {system_stats.get('pending_messages', 0)} پیام\n\n"
    )
    
    # آمار حضور ۷ روز اخیر
    if attendance_stats:
        stats_text += "📅 حضور ۷ روز اخیر:\n"
        for date, count in list(attendance_stats.items())[:7]:
            stats_text += f"• {date}: {count} نفر\n"
        stats_text += "\n"
    
    stats_text += (
        f"💾 **سیستم:**\n"
        f"• حجم دیتابیس: {db_info.get('database_size', 'نامشخص')}\n"
        f"• سلامت دیتابیس: ✅\n"
        f"• آخرین بروزرسانی: {jdatetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')}"
    )
    
    keyboard = [
        [InlineKeyboardButton("🔄 بروزرسانی آمار", callback_data="admin_stats")],
        [InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="admin_panel")],
        [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(stats_text, reply_markup=reply_markup)

async def admin_manage_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        await query.edit_message_text("❌ شما دسترسی به این بخش را ندارید.")
        return
    
    users = database.get_all_users(active_only=False)
    
    users_text = "👥 مدیریت کاربران\n\n"
    keyboard = []
    
    for user in users[:10]:  # فقط ۱۰ کاربر اول
        status = "✅ فعال" if user.is_active else "❌ غیرفعال"
        username = f"@{user.username}" if user.username else "بدون یوزرنیم"
        
        users_text += f"🆔 {user.user_id}\n"
        users_text += f"👤 {user.first_name} {user.last_name or ''}\n"
        users_text += f"📱 {username}\n"
        users_text += f"📅 عضویت: {user.join_date.strftime('%Y/%m/%d')}\n"
        users_text += f"🔸 وضعیت: {status}\n\n"
        
        keyboard.append([
            InlineKeyboardButton(f"👁️ {user.user_id}", callback_data=f"admin_view_user_{user.user_id}"),
            InlineKeyboardButton(f"{'❌' if user.is_active else '✅'} {user.user_id}", 
                               callback_data=f"admin_toggle_user_{user.user_id}")
        ])
    
    keyboard.append([InlineKeyboardButton("📊 کاربران غیرفعال", callback_data="admin_inactive_users")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="admin_panel")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(users_text, reply_markup=reply_markup)

async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        await query.edit_message_text("❌ شما دسترسی به این بخش را ندارید.")
        return
    
    context.user_data['waiting_for_broadcast'] = True
    
    keyboard = [
        [InlineKeyboardButton("❌ انصراف", callback_data="admin_panel")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    active_users_count = len(database.get_all_users(active_only=True))
    
    await query.edit_message_text(
        "📢 ارسال پیام همگانی\n\n"
        f"👥 این پیام به {active_users_count} کاربر فعال ارسال خواهد شد.\n\n"
        "لطفاً متن پیام همگانی را وارد کنید:\n\n"
        "💡 نکات:\n"
        "• حداکثر ۴۰۰۰ کاراکتر\n"
        "• از اموجی استفاده کنید\n"
        "• پیام واضح و مختصر باشد",
        reply_markup=reply_markup
    )

async def handle_broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_for_broadcast') and is_admin(update.message.from_user.id):
        broadcast_text = update.message.text
        
        if len(broadcast_text) > 4000:
            await update.message.reply_text(
                "❌ طول پیام بیش از حد مجاز است (حداکثر ۴۰۰۰ کاراکتر)"
            )
            return
        
        context.user_data.pop('waiting_for_broadcast', None)
        
        users = database.get_all_users(active_only=True)
        
        keyboard = [
            [InlineKeyboardButton("📢 ارسال پیام جدید", callback_data="admin_broadcast")],
            [InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="admin_panel")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"✅ پیام همگانی آماده ارسال!\n\n"
            f"📝 متن پیام: {broadcast_text}\n"
            f"👥 تعداد دریافت‌کنندگان: {len(users)} کاربر فعال\n\n"
            f"💡 پیام در حال ارسال به کاربران است...\n"
            f"این فرآیند ممکن است چند دقیقه طول بکشد.",
            reply_markup=reply_markup
        )

async def admin_user_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        await query.edit_message_text("❌ شما دسترسی به این بخش را ندارید.")
        return
    
    pending_messages = database.get_pending_messages()
    
    if not pending_messages:
        keyboard = [
            [InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="admin_panel")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "📭 هیچ پیام در انتظار پاسخی وجود ندارد. ✅",
            reply_markup=reply_markup
        )
        return
    
    messages_text = "📩 پیام‌های کاربران در انتظار پاسخ\n\n"
    keyboard = []
    
    for msg in pending_messages[:5]:
        user = database.get_user(msg.user_id)
        username = f"@{user.username}" if user and user.username else "بدون یوزرنیم"
        user_name = f"{user.first_name} {user.last_name or ''}" if user else "کاربر ناشناس"
        
        messages_text += f"🆔 پیام #{msg.id}\n"
        messages_text += f"👤 کاربر: {user_name} ({username})\n"
        messages_text += f"📅 تاریخ: {msg.created_at.strftime('%Y/%m/%d %H:%M')}\n"
        messages_text += f"📝 متن: {msg.message_text[:80]}...\n\n"
        
        keyboard.append([
            InlineKeyboardButton(f"📨 پاسخ {msg.id}", callback_data=f"admin_reply_{msg.id}"),
            InlineKeyboardButton(f"✅ انجام شده {msg.id}", callback_data=f"admin_mark_done_{msg.id}")
        ])
    
    keyboard.append([InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="admin_panel")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(messages_text, reply_markup=reply_markup)

async def admin_database(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        await query.edit_message_text("❌ شما دسترسی به این بخش را ندارید.")
        return
    
    db_info = db_manager.get_database_info()
    health_status = db_manager.health_check()
    
    message_text = (
        "💾 مدیریت دیتابیس\n\n"
        f"📊 اطلاعات دیتابیس:\n"
        f"• حجم: {db_info.get('database_size', 'نامشخص')}\n"
        f"• کاربران: {db_info.get('total_users', 0)} نفر\n"
        f"• جلسات مطالعه: {db_info.get('total_study_sessions', 0)} جلسه\n"
        f"• حضور و غیاب: {db_info.get('total_attendance', 0)} رکورد\n\n"
        f"🔧 وضعیت سیستم: {health_status.get('database_connection', 'نامشخص')}\n"
        f"📅 آخرین بررسی: {health_status.get('timestamp', 'نامشخص')[:16]}"
    )
    
    keyboard = [
        [InlineKeyboardButton("💾 پشتیبان‌گیری", callback_data="admin_backup")],
        [InlineKeyboardButton("🧹 پاکسازی داده‌های قدیمی", callback_data="admin_cleanup")],
        [InlineKeyboardButton("⚡ بهینه‌سازی دیتابیس", callback_data="admin_optimize")],
        [InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="admin_panel")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message_text, reply_markup=reply_markup)

async def admin_backup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        await query.edit_message_text("❌ شما دسترسی به این بخش را ندارید.")
        return
    
    success = db_manager.backup_database()
    
    if success:
        message = "✅ پشتیبان‌گیری با موفقیت انجام شد!"
    else:
        message = "❌ خطا در پشتیبان‌گیری"
    
    keyboard = [
        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_database")],
        [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup)

async def admin_cleanup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        await query.edit_message_text("❌ شما دسترسی به این بخش را ندارید.")
        return
    
    cleanup_result = db_manager.cleanup_old_data(90)
    
    message = "🧹 پاکسازی داده‌های قدیمی انجام شد!\n\n"
    if cleanup_result:
        message += f"• جلسات مطالعه حذف شده: {cleanup_result.get('old_sessions_deleted', 0)}\n"
        message += f"• رکوردهای حضور حذف شده: {cleanup_result.get('old_attendance_deleted', 0)}\n"
        message += f"• لاگ‌های قدیمی حذف شده: {cleanup_result.get('old_logs_deleted', 0)}"
    else:
        message += "❌ خطا در پاکسازی داده‌ها"
    
    keyboard = [
        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_database")],
        [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup)

def setup_admin_handlers(application):
    application.add_handler(CallbackQueryHandler(admin_panel, pattern="^admin_panel$"))
    application.add_handler(CallbackQueryHandler(admin_stats, pattern="^admin_stats$"))
    application.add_handler(CallbackQueryHandler(admin_manage_users, pattern="^admin_manage_users$"))
    application.add_handler(CallbackQueryHandler(admin_broadcast, pattern="^admin_broadcast$"))
    application.add_handler(CallbackQueryHandler(admin_user_messages, pattern="^admin_user_messages$"))
    application.add_handler(CallbackQueryHandler(admin_database, pattern="^admin_database$"))
    application.add_handler(CallbackQueryHandler(admin_backup, pattern="^admin_backup$"))
    application.add_handler(CallbackQueryHandler(admin_cleanup, pattern="^admin_cleanup$"))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_broadcast_message), group=9)
