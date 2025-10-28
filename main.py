import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from datetime import datetime
import random
import os

from config import BOT_TOKEN, MOTIVATIONAL_MESSAGES
from exam_data import EXAMS_1405
from keyboards import main_menu, countdown_actions

# تنظیمات لاگ
logger = logging.getLogger(__name__)

class ExamBot:
    def __init__(self):
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """تنظیم هندلرهای ربات"""
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("konkoor", self.countdown_menu))
        self.application.add_handler(MessageHandler(filters.Text("⏳ چند روز تا کنکور؟"), self.countdown_menu))
        self.application.add_handler(MessageHandler(filters.Text("📅 برنامه مطالعاتی"), self.study_plan))
        self.application.add_handler(MessageHandler(filters.Text("📊 آمار مطالعه"), self.study_stats))
        self.application.add_handler(MessageHandler(filters.Text("ℹ️ راهنمای استفاده"), self.help_command))
        self.application.add_handler(CallbackQueryHandler(self.button_handler))
        
        logger.info("✅ Bot handlers setup completed")
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور شروع ربات"""
        user = update.effective_user
        logger.info(f"👤 New user: {user.first_name} (ID: {user.id})")
        
        welcome_text = f"""
        🎓 سلام {user.first_name} عزیز!
        به ربات کنکور ۱۴۰۵ خوش آمدید!

        🔍 با استفاده از این ربات می‌توانید:
        • ⏳ زمان دقیق باقی‌مانده تا کنکور را مشاهده کنید
        • 📅 برنامه مطالعاتی خود را مدیریت کنید
        • 📊 آمار مطالعه خود را پیگیری کنید

        👇 از منوی زیر انتخاب کنید:
        """
        await update.message.reply_text(welcome_text, reply_markup=main_menu())
    
    async def countdown_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش زمان باقی‌مانده تا کنکور"""
        logger.info(f"⏰ Countdown requested by user {update.effective_user.id}")
        await self.send_countdown_message(update, context)
    
    async def send_countdown_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, is_callback: bool = False):
        """ارسال پیام زمان‌سنجی"""
        message_text = self.generate_countdown_text()
        
        try:
            if is_callback:
                await update.callback_query.edit_message_text(
                    message_text, 
                    reply_markup=countdown_actions(),
                    parse_mode='HTML'
                )
            else:
                await update.message.reply_text(
                    message_text, 
                    reply_markup=countdown_actions(),
                    parse_mode='HTML'
                )
            logger.info("✅ Countdown message sent successfully")
        except Exception as e:
            logger.error(f"❌ Error sending countdown: {e}")
    
    def generate_countdown_text(self) -> str:
        """تولید متن زمان‌سنجی"""
        now = datetime.now()
        text = "⏳ <b>زمان باقی‌مانده تا کنکور ۱۴۰۵</b>\n\n"
        
        for exam_key, exam_info in EXAMS_1405.items():
            text += f"🎯 <b>{exam_info['name']}</b>\n"
            text += f"📅 تاریخ: {exam_info['persian_date']}\n"
            text += f"⏰ ساعت: {exam_info['time']}\n"
            
            if isinstance(exam_info['date'], list):
                # برای کنکور فرهنگیان که دو تاریخ دارد
                for i, exam_date in enumerate(exam_info['date']):
                    target_date = datetime(*exam_date)
                    if now < target_date:
                        time_left = target_date - now
                        text += f"📋 روز <b>{i+1}</b>: {self.format_time_left(time_left)}\n"
            else:
                # برای سایر کنکورها
                target_date = datetime(*exam_info['date'])
                if now < target_date:
                    time_left = target_date - now
                    text += f"⏳ {self.format_time_left(time_left)}\n"
            
            text += "─" * 30 + "\n\n"
        
        # افزودن جمله انگیزشی تصادفی
        motivational_msg = random.choice(MOTIVATIONAL_MESSAGES)
        text += f"\n💫 <i>{motivational_msg}</i>\n\n"
        
        # پیام مشاوره‌ای بر اساس زمان باقی‌مانده
        text += self.get_advice_message()
        
        return text
    
    def format_time_left(self, time_delta) -> str:
        """قالب‌بندی زمان باقی‌مانده"""
        days = time_delta.days
        hours, remainder = divmod(time_delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        weeks = days // 7
        remaining_days = days % 7
        
        if days > 60:
            return f"<b>{weeks} هفته و {remaining_days} روز</b> باقی مانده"
        elif days > 30:
            return f"<b>{days} روز</b> - {hours:02d}:{minutes:02d}:{seconds:02d}"
        elif days > 7:
            return f"<b>{days} روز</b> - {hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"<b>{days} روز, {hours:02d} ساعت, {minutes:02d} دقیقه, {seconds:02d} ثانیه</b>"
    
    def get_advice_message(self) -> str:
        """پیام مشاوره‌ای بر اساس زمان باقی‌مانده"""
        now = datetime.now()
        # پیدا کردن نزدیک‌ترین کنکور
        upcoming_dates = []
        
        for exam_info in EXAMS_1405.values():
            if isinstance(exam_info['date'], list):
                for date_item in exam_info['date']:
                    exam_date = datetime(*date_item)
                    if now < exam_date:
                        upcoming_dates.append(exam_date)
            else:
                exam_date = datetime(*exam_info['date'])
                if now < exam_date:
                    upcoming_dates.append(exam_date)
        
        if upcoming_dates:
            closest_exam = min(upcoming_dates)
            days_left = (closest_exam - now).days
            
            if days_left > 365:
                return "📘 <b>مشاوره:</b> زمان کافی داری
