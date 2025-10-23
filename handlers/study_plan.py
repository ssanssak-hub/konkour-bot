from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters
from database.operations import database
import jdatetime

async def study_plan_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # دریافت آمار مطالعه کاربر
    daily_time = database.get_daily_study_time(user_id)
    weekly_time = database.get_weekly_study_time(user_id)
    
    keyboard = [
        [InlineKeyboardButton("🎯 ثبت هدف جدید", callback_data="add_study_goal")],
        [InlineKeyboardButton("📚 ثبت جلسه مطالعه", callback_data="add_study_session")],
        [InlineKeyboardButton("⏱️ زمان‌سنج مطالعه", callback_data="study_timer")],
        [InlineKeyboardButton("📊 مدیریت اهداف و برنامه‌ها", callback_data="manage_study_plans")],
        [InlineKeyboardButton("📈 آمار مطالعه", callback_data="study_stats")],
        [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = (
        "📚 اهداف و برنامه‌ریزی و ثبت مطالعه\n\n"
        f"📊 آمار مطالعه شما:\n"
        f"• 📅 امروز: {daily_time:.1f} ساعت\n"
        f"• 📆 این هفته: {weekly_time:.1f} ساعت\n\n"
        "لطفاً گزینه مورد نظر خود را انتخاب کنید:"
    )
    
    await query.edit_message_text(message_text, reply_markup=reply_markup)

async def add_study_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("📅 روزانه", callback_data="goal_daily")],
        [InlineKeyboardButton("📆 هفتگی", callback_data="goal_weekly")],
        [InlineKeyboardButton("🗓️ ماهانه", callback_data="goal_monthly")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="study_plan")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    context.user_data['waiting_for_goal'] = True
    
    await query.edit_message_text(
        "🎯 ثبت هدف جدید\n\n"
        "لطفاً نوع هدف را انتخاب کنید:",
        reply_markup=reply_markup
    )

async def set_goal_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    goal_type = query.data.replace("goal_", "")
    context.user_data['goal_type'] = goal_type
    
    type_text = {
        'daily': 'روزانه',
        'weekly': 'هفتگی', 
        'monthly': 'ماهانه'
    }
    
    await query.edit_message_text(
        f"📝 ثبت هدف {type_text[goal_type]}\n\n"
        "لطفاً عنوان هدف را ارسال کنید:\n"
        "مثال: 'خواندن فصل ۱ ریاضی' یا 'حل ۵۰ تست شیمی'"
    )

async def save_study_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_for_goal'):
        title = update.message.text
        goal_type = context.user_data.get('goal_type')
        
        # درخواست ساعت هدف
        context.user_data['goal_title'] = title
        context.user_data['waiting_for_hours'] = True
        
        type_text = {
            'daily': 'روزانه',
            'weekly': 'هفتگی',
            'monthly': 'ماهانه'
        }
        
        await update.message.reply_text(
            f"✅ عنوان هدف ثبت شد: {title}\n\n"
            f"لطفاً تعداد ساعت‌های هدف {type_text[goal_type]} را وارد کنید:\n"
            "مثال: 2.5 (یعنی ۲ ساعت و ۳۰ دقیقه)"
        )

async def save_study_goal_hours(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_for_hours'):
        try:
            target_hours = float(update.message.text)
            title = context.user_data.get('goal_title')
            goal_type = context.user_data.get('goal_type')
            
            user_id = update.message.from_user.id
            
            # ذخیره هدف در دیتابیس
            plan = database.add_study_plan(
                user_id=user_id,
                title=title,
                subject="عمومی",  # می‌تواند بعداً تنظیم شود
                plan_type=goal_type,
                target_hours=target_hours
            )
            
            # پاک کردن وضعیت
            context.user_data.pop('waiting_for_goal', None)
            context.user_data.pop('goal_type', None)
            context.user_data.pop('goal_title', None)
            context.user_data.pop('waiting_for_hours', None)
            
            type_text = {
                'daily': 'روزانه',
                'weekly': 'هفتگی',
                'monthly': 'ماهانه'
            }
            
            keyboard = [
                [InlineKeyboardButton("📚 ثبت جلسه مطالعه", callback_data="add_study_session")],
                [InlineKeyboardButton("📊 مدیریت اهداف", callback_data="manage_study_plans")],
                [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"✅ هدف {type_text[goal_type]} با موفقیت ثبت شد! 🎉\n\n"
                f"🎯 عنوان: {title}\n"
                f"⏰ ساعت هدف: {target_hours} ساعت\n"
                f"📅 نوع: {type_text[goal_type]}\n"
                f"🆔 کد هدف: {plan.id}\n\n"
                "حالا می‌تونی جلسات مطالعه‌ات رو ثبت کنی!",
                reply_markup=reply_markup
            )
            
        except ValueError:
            await update.message.reply_text(
                "❌ لطفاً یک عدد معتبر وارد کنید:\n"
                "مثال: 2.5 (برای ۲ ساعت و ۳۰ دقیقه)"
            )

async def add_study_session_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    context.user_data['waiting_for_session_subject'] = True
    
    await query.edit_message_text(
        "📚 ثبت جلسه مطالعه\n\n"
        "لطفاً نام درس یا موضوع مطالعه را ارسال کنید:\n"
        "مثال: 'ریاضی - فصل ۱' یا 'شیمی - مسائل استوکیومتری'"
    )

async def save_study_session_subject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_for_session_subject'):
        subject = update.message.text
        context.user_data['session_subject'] = subject
        context.user_data['waiting_for_session_duration'] = True
        
        await update.message.reply_text(
            f"✅ موضوع ثبت شد: {subject}\n\n"
            "لطفاً مدت زمان مطالعه (به ساعت) را وارد کنید:\n"
            "مثال: 1.5 (یعنی ۱ ساعت و ۳۰ دقیقه)"
        )

async def save_study_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_for_session_duration'):
        try:
            duration = float(update.message.text)
            subject = context.user_data.get('session_subject')
            user_id = update.message.from_user.id
            
            # ذخیره جلسه مطالعه در دیتابیس
            session = database.add_study_session(
                user_id=user_id,
                subject=subject,
                duration=duration
            )
            
            # پاک کردن وضعیت
            context.user_data.pop('waiting_for_session_subject', None)
            context.user_data.pop('session_subject', None)
            context.user_data.pop('waiting_for_session_duration', None)
            
            # بروزرسانی آمار
            daily_time = database.get_daily_study_time(user_id)
            weekly_time = database.get_weekly_study_time(user_id)
            
            keyboard = [
                [InlineKeyboardButton("🎯 ثبت هدف جدید", callback_data="add_study_goal")],
                [InlineKeyboardButton("📊 آمار مطالعه", callback_data="study_stats")],
                [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"✅ جلسه مطالعه با موفقیت ثبت شد! 📚\n\n"
                f"📚 موضوع: {subject}\n"
                f"⏰ مدت زمان: {duration} ساعت\n"
                f"📅 تاریخ: {jdatetime.datetime.now().strftime('%Y/%m/%d')}\n"
                f"🆔 کد جلسه: {session.id}\n\n"
                f"📊 آمار به روز شما:\n"
                f"• 📅 امروز: {daily_time:.1f} ساعت\n"
                f"• 📆 این هفته: {weekly_time:.1f} ساعت\n\n"
                "آفرین! ادامه بده 💪",
                reply_markup=reply_markup
            )
            
        except ValueError:
            await update.message.reply_text(
                "❌ لطفاً یک عدد معتبر وارد کنید:\n"
                "مثال: 1.5 (برای ۱ ساعت و ۳۰ دقیقه)"
            )

async def manage_study_plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    plans = database.get_user_study_plans(user_id, active_only=True)
    
    if not plans:
        keyboard = [
            [InlineKeyboardButton("🎯 ثبت هدف جدید", callback_data="add_study_goal")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="study_plan")],
            [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "ℹ️ شما هیچ هدف فعالی ندارید.\n\n"
            "می‌توانید با ثبت هدف جدید شروع کنید!",
            reply_markup=reply_markup
        )
        return
    
    message_text = "📋 اهداف و برنامه‌های شما:\n\n"
    keyboard = []
    
    for plan in plans[:10]:  # فقط ۱۰ هدف اول
        progress = plan.progress_percentage()
        status = "✅ انجام شده" if plan.is_completed else "🟡 در حال انجام"
        
        message_text += f"🎯 {plan.title}\n"
        message_text += f"📚 {plan.subject} | {plan.plan_type}\n"
        message_text += f"⏰ {plan.completed_hours:.1f}/{plan.target_hours:.1f} ساعت ({progress:.1f}%)\n"
        message_text += f"🔸 {status}\n\n"
        
        keyboard.append([
            InlineKeyboardButton(f"✏️ ویرایش {plan.id}", callback_data=f"edit_plan_{plan.id}"),
            InlineKeyboardButton(f"✅ کامل {plan.id}", callback_data=f"complete_plan_{plan.id}")
        ])
    
    keyboard.append([InlineKeyboardButton("🎯 هدف جدید", callback_data="add_study_goal")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="study_plan")])
    keyboard.append([InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message_text, reply_markup=reply_markup)

async def study_stats_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # دریافت آمار کامل
    user_stats = database.get_user_statistics(user_id)
    study_by_subject = database.study_repo.get_study_time_by_subject(user_id, 30)
    
    message_text = "📊 آمار مطالعه شما\n\n"
    
    if user_stats:
        message_text += f"📅 ۳۰ روز اخیر:\n"
        message_text += f"• 📆 روزهای مطالعه: {user_stats['attendance']['attendance_days']} روز\n"
        message_text += f"• ⏰ مجموع ساعت: {user_stats['study_time']['total_30_days']:.1f} ساعت\n"
        message_text += f"• 📈 میانگین روزانه: {user_stats['sessions']['average_duration']:.1f} ساعت\n"
        message_text += f"• 🎯 نرخ موفقیت: {user_stats['plans']['completion_rate']:.1f}%\n\n"
    
    if study_by_subject:
        message_text += "📚 مطالعه بر اساس درس:\n"
        for subject, hours in list(study_by_subject.items())[:5]:  # ۵ درس اول
            message_text += f"• {subject}: {hours:.1f} ساعت\n"
    
    keyboard = [
        [InlineKeyboardButton("📅 آمار روزانه", callback_data="daily_study_stats")],
        [InlineKeyboardButton("📆 آمار هفتگی", callback_data="weekly_study_stats")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="study_plan")],
        [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message_text, reply_markup=reply_markup)

def setup_study_plan_handlers(application):
    application.add_handler(CallbackQueryHandler(study_plan_menu, pattern="^study_plan$"))
    application.add_handler(CallbackQueryHandler(add_study_goal, pattern="^add_study_goal$"))
    application.add_handler(CallbackQueryHandler(set_goal_type, pattern="^goal_"))
    application.add_handler(CallbackQueryHandler(add_study_session_menu, pattern="^add_study_session$"))
    application.add_handler(CallbackQueryHandler(manage_study_plans, pattern="^manage_study_plans$"))
    application.add_handler(CallbackQueryHandler(study_stats_menu, pattern="^study_stats$"))
    application.add_handler(CallbackQueryHandler(study_stats_menu, pattern="^daily_study_stats$"))
    application.add_handler(CallbackQueryHandler(study_stats_menu, pattern="^weekly_study_stats$"))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_study_goal), group=1)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_study_goal_hours), group=2)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_study_session_subject), group=3)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_study_session), group=4)
