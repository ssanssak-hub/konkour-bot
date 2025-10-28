import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from datetime import datetime
import random
import os

from config import BOT_TOKEN, ADMIN_ID, MOTIVATIONAL_MESSAGES
from exam_data import EXAMS_1405
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
        logger.info("✅ ربات کنکور راه‌اندازی شد")
        logger.info(f"👑 ادمین: {ADMIN_ID}")
    
    def setup_handlers(self):
        """تنظیم هندلرهای ربات"""
        # دستورات عمومی
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(MessageHandler(filters.Text("⏳ چند روز تا کنکور؟"), self.countdown_menu))
        self.application.add_handler(MessageHandler(filters.Text("📅 برنامه مطالعاتی"), self.study_plan))
        self.application.add_handler(MessageHandler(filters.Text("📊 آمار مطالعه"), self.study_stats))
        self.application.add_handler(MessageHandler(filters.Text("ℹ️ راهنمای استفاده"), self.help_command))
        self.application.add_handler(CallbackQueryHandler(self.button_handler))
        
        # دستورات ادمین
        self.application.add_handler(CommandHandler("admin", self.admin_panel))
        self.application.add_handler(CommandHandler("stats", self.bot_stats))
        self.application.add_handler(CommandHandler("broadcast", self.broadcast))
    
    def is_admin(self, user_id: int) -> bool:
        """بررسی آیا کاربر ادمین است"""
        return user_id == ADMIN_ID
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور شروع ربات"""
        user = update.effective_user
        is_admin = self.is_admin(user.id)
        
        welcome_text = f"""
        🎓 سلام {user.first_name} عزیز!
        به ربات کنکور ۱۴۰۵ خوش آمدید!
        
        {"👑 **شما ادمین هستید**" if is_admin else ""}
        
        🔍 با استفاده از این ربات می‌توانید:
        • ⏳ زمان دقیق باقی‌مانده تا کنکور را مشاهده کنید
        • 📅 برنامه مطالعاتی خود را مدیریت کنید
        • 📊 آمار مطالعه خود را پیگیری کنید
        
        👇 از منوی زیر انتخاب کنید:
        """
        await update.message.reply_text(welcome_text, reply_markup=main_menu())
    
    async def admin_panel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """پنل مدیریت ادمین"""
        user = update.effective_user
        
        if not self.is_admin(user.id):
            await update.message.reply_text("❌ دسترسی denied!")
            return
        
        admin_text = f"""
        👑 **پنل مدیریت**
        
        دستورات موجود:
        /stats - آمار ربات
        /broadcast - ارسال پیام همگانی
        
        اطلاعات سرور:
        • ادمین: {ADMIN_ID}
        • کاربر: {user.id}
        • زمان: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        await update.message.reply_text(admin_text)
    
    async def bot_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """آمار ربات"""
        user = update.effective_user
        
        if not self.is_admin(user.id):
            await update.message.reply_text("❌ دسترسی denied!")
            return
        
        stats_text = f"""
        📊 **آمار ربات**
        
        • ادمین اصلی: {ADMIN_ID}
        • کاربر فعلی: {user.id}
        • نام: {user.first_name}
        • یوزرنیم: @{user.username or 'ندارد'}
        • زمان سرور: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        • ربات فعال: ✅
        """
        await update.message.reply_text(stats_text)
    
    async def broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ارسال پیام همگانی"""
        user = update.effective_user
        
        if not self.is_admin(user.id):
            await update.message.reply_text("❌ دسترسی denied!")
            return
        
        if not context.args:
            await update.message.reply_text("⚠️ لطفاً پیام خود را بعد از دستور وارد کنید:\n/broadcast <پیام>")
            return
        
        message = " ".join(context.args)
        broadcast_text = f"""
        📢 **پیام همگانی**
        
        {message}
        
        ───────────────
        🎯 ربات کنکور ۱۴۰۵
        """
        
        await update.message.reply_text(f"✅ پیام همگانی آماده ارسال:\n{message}")
    
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
            "📅 بخش برنامه مطالعاتی به زودی اضافه خواهد شد!\n\n"
            "در این بخش می‌توانید:\n"
            "• برنامه روزانه خود را تنظیم کنید\n"
            "• زمان‌بندی دروس را مدیریت کنید\n"
            "• پیشرفت خود را پیگیری کنید",
            reply_markup=main_menu()
        )
    
    async def study_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """آمار مطالعه"""
        await update.message.reply_text(
            "📊 بخش آمار مطالعه به زودی اضافه خواهد شد!\n\n"
            "در این بخش می‌توانید:\n"
            "• ساعات مطالعه خود را ثبت کنید\n"
            "• نمودار پیشرفت را مشاهده کنید\n"
            "• با دوستان خود رقابت کنید",
            reply_markup=main_menu()
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """راهنمای استفاده"""
        help_text = """
        ℹ️ <b>راهنمای استفاده از ربات کنکور ۱۴۰۵</b>

        <b>⏳ چند روز تا کنکور؟</b>
        • نمایش زمان دقیق باقی‌مانده تا تمامی کنکورها
        • اطلاعات کامل هر کنکور شامل تاریخ و ساعت
        • جملات انگیزشی و مشاوره‌ای متناسب با زمان

        <b>📅 برنامه مطالعاتی</b>
        • مدیریت برنامه درسی شخصی
        • زمان‌بندی و تنظیم اهداف

        <b>📊 آمار مطالعه</b>
        • ثبت ساعات مطالعه
        • پیگیری پیشرفت تحصیلی

        <b>🔄 بروزرسانی</b>
        • به‌روزرسانی لحظه‌ای زمان
        • نمایش ثانیه‌شمار دقیق

        <b>🔙 بازگشت به منو</b>
        • بازگشت به منوی اصلی

        🎯 <i>برای شروع از منوی اصلی استفاده کنید</i>
        
        👑 <b>دستورات ادمین:</b>
        /admin - پنل مدیریت
        /stats - آمار ربات
        /broadcast - ارسال پیام همگانی
        """
        await update.message.reply_text(help_text, parse_mode='HTML', reply_markup=main_menu())

# ایجاد نمونه ربات
bot = ExamBot()

# برای تست محلی (اختیاری)
if __name__ == "__main__":
    import asyncio
    print("🚀 شروع ربات در حالت Polling...")
    
    async def main():
        await bot.application.initialize()
        await bot.application.start()
        await bot.application.updater.start_polling()
        
        # نگه داشتن برنامه
        await asyncio.Event().wait()
    
    asyncio.run(main())
