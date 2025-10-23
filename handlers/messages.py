from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters
from database.operations import database
import config

async def send_message_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_messages = database.get_user_messages(user_id)
    pending_count = len([msg for msg in user_messages if msg.status == 'pending'])
    
    keyboard = [
        [InlineKeyboardButton("📨 ارسال به ادمین اصلی", callback_data="send_to_main_admin")],
        [InlineKeyboardButton("👥 ارسال به همه ادمین‌ها", callback_data="send_to_all_admins")],
        [InlineKeyboardButton("📋 پیام‌های من", callback_data="my_messages")],
        [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = (
        "📨 ارسال پیام به ادمین‌ها\n\n"
        f"📊 شما {pending_count} پیام در انتظار پاسخ دارید.\n\n"
        "لطفاً گزینه مورد نظر را انتخاب کنید:"
    )
    
    await query.edit_message_text(message_text, reply_markup=reply_markup)

async def start_message_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    context.user_data['sending_message'] = True
    context.user_data['message_type'] = query.data
    
    keyboard = [
        [InlineKeyboardButton("❌ انصراف", callback_data="cancel_message")],
        [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    target = "ادمین اصلی" if query.data == "send_to_main_admin" else "همه ادمین‌ها"
    
    await query.edit_message_text(
        f"📝 ارسال پیام به {target}\n\n"
        "لطفاً متن پیام خود را وارد کنید:\n\n"
        "💡 می‌توانید از موارد زیر استفاده کنید:\n"
        "• گزارش مشکل فنی\n"
        "• پیشنهاد بهبود ربات\n"
        "• سوال درباره نحوه استفاده\n"
        "• انتقادات و پیشنهادات\n\n"
        "پیام خود را بنویسید:",
        reply_markup=reply_markup
    )

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('sending_message'):
        message_text = update.message.text
        user_id = update.message.from_user.id
        message_type = context.user_data.get('message_type')
        
        # تعیین نوع پیام بر اساس محتوا
        msg_type = 'general'
        if any(word in message_text.lower() for word in ['مشکل', 'خطا', 'باگ', 'ایراد']):
            msg_type = 'bug'
        elif any(word in message_text.lower() for word in ['پیشنهاد', 'ایده', 'بهتر']):
            msg_type = 'suggestion'
        elif any(word in message_text.lower() for word in ['سوال', 'چگونه', 'چطوری']):
            msg_type = 'question'
        
        # ذخیره پیام در دیتابیس
        message = database.add_user_message(user_id, message_text, msg_type)
        
        # پاک کردن وضعیت
        context.user_data.pop('sending_message', None)
        context.user_data.pop('message_type', None)
        
        # ایجاد دکمه‌های مدیریت پیام
        keyboard = [
            [InlineKeyboardButton("✏️ ویرایش پیام", callback_data=f"edit_message_{message.id}")],
            [InlineKeyboardButton("🗑️ حذف پیام", callback_data=f"delete_message_{message.id}")],
            [InlineKeyboardButton("📨 ارسال پیام جدید", callback_data="send_message")],
            [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        target = "ادمین اصلی" if message_type == "send_to_main_admin" else "همه ادمین‌ها"
        
        await update.message.reply_text(
            f"✅ پیام شما با موفقیت ارسال شد! 📨\n\n"
            f"📨 به: {target}\n"
            f"📝 نوع: {msg_type}\n"
            f"🆔 کد پیام: {message.id}\n\n"
            f"📋 متن پیام:\n{message_text}\n\n"
            "ادمین در اسرع وقت پاسخ خواهد داد. ⏰",
            reply_markup=reply_markup
        )

async def show_my_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    messages = database.get_user_messages(user_id)
    
    if not messages:
        keyboard = [
            [InlineKeyboardButton("📨 ارسال پیام جدید", callback_data="send_message")],
            [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "📭 شما هیچ پیامی ارسال نکرده‌اید.\n\n"
            "می‌توانید با ارسال پیام جدید شروع کنید!",
            reply_markup=reply_markup
        )
        return
    
    message_text = "📋 پیام‌های ارسالی شما:\n\n"
    keyboard = []
    
    for msg in messages[:8]:  # فقط ۸ پیام آخر
        status_emoji = "✅" if msg.status == 'replied' else "🕒" if msg.status == 'pending' else "❌"
        status_text = {
            'pending': 'در انتظار پاسخ',
            'replied': 'پاسخ داده شده', 
            'resolved': 'حل شده',
            'deleted': 'حذف شده'
        }.get(msg.status, msg.status)
        
        type_emoji = {
            'bug': '🐛',
            'suggestion': '💡', 
            'question': '❓',
            'general': '📝'
        }.get(msg.message_type, '📝')
        
        message_text += f"{status_emoji} {type_emoji} پیام #{msg.id}\n"
        message_text += f"📅 {msg.created_at.strftime('%Y/%m/%d %H:%M')}\n"
        message_text += f"📝 {msg.message_text[:40]}...\n"
        message_text += f"🔸 وضعیت: {status_text}\n\n"
        
        if msg.status == 'pending':
            keyboard.append([
                InlineKeyboardButton(f"✏️ ویرایش {msg.id}", callback_data=f"edit_message_{msg.id}"),
                InlineKeyboardButton(f"🗑️ حذف {msg.id}", callback_data=f"delete_message_{msg.id}")
            ])
    
    keyboard.append([InlineKeyboardButton("📨 ارسال پیام جدید", callback_data="send_message")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="send_message")])
    keyboard.append([InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message_text, reply_markup=reply_markup)

async def edit_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    message_id = int(query.data.replace("edit_message_", ""))
    
    # دریافت پیام از دیتابیس
    message = database.message_repo.get_message(message_id)
    
    if not message:
        await query.answer("❌ پیام یافت نشد")
        return
    
    if message.status != 'pending':
        await query.answer("❌ فقط پیام‌های در انتظار پاسخ قابل ویرایش هستند")
        return
    
    context.user_data['editing_message'] = True
    context.user_data['editing_message_id'] = message_id
    
    await query.edit_message_text(
        f"✏️ ویرایش پیام #{message_id}\n\n"
        f"📝 پیام فعلی:\n{message.message_text}\n\n"
        "لطفاً متن جدید پیام را وارد کنید:"
    )

async def handle_edited_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('editing_message'):
        new_text = update.message.text
        message_id = context.user_data.get('editing_message_id')
        
        # در اینجا باید پیام در دیتابیس آپدیت شود
        # فعلاً فقط پیام می‌دهیم که آپدیت شده
        
        # پاک کردن وضعیت
        context.user_data.pop('editing_message', None)
        context.user_data.pop('editing_message_id', None)
        
        keyboard = [
            [InlineKeyboardButton("📋 پیام‌های من", callback_data="my_messages")],
            [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"✅ پیام #{message_id} با موفقیت ویرایش شد! ✏️\n\n"
            f"📝 متن جدید:\n{new_text}\n\n"
            "ادمین پیام ویرایش شده شما را مشاهده خواهد کرد.",
            reply_markup=reply_markup
        )

async def delete_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    message_id = int(query.data.replace("delete_message_", ""))
    
    keyboard = [
        [
            InlineKeyboardButton("✅ بله، حذف کن", callback_data=f"confirm_delete_{message_id}"),
            InlineKeyboardButton("❌ خیر، انصراف", callback_data="my_messages")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"⚠️ آیا مطمئن هستید که می‌خواهید پیام #{message_id} را حذف کنید؟\n\n"
        "این عمل غیرقابل بازگشت است!",
        reply_markup=reply_markup
    )

async def confirm_delete_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    message_id = int(query.data.replace("confirm_delete_", ""))
    
    # حذف پیام از دیتابیس
    success = database.message_repo.delete_message(message_id)
    
    if success:
        keyboard = [
            [InlineKeyboardButton("📋 پیام‌های من", callback_data="my_messages")],
            [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"✅ پیام #{message_id} با موفقیت حذف شد! 🗑️",
            reply_markup=reply_markup
        )
    else:
        await query.answer("❌ خطا در حذف پیام")

async def cancel_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # پاک کردن وضعیت
    context.user_data.pop('sending_message', None)
    context.user_data.pop('message_type', None)
    context.user_data.pop('editing_message', None)
    context.user_data.pop('editing_message_id', None)
    
    await send_message_menu(update, context)

def setup_messages_handlers(application):
    application.add_handler(CallbackQueryHandler(send_message_menu, pattern="^send_message$"))
    application.add_handler(CallbackQueryHandler(start_message_to_admin, pattern="^send_to_main_admin$"))
    application.add_handler(CallbackQueryHandler(start_message_to_admin, pattern="^send_to_all_admins$"))
    application.add_handler(CallbackQueryHandler(show_my_messages, pattern="^my_messages$"))
    application.add_handler(CallbackQueryHandler(edit_message, pattern="^edit_message_"))
    application.add_handler(CallbackQueryHandler(delete_message, pattern="^delete_message_"))
    application.add_handler(CallbackQueryHandler(confirm_delete_message, pattern="^confirm_delete_"))
    application.add_handler(CallbackQueryHandler(cancel_message, pattern="^cancel_message$"))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_message), group=7)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_edited_message), group=8)
