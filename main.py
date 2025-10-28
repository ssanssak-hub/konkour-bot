import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from datetime import datetime
import random
import os
import asyncio

from config import BOT_TOKEN, MOTIVATIONAL_MESSAGES
from exam_data import EXAMS_1405, get_upcoming_exams, get_exam_group_info
from keyboards import main_menu, countdown_actions

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ExamBot:
    def __init__(self):
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """تنظیم هندلرهای ربات"""
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(MessageHandler(filters.Text("⏳ چند روز تا کنکور؟"), self.countdown_menu))
        self.application.add_handler(MessageHandler(filters.Text("📅 برنامه مطالعاتی"), self.study_plan))
        self.application.add_handler(MessageHandler(filters.Text("📊 آمار مطالعه"), self.study_stats))
        self.application.add_handler(MessageHandler(filters.Text("ℹ️ راهنمای استفاده"), self.help_command))
        self.application.add_handler(CallbackQueryHandler(self.button_handler))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور شروع ربات"""
        welcome_text = """
        🎓 به ربات کنکور ۱۴۰۵ خوش آمدید!

        🔍 با استفاده از این ربات می‌توانید:
        • ⏳ زمان دقیق باقی‌مانده تا کنکور را مشاهده کنید
        • 📅 برنامه مطالعاتی خود را مدیریت کنید
        • 📊 آمار مطالعه خود را پیگیری کنید

        👇 از منوی زیر انتخاب کنید:
        """
        await update.message.reply_text(welcome_text, reply_markup=main_menu())
    
    async def countdown_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش زمان باقی‌مانده تا کنکور"""
        await self.send_countdown_message(update, context)
    
    async def send_countdown_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, is_callback: bool = False):
        """ارسال پیام زمان‌سنجی"""
        message_text = self.generate_countdown_text()
        
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
    
    def generate_countdown_text(self) -> str:
        """تولید متن زمان‌سنجی"""
        now = datetime.now()
        text = "⏳ <b>زمان باقی‌مانده تا کنکور ۱۴۰۵</b>\n\n"
        
        # استفاده از داده‌های جداگانه
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
        # استفاده از تابع جدید برای دریافت کنکورهای آینده
        upcoming_exams = get_upcoming_exams()
        if upcoming_exams:
            first_exam_date = upcoming_exams[0]["date"]
            days_left = (first_exam_date - now).days
            
            if days_left > 365:
                return "📘 <b>مشاوره:</b> زمان کافی داری! با برنامه‌ریزی بلندمدت پیش برو و پایه‌ها رو قوی کن."
            elif days_left > 180:
                return "📗 <b>مشاوره:</b> نیمه راهی! حالا وقت مرور و تست‌زنی حرفه‌ای‌تره."
            elif days_left > 90:
                return "📒 <b>مشاوره:</b> فاز آخر! روی جمع‌بندی و رفع اشکال تمرکز کن."
            elif days_left > 30:
                return "📙 <b>مشاوره:</b> دوران طلایی! تست‌های زمان‌دار و شبیه‌ساز کنکور رو شروع کن."
            else:
                return "📕 <b>مشاوره:</b> آرامش خودت رو حفظ کن! همین الان هم می‌تونی با مرور هدفمند نتیجه بگیری!"
        
        return "🎉 <b>همه کنکورها برگزار شده‌اند!</b>"
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت کلیک روی دکمه‌های اینلاین"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "refresh_countdown":
            await self.send_countdown_message(update, context, is_callback=True)
        elif query.data == "back_to_main":
            await query.edit_message_text(
                "🔙 به منوی اصلی بازگشتید:",
                reply_markup=main_menu()
            )
    
    async def study_plan(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """برنامه مطالعاتی"""
        await update.message.reply_text(
            "📅 بخش برنامه مطالعاتی به زودی اضافه خواهد شد!",
            reply_markup=main_menu()
        )
    
    async def study_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """آمار مطالعه"""
        await update.message.reply_text(
            "📊 بخش آمار مطالعه به زونی اضافه خواهد شد!",
            reply_markup=main_menu()
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """راهنمای استفاده"""
        help_text = """
        ℹ️ <b>راهنمای استفاده از ربات</b>

        <b>⏳ چند روز تا کنکور؟</b>
        • نمایش زمان دقیق باقی‌مانده تا تمامی کنکورها
        • اطلاعات کامل هر کنکور شامل تاریخ و ساعت
        • جملات انگیزشی و مشاوره‌ای متناسب با زمان

        <b>🔄 بروزرسانی</b>
        • به‌روزرسانی لحظه‌ای زمان
        • نمایش ثانیه‌شمار دقیق

        <b>🔙 بازگشت به منو</b>
        • بازگشت به منوی اصلی

        🎯 <i>برای شروع از منوی اصلی استفاده کنید</i>
        """
        await update.message.reply_text(help_text, parse_mode='HTML', reply_markup=main_menu())

# ایجاد نمونه ربات
bot = ExamBot()
