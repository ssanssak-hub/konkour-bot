import logging
import random
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

# ایجاد Application به صورت مستقیم
application = Application.builder().token(BOT_TOKEN).build()

# --- هندلرهای ساده و مستقیم ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /start"""
    user = update.effective_user
    logger.info(f"🎯 دریافت /start از {user.first_name} ({user.id})")
    
    welcome = f"""
👋 سلام {user.first_name} عزیز!
به ربات کنکور ۱۴۰۵ خوش آمدی! 🎯

از منوی زیر استفاده کن:
"""
    await update.message.reply_text(welcome, reply_markup=main_menu())

async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /test"""
    user = update.effective_user
    logger.info(f"🧪 دریافت /test از {user.first_name} ({user.id})")
    
    await update.message.reply_text(
        "✅ تست موفق! ربات کار می‌کند.\n"
        "🎯 حالا از منو استفاده کن.",
        reply_markup=main_menu()
    )

async def show_exams_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش منوی کنکورها"""
    user = update.effective_user
    logger.info(f"⏰ کاربر {user.first_name} منوی کنکورها را انتخاب کرد")
    
    await update.message.reply_text(
        "🎯 انتخاب کنکور مورد نظر:",
        reply_markup=exams_menu()
    )

async def handle_unknown_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت پیام‌های ناشناخته"""
    user = update.effective_user
    text = update.message.text
    logger.info(f"📝 پیام ناشناخته از {user.first_name}: {text}")
    
    await update.message.reply_text(
        "🤔 لطفاً از دکمه‌های منو استفاده کنید:",
        reply_markup=main_menu()
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت کلیک دکمه‌ها"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user = query.from_user
    logger.info(f"🔘 کلیک از {user.first_name}: {data}")
    
    if data.startswith("exam_"):
        exam_key = data.replace("exam_", "")
        await send_exam_countdown(query, exam_key)
    elif data == "back_to_main":
        await query.edit_message_text("🏠 منوی اصلی:", reply_markup=main_menu())
    elif data == "show_all_exams":
        await show_all_exams_countdown(query)

async def send_exam_countdown(query, exam_key):
    """ارسال شمارش معکوس کنکور"""
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
        countdown = f"⏳ {days} روز و {hours} ساعت"
    
    message = f"""
📘 <b>{exam['name']}</b>
📅 {exam['persian_date']} - 🕒 {exam['time']}

{countdown}

🎯 {random.choice(MOTIVATIONAL_MESSAGES)}
"""
    await query.edit_message_text(message, reply_markup=countdown_actions(exam_key), parse_mode='HTML')

async def show_all_exams_countdown(query):
    """نمایش همه کنکورها"""
    message = "⏳ <b>کنکورهای ۱۴۰۵</b>\n\n"
    
    for exam_key, exam in EXAMS_1405.items():
        now = datetime.now()
        dates = exam["date"] if isinstance(exam["date"], list) else [exam["date"]]
        future_dates = [datetime(*d) for d in dates if datetime(*d) > now]
        
        if future_dates:
            target = min(future_dates)
            delta = target - now
            countdown = f"{delta.days} روز"
        else:
            countdown = "✅ برگزار شده"
        
        message += f"🎯 {exam['name']}\n"
        message += f"📅 {exam['persian_date']} - {countdown}\n"
        message += "─" * 20 + "\n\n"
    
    await query.edit_message_text(message, reply_markup=countdown_actions(), parse_mode='HTML')

# --- ثبت هندلرها ---
def setup_handlers():
    """ثبت همه هندلرها"""
    # دستورات
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("test", test_command))
    
    # منوهای متنی
    application.add_handler(MessageHandler(filters.Text(["⏳ زمان‌سنجی کنکورها"]), show_exams_menu))
    application.add_handler(MessageHandler(filters.Text(["📅 برنامه مطالعاتی پیشرفته"]), show_exams_menu))
    application.add_handler(MessageHandler(filters.Text(["📊 آمار مطالعه حرفه‌ای"]), show_exams_menu))
    application.add_handler(MessageHandler(filters.Text(["👑 پنل مدیریت"]), show_exams_menu))
    
    # پیام‌های متنی ناشناخته
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_unknown_text))
    
    # دکمه‌های اینلاین
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    logger.info("✅ همه هندلرها ثبت شدند")

# --- راه‌اندازی ---
setup_handlers()
logger.info("🎯 ربات ساده راه‌اندازی شد")

# تابع برای app.py
def get_application():
    return application
