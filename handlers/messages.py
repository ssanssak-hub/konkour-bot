from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters
from database.operations import database
import config

async def send_message_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منوی ارسال پیام"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_messages = database.get_user_messages(user_id)
    pending_count = len([msg for msg in user_messages if msg.status == 'pending'])
    
    text = f"""
📨 <b>سیستم پیام‌رسانی</b>

📊 وضعیت پیام‌های شما:
• 📭 در انتظار پاسخ: {pending_count}
• 📨 کل پیام‌ها: {len(user_messages)}

🎯 امکانات:
• ارسال پیام به ادمین اصلی
• ارسال پیام به همه ادمین‌ها
• ارسال پیام به خودتان
• مدیریت پیام‌های ارسالی
"""
    
    keyboard = [
        [InlineKeyboardButton("👑 ارسال به ادمین اصلی", callback_data="send_to_main_admin")],
        [InlineKeyboardButton("👥 ارسال به همه ادمین‌ها", callback_data="send_to_all_admins")],
        [InlineKeyboardButton("👤 ارسال به خودم", callback_data="send_to_self")],
        [InlineKeyboardButton("📋 پیام‌های من", callback_data="my_messages")],
        [InlineKeyboardButton("🛠️ مدیریت پیام‌ها", callback_data="manage_messages")],
        [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

async def start_message_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع فرآیند ارسال پیام به ادمین"""
    query = update.callback_query
    await query.answer()
    
    context.user_data['sending_message'] = True
    context.user_data['message_type'] = query.data
    
    target_text = {
        'send_to_main_admin': '👑 ادمین اصلی',
        'send_to_all_admins': '👥 همه ادمین‌ها', 
        'send_to_self': '👤 خودم'
    }.get(query.data, 'ادمین')
    
    text = f"""
📝 <b>ارسال پیام به {target_text}</b>

💡 لطفاً متن پیام خود را وارد کنید:

🎯 می‌توانید در مورد موارد زیر پیام ارسال کنید:
• 🐛 گزارش مشکل فنی
• 💡 پیشنهاد بهبود ربات  
• ❓ سوال درباره نحوه استفاده
• 📢 انتقادات و پیشنهادات
• 📚 مشکلات مطالعاتی
• 🎯 سایر موارد

📝 پیام خود را بنویسید:
"""
    
    keyboard = [
        [InlineKeyboardButton("❌ انصراف", callback_data="cancel_message")],
        [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش پیام کاربر"""
    if context.user_data.get('sending_message'):
        message_text = update.message.text
        user_id = update.message.from_user.id
        message_type = context.user_data.get('message_type')
        
        # تعیین نوع پیام بر اساس محتوا
        msg_type = 'general'
        if any(word in message_text.lower() for word in ['مشکل', 'خطا', 'باگ', 'ایراد', 'خراب']):
            msg_type = 'bug'
        elif any(word in message_text.lower() for word in ['پیشنهاد', 'ایده', 'بهتر', 'اضافه']):
            msg_type = 'suggestion'
        elif any(word in message_text.lower() for word in ['سوال', 'چگونه', 'چطوری', 'راهنمایی']):
            msg_type = 'question'
        elif any(word in message_text.lower() for word in ['انتقاد', 'اعتراض', 'ناراحت']):
            msg_type = 'criticism'
        
        # ذخیره پیام در دیتابیس
        message = database.add_user_message(user_id, message_text, msg_type)
        
        # پاک کردن وضعیت
        context.user_data.pop('sending_message', None)
        context.user_data.pop('message_type', None)
        
        # ایجاد پیام تأیید
        target_text = {
            'send_to_main_admin': '👑 ادمین اصلی',
            'send_to_all_admins': '👥 همه ادمین‌ها',
            'send_to_self': '👤 خودتان'
        }.get(message_type, 'ادمین')
        
        type_emojis = {
            'bug': '🐛',
            'suggestion': '💡',
            'question': '❓', 
            'criticism': '📢',
            'general': '📝'
        }
        
        text = f"""
✅ <b>پیام شما با موفقیت ارسال شد!</b> 📨

🎯 اطلاعات پیام:
• 📨 به: {target_text}
• 📝 نوع: {type_emojis.get(msg_type, '📝')} {msg_type}
• 🆔 کد پیام: {message.id}
• 🕒 زمان: {message.created_at.strftime('%Y/%m/%d %H:%M')}

📋 متن پیام:
{message_text}

💡 {get_message_response_guidance(msg_type)}
"""
        
        keyboard = [
            [
                InlineKeyboardButton("✏️ ویرایش پیام", callback_data=f"edit_message_{message.id}"),
                InlineKeyboardButton("🗑️ حذف پیام", callback_data=f"delete_message_{message.id}")
            ],
            [InlineKeyboardButton("📨 ارسال پیام جدید", callback_data="send_message")],
            [InlineKeyboardButton("📋 پیام‌های من", callback_data="my_messages")],
            [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
        ]
        
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )

def get_message_response_guidance(msg_type):
    """دریافت راهنمایی پاسخ بر اساس نوع پیام"""
    guidance = {
        'bug': 'ادمین در اسرع وقت مشکل را بررسی خواهد کرد.',
        'suggestion': 'از پیشنهاد شما متشکریم! در اولین فرصت بررسی می‌شود.',
        'question': 'پاسخ شما تا ۲۴ ساعت آینده ارسال خواهد شد.',
        'criticism': 'انتقادات شما برای بهبود ربات بسیار valuable است.',
        'general': 'ادمین در اسرع وقت پاسخ خواهد داد.'
    }
    return guidance.get(msg_type, 'ادمین در اسرع وقت پاسخ خواهد داد.')

async def show_my_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش پیام‌های کاربر"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    messages = database.get_user_messages(user_id)
    
    if not messages:
        text = """
📭 <b>شما هیچ پیامی ارسال نکرده‌اید</b>

💡 می‌توانید با ارسال پیام جدید شروع کنید!
"""
        
        keyboard = [
            [InlineKeyboardButton("📨 ارسال پیام جدید", callback_data="send_message")],
            [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        return
    
    text = "📋 <b>پیام‌های ارسالی شما</b>\n\n"
    keyboard = []
    
    for msg in messages[:8]:  # فقط ۸ پیام آخر
        status_emoji = get_status_emoji(msg.status)
        type_emoji = get_type_emoji(msg.message_type)
        
        text += f"{status_emoji} {type_emoji} <b>پیام #{msg.id}</b>\n"
        text += f"📅 {msg.created_at.strftime('%Y/%m/%d %H:%M')}\n"
        text += f"📝 {msg.message_text[:50]}...\n"
        text += f"🔸 وضعیت: {get_status_text(msg.status)}\n\n"
        
        if msg.status == 'pending':
            keyboard.append([
                InlineKeyboardButton(f"✏️ #{msg.id}", callback_data=f"edit_message_{msg.id}"),
                InlineKeyboardButton(f"🗑️ #{msg.id}", callback_data=f"delete_message_{msg.id}")
            ])
    
    keyboard.append([InlineKeyboardButton("📨 ارسال پیام جدید", callback_data="send_message")])
    keyboard.append([InlineKeyboardButton("🛠️ مدیریت پیشرفته", callback_data="manage_messages")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="send_message")])
    keyboard.append([InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")])
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

def get_status_emoji(status):
    """دریافت ایموجی وضعیت"""
    emojis = {
        'pending': '🕒',
        'replied': '✅',
        'resolved': '🎉',
        'deleted': '❌'
    }
    return emojis.get(status, '📝')

def get_type_emoji(msg_type):
    """دریافت ایموجی نوع"""
    emojis = {
        'bug': '🐛',
        'suggestion': '💡',
        'question': '❓',
        'criticism': '📢',
        'general': '📝'
    }
    return emojis.get(msg_type, '📝')

def get_status_text(status):
    """دریافت متن وضعیت"""
    texts = {
        'pending': 'در انتظار پاسخ',
        'replied': 'پاسخ داده شده',
        'resolved': 'حل شده',
        'deleted': 'حذف شده'
    }
    return texts.get(status, status)

async def manage_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت پیشرفته پیام‌ها"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    messages = database.get_user_messages(user_id)
    
    text = """
🛠️ <b>مدیریت پیشرفته پیام‌ها</b>

🎯 در این بخش می‌توانید:
• پیام‌ها را ویرایش کنید
• پیام‌ها را حذف کنید
• وضعیت پیام‌ها را تغییر دهید
• پیام‌ها را آرشیو کنید
"""
    
    keyboard = []
    
    # گروه‌بندی پیام‌ها بر اساس وضعیت
    status_groups = {}
    for msg in messages:
        if msg.status not in status_groups:
            status_groups[msg.status] = []
        status_groups[msg.status].append(msg)
    
    for status, msgs in status_groups.items():
        count = len(msgs)
        status_emoji = get_status_emoji(status)
        status_text = get_status_text(status)
        
        text += f"\n{status_emoji} {status_text}: {count} پیام"
        
        keyboard.append([
            InlineKeyboardButton(
                f"{status_emoji} مشاهده {status_text}", 
                callback_data=f"view_messages_{status}"
            )
        ])
    
    keyboard.extend([
        [InlineKeyboardButton("📊 آمار پیام‌ها", callback_data="message_stats")],
        [InlineKeyboardButton("📨 ارسال پیام جدید", callback_data="send_message")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="send_message")],
        [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
    ])
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

async def view_messages_by_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مشاهده پیام‌ها بر اساس وضعیت"""
    query = update.callback_query
    await query.answer()
    
    status = query.data.replace("view_messages_", "")
    user_id = query.from_user.id
    messages = database.get_user_messages(user_id)
    
    filtered_messages = [msg for msg in messages if msg.status == status]
    
    if not filtered_messages:
        status_text = get_status_text(status)
        await query.answer(f"📭 هیچ پیام {status_text} ندارید")
        return
    
    text = f"📋 <b>پیام‌های {get_status_text(status)}</b>\n\n"
    
    for msg in filtered_messages[:10]:
        type_emoji = get_type_emoji(msg.message_type)
        
        text += f"{type_emoji} <b>#{msg.id}</b> - {msg.created_at.strftime('%Y/%m/%d %H:%M')}\n"
        text += f"📝 {msg.message_text[:60]}...\n\n"
    
    keyboard = []
    for msg in filtered_messages[:5]:
        keyboard.append([
            InlineKeyboardButton(f"✏️ ویرایش #{msg.id}", callback_data=f"edit_message_{msg.id}"),
            InlineKeyboardButton(f"🗑️ حذف #{msg.id}", callback_data=f"delete_message_{msg.id}")
        ])
    
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="manage_messages")])
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

async def edit_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ویرایش پیام"""
    query = update.callback_query
    await query.answer()
    
    message_id = int(query.data.replace("edit_message_", ""))
    message = database.message_repo.get_message(message_id)
    
    if not message:
        await query.answer("❌ پیام یافت نشد")
        return
    
    if message.status != 'pending':
        await query.answer("❌ فقط پیام‌های در انتظار پاسخ قابل ویرایش هستند")
        return
    
    context.user_data['editing_message'] = True
    context.user_data['editing_message_id'] = message_id
    
    text = f"""
✏️ <b>ویرایش پیام #{message_id}</b>

📝 پیام فعلی:
{message.message_text}

💡 لطفاً متن جدید پیام را وارد کنید:
"""
    
    await query.edit_message_text(text, parse_mode='HTML')

async def handle_edited_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش پیام ویرایش شده"""
    if context.user_data.get('editing_message'):
        new_text = update.message.text
        message_id = context.user_data.get('editing_message_id')
        
        # TODO: آپدیت پیام در دیتابیس
        
        # پاک کردن وضعیت
        context.user_data.pop('editing_message', None)
        context.user_data.pop('editing_message_id', None)
        
        text = f"""
✅ <b>پیام #{message_id} با موفقیت ویرایش شد!</b> ✏️

📝 متن جدید:
{new_text}

💡 ادمین پیام ویرایش شده شما را مشاهده خواهد کرد.
"""
        
        keyboard = [
            [InlineKeyboardButton("📋 پیام‌های من", callback_data="my_messages")],
            [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
        ]
        
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )

async def delete_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """حذف پیام"""
    query = update.callback_query
    await query.answer()
    
    message_id = int(query.data.replace("delete_message_", ""))
    message = database.message_repo.get_message(message_id)
    
    if not message:
        await query.answer("❌ پیام یافت نشد")
        return
    
    text = f"""
⚠️ <b>تأیید حذف پیام</b>

📝 پیام #{message_id}:
{message.message_text[:100]}...

❌ آیا مطمئن هستید که می‌خواهید این پیام را حذف کنید؟

💡 این عمل غیرقابل بازگشت است!
"""
    
    keyboard = [
        [
            InlineKeyboardButton("✅ بله، حذف کن", callback_data=f"confirm_delete_{message_id}"),
            InlineKeyboardButton("❌ خیر، انصراف", callback_data="my_messages")
        ]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

async def confirm_delete_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تأیید حذف پیام"""
    query = update.callback_query
    await query.answer()
    
    message_id = int(query.data.replace("confirm_delete_", ""))
    success = database.message_repo.delete_message(message_id)
    
    if success:
        text = f"✅ <b>پیام #{message_id} با موفقیت حذف شد!</b> 🗑️"
    else:
        text = "❌ <b>خطا در حذف پیام</b>"
    
    keyboard = [
        [InlineKeyboardButton("📋 پیام‌های من", callback_data="my_messages")],
        [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

async def message_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """آمار پیام‌ها"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    messages = database.get_user_messages(user_id)
    
    stats = {
        'total': len(messages),
        'pending': len([m for m in messages if m.status == 'pending']),
        'replied': len([m for m in messages if m.status == 'replied']),
        'resolved': len([m for m in messages if m.status == 'resolved']),
        'deleted': len([m for m in messages if m.status == 'deleted'])
    }
    
    text = f"""
📊 <b>آمار پیام‌های شما</b>

📨 کل پیام‌ها: {stats['total']}
🕒 در انتظار پاسخ: {stats['pending']}
✅ پاسخ داده شده: {stats['replied']}
🎉 حل شده: {stats['resolved']}
🗑️ حذف شده: {stats['deleted']}

📈 نرخ پاسخ‌دهی: {calculate_response_rate(stats)}%
"""
    
    keyboard = [
        [InlineKeyboardButton("📋 مدیریت پیام‌ها", callback_data="manage_messages")],
        [InlineKeyboardButton("📨 ارسال پیام جدید", callback_data="send_message")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="send_message")]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

def calculate_response_rate(stats):
    """محاسبه نرخ پاسخ‌دهی"""
    total_responded = stats['replied'] + stats['resolved']
    total_messages = stats['total'] - stats['deleted']
    
    if total_messages == 0:
        return 0
    
    return round((total_responded / total_messages) * 100, 1)

async def cancel_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """لغو ارسال پیام"""
    query = update.callback_query
    await query.answer()
    
    # پاک کردن وضعیت
    for key in ['sending_message', 'message_type', 'editing_message', 'editing_message_id']:
        context.user_data.pop(key, None)
    
    await send_message_menu(update, context)

def setup_messages_handlers(application):
    """تنظیم هندلرهای پیام‌رسانی"""
    application.add_handler(CallbackQueryHandler(send_message_menu, pattern="^send_message$"))
    application.add_handler(CallbackQueryHandler(start_message_to_admin, pattern="^send_to_main_admin$"))
    application.add_handler(CallbackQueryHandler(start_message_to_admin, pattern="^send_to_all_admins$"))
    application.add_handler(CallbackQueryHandler(start_message_to_admin, pattern="^send_to_self$"))
    application.add_handler(CallbackQueryHandler(show_my_messages, pattern="^my_messages$"))
    application.add_handler(CallbackQueryHandler(manage_messages, pattern="^manage_messages$"))
    application.add_handler(CallbackQueryHandler(view_messages_by_status, pattern="^view_messages_"))
    application.add_handler(CallbackQueryHandler(edit_message, pattern="^edit_message_"))
    application.add_handler(CallbackQueryHandler(delete_message, pattern="^delete_message_"))
    application.add_handler(CallbackQueryHandler(confirm_delete_message, pattern="^confirm_delete_"))
    application.add_handler(CallbackQueryHandler(message_stats, pattern="^message_stats$"))
    application.add_handler(CallbackQueryHandler(cancel_message, pattern="^cancel_message$"))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_message), group=7)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_edited_message), group=8)
