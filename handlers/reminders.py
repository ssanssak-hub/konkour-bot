import os
import logging
import asyncio
import jdatetime
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters

from database.operations import database
from utils.helpers import validate_time_format
from config import Config

logger = logging.getLogger(__name__)

class ReminderSystem:
    def __init__(self):
        self.reminder_check_interval = Config.REMINDER_CHECK_INTERVAL
        self.timezone = Config.TIMEZONE
    
    async def start_reminder_scheduler(self, application):
        """شروع زمان‌بند چک کردن یادآوری‌ها"""
        while True:
            try:
                await self.check_and_send_reminders(application)
                await asyncio.sleep(self.reminder_check_interval)
            except Exception as e:
                logger.error(f"❌ خطا در زمان‌بند یادآوری: {e}")
                await asyncio.sleep(60)  # در صورت خطا ۱ دقیقه صبر کن
    
    async def check_and_send_reminders(self, application):
        """چک کردن و ارسال یادآوری‌ها"""
        try:
            now_tehran = jdatetime.datetime.now()
            current_time = now_tehran.strftime("%H:%M")
            current_date = now_tehran.strftime("%Y-%m-%d")
            
            # دریافت تمام یادآوری‌های فعال
            active_reminders = database.reminder_repo.get_active_reminders()
            
            for reminder in active_reminders:
                if await self.should_send_reminder(reminder, current_time, current_date):
                    await self.send_reminder_message(application, reminder)
                    # علامت‌گذاری به عنوان ارسال شده
                    database.reminder_repo.mark_reminder_triggered(reminder.id)
                    
        except Exception as e:
            logger.error(f"❌ خطا در چک کردن یادآوری‌ها: {e}")
    
    async def should_send_reminder(self, reminder, current_time, current_date):
        """بررسی آیا باید یادآوری ارسال شود"""
        # بررسی زمان
        if reminder.reminder_time != current_time:
            return False
        
        # بررسی روزهای هفته
        if reminder.days_of_week:
            current_weekday = jdatetime.datetime.now().weekday()
            if current_weekday not in reminder.days_of_week:
                return False
        
        # بررسی اینکه آیا امروز ارسال شده
        if reminder.last_triggered:
            last_triggered_date = reminder.last_triggered.strftime("%Y-%m-%d")
            if last_triggered_date == current_date:
                return False
        
        return True
    
    async def send_reminder_message(self, application, reminder):
        """ارسال پیام یادآوری به کاربر"""
        try:
            user = database.user_repo.get_user(reminder.user_id)
            if not user:
                return
            
            message_text = self.generate_reminder_message(reminder)
            keyboard = self.create_reminder_keyboard(reminder.id)
            
            await application.bot.send_message(
                chat_id=user.user_id,
                text=message_text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
            logger.info(f"✅ یادآوری ارسال شد به کاربر {user.user_id}")
            
        except Exception as e:
            logger.error(f"❌ خطا در ارسال یادآوری: {e}")
    
    def generate_reminder_message(self, reminder):
        """تولید متن پیام یادآوری"""
        base_message = "⏰ <b>یادآوری تنظیم شده</b>\n\n"
        
        if reminder.reminder_type == "exam":
            message = f"{base_message}📚 <b>یادآوری کنکور</b>\n"
            message += f"🎯 {reminder.exam_name}\n"
            message += f"📅 زمان: {reminder.reminder_time}\n\n"
            message += "💡 برای موفقیت در کنکور برنامه‌ریزی دقیق داشته باش!"
            
        elif reminder.reminder_type == "study":
            message = f"{base_message}📖 <b>یادآوری مطالعه</b>\n"
            message += f"🎯 {reminder.title}\n"
            message += f"📅 زمان: {reminder.reminder_time}\n\n"
            message += "📚 وقت مطالعه رسیده! تمرکزت رو حفظ کن."
            
        elif reminder.reminder_type == "custom":
            message = f"{base_message}📝 <b>یادآوری شخصی</b>\n"
            message += f"🎯 {reminder.title}\n"
            if reminder.custom_message:
                message += f"📋 {reminder.custom_message}\n"
            message += f"📅 زمان: {reminder.reminder_time}"
            
        else:
            message = f"{base_message}🔔 <b>یادآوری</b>\n"
            message += f"📅 زمان: {reminder.reminder_time}\n"
            if reminder.custom_message:
                message += f"📋 {reminder.custom_message}"
        
        message += f"\n\n🕒 ارسال شده در: {jdatetime.datetime.now().strftime('%Y/%m/%d %H:%M')}"
        return message
    
    def create_reminder_keyboard(self, reminder_id):
        """ایجاد کیبورد برای پیام یادآوری"""
        keyboard = [
            [InlineKeyboardButton("✅ انجام شد", callback_data=f"reminder_done_{reminder_id}")],
            [InlineKeyboardButton("⏰ به تعویق بینداز", callback_data=f"reminder_snooze_{reminder_id}")],
            [InlineKeyboardButton("🔕 غیرفعال کن", callback_data=f"reminder_disable_{reminder_id}")]
        ]
        return InlineKeyboardMarkup(keyboard)

# ایجاد نمونه جهانی
reminder_system = ReminderSystem()

# ==================== HANDLERS ====================

async def reminders_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منوی مدیریت یادآوری‌ها"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_reminders = database.reminder_repo.get_user_reminders(user_id)
    active_count = len([r for r in user_reminders if r.is_active])
    
    text = f"""
🔔 <b>مدیریت یادآوری‌ها</b>

📊 وضعیت فعلی:
• ✅ یادآوری‌های فعال: {active_count}
• 📋 کل یادآوری‌ها: {len(user_reminders)}
• ⏰ چک هر ۵ دقیقه

🎯 امکانات:
• ⏰ تنظیم یادآوری کنکور
• 📚 یادآوری مطالعه
• 📝 یادآوری شخصی
• 🛠️ مدیریت یادآوری‌ها
"""
    
    keyboard = [
        [InlineKeyboardButton("⏰ یادآوری کنکور", callback_data="reminder_exam")],
        [InlineKeyboardButton("📚 یادآوری مطالعه", callback_data="reminder_study")],
        [InlineKeyboardButton("📝 یادآوری متفرقه", callback_data="reminder_custom")],
        [InlineKeyboardButton("📋 مدیریت یادآوری‌ها", callback_data="reminder_manage")],
        [InlineKeyboardButton("🔄 بروزرسانی", callback_data="reminders")],
        [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
    ]
    
    await query.edit_message_text(
        text, 
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

async def setup_exam_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تنظیم یادآوری کنکور"""
    query = update.callback_query
    await query.answer()
    
    text = """
⏰ <b>تنظیم یادآوری کنکور</b>

🎯 لطفاً کنکور مورد نظر را انتخاب کنید:

💡 این یادآوری هر روز در ساعت مشخص شده به شما اطلاع می‌دهد.
"""
    
    keyboard = []
    exams = Config.get_all_exam_names()
    
    for exam in exams:
        if not Config.is_exam_passed(exam):
            keyboard.append([
                InlineKeyboardButton(
                    f"{Config.get_exam_emoji(exam)} {exam}", 
                    callback_data=f"reminder_exam_{exam}"
                )
            ])
    
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="reminders")])
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

async def select_exam_for_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """انتخاب کنکور برای یادآوری"""
    query = update.callback_query
    await query.answer()
    
    exam_name = query.data.replace("reminder_exam_", "")
    context.user_data['reminder_exam'] = exam_name
    context.user_data['reminder_type'] = 'exam'
    
    text = f"""
⏰ <b>تنظیم یادآوری کنکور {exam_name}</b>

🕒 لطفاً زمان یادآوری را وارد کنید (فرمت 24 ساعته):

📝 مثال: 
• 08:00 برای ۸ صبح
• 14:30 برای ۲:۳۰ بعدازظهر
• 22:15 برای ۱۰:۱۵ شب

💡 یادآوری هر روز در این زمان برای شما ارسال می‌شود.
"""
    
    keyboard = [
        [InlineKeyboardButton("🔙 بازگشت", callback_data="reminder_exam")],
        [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

async def setup_study_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تنظیم یادآوری مطالعه"""
    query = update.callback_query
    await query.answer()
    
    context.user_data['reminder_type'] = 'study'
    context.user_data['waiting_for_reminder_title'] = True
    
    text = """
📚 <b>تنظیم یادآوری مطالعه</b>

📝 لطفاً عنوان جلسه مطالعه را وارد کنید:

💡 مثال:
• "جلسه مطالعه ریاضی"
• "مرور فصل ۱ فیزیک" 
• "حل تست شیمی"
"""
    
    keyboard = [
        [InlineKeyboardButton("🔙 بازگشت", callback_data="reminders")],
        [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

async def setup_custom_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تنظیم یادآوری متفرقه"""
    query = update.callback_query
    await query.answer()
    
    context.user_data['reminder_type'] = 'custom'
    context.user_data['waiting_for_reminder_title'] = True
    
    text = """
📝 <b>تنظیم یادآوری متفرقه</b>

📝 لطفاً عنوان یادآوری را وارد کنید:

💡 مثال:
• "تماس با پشتیبانی"
• "خرید کتاب کمک آموزشی"
• "شرکت در آزمون آزمایشی"
"""
    
    keyboard = [
        [InlineKeyboardButton("🔙 بازگشت", callback_data="reminders")],
        [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

async def handle_reminder_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش عنوان یادآوری"""
    if context.user_data.get('waiting_for_reminder_title'):
        title = update.message.text
        context.user_data['reminder_title'] = title
        context.user_data['waiting_for_reminder_time'] = True
        context.user_data.pop('waiting_for_reminder_title', None)
        
        reminder_type = context.user_data.get('reminder_type', 'custom')
        
        text = f"""
✅ عنوان ثبت شد: <b>{title}</b>

🕒 لطفاً زمان یادآوری را وارد کنید (فرمت 24 ساعته):

📝 مثال:
• 08:00 برای ۸ صبح
• 14:30 برای ۲:۳۰ بعدازظهر  
• 22:15 برای ۱۰:۱۵ شب

💡 یادآوری هر روز در این زمان ارسال می‌شود.
"""
        
        await update.message.reply_text(text, parse_mode='HTML')

async def handle_reminder_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش زمان یادآوری"""
    if context.user_data.get('waiting_for_reminder_time'):
        time_str = update.message.text
        
        if not validate_time_format(time_str):
            await update.message.reply_text(
                "❌ فرمت زمان نامعتبر!\n\n"
                "لطفاً زمان را به فرمت صحیح وارد کنید:\n"
                "📝 مثال: 08:00 یا 14:30 یا 22:15"
            )
            return
        
        user_id = update.message.from_user.id
        reminder_type = context.user_data.get('reminder_type')
        title = context.user_data.get('reminder_title')
        exam_name = context.user_data.get('reminder_exam')
        
        # ذخیره یادآوری در دیتابیس
        reminder = database.reminder_repo.add_reminder(
            user_id=user_id,
            reminder_type=reminder_type,
            reminder_time=time_str,
            title=title,
            exam_name=exam_name,
            days_of_week=list(range(7)),  # همه روزهای هفته
            is_recurring=True
        )
        
        # پاک کردن داده‌های موقت
        for key in ['reminder_type', 'reminder_title', 'reminder_exam', 'waiting_for_reminder_time']:
            context.user_data.pop(key, None)
        
        # ایجاد پیام تأیید
        type_emojis = {
            'exam': '⏰',
            'study': '📚', 
            'custom': '📝'
        }
        
        text = f"""
✅ {type_emojis.get(reminder_type, '🔔')} <b>یادآوری تنظیم شد!</b>

📋 اطلاعات یادآوری:
• 🎯 نوع: {reminder_type}
• 📝 عنوان: {title}
• 🕒 زمان: {time_str}
• 🔄 تکرار: روزانه
• 🆔 کد: {reminder.id}

💡 یادآوری هر روز در زمان مشخص شده برای شما ارسال خواهد شد.
"""
        
        keyboard = [
            [InlineKeyboardButton("🔔 مدیریت یادآوری‌ها", callback_data="reminder_manage")],
            [InlineKeyboardButton("⏰ یادآوری جدید", callback_data="reminders")],
            [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
        ]
        
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )

async def manage_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت یادآوری‌های کاربر"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    reminders = database.reminder_repo.get_user_reminders(user_id, active_only=False)
    
    if not reminders:
        text = """
📭 <b>شما هیچ یادآوری ندارید</b>

💡 می‌توانید با استفاده از دکمه زیر اولین یادآوری خود را ایجاد کنید.
"""
        
        keyboard = [
            [InlineKeyboardButton("⏰ ایجاد یادآوری", callback_data="reminders")],
            [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
        ]
    else:
        text = "📋 <b>مدیریت یادآوری‌های شما</b>\n\n"
        
        keyboard = []
        for reminder in reminders[:10]:  # حداکثر ۱۰ یادآوری
            status_emoji = "✅" if reminder.is_active else "❌"
            type_emojis = {
                'exam': '⏰',
                'study': '📚',
                'custom': '📝'
            }
            
            text += f"{status_emoji} {type_emojis.get(reminder.reminder_type, '🔔')} #{reminder.id}\n"
            text += f"📝 {reminder.title or reminder.exam_name or 'بدون عنوان'}\n"
            text += f"🕒 {reminder.reminder_time} | {'فعال' if reminder.is_active else 'غیرفعال'}\n\n"
            
            if reminder.is_active:
                keyboard.append([
                    InlineKeyboardButton(f"❌ غیرفعال #{reminder.id}", callback_data=f"reminder_toggle_{reminder.id}"),
                    InlineKeyboardButton(f"🗑️ حذف #{reminder.id}", callback_data=f"reminder_delete_{reminder.id}")
                ])
            else:
                keyboard.append([
                    InlineKeyboardButton(f"✅ فعال #{reminder.id}", callback_data=f"reminder_toggle_{reminder.id}"),
                    InlineKeyboardButton(f"🗑️ حذف #{reminder.id}", callback_data=f"reminder_delete_{reminder.id}")
                ])
        
        keyboard.append([InlineKeyboardButton("⏰ ایجاد یادآوری جدید", callback_data="reminders")])
    
    keyboard.append([InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")])
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

async def toggle_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تغییر وضعیت فعال/غیرفعال یادآوری"""
    query = update.callback_query
    await query.answer()
    
    reminder_id = int(query.data.replace("reminder_toggle_", ""))
    new_status = database.reminder_repo.toggle_reminder(reminder_id)
    
    status_text = "فعال" if new_status else "غیرفعال"
    await query.answer(f"✅ یادآوری {status_text} شد")
    
    # بازگشت به منوی مدیریت
    await manage_reminders(update, context)

async def delete_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """حذف یادآوری"""
    query = update.callback_query
    await query.answer()
    
    reminder_id = int(query.data.replace("reminder_delete_", ""))
    
    keyboard = [
        [
            InlineKeyboardButton("✅ بله، حذف کن", callback_data=f"reminder_confirm_delete_{reminder_id}"),
            InlineKeyboardButton("❌ خیر، انصراف", callback_data="reminder_manage")
        ]
    ]
    
    await query.edit_message_text(
        "⚠️ <b>آیا مطمئن هستید که می‌خواهید این یادآوری را حذف کنید؟</b>\n\n"
        "این عمل غیرقابل بازگشت است!",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

async def confirm_delete_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تأیید حذف یادآوری"""
    query = update.callback_query
    await query.answer()
    
    reminder_id = int(query.data.replace("reminder_confirm_delete_", ""))
    success = database.reminder_repo.delete_reminder(reminder_id)
    
    if success:
        await query.answer("✅ یادآوری حذف شد")
    else:
        await query.answer("❌ خطا در حذف یادآوری")
    
    await manage_reminders(update, context)

async def handle_reminder_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش اقدامات روی پیام‌های یادآوری"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith("reminder_done_"):
        reminder_id = int(data.replace("reminder_done_", ""))
        await query.answer("✅ انجام شده علامت‌گذاری شد")
        await query.edit_message_text("✅ این یادآوری انجام شده علامت‌گذاری شد.")
        
    elif data.startswith("reminder_snooze_"):
        reminder_id = int(data.replace("reminder_snooze_", ""))
        await query.answer("⏰ یادآوری ۱۰ دقیقه به تعویق افتاد")
        # در اینجا می‌توانید زمان یادآوری را به تعویق بیندازید
        await query.edit_message_text("⏰ این یادآوری ۱۰ دقیقه به تعویق افتاد.")
        
    elif data.startswith("reminder_disable_"):
        reminder_id = int(data.replace("reminder_disable_", ""))
        database.reminder_repo.deactivate_reminder(reminder_id)
        await query.answer("🔕 یادآوری غیرفعال شد")
        await query.edit_message_text("🔕 این یادآوری غیرفعال شد.")

def setup_reminders_handlers(application):
    """تنظیم هندلرهای یادآوری"""
    application.add_handler(CallbackQueryHandler(reminders_menu, pattern="^reminders$"))
    application.add_handler(CallbackQueryHandler(setup_exam_reminder, pattern="^reminder_exam$"))
    application.add_handler(CallbackQueryHandler(setup_study_reminder, pattern="^reminder_study$"))
    application.add_handler(CallbackQueryHandler(setup_custom_reminder, pattern="^reminder_custom$"))
    application.add_handler(CallbackQueryHandler(select_exam_for_reminder, pattern="^reminder_exam_"))
    application.add_handler(CallbackQueryHandler(manage_reminders, pattern="^reminder_manage$"))
    application.add_handler(CallbackQueryHandler(toggle_reminder, pattern="^reminder_toggle_"))
    application.add_handler(CallbackQueryHandler(delete_reminder, pattern="^reminder_delete_"))
    application.add_handler(CallbackQueryHandler(confirm_delete_reminder, pattern="^reminder_confirm_delete_"))
    application.add_handler(CallbackQueryHandler(handle_reminder_action, pattern="^reminder_(done|snooze|disable)_"))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_reminder_title), group=3)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_reminder_time), group=4)
    
    # شروع زمان‌بند یادآوری‌ها
    asyncio.create_task(reminder_system.start_reminder_scheduler(application))
