import logging
import random
import traceback
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
from keyboards import main_menu, exams_menu, countdown_actions, study_plan_menu, stats_menu, admin_menu

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
        # دستورات
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("test", self.test_message))
        
        # هندلر برای دکمه‌های متنی منو
        self.application.add_handler(MessageHandler(filters.Text(["⏳ زمان‌سنجی کنکورها"]), self.show_exams_menu))
        self.application.add_handler(MessageHandler(filters.Text(["📅 برنامه مطالعاتی پیشرفته"]), self.show_study_plan_menu))
        self.application.add_handler(MessageHandler(filters.Text(["📊 آمار مطالعه حرفه‌ای"]), self.show_stats_menu))
        self.application.add_handler(MessageHandler(filters.Text(["👑 پنل مدیریت"]), self.show_admin_menu))
        
        # هندلر برای سایر پیام‌های متنی
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_unknown_text))
        
        # هندلر برای دکمه‌های اینلاین
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        logger.info(f"✅ دریافت /start از {user.first_name} ({user.id})")

        try:
            welcome = f"""
👋 سلام {user.first_name} عزیز!
به ربات برنامه‌ریزی و شمارش معکوس کنکور ۱۴۰۵ خوش آمدی 🎯

از منوی زیر یکی از گزینه‌ها رو انتخاب کن:
"""
            logger.info(f"🚀 تلاش برای ارسال پیام خوشآمدگویی به {user.id}")
            
            # اضافه کردن await و لاگ بیشتر
            message = await update.message.reply_text(
                welcome, 
                reply_markup=main_menu(), 
                parse_mode='HTML'
            )
            
            logger.info(f"✅ پیام خوشآمدگویی با موفقیت ارسال شد. Message ID: {message.message_id}")
            
        except Exception as e:
            logger.error(f"❌ خطا در ارسال پیام خوشآمدگویی: {e}")
            logger.error(traceback.format_exc())

    async def test_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تست ارسال پیام"""
        try:
            logger.info("🧪 درخواست تست پیام دریافت شد")
            test_msg = await update.message.reply_text("🧪 تست پیام ساده - اگر این رو می‌بینید، ربات سالم است!")
            logger.info(f"✅ تست پیام موفق. Message ID: {test_msg.message_id}")
        except Exception as e:
            logger.error(f"❌ خطا در تست پیام: {e}")
            logger.error(traceback.format_exc())

    async def show_exams_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش منوی کنکورها"""
        logger.info("⏰ کاربر منوی کنکورها رو انتخاب کرد")
        try:
            message = await update.message.reply_text("🎯 انتخاب کنکور مورد نظر:", reply_markup=exams_menu())
            logger.info(f"✅ منوی کنکورها ارسال شد. Message ID: {message.message_id}")
        except Exception as e:
            logger.error(f"❌ خطا در نمایش منوی کنکورها: {e}")
            logger.error(traceback.format_exc())

    async def show_study_plan_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش منوی برنامه مطالعاتی"""
        logger.info("📅 کاربر منوی برنامه مطالعاتی رو انتخاب کرد")
        try:
            message = await update.message.reply_text("📅 برنامه مطالعاتی پیشرفته:", reply_markup=study_plan_menu())
            logger.info(f"✅ منوی برنامه مطالعاتی ارسال شد. Message ID: {message.message_id}")
        except Exception as e:
            logger.error(f"❌ خطا در نمایش منوی برنامه مطالعاتی: {e}")
            logger.error(traceback.format_exc())

    async def show_stats_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش منوی آمار مطالعه"""
        logger.info("📊 کاربر منوی آمار مطالعه رو انتخاب کرد")
        try:
            message = await update.message.reply_text("📊 آمار مطالعه حرفه‌ای:", reply_markup=stats_menu())
            logger.info(f"✅ منوی آمار مطالعه ارسال شد. Message ID: {message.message_id}")
        except Exception as e:
            logger.error(f"❌ خطا در نمایش منوی آمار مطالعه: {e}")
            logger.error(traceback.format_exc())

    async def show_admin_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش منوی مدیریت"""
        user = update.effective_user
        logger.info(f"👑 کاربر {user.first_name} منوی مدیریت رو انتخاب کرد")
        
        if user.id != ADMIN_ID:
            await update.message.reply_text("❌ دسترسی denied!")
            return
            
        try:
            message = await update.message.reply_text("👑 پنل مدیریت:", reply_markup=admin_menu())
            logger.info(f"✅ منوی مدیریت ارسال شد. Message ID: {message.message_id}")
        except Exception as e:
            logger.error(f"❌ خطا در نمایش منوی مدیریت: {e}")
            logger.error(traceback.format_exc())

    async def handle_unknown_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت پیام‌های متنی ناشناخته"""
        user = update.effective_user
        text = update.message.text
        logger.info(f"📝 کاربر {user.first_name} پیام فرستاد: {text}")
        
        try:
            message = await update.message.reply_text(
                "لطفاً از دکمه‌های منو استفاده کنید:",
                reply_markup=main_menu()
            )
            logger.info(f"✅ پاسخ به پیام ناشناخته ارسال شد. Message ID: {message.message_id}")
        except Exception as e:
            logger.error(f"❌ خطا در پاسخ به پیام ناشناخته: {e}")
            logger.error(traceback.format_exc())

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        data = query.data
        logger.info(f"🔘 دکمه کلیک شد: {data}")

        try:
            if data.startswith("exam_"):
                exam_key = data.replace("exam_", "")
                await self.send_exam_countdown(query, exam_key)
            elif data == "back_to_main":
                await query.edit_message_text("بازگشت به منوی اصلی:", reply_markup=main_menu())
            elif data == "show_all_exams":
                await self.show_all_exams_countdown(query)
            else:
                await query.edit_message_text("دستور نامعتبر!")
                
        except Exception as e:
            logger.error(f"❌ خطا در پردازش کال‌بک: {e}")
            logger.error(traceback.format_exc())
            await query.edit_message_text("❌ خطا در پردازش درخواست!")

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

    async def show_all_exams_countdown(self, query):
        """نمایش زمان تمامی کنکورها"""
        message = "⏳ <b>زمان باقی‌مانده تا کنکورهای ۱۴۰۵</b>\n\n"
        
        for exam_key, exam in EXAMS_1405.items():
            now = datetime.now()
            dates = exam["date"] if isinstance(exam["date"], list) else [exam["date"]]
            future_dates = [datetime(*d) for d in dates if datetime(*d) > now]
            
            message += f"🎯 <b>{exam['name']}</b>\n"
            message += f"📅 {exam['persian_date']} - 🕒 {exam['time']}\n"
            
            if future_dates:
                target = min(future_dates)
                delta = target - now
                message += f"⏳ {self.format_simple_countdown(delta)}\n"
            else:
                message += "✅ برگزار شده\n"
            
            message += "─" * 30 + "\n\n"
        
        message += f"💫 <i>{random.choice(MOTIVATIONAL_MESSAGES)}</i>"
        
        await query.edit_message_text(message, reply_markup=countdown_actions(), parse_mode='HTML')

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

    def format_simple_countdown(self, delta):
        """قالب ساده برای نمایش همه کنکورها"""
        days = delta.days
        hours = delta.seconds // 3600
        return f"{days} روز و {hours} ساعت"

# تابع برای app.py
def get_application():
    bot = ExamBot()
    return bot.application
