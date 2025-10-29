import logging
import random
from datetime import datetime
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

from config import BOT_TOKEN, ADMIN_ID, MOTIVATIONAL_MESSAGES
from exam_data import EXAMS_1405
from keyboards import main_menu, countdown_actions

# تنظیم لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ExamBot:
    def __init__(self):
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()
        logger.info("✅ ربات کنکور ۱۴۰۵ آماده شد")

def setup_handlers(self):
    self.application.add_handler(CommandHandler("start", self.start))
    
    # هندلر برای دکمه‌های متنی منو
    self.application.add_handler(MessageHandler(filters.Text(["⏳ زمان‌سنجی کنکورها"]), self.exams_menu))
    self.application.add_handler(MessageHandler(filters.Text(["📅 برنامه مطالعاتی پیشرفته"]), self.study_plan_menu))
    self.application.add_handler(MessageHandler(filters.Text(["📊 آمار مطالعه حرفه‌ای"]), self.stats_menu))
    self.application.add_handler(MessageHandler(filters.Text(["👑 پنل مدیریت"]), self.admin_menu))
    
    # هندلر برای سایر پیام‌های متنی
    self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
    self.application.add_handler(CallbackQueryHandler(self.handle_callback))

async def exams_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منوی کنکورها"""
    await update.message.reply_text("🎯 انتخاب کنکور مورد نظر:", reply_markup=exams_menu())

async def study_plan_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منوی برنامه مطالعاتی"""
    await update.message.reply_text("📅 برنامه مطالعاتی پیشرفته:", reply_markup=study_plan_menu())

async def stats_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منوی آمار مطالعه"""
    await update.message.reply_text("📊 آمار مطالعه حرفه‌ای:", reply_markup=stats_menu())

async def admin_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منوی مدیریت"""
    user = update.effective_user
    if user.id != ADMIN_ID:
        await update.message.reply_text("❌ دسترسی denied!")
        return
    await update.message.reply_text("👑 پنل مدیریت:", reply_markup=admin_menu())

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        logger.info(f"✅ دریافت /start از {user.first_name} ({user.id})")

        welcome = f"""
        👋 سلام {user.first_name} عزیز!
        به ربات برنامه‌ریزی و شمارش معکوس کنکور ۱۴۰۵ خوش آمدی 🎯

        از منوی زیر یکی از گزینه‌ها رو انتخاب کن:
        """
        await update.message.reply_text(welcome, reply_markup=main_menu(), parse_mode='HTML')

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("از منوی زیر گزینه‌ای را انتخاب کنید:", reply_markup=main_menu())

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        data = query.data
        logger.info(f"🔘 دکمه کلیک شد: {data}")

        if data.startswith("exam_"):
            exam_key = data.replace("exam_", "")
            await self.send_exam_countdown(query, exam_key)
        elif data == "back_to_main":
            await query.edit_message_text("بازگشت به منوی اصلی:", reply_markup=main_menu())

    async def send_exam_countdown(self, query, exam_key):
        if exam_key not in EXAMS_1405:
            await query.edit_message_text("❌ آزمون مورد نظر یافت نشد.")
            return

        exam = EXAMS_1405[exam_key]
        now = datetime.now()

        # تبدیل تاریخ‌ها به لیست datetime کامل
        dates = exam["date"] if isinstance(exam["date"], list) else [exam["date"]]
        future_dates = [datetime(*d) for d in dates if datetime(*d) > now]

        if not future_dates:
            countdown = "⛳ همه‌ی مراحل این آزمون برگزار شده‌اند."
        else:
            target = min(future_dates)
            delta = target - now
            countdown = self.format_modern_countdown(delta)

        # پیام انگیزشی تصادفی
        motivation = f"\n\n🎯 {random.choice(MOTIVATIONAL_MESSAGES)}"

        message = f"""
📘 <b>{exam['name']}</b>
📅 تاریخ: {exam['persian_date']}
🕒 ساعت: {exam['time']}

{countdown}
{motivation}
"""
        await query.edit_message_text(message, reply_markup=countdown_actions(exam_key), parse_mode='HTML')

    def format_modern_countdown(self, delta):
        total_seconds = int(delta.total_seconds())
        weeks = delta.days // 7
        days = delta.days % 7
        hours = total_seconds % (24 * 3600) // 3600
        minutes = total_seconds % 3600 // 60
        seconds = total_seconds % 60

        return f"""
⏳ زمان باقی‌مانده:

🗓 {weeks} هفته  
📆 {days} روز  
⏰ {hours} ساعت  
🕑 {minutes} دقیقه  
⏱ {seconds} ثانیه
"""

# تابع برای app.py
def get_application():
    bot = ExamBot()
    return bot.application
