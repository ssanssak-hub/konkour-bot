import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from datetime import datetime
import random
import os

from config import BOT_TOKEN, ADMIN_ID, MOTIVATIONAL_MESSAGES
from exam_data import EXAMS_1405
from keyboards import main_menu, exams_menu, countdown_actions, study_plan_menu, stats_menu, admin_menu

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
    
    def setup_handlers(self):
        """تنظیم هندلرهای ربات"""
        # دستورات عمومی
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(MessageHandler(filters.Text("⏳ زمان‌سنجی کنکورها"), self.exams_menu))
        self.application.add_handler(MessageHandler(filters.Text("📅 برنامه مطالعاتی پیشرفته"), self.study_plan_menu))
        self.application.add_handler(MessageHandler(filters.Text("📊 آمار مطالعه حرفه‌ای"), self.stats_menu))
        self.application.add_handler(MessageHandler(filters.Text("👑 پنل مدیریت"), self.admin_menu))
        self.application.add_handler(CallbackQueryHandler(self.button_handler))
        
        # هندلر برای پیام‌های متنی که با دکمه‌ها مطابقت ندارند
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_unknown_text))
    
    async def handle_unknown_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت پیام‌های متنی ناشناخته"""
        user = update.effective_user
        text = update.message.text
        logger.info(f"📝 کاربر {user.first_name} پیام فرستاد: {text}")
        
        # اگر پیام جزو دکمه‌ها نبود، منو رو نمایش بده
        if text not in ["⏳ زمان‌سنجی کنکورها", "📅 برنامه مطالعاتی پیشرفته", "📊 آمار مطالعه حرفه‌ای", "👑 پنل مدیریت"]:
            await update.message.reply_text(
                "لطفاً از دکمه‌های منو استفاده کنید:",
                reply_markup=main_menu()
            )
    
    def is_admin(self, user_id: int) -> bool:
        """بررسی آیا کاربر ادمین است"""
        return user_id == ADMIN_ID
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور شروع ربات"""
        user = update.effective_user
        is_admin = self.is_admin(user.id)
        logger.info(f"🎯 کاربر {user.first_name} دستور /start رو فرستاد")
        
        welcome_text = f"""
        🎓 سلام {user.first_name} عزیز!
        به ربات کنکور ۱۴۰۵ خوش آمدید!
        
        {"👑 **شما ادمین هستید**" if is_admin else ""}
        
        🔍 با استفاده از این ربات می‌توانید:
        • ⏳ زمان دقیق باقی‌مانده تا کنکورها را مشاهده کنید
        • 📅 برنامه مطالعاتی پیشرفته تنظیم کنید
        • 📊 آمار مطالعه حرفه‌ای داشته باشید
        
        👇 از منوی زیر انتخاب کنید:
        """
        
        try:
            await update.message.reply_text(welcome_text, reply_markup=main_menu())
            logger.info("✅ منوی اصلی نمایش داده شد")
        except Exception as e:
            logger.error(f"❌ خطا در نمایش منو: {e}")
            await update.message.reply_text(welcome_text)
    
    async def exams_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """منوی کنکورها"""
        logger.info("⏰ کاربر دکمه 'زمان‌سنجی کنکورها' رو زد")
        await update.message.reply_text(
            "🎯 انتخاب کنکور مورد نظر:",
            reply_markup=exams_menu()
        )
    
    async def study_plan_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """منوی برنامه مطالعاتی"""
        logger.info("📅 کاربر دکمه 'برنامه مطالعاتی' رو زد")
        menu_text = """
        📅 **برنامه مطالعاتی پیشرفته**
        
        امکانات موجود:
        • 📝 ایجاد برنامه شخصی‌سازی شده
        • 📊 مشاهده و مدیریت برنامه
        • ✏️ ویرایش برنامه درسی
        • 📈 پیگیری پیشرفت تحصیلی
        
        👇 گزینه مورد نظر را انتخاب کنید:
        """
        await update.message.reply_text(menu_text, reply_markup=study_plan_menu(), parse_mode='HTML')
    
    async def stats_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """منوی آمار مطالعه"""
        logger.info("📊 کاربر دکمه 'آمار مطالعه' رو زد")
        menu_text = """
        📊 **آمار مطالعه حرفه‌ای**
        
        امکانات موجود:
        • ⏱️ ثبت ساعات مطالعه
        • 📊 آمار روزانه و هفتگی
        • 🏆 جدول رقابت و لیدربرد
        • 📋 گزارش کامل عملکرد
        
        👇 گزینه مورد نظر را انتخاب کنید:
        """
        await update.message.reply_text(menu_text, reply_markup=stats_menu(), parse_mode='HTML')
    
    async def admin_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """منوی پنل مدیریت"""
        user = update.effective_user
        logger.info(f"👑 کاربر {user.first_name} دکمه 'پنل مدیریت' رو زد")
        
        if not self.is_admin(user.id):
            await update.message.reply_text("❌ دسترسی denied!")
            return
        
        admin_text = f"""
        👑 **پنل مدیریت**
        
        کاربر: {user.first_name} (@{user.username})
        ادمین: {ADMIN_ID}
        
        امکانات مدیریتی:
        • 📊 مشاهده آمار ربات
        • 👥 مدیریت کاربران
        • 📢 ارسال پیام همگانی
        • ⚙️ تنظیمات پیشرفته
        
        👇 گزینه مورد نظر را انتخاب کنید:
        """
        await update.message.reply_text(admin_text, reply_markup=admin_menu(), parse_mode='HTML')
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت کلیک روی دکمه‌های اینلاین"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        logger.info(f"🔘 کاربر دکمه اینلاین زد: {data}")
        
        if data.startswith("exam_"):
            exam_key = data.replace("exam_", "")
            await self.show_exam_countdown(query, exam_key)
        
        elif data.startswith("refresh_"):
            if data == "refresh_all":
                await self.show_all_exams_countdown(query)
            else:
                exam_key = data.replace("refresh_", "")
                await self.show_exam_countdown(query, exam_key, is_refresh=True)
        
        elif data == "show_all_exams":
            await self.show_all_exams_countdown(query)
        
        elif data == "back_to_main":
            await query.edit_message_text(
                "🔙 به منوی اصلی بازگشتید:",
                reply_markup=main_menu()
            )
        
        # منوی برنامه مطالعاتی
        elif data in ["create_plan", "view_plan", "edit_plan", "progress", "refresh_plan"]:
            await self.handle_study_plan(query, data)
        
        # منوی آمار مطالعه
        elif data in ["log_study", "daily_stats", "weekly_stats", "leaderboard", "full_report"]:
            await self.handle_stats(query, data)
        
        # منوی مدیریت
        elif data in ["admin_stats", "admin_users", "admin_broadcast", "admin_settings", "admin_refresh"]:
            await self.handle_admin(query, data)
    
    async def show_exam_countdown(self, query, exam_key, is_refresh=False):
        """نمایش زمان باقی‌مانده برای یک کنکور خاص"""
        if exam_key not in EXAMS_1405:
            await query.edit_message_text("❌ کنکور مورد نظر یافت نشد!")
            return
        
        exam_info = EXAMS_1405[exam_key]
        message_text = self.generate_exam_countdown_text(exam_info, exam_key)
        
        await query.edit_message_text(
            message_text,
            reply_markup=countdown_actions(exam_key),
            parse_mode='HTML'
        )
    
    async def show_all_exams_countdown(self, query):
        """نمایش زمان تمامی کنکورها"""
        message_text = self.generate_all_exams_countdown_text()
        
        await query.edit_message_text(
            message_text,
            reply_markup=countdown_actions(),
            parse_mode='HTML'
        )
    
    def generate_exam_countdown_text(self, exam_info, exam_key):
        """تولید متن زمان‌سنجی برای یک کنکور"""
        now = datetime.now()
        text = f"🎯 <b>{exam_info['name']}</b>\n"
        text += f"📅 تاریخ: {exam_info['persian_date']}\n"
        text += f"⏰ ساعت: {exam_info['time']}\n\n"
        
        if isinstance(exam_info['date'], list):
            for i, exam_date in enumerate(exam_info['date']):
                target_date = datetime(*exam_date)
                if now < target_date:
                    time_left = target_date - now
                    text += f"📋 <b>روز {i+1}:</b>\n{self.format_detailed_time_left(time_left)}\n"
                else:
                    text += f"📋 <b>روز {i+1}:</b> ✅ برگزار شده\n"
        else:
            target_date = datetime(*exam_info['date'])
            if now < target_date:
                time_left = target_date - now
                text += f"⏳ {self.format_detailed_time_left(time_left)}\n"
            else:
                text += "✅ <b>کنکور برگزار شده</b>\n"
        
        text += f"\n💫 <i>{random.choice(MOTIVATIONAL_MESSAGES)}</i>\n"
        return text
    
    def generate_all_exams_countdown_text(self):
        """تولید متن زمان‌سنجی برای تمامی کنکورها"""
        now = datetime.now()
        text = "⏳ <b>زمان باقی‌مانده تا کنکورهای ۱۴۰۵</b>\n\n"
        
        for exam_key, exam_info in EXAMS_1405.items():
            text += f"🎯 <b>{exam_info['name']}</b>\n"
            text += f"📅 {exam_info['persian_date']} - ⏰ {exam_info['time']}\n"
            
            if isinstance(exam_info['date'], list):
                upcoming_dates = []
                for exam_date in exam_info['date']:
                    target_date = datetime(*exam_date)
                    if now < target_date:
                        upcoming_dates.append(target_date)
                
                if upcoming_dates:
                    closest_date = min(upcoming_dates)
                    time_left = closest_date - now
                    text += f"⏳ {self.format_detailed_time_left(time_left)}\n"
                else:
                    text += "✅ برگزار شده\n"
            else:
                target_date = datetime(*exam_info['date'])
                if now < target_date:
                    time_left = target_date - now
                    text += f"⏳ {self.format_detailed_time_left(time_left)}\n"
                else:
                    text += "✅ برگزار شده\n"
            
            text += "─" * 40 + "\n\n"
        
        text += f"💫 <i>{random.choice(MOTIVATIONAL_MESSAGES)}</i>\n"
        return text
    
    def format_detailed_time_left(self, time_delta):
        """قالب‌بندی دقیق زمان باقی‌مانده"""
        total_seconds = int(time_delta.total_seconds())
        
        weeks = total_seconds // (7 * 24 * 3600)
        days = (total_seconds % (7 * 24 * 3600)) // (24 * 3600)
        hours = (total_seconds % (24 * 3600)) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        parts = []
        if weeks > 0:
            parts.append(f"{weeks} هفته")
        if days > 0:
            parts.append(f"{days} روز")
        if hours > 0:
            parts.append(f"{hours} ساعت")
        if minutes > 0:
            parts.append(f"{minutes} دقیقه")
        if seconds > 0 or not parts:
            parts.append(f"{seconds} ثانیه")
        
        return " 🕒 ".join(parts)
    
    async def handle_study_plan(self, query, action):
        """مدیریت منوی برنامه مطالعاتی"""
        messages = {
            "create_plan": "📝 <b>ایجاد برنامه مطالعاتی</b>\n\nاین بخش به زودی اضافه خواهد شد...",
            "view_plan": "📊 <b>مشاهده برنامه</b>\n\nاین بخش به زودی اضافه خواهد شد...",
            "edit_plan": "✏️ <b>ویرایش برنامه</b>\n\nاین بخش به زودی اضافه خواهد شد...",
            "progress": "📈 <b>پیگیری پیشرفت</b>\n\nاین بخش به زودی اضافه خواهد شد...",
            "refresh_plan": "🔄 <b>بروزرسانی</b>\n\nبرنامه مطالعاتی بروزرسانی شد!"
        }
        
        await query.edit_message_text(
            messages[action],
            reply_markup=study_plan_menu(),
            parse_mode='HTML'
        )
    
    async def handle_stats(self, query, action):
        """مدیریت منوی آمار مطالعه"""
        messages = {
            "log_study": "⏱️ <b>ثبت مطالعه</b>\n\nاین بخش به زودی اضافه خواهد شد...",
            "daily_stats": "📊 <b>آمار روزانه</b>\n\nاین بخش به زودی اضافه خواهد شد...",
            "weekly_stats": "📈 <b>آمار هفتگی</b>\n\nاین بخش به زونی اضافه خواهد شد...",
            "leaderboard": "🏆 <b>جدول رقابت</b>\n\nاین بخش به زودی اضافه خواهد شد...",
            "full_report": "📋 <b>گزارش کامل</b>\n\nاین بخش به زودی اضافه خواهد شد..."
        }
        
        await query.edit_message_text(
            messages[action],
            reply_markup=stats_menu(),
            parse_mode='HTML'
        )
    
    async def handle_admin(self, query, action):
        """مدیریت منوی ادمین"""
        user = query.from_user
        
        if not self.is_admin(user.id):
            await query.edit_message_text("❌ دسترسی denied!")
            return
        
        messages = {
            "admin_stats": f"📊 <b>آمار ربات</b>\n\n• ادمین: {ADMIN_ID}\n• کاربر: {user.id}\n• زمان: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "admin_users": "👥 <b>مدیریت کاربران</b>\n\nاین بخش به زودی اضافه خواهد شد...",
            "admin_broadcast": "📢 <b>ارسال همگانی</b>\n\nاین بخش به زودی اضافه خواهد شد...",
            "admin_settings": "⚙️ <b>تنظیمات</b>\n\nاین بخش به زودی اضافه خواهد شد...",
            "admin_refresh": "🔄 <b>بروزرسانی</b>\n\nاطلاعات بروزرسانی شد!"
        }
        
        await query.edit_message_text(
            messages[action],
            reply_markup=admin_menu(),
            parse_mode='HTML'
        )

# ایجاد نمونه ربات
bot = ExamBot()

# برای دسترسی از app.py
def get_application():
    return bot.application

# اگر مستقیماً اجرا شد (برای تست)
if __name__ == '__main__':
    logger.info("🚀 اجرای ربات به صورت مستقیم...")
    bot.application.run_polling()
