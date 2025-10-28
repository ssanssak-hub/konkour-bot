import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from datetime import datetime
import random
import os

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# داده‌های کنکور
EXAMS_1405 = {
    "علوم_انسانی": {
        "name": "کنکور علوم انسانی",
        "date": (2026, 6, 30),
        "time": "08:00",
        "persian_date": "۱۱ تیر ۱۴۰۵"
    },
    "ریاضی_فنی": {
        "name": "کنکور ریاضی و فنی", 
        "date": (2026, 6, 30),
        "time": "08:00",
        "persian_date": "۱۱ تیر ۱۴۰۵"
    },
    "فرهنگیان": {
        "name": "کنکور فرهنگیان",
        "date": [(2026, 5, 6), (2026, 5, 7)],
        "time": "08:00", 
        "persian_date": "۱۷ و ۱۸ اردیبهشت ۱۴۰۵"
    },
    "سایر": {
        "name": "کنکور علوم تجربی، هنر، زبان",
        "date": (2026, 7, 1),
        "time": "08:00",
        "persian_date": "۱۲ تیر ۱۴۰۵"
    }
}

MOTIVATIONAL_MESSAGES = [
    "🎯 هر روز یک قدم نزدیک‌تر به هدف!",
    "💪 تو می‌تونی!",
    "🚀 ادامه بده!",
    "⭐ موفقیت در انتظار توست!",
]

def main_menu():
    """منوی اصلی"""
    from telegram import ReplyKeyboardMarkup
    keyboard = [
        ["⏳ چند روز تا کنکور؟"],
        ["📅 برنامه مطالعاتی"],
        ["📊 آمار مطالعه"],
        ["ℹ️ راهنمای استفاده"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def countdown_actions():
    """دکمه‌های زمان‌سنجی"""
    from telegram import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = [
        [InlineKeyboardButton("🔄 بروزرسانی", callback_data="refresh_countdown")],
        [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

class ExamBot:
    def __init__(self):
        self.token = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
        self.application = Application.builder().token(self.token).build()
        self.setup_handlers()
        logger.info("✅ Bot initialized successfully")
    
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
        
        for exam_key, exam_info in EXAMS_1405.items():
            text += f"🎯 <b>{exam_info['name']}</b>\n"
            text += f"📅 تاریخ: {exam_info['persian_date']}\n"
            text += f"⏰ ساعت: {exam_info['time']}\n"
            
            if isinstance(exam_info['date'], list):
                for i, exam_date in enumerate(exam_info['date']):
                    target_date = datetime(*exam_date)
                    if now < target_date:
                        time_left = target_date - now
                        text += f"📋 روز {i+1}: {self.format_time_left(time_left)}\n"
            else:
                target_date = datetime(*exam_info['date'])
                if now < target_date:
                    time_left = target_date - now
                    text += f"⏳ {self.format_time_left(time_left)}\n"
            
            text += "─" * 30 + "\n"
        
        text += f"\n💫 {random.choice(MOTIVATIONAL_MESSAGES)}\n"
        return text
    
    def format_time_left(self, time_delta) -> str:
        """قالب‌بندی زمان باقی‌مانده"""
        days = time_delta.days
        hours, remainder = divmod(time_delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 60:
            weeks = days // 7
            remaining_days = days % 7
            return f"<b>{weeks} هفته و {remaining_days} روز</b> باقی مانده"
        elif days > 7:
            return f"<b>{days} روز</b> باقی مانده"
        else:
            return f"<b>{days} روز, {hours:02d} ساعت, {minutes:02d} دقیقه</b>"
    
    def get_advice_message(self) -> str:
        """پیام مشاوره‌ای - بدون خطای string"""
        now = datetime.now()
        first_exam_date = datetime(2026, 5, 6)
        days_left = (first_exam_date - now).days
        
        if days_left > 365:
            return "📘 <b>مشاوره:</b> زمان کافی داری! با برنامه‌ریزی بلندمدت پیش برو."
        elif days_left > 180:
            return "📗 <b>مشاوره:</b> نیمه راهی! حالا وقت مرور و تست‌زنی حرفه‌ای."
        elif days_left > 90:
            return "📒 <b>مشاوره:</b> فاز آخر! روی جمع‌بندی و رفع اشکال تمرکز کن."
        elif days_left > 30:
            return "📙 <b>مشاوره:</b> دوران طلایی! تست‌های زمان‌دار رو شروع کن."
        else:
            return "📕 <b>مشاوره:</b> آرامش خودت رو حفظ کن!"
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت کلیک روی دکمه‌های اینلاین"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "refresh_countdown":
            await self.send_countdown_message(update, context, is_callback=True)
        elif query.data == "back_to_main":
            await query.edit_message_text("🔙 به منوی اصلی بازگشتید:", reply_markup=main_menu())
    
    async def study_plan(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """برنامه مطالعاتی"""
        await update.message.reply_text("📅 به زودی...", reply_markup=main_menu())
    
    async def study_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """آمار مطالعه"""
        await update.message.reply_text("📊 به زودی...", reply_markup=main_menu())
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """راهنمای استفاده"""
        help_text = "ℹ️ راهنمای استفاده از ربات"
        await update.message.reply_text(help_text, reply_markup=main_menu())

# ایجاد نمونه ربات
bot = ExamBot()
