import logging
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

from config import BOT_TOKEN, ADMIN_ID
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
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))

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
        target = datetime(*exam["date"])  # مثال: [2025, 7, 15, 8, 0]

        if now >= target:
            countdown = "⛳ آزمون برگزار شده است."
        else:
            delta = target - now
            weeks = delta.days // 7
            days = delta.days % 7
            hours = delta.seconds // 3600
            minutes = (delta.seconds % 3600) // 60
            seconds = delta.seconds % 60

            countdown = f"""
            ⏳ زمان باقی‌مانده:
            {weeks} هفته، {days} روز، {hours} ساعت، {minutes} دقیقه، {seconds} ثانیه
            """

        message = f"""
        📘 <b>{exam['name']}</b>
        📅 تاریخ: {exam['persian_date']}
        🕒 ساعت: {exam['time']}

        {countdown}
        """
        await query.edit_message_text(message, reply_markup=countdown_actions(exam_key), parse_mode='HTML')

# تابع برای app.py
def get_application():
    bot = ExamBot()
    return bot.application
