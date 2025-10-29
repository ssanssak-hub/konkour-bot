import logging
import random
import traceback
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

from config import BOT_TOKEN, ADMIN_ID, MOTIVATIONAL_MESSAGES
from exam_data import EXAMS_1405
from keyboards import main_menu, exams_menu, countdown_actions

# تنظیم لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ایجاد Application
try:
    application = Application.builder().token(BOT_TOKEN).build()
    logger.info("✅ Application ساخته شد")
except Exception as e:
    logger.error(f"❌ خطا در ساخت Application: {e}")
    raise

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /start"""
    try:
        user = update.effective_user
        logger.info(f"🎯 شروع اجرای تابع start برای کاربر {user.id}")
        
        welcome = f"""
👋 سلام {user.first_name} عزیز!
به ربات کنکور ۱۴۰۵ خوش آمدی! 🎯

از منوی زیر استفاده کن:
"""
        logger.info(f"📤 ارسال پیام welcome به کاربر {user.id}")
        
        message = await update.message.reply_text(welcome, reply_markup=main_menu())
        logger.info(f"✅ پیام welcome با موفقیت ارسال شد. Message ID: {message.message_id}")
        
    except Exception as e:
        logger.error(f"❌ خطا در تابع start: {e}")
        logger.error(traceback.format_exc())

async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /test"""
    try:
        user = update.effective_user
        logger.info(f"🧪 شروع اجرای تابع test برای کاربر {user.id}")
        
        response = "✅ تست موفق! ربات در حال کار است.\n🎯 این پیام از تابع test ارسال شده."
        
        logger.info(f"📤 ارسال پیام test به کاربر {user.id}")
        message = await update.message.reply_text(response, reply_markup=main_menu())
        logger.info(f"✅ پیام test با موفقیت ارسال شد. Message ID: {message.message_id}")
        
    except Exception as e:
        logger.error(f"❌ خطا در تابع test: {e}")
        logger.error(traceback.format_exc())

async def show_exams_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش منوی کنکورها"""
    try:
        user = update.effective_user
        logger.info(f"⏰ کاربر {user.id} منوی کنکورها را انتخاب کرد")
        
        message = await update.message.reply_text(
            "🎯 انتخاب کنکور مورد نظر:",
            reply_markup=exams_menu()
        )
        logger.info(f"✅ منوی کنکورها ارسال شد. Message ID: {message.message_id}")
        
    except Exception as e:
        logger.error(f"❌ خطا در نمایش منوی کنکورها: {e}")
        logger.error(traceback.format_exc())

async def handle_unknown_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت پیام‌های ناشناخته"""
    try:
        user = update.effective_user
        text = update.message.text
        logger.info(f"📝 پیام ناشناخته از {user.id}: {text}")
        
        message = await update.message.reply_text(
            "🤔 لطفاً از دکمه‌های منو استفاده کنید:",
            reply_markup=main_menu()
        )
        logger.info(f"✅ پاسخ به پیام ناشناخته ارسال شد. Message ID: {message.message_id}")
        
    except Exception as e:
        logger.error(f"❌ خطا در پاسخ به پیام ناشناخته: {e}")
        logger.error(traceback.format_exc())

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت کلیک دکمه‌ها"""
    try:
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user = query.from_user
        logger.info(f"🔘 کلیک اینلاین از {user.id}: {data}")
        
        if data.startswith("exam_"):
            exam_key = data.replace("exam_", "")
            await send_exam_countdown(query, exam_key)
        elif data == "back_to_main":
            await query.edit_message_text("🏠 منوی اصلی:", reply_markup=main_menu())
        elif data == "show_all_exams":
            await show_all_exams_countdown(query)
            
    except Exception as e:
        logger.error(f"❌ خطا در پردازش کال‌بک: {e}")
        logger.error(traceback.format_exc())

async def send_exam_countdown(query, exam_key):
    """ارسال شمارش معکوس کنکور"""
    try:
        logger.info(f"📊 درخواست شمارش معکوس برای {exam_key}")
        
        if exam_key not in EXAMS_1405:
            await query.edit_message_text("❌ آزمون یافت نشد")
            return
        
        exam = EXAMS_1405[exam_key]
        now = datetime.now()
        
        dates = exam["date"] if isinstance(exam["date"], list) else [exam["date"]]
        future_dates = [datetime(*d) for d in dates if datetime(*d) > now]
        
        if not future_dates:
            countdown = "✅ برگزار شده"
        else:
            target = min(future_dates)
            delta = target - now
            days = delta.days
            hours = delta.seconds // 3600
            countdown = f"⏳ {days} روز و {hours} ساعت باقی مانده"
        
        message = f"""
📘 <b>{exam['name']}</b>
📅 {exam['persian_date']} - 🕒 {exam['time']}

{countdown}

🎯 {random.choice(MOTIVATIONAL_MESSAGES)}
"""
        await query.edit_message_text(message, reply_markup=countdown_actions(exam_key), parse_mode='HTML')
        logger.info(f"✅ شمارش معکوس برای {exam_key} ارسال شد")
        
    except Exception as e:
        logger.error(f"❌ خطا در ارسال شمارش معکوس: {e}")
        logger.error(traceback.format_exc())

async def show_all_exams_countdown(query):
    """نمایش همه کنکورها"""
    try:
        logger.info("📋 درخواست نمایش همه کنکورها")
        
        message = "⏳ <b>کنکورهای ۱۴۰۵</b>\n\n"
        
        for exam_key, exam in EXAMS_1405.items():
            now = datetime.now()
            dates = exam["date"] if isinstance(exam["date"], list) else [exam["date"]]
            future_dates = [datetime(*d) for d in dates if datetime(*d) > now]
            
            if future_dates:
                target = min(future_dates)
                delta = target - now
                countdown = f"{delta.days} روز باقی مانده"
            else:
                countdown = "✅ برگزار شده"
            
            message += f"🎯 {exam['name']}\n"
            message += f"📅 {exam['persian_date']} - {countdown}\n"
            message += "─" * 20 + "\n\n"
        
        await query.edit_message_text(message, reply_markup=countdown_actions(), parse_mode='HTML')
        logger.info("✅ همه کنکورها نمایش داده شد")
        
    except Exception as e:
        logger.error(f"❌ خطا در نمایش همه کنکورها: {e}")
        logger.error(traceback.format_exc())

# ثبت هندلرها
try:
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("test", test_command))
    application.add_handler(MessageHandler(filters.Text(["⏳ زمان‌سنجی کنکورها"]), show_exams_menu))
    application.add_handler(MessageHandler(filters.Text(["📅 برنامه مطالعاتی پیشرفته"]), show_exams_menu))
    application.add_handler(MessageHandler(filters.Text(["📊 آمار مطالعه حرفه‌ای"]), show_exams_menu))
    application.add_handler(MessageHandler(filters.Text(["👑 پنل مدیریت"]), show_exams_menu))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_unknown_text))
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    logger.info("✅ همه هندلرها با موفقیت ثبت شدند")
    
except Exception as e:
    logger.error(f"❌ خطا در ثبت هندلرها: {e}")
    logger.error(traceback.format_exc())

def get_application():
    logger.info("📦 درخواست Application از app.py")
    return application
