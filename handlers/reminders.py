from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters
from database.operations import database
import re

async def reminders_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_reminders = database.get_user_reminders(user_id, active_only=True)
    reminder_count = len(user_reminders)
    
    keyboard = [
        [InlineKeyboardButton("⏰ یادآوری کنکور", callback_data="exam_reminder")],
        [InlineKeyboardButton("📝 یادآوری متفرقه", callback_data="custom_reminder")],
        [InlineKeyboardButton("📚 یادآوری مطالعه و امتحان", callback_data="study_reminder")],
        [InlineKeyboardButton("📋 مدیریت یادآوری‌ها", callback_data="manage_reminders")],
        [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = (
        "🔔 مدیریت یادآوری‌ها\n\n"
        f"📊 شما {reminder_count} یادآوری فعال دارید.\n\n"
        "لطفاً نوع یادآوری مورد نظر خود را انتخاب کنید:"
    )
    
    await query.edit_message_text(message_text, reply_markup=reply_markup)

async def exam_reminder_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = []
    # ایجاد دکمه‌ها برای ساعات رند
    hours = [f"{i:02d}:00" for i in range(24)]
    for i in range(0, len(hours), 4):
        keyboard.append([InlineKeyboardButton(hours[j], callback_data=f"set_exam_reminder_{hours[j]}") for j in range(i, min(i+4, len(hours)))])
    
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="reminders")])
    keyboard.append([InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🎯 یادآوری کنکور\n\n"
        "با تنظیم این یادآوری، هر روز در ساعت مشخص شده:\n"
        "• ⏳ زمان باقی‌مانده تا کنکورها\n"
        "• 📊 نکات انگیزشی و برنامه‌ای\n"
        "• 💡 توصیه‌های مطالعاتی\n\n"
        "لطفاً ساعت یادآوری را انتخاب کنید (ساعات رند):",
        reply_markup=reply_markup
    )

async def set_exam_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    reminder_time = query.data.replace("set_exam_reminder_", "")
    user_id = query.from_user.id
    
    # اضافه کردن یادآوری برای کنکور
    reminder = database.add_reminder(
        user_id=user_id,
        reminder_type="exam",
        reminder_time=reminder_time,
        title="یادآوری کنکور",
        is_recurring=True
    )
    
    keyboard = [
        [InlineKeyboardButton("📋 مدیریت یادآوری‌ها", callback_data="manage_reminders")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="exam_reminder")],
        [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"✅ یادآوری کنکور با موفقیت تنظیم شد! 🎓\n\n"
        f"🕒 ساعت: {reminder_time}\n"
        f"📅 از این پس هر روز در این ساعت:\n"
        f"• ⏳ زمان باقی‌مانده تا کنکورها\n"
        f"• 📊 نکات انگیزشی دریافت می‌کنید\n"
        f"• 💡 توصیه‌های مطالعاتی روزانه\n\n"
        f"🆔 کد یادآوری: {reminder.id}",
        reply_markup=reply_markup
    )

async def custom_reminder_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = []
    hours = [f"{i:02d}:00" for i in range(24)]
    for i in range(0, len(hours), 4):
        keyboard.append([InlineKeyboardButton(hours[j], callback_data=f"custom_time_{hours[j]}") for j in range(i, min(i+4, len(hours)))])
    
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="reminders")])
    keyboard.append([InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    context.user_data['waiting_for_custom_message'] = True
    
    await query.edit_message_text(
        "📝 یادآوری متفرقه\n\n"
        "با این قابلیت می‌توانید:\n"
        "• 📅 یادآوری کارهای شخصی\n"
        "• ⏰ تنظیم زمان استراحت\n"
        "• 🔔 پیام‌های دلخواه خودتان\n\n"
        "لطفاً ابتدا ساعت یادآوری را انتخاب کنید:",
        reply_markup=reply_markup
    )

async def set_custom_reminder_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    reminder_time = query.data.replace("custom_time_", "")
    context.user_data['reminder_time'] = reminder_time
    
    await query.edit_message_text(
        f"🕒 ساعت {reminder_time} انتخاب شد.\n\n"
        "لطفاً متن یادآوری خود را ارسال کنید:\n"
        "مثال: 'وقت استراحت ☕' یا 'جلسه رفع اشکال 📚'"
    )

async def save_custom_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_for_custom_message'):
        message_text = update.message.text
        reminder_time = context.user_data.get('reminder_time')
        user_id = update.message.from_user.id
        
        # ذخیره یادآوری در دیتابیس
        reminder = database.add_reminder(
            user_id=user_id,
            reminder_type="custom",
            reminder_time=reminder_time,
            title="یادآوری متفرقه",
            custom_message=message_text,
            is_recurring=True
        )
        
        # پاک کردن وضعیت
        context.user_data.pop('waiting_for_custom_message', None)
        context.user_data.pop('reminder_time', None)
        
        keyboard = [
            [InlineKeyboardButton("📋 مدیریت یادآوری‌ها", callback_data="manage_reminders")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="custom_reminder")],
            [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"✅ یادآوری متفرقه با موفقیت تنظیم شد! 🔔\n\n"
            f"🕒 ساعت: {reminder_time}\n"
            f"📝 متن: {message_text}\n"
            f"🆔 کد یادآوری: {reminder.id}\n\n"
            "یادآوری هر روز در ساعت مشخص شده برای شما ارسال می‌شود.",
            reply_markup=reply_markup
        )

async def study_reminder_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = []
    hours = [f"{i:02d}:00" for i in range(24)]
    for i in range(0, len(hours), 4):
        keyboard.append([InlineKeyboardButton(hours[j], callback_data=f"study_time_{hours[j]}") for j in range(i, min(i+4, len(hours)))])
    
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="reminders")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    context.user_data['waiting_for_study_reminder'] = True
    
    await query.edit_message_text(
        "📚 یادآوری مطالعه و امتحان\n\n"
        "با این قابلیت می‌توانید:\n"
        "• 📖 یادآوری شروع جلسه مطالعه\n"
        "• 🎯 یادآوری مرور دروس\n"
        "• 📝 یادآوری آزمون‌های آزمایشی\n\n"
        "لطفاً ساعت یادآوری را انتخاب کنید:",
        reply_markup=reply_markup
    )

async def set_study_reminder_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    reminder_time = query.data.replace("study_time_", "")
    context.user_data['study_reminder_time'] = reminder_time
    context.user_data['waiting_for_study_subject'] = True
    
    await query.edit_message_text(
        f"🕒 ساعت {reminder_time} انتخاب شد.\n\n"
        "لطفاً عنوان درس یا موضوع مطالعه را وارد کنید:\n"
        "مثال: 'ریاضی' یا 'مرور زیست شناسی'"
    )

async def save_study_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_for_study_subject'):
        subject = update.message.text
        reminder_time = context.user_data.get('study_reminder_time')
        user_id = update.message.from_user.id
        
        # ذخیره یادآوری مطالعه در دیتابیس
        reminder = database.add_reminder(
            user_id=user_id,
            reminder_type="study",
            reminder_time=reminder_time,
            title="یادآوری مطالعه",
            custom_message=f"وقت مطالعه {subject} 📚",
            is_recurring=True
        )
        
        # پاک کردن وضعیت
        context.user_data.pop('waiting_for_study_reminder', None)
        context.user_data.pop('study_reminder_time', None)
        context.user_data.pop('waiting_for_study_subject', None)
        
        keyboard = [
            [InlineKeyboardButton("📋 مدیریت یادآوری‌ها", callback_data="manage_reminders")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="study_reminder")],
            [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"✅ یادآوری مطالعه با موفقیت تنظیم شد! 📖\n\n"
            f"🕒 ساعت: {reminder_time}\n"
            f"📚 موضوع: {subject}\n"
            f"🆔 کد یادآوری: {reminder.id}\n\n"
            "یادآوری هر روز در ساعت مشخص شده برای شما ارسال می‌شود.",
            reply_markup=reply_markup
        )

async def manage_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    reminders = database.get_user_reminders(user_id)
    
    if not reminders:
        keyboard = [
            [InlineKeyboardButton("⏰ افزودن یادآوری", callback_data="reminders")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="reminders")],
            [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "ℹ️ شما هیچ یادآوری فعالی ندارید.\n\n"
            "می‌توانید با افزودن یادآوری جدید شروع کنید!",
            reply_markup=reply_markup
        )
        return
    
    message_text = "📋 یادآوری‌های شما:\n\n"
    keyboard = []
    
    for reminder in reminders[:10]:  # فقط ۱۰ یادآوری اول
        status = "✅ فعال" if reminder.is_active else "❌ غیرفعال"
        
        if reminder.reminder_type == "exam":
            reminder_info = "⏰ یادآوری کنکور"
        elif reminder.reminder_type == "custom":
            reminder_info = f"📝 {reminder.custom_message[:20]}..."
        elif reminder.reminder_type == "study":
            reminder_info = f"📚 {reminder.custom_message[:20]}..."
        else:
            reminder_info = "🔔 یادآوری"
        
        message_text += f"{reminder_info}\n"
        message_text += f"🕒 {reminder.reminder_time} - {status}\n"
        message_text += f"🆔 کد: {reminder.id}\n\n"
        
        # دکمه‌های مدیریت برای هر یادآوری
        keyboard.append([
            InlineKeyboardButton(f"❌ حذف {reminder.id}", callback_data=f"delete_reminder_{reminder.id}"),
            InlineKeyboardButton(f"🔁 {'غیرفعال' if reminder.is_active else 'فعال'} {reminder.id}", callback_data=f"toggle_reminder_{reminder.id}")
        ])
    
    keyboard.append([InlineKeyboardButton("⏰ افزودن یادآوری جدید", callback_data="reminders")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="reminders")])
    keyboard.append([InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message_text, reply_markup=reply_markup)

async def delete_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    reminder_id = int(query.data.replace("delete_reminder_", ""))
    
    success = database.delete_reminder(reminder_id)
    
    if success:
        await query.answer("✅ یادآوری حذف شد")
    else:
        await query.answer("❌ خطا در حذف یادآوری")
    
    # بازگشت به مدیریت یادآوری‌ها
    await manage_reminders(update, context)

async def toggle_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    reminder_id = int(query.data.replace("toggle_reminder_", ""))
    
    new_status = database.toggle_reminder(reminder_id)
    
    status_text = "فعال" if new_status else "غیرفعال"
    await query.answer(f"✅ یادآوری {status_text} شد")
    
    # بازگشت به مدیریت یادآوری‌ها
    await manage_reminders(update, context)

def setup_reminders_handlers(application):
    application.add_handler(CallbackQueryHandler(reminders_menu, pattern="^reminders$"))
    application.add_handler(CallbackQueryHandler(exam_reminder_menu, pattern="^exam_reminder$"))
    application.add_handler(CallbackQueryHandler(custom_reminder_menu, pattern="^custom_reminder$"))
    application.add_handler(CallbackQueryHandler(study_reminder_menu, pattern="^study_reminder$"))
    application.add_handler(CallbackQueryHandler(set_exam_reminder, pattern="^set_exam_reminder_"))
    application.add_handler(CallbackQueryHandler(set_custom_reminder_time, pattern="^custom_time_"))
    application.add_handler(CallbackQueryHandler(set_study_reminder_time, pattern="^study_time_"))
    application.add_handler(CallbackQueryHandler(manage_reminders, pattern="^manage_reminders$"))
    application.add_handler(CallbackQueryHandler(delete_reminder, pattern="^delete_reminder_"))
    application.add_handler(CallbackQueryHandler(toggle_reminder, pattern="^toggle_reminder_"))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_custom_reminder), group=5)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_study_reminder), group=6)
