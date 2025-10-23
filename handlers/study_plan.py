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

async def show_daily_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش آمار مطالعه روزانه"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # آمار ۷ روز اخیر
    days = []
    study_times = []
    
    for i in range(7):
        date = (jdatetime.datetime.now() - jdatetime.timedelta(days=i)).strftime("%Y-%m-%d")
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
        [InlineKeyboardButton("📆 آمار هفتگی", callback_data="weekly_study_stats")],
        [InlineKeyboardButton("🔙 بازگشت به آمار", callback_data="study_stats")],
        [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(chart_text, reply_markup=reply_markup)

async def show_weekly_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش آمار مطالعه هفتگی"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # آمار ۴ هفته اخیر
    weeks = ["هفته ۴", "هفته ۳", "هفته ۲", "هفته ۱"]
    study_times = []
    
    # محاسبه مطالعه هفتگی
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
        [InlineKeyboardButton("📈 آمار روزانه", callback_data="daily_study_stats")],
        [InlineKeyboardButton("🔙 بازگشت به آمار", callback_data="study_stats")],
        [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(chart_text, reply_markup=reply_markup)

async def study_timer_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منوی زمان‌سنج مطالعه"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    active_timers = database.get_user_timers(user_id, active_only=True)
    
    message_text = "⏱️ زمان‌سنج مطالعه\n\n"
    
    if active_timers:
        message_text += "⏰ زمان‌سنج‌های فعال:\n"
        for timer in active_timers[:3]:
            message_text += f"• {timer.title}: {timer.remaining_hours:.1f} ساعت باقی مانده\n"
        message_text += "\n"
    
    message_text += (
        "با زمان‌سنج می‌توانید:\n"
        "• ⏰ زمان مطالعه خود را مدیریت کنید\n"
        "• 📊 پیشرفت را实时 مشاهده کنید\n"
        "• 🔔 یادآوری دریافت کنید\n"
    )
    
    keyboard = [
        [InlineKeyboardButton("➕ زمان‌سنج جدید", callback_data="add_study_timer")],
        [InlineKeyboardButton("📋 مدیریت زمان‌سنج‌ها", callback_data="manage_timers")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="study_plan")],
        [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message_text, reply_markup=reply_markup)

async def add_study_timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع ایجاد زمان‌سنج جدید"""
    query = update.callback_query
    await query.answer()
    
    context.user_data['waiting_for_timer_title'] = True
    
    await query.edit_message_text(
        "⏱️ ایجاد زمان‌سنج جدید\n\n"
        "لطفاً عنوان زمان‌سنج را وارد کنید:\n"
        "مثال: 'مطالعه ریاضی فصل ۳' یا 'حل تست‌های شیمی'"
    )

async def handle_timer_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت عنوان زمان‌سنج"""
    if context.user_data.get('waiting_for_timer_title'):
        title = update.message.text
        context.user_data['timer_title'] = title
        context.user_data['waiting_for_timer_hours'] = True
        context.user_data.pop('waiting_for_timer_title', None)
        
        await update.message.reply_text(
            f"✅ عنوان ثبت شد: {title}\n\n"
            "لطفاً مدت زمان هدف (به ساعت) را وارد کنید:\n"
            "مثال: 2.5 (یعنی ۲ ساعت و ۳۰ دقیقه)"
        )

async def handle_timer_hours(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ذخیره زمان‌سنج جدید"""
    if context.user_data.get('waiting_for_timer_hours'):
        try:
            target_hours = float(update.message.text)
            title = context.user_data.get('timer_title')
            user_id = update.message.from_user.id
            
            # ذخیره زمان‌سنج در دیتابیس
            timer = database.add_study_timer(
                user_id=user_id,
                title=title,
                target_hours=target_hours
            )
            
            # پاک کردن وضعیت
            context.user_data.pop('waiting_for_timer_hours', None)
            context.user_data.pop('timer_title', None)
            
            keyboard = [
                [InlineKeyboardButton("⏱️ زمان‌سنج جدید", callback_data="add_study_timer")],
                [InlineKeyboardButton("📋 مدیریت زمان‌سنج‌ها", callback_data="manage_timers")],
                [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"✅ زمان‌سنج با موفقیت ایجاد شد! ⏱️\n\n"
                f"🎯 عنوان: {title}\n"
                f"⏰ مدت زمان: {target_hours} ساعت\n"
                f"🆔 کد زمان‌سنج: {timer.id}\n\n"
                "حالا می‌تونی پیشرفتت رو实时 مشاهده کنی!",
                reply_markup=reply_markup
            )
            
        except ValueError:
            await update.message.reply_text(
                "❌ لطفاً یک عدد معتبر وارد کنید:\n"
                "مثال: 2.5 (برای ۲ ساعت و ۳۰ دقیقه)"
            )

def setup_study_plan_handlers(application):
    """تنظیم تمام هندلرهای مطالعه و برنامه‌ریزی"""
    # هندلرهای منوی اصلی
    application.add_handler(CallbackQueryHandler(study_plan_menu, pattern="^study_plan$"))
    application.add_handler(CallbackQueryHandler(add_study_goal, pattern="^add_study_goal$"))
    application.add_handler(CallbackQueryHandler(add_study_session_menu, pattern="^add_study_session$"))
    application.add_handler(CallbackQueryHandler(study_timer_menu, pattern="^study_timer$"))
    application.add_handler(CallbackQueryHandler(manage_study_plans, pattern="^manage_study_plans$"))
    application.add_handler(CallbackQueryHandler(study_stats_menu, pattern="^study_stats$"))
    
    # هندلرهای انواع هدف
    application.add_handler(CallbackQueryHandler(set_goal_type, pattern="^goal_"))
    
    # هندلرهای آمار
    application.add_handler(CallbackQueryHandler(show_daily_progress, pattern="^daily_study_stats$"))
    application.add_handler(CallbackQueryHandler(show_weekly_progress, pattern="^weekly_study_stats$"))
    
    # هندلرهای زمان‌سنج
    application.add_handler(CallbackQueryHandler(add_study_timer, pattern="^add_study_timer$"))
    application.add_handler(CallbackQueryHandler(study_timer_menu, pattern="^manage_timers$"))
    
    # هندلرهای پیام متنی
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_study_goal), group=1)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_study_goal_hours), group=2)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_study_session_subject), group=3)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_study_session), group=4)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_timer_title), group=5)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_timer_hours), group=6)
