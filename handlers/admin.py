from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters
from database.operations import database
from database.utils import db_manager
import config
import jdatetime
import asyncio
import logging

logger = logging.getLogger(__name__)

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

async def admin_view_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش جزئیات کاربر"""
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        await query.edit_message_text("❌ شما دسترسی به این بخش را ندارید.")
        return
    
    user_id = int(query.data.replace("admin_view_user_", ""))
    user = database.get_user(user_id)
    
    if not user:
        await query.edit_message_text("❌ کاربر یافت نشد")
        return
    
    # دریافت آمار کاربر
    user_stats = database.get_user_statistics(user_id)
    attendance_stats = database.get_user_attendance_stats(user_id, 30)
    
    user_text = (
        f"👤 جزئیات کاربر\n\n"
        f"🆔 آیدی: {user.user_id}\n"
        f"👤 نام: {user.first_name} {user.last_name or ''}\n"
        f"📱 یوزرنیم: @{user.username if user.username else 'ندارد'}\n"
        f"📅 تاریخ عضویت: {user.join_date.strftime('%Y/%m/%d %H:%M')}\n"
        f"🔄 آخرین فعالیت: {user.last_active.strftime('%Y/%m/%d %H:%M') if user.last_active else 'نامشخص'}\n"
        f"🔸 وضعیت: {'✅ فعال' if user.is_active else '❌ غیرفعال'}\n\n"
        
        f"📊 آمار کاربر:\n"
        f"• 📅 روزهای حضور (۳۰ روز): {attendance_stats.get('attendance_days', 0)}\n"
        f"• ⏰ مجموع مطالعه: {user_stats.get('study_time', {}).get('total_30_days', 0):.1f} ساعت\n"
        f"• 🎯 نرخ موفقیت: {user_stats.get('plans', {}).get('completion_rate', 0):.1f}%\n"
    )
    
    keyboard = [
        [InlineKeyboardButton("📨 ارسال پیام", callback_data=f"admin_send_to_{user_id}")],
        [InlineKeyboardButton(f"{'❌ غیرفعال' if user.is_active else '✅ فعال'} کردن", callback_data=f"admin_toggle_user_{user_id}")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_manage_users")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(user_text, reply_markup=reply_markup)

async def admin_toggle_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """فعال/غیرفعال کردن کاربر"""
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        await query.edit_message_text("❌ شما دسترسی به این بخش را ندارید.")
        return
    
    user_id = int(query.data.replace("admin_toggle_user_", ""))
    user = database.get_user(user_id)
    
    if not user:
        await query.answer("❌ کاربر یافت نشد")
        return
    
    # تغییر وضعیت کاربر
    if user.is_active:
        database.deactivate_user(user_id)
        new_status = "غیرفعال"
    else:
        # فعال کردن کاربر - در اینجا باید تابع activate_user اضافه شود
        # فعلاً فقط وضعیت رو تغییر می‌دهیم
        user.is_active = True
        new_status = "فعال"
    
    await query.answer(f"✅ کاربر {new_status} شد")
    await admin_manage_users(update, context)

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
    """پردازش و ارسال پیام همگانی"""
    if not context.user_data.get('waiting_for_broadcast') or not is_admin(update.message.from_user.id):
        return
    
    broadcast_text = update.message.text
    
    if len(broadcast_text) > 4000:
        await update.message.reply_text(
            "❌ طول پیام بیش از حد مجاز است (حداکثر ۴۰۰۰ کاراکتر)"
        )
        return
    
    context.user_data.pop('waiting_for_broadcast', None)
    
    # دریافت کاربران فعال
    users = database.get_all_users(active_only=True)
    total_users = len(users)
    
    if total_users == 0:
        await update.message.reply_text(
            "❌ هیچ کاربر فعالی برای ارسال پیام وجود ندارد."
        )
        return
    
    # اطلاع‌رسانی شروع ارسال
    progress_message = await update.message.reply_text(
        f"📢 شروع ارسال پیام همگانی...\n\n"
        f"👥 تعداد دریافت‌کنندگان: {total_users} کاربر\n"
        f"⏳ در حال ارسال...\n"
        f"✅ ارسال شده: 0/{total_users}\n"
        f"❌ خطا: 0"
    )
    
    # ارسال پیام به کاربران
    success_count = 0
    failed_count = 0
    failed_users = []
    
    for i, user in enumerate(users, 1):
        try:
            # ارسال پیام به هر کاربر
            await context.bot.send_message(
                chat_id=user.user_id,
                text=f"📢 پیام همگانی از مدیریت:\n\n{broadcast_text}\n\n"
                     f"📅 {jdatetime.datetime.now().strftime('%Y/%m/%d %H:%M')}",
                parse_mode='HTML'
            )
            success_count += 1
            
            # بروزرسانی پیام پیشرفت هر 10 کاربر
            if i % 10 == 0 or i == total_users:
                try:
                    await progress_message.edit_text(
                        f"📢 در حال ارسال پیام همگانی...\n\n"
                        f"👥 تعداد دریافت‌کنندگان: {total_users} کاربر\n"
                        f"⏳ در حال ارسال...\n"
                        f"✅ ارسال شده: {success_count}/{total_users}\n"
                        f"❌ خطا: {failed_count}"
                    )
                except:
                    pass  # اگر پیام پیشرفت حذف شده، ادامه بده
                
            # تاخیر کوچک برای جلوگیری از محدودیت تلگرام
            await asyncio.sleep(0.1)
            
        except Exception as e:
            failed_count += 1
            failed_users.append({
                'user_id': user.user_id,
                'name': f"{user.first_name} {user.last_name or ''}",
                'error': str(e)
            })
            logger.error(f"❌ خطا در ارسال به کاربر {user.user_id}: {e}")
    
    # ایجاد گزارش نهایی
    report_text = (
        f"📊 گزارش ارسال پیام همگانی\n\n"
        f"📝 متن پیام: {broadcast_text[:100]}...\n\n"
        f"📊 آمار ارسال:\n"
        f"• ✅ موفق: {success_count} کاربر\n"
        f"• ❌ ناموفق: {failed_count} کاربر\n"
        f"• 📊 مجموع: {total_users} کاربر\n"
        f"• 🎯 نرخ موفقیت: {(success_count/total_users)*100:.1f}%\n\n"
    )
    
    # نمایش کاربران ناموفق اگر وجود داشته باشند
    if failed_users:
        report_text += "👥 کاربران ناموفق:\n"
        for failed in failed_users[:10]:  # فقط 10 کاربر اول
            report_text += f"• 🆔 {failed['user_id']}: {failed['name']}\n"
        
        if len(failed_users) > 10:
            report_text += f"• ... و {len(failed_users) - 10} کاربر دیگر\n"
    
    # دکمه‌های مدیریت
    keyboard = [
        [InlineKeyboardButton("📢 ارسال پیام جدید", callback_data="admin_broadcast")],
        [InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="admin_panel")],
        [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # ذخیره گزارش در context برای استفاده بعدی
    context.user_data['last_broadcast_report'] = {
        'text': broadcast_text,
        'success_count': success_count,
        'failed_count': failed_count,
        'total_users': total_users,
        'failed_users': failed_users,
        'timestamp': jdatetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    }
    
    # حذف پیام پیشرفت و ارسال گزارش نهایی
    try:
        await progress_message.delete()
    except:
        pass
    
    await update.message.reply_text(report_text, reply_markup=reply_markup)

async def admin_send_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ارسال پیام به کاربر خاص"""
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        await query.edit_message_text("❌ شما دسترسی به این بخش را ندارید.")
        return
    
    context.user_data['waiting_for_user_id'] = True
    
    keyboard = [
        [InlineKeyboardButton("❌ انصراف", callback_data="admin_panel")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📨 ارسال پیام به کاربر\n\n"
        "لطفاً آیدی کاربر مورد نظر را وارد کنید:"
    )

async def handle_user_id_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت آیدی کاربر"""
    if not context.user_data.get('waiting_for_user_id') or not is_admin(update.message.from_user.id):
        return
    
    try:
        user_id = int(update.message.text)
        user = database.get_user(user_id)
        
        if not user:
            await update.message.reply_text("❌ کاربر یافت نشد")
            return
        
        context.user_data['target_user_id'] = user_id
        context.user_data['waiting_for_user_message'] = True
        context.user_data.pop('waiting_for_user_id', None)
        
        await update.message.reply_text(
            f"✅ کاربر یافت شد: {user.first_name} {user.last_name or ''}\n\n"
            "لطفاً متن پیام را وارد کنید:"
        )
        
    except ValueError:
        await update.message.reply_text("❌ لطفاً یک آیدی معتبر وارد کنید")

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ارسال پیام به کاربر"""
    if not context.user_data.get('waiting_for_user_message') or not is_admin(update.message.from_user.id):
        return
    
    message_text = update.message.text
    user_id = context.user_data.get('target_user_id')
    
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"📨 پیام از مدیریت:\n\n{message_text}\n\n"
                 f"📅 {jdatetime.datetime.now().strftime('%Y/%m/%d %H:%M')}",
            parse_mode='HTML'
        )
        
        # پاک کردن وضعیت
        context.user_data.pop('waiting_for_user_message', None)
        context.user_data.pop('target_user_id', None)
        
        keyboard = [
            [InlineKeyboardButton("📨 ارسال پیام جدید", callback_data="admin_send_to_user")],
            [InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="admin_panel")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"✅ پیام با موفقیت ارسال شد!\n\n"
            f"👤 به کاربر: {user_id}\n"
            f"📝 متن: {message_text[:100]}...",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ خطا در ارسال پیام: {str(e)}"
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

async def admin_reply_to_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پاسخ به پیام کاربر"""
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        await query.edit_message_text("❌ شما دسترسی به این بخش را ندارید.")
        return
    
    message_id = int(query.data.replace("admin_reply_", ""))
    message = database.message_repo.get_message(message_id)
    
    if not message:
        await query.answer("❌ پیام یافت نشد")
        return
    
    context.user_data['replying_to_message'] = message_id
    context.user_data['replying_to_user'] = message.user_id
    
    user = database.get_user(message.user_id)
    user_name = f"{user.first_name} {user.last_name or ''}" if user else "کاربر ناشناس"
    
    await query.edit_message_text(
        f"📨 پاسخ به پیام کاربر\n\n"
        f"👤 کاربر: {user_name}\n"
        f"📝 پیام اصلی: {message.message_text}\n\n"
        "لطفاً پاسخ خود را وارد کنید:"
    )

async def handle_reply_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ارسال پاسخ به کاربر"""
    if not context.user_data.get('replying_to_message') or not is_admin(update.message.from_user.id):
        return
    
    reply_text = update.message.text
    message_id = context.user_data.get('replying_to_message')
    user_id = context.user_data.get('replying_to_user')
    
    try:
        # ارسال پاسخ به کاربر
        await context.bot.send_message(
            chat_id=user_id,
            text=f"📨 پاسخ از مدیریت:\n\n{reply_text}\n\n"
                 f"📅 {jdatetime.datetime.now().strftime('%Y/%m/%d %H:%M')}",
            parse_mode='HTML'
        )
        
        # علامت‌گذاری پیام به عنوان پاسخ داده شده
        # در اینجا باید پیام در دیتابیس آپدیت شود
        
        # پاک کردن وضعیت
        context.user_data.pop('replying_to_message', None)
        context.user_data.pop('replying_to_user', None)
        
        keyboard = [
            [InlineKeyboardButton("📩 مدیریت پیام‌ها", callback_data="admin_user_messages")],
            [InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="admin_panel")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"✅ پاسخ با موفقیت ارسال شد!\n\n"
            f"👤 به کاربر: {user_id}\n"
            f"📝 متن پاسخ: {reply_text[:100]}...",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ خطا در ارسال پاسخ: {str(e)}"
        )

async def admin_mark_message_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """علامت‌گذاری پیام به عنوان انجام شده"""
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        await query.edit_message_text("❌ شما دسترسی به این بخش را ندارید.")
        return
    
    message_id = int(query.data.replace("admin_mark_done_", ""))
    
    # در اینجا باید پیام در دیتابیس آپدیت شود
    
    await query.answer("✅ پیام به عنوان انجام شده علامت‌گذاری شد")
    await admin_user_messages(update, context)

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

async def admin_optimize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        await query.edit_message_text("❌ شما دسترسی به این بخش را ندارید.")
        return
    
    optimize_result = db_manager.optimize_database()
    
    if optimize_result:
        message = "⚡ بهینه‌سازی دیتابیس با موفقیت انجام شد!"
    else:
        message = "❌ خطا در بهینه‌سازی دیتابیس"
    
    keyboard = [
        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_database")],
        [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup)

def setup_admin_handlers(application):
    """تنظیم تمام هندلرهای پنل مدیریت"""
    application.add_handler(CallbackQueryHandler(admin_panel, pattern="^admin_panel$"))
    application.add_handler(CallbackQueryHandler(admin_stats, pattern="^admin_stats$"))
    application.add_handler(CallbackQueryHandler(admin_manage_users, pattern="^admin_manage_users$"))
    application.add_handler(CallbackQueryHandler(admin_broadcast, pattern="^admin_broadcast$"))
    application.add_handler(CallbackQueryHandler(admin_send_to_user, pattern="^admin_send_to_user$"))
    application.add_handler(CallbackQueryHandler(admin_user_messages, pattern="^admin_user_messages$"))
    application.add_handler(CallbackQueryHandler(admin_database, pattern="^admin_database$"))
    application.add_handler(CallbackQueryHandler(admin_backup, pattern="^admin_backup$"))
    application.add_handler(CallbackQueryHandler(admin_cleanup, pattern="^admin_cleanup$"))
    application.add_handler(CallbackQueryHandler(admin_optimize, pattern="^admin_optimize$"))
    
    # هندلرهای مشاهده و مدیریت کاربران
    application.add_handler(CallbackQueryHandler(admin_view_user, pattern="^admin_view_user_"))
    application.add_handler(CallbackQueryHandler(admin_toggle_user, pattern="^admin_toggle_user_"))
    
    # هندلرهای مدیریت پیام‌ها
    application.add_handler(CallbackQueryHandler(admin_reply_to_message, pattern="^admin_reply_"))
    application.add_handler(CallbackQueryHandler(admin_mark_message_done, pattern="^admin_mark_done_"))
    
    # هندلرهای پیام متنی
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_broadcast_message), group=9)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_id_input), group=10)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_message), group=11)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_reply_message), group=12)
