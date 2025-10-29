import logging
import random
import traceback
from datetime import datetime
from typing import Dict, Any, List
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
    ConversationHandler
)

from config import BOT_TOKEN, ADMIN_ID, MOTIVATIONAL_MESSAGES
from exam_data import EXAMS_1405
from keyboards import main_menu, exams_menu, countdown_actions, study_plan_menu, stats_menu, admin_menu

# تنظیمات پیشرفته لاگ‌گیری
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# وضعیت‌های گفتگو
STATE_STUDY_PLAN, STATE_STATS, STATE_ADMIN = range(3)

class KonkourBot:
    """ربات حرفه‌ای کنکور ۱۴۰۵"""
    
    def __init__(self):
        try:
            self.application = Application.builder().token(BOT_TOKEN).build()
            self.user_sessions: Dict[int, Dict[str, Any]] = {}
            self.setup_handlers()
            self.setup_error_handler()
            logger.info("🎯 ربات کنکور ۱۴۰۵ با موفقیت راه‌اندازی شد")
        except Exception as e:
            logger.critical(f"💥 خطای بحرانی در راه‌اندازی ربات: {e}")
            raise

    def setup_handlers(self):
        """تنظیم هندلرهای ربات"""
        # هندلرهای اصلی
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("test", self.test_command))
        self.application.add_handler(CommandHandler("exams", self.show_exams_menu))
        self.application.add_handler(CommandHandler("stats", self.show_stats_menu))
        self.application.add_handler(CommandHandler("admin", self.show_admin_menu))

        # هندلرهای متنی
        text_handlers = [
            MessageHandler(filters.Text(["⏳ زمان‌سنجی کنکورها"]), self.show_exams_menu),
            MessageHandler(filters.Text(["📅 برنامه مطالعاتی پیشرفته"]), self.show_study_plan_menu),
            MessageHandler(filters.Text(["📊 آمار مطالعه حرفه‌ای"]), self.show_stats_menu),
            MessageHandler(filters.Text(["👑 پنل مدیریت"]), self.show_admin_menu),
            MessageHandler(filters.Text(["🏠 منوی اصلی"]), self.back_to_main_menu),
        ]
        
        for handler in text_handlers:
            self.application.add_handler(handler)

        # هندلر پیام‌های متنی ناشناخته
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            self.handle_unknown_text
        ))

        # هندلر کال‌بک‌ها
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))

    def setup_error_handler(self):
        """تنظیم هندلر خطا"""
        self.application.add_error_handler(self.error_handler)

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور /start"""
        user = update.effective_user
        self._init_user_session(user.id)
        
        logger.info(f"🚀 کاربر جدید: {user.first_name} (ID: {user.id})")
        
        welcome_text = self._generate_welcome_message(user)
        
        try:
            await update.message.reply_text(
                welcome_text,
                reply_markup=main_menu(),
                parse_mode='HTML'
            )
            logger.info(f"✅ پیام خوشآمدگویی برای {user.id} ارسال شد")
        except Exception as e:
            logger.error(f"❌ خطا در ارسال welcome: {e}")
            await self._send_error_message(update, "خطا در ارسال پیام")

    async def test_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور تست /test"""
        user = update.effective_user
        logger.info(f"🧪 تست از کاربر: {user.first_name}")
        
        try:
            test_message = await update.message.reply_text(
                "✅ تست موفق! ربات در حال کار است.\n"
                "🎯 اکنون از منوی اصلی استفاده کنید.",
                reply_markup=main_menu()
            )
            logger.info(f"✅ تست موفق برای کاربر {user.id}")
        except Exception as e:
            logger.error(f"❌ خطا در تست: {e}")
            await self._send_error_message(update, "خطا در تست")

    async def show_exams_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش منوی کنکورها"""
        user = update.effective_user
        logger.info(f"⏰ کاربر {user.first_name} منوی کنکورها را انتخاب کرد")
        
        try:
            if update.message:
                await update.message.reply_text(
                    "🎯 انتخاب کنکور مورد نظر:",
                    reply_markup=exams_menu()
                )
            else:
                await update.callback_query.edit_message_text(
                    "🎯 انتخاب کنکور مورد نظر:",
                    reply_markup=exams_menu()
                )
            logger.info(f"✅ منوی کنکورها برای {user.id} نمایش داده شد")
        except Exception as e:
            logger.error(f"❌ خطا در نمایش منوی کنکورها: {e}")
            await self._send_error_message(update, "خطا در نمایش منوی کنکورها")

    async def show_study_plan_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش منوی برنامه مطالعاتی"""
        user = update.effective_user
        logger.info(f"📅 کاربر {user.first_name} منوی برنامه مطالعاتی را انتخاب کرد")
        
        try:
            await update.message.reply_text(
                "📅 برنامه مطالعاتی پیشرفته:\n\n"
                "🎯 این بخش به زودی فعال خواهد شد...",
                reply_markup=study_plan_menu()
            )
        except Exception as e:
            logger.error(f"❌ خطا در نمایش منوی برنامه مطالعاتی: {e}")
            await self._send_error_message(update, "خطا در نمایش منوی برنامه مطالعاتی")

    async def show_stats_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش منوی آمار مطالعه"""
        user = update.effective_user
        logger.info(f"📊 کاربر {user.first_name} منوی آمار مطالعه را انتخاب کرد")
        
        try:
            await update.message.reply_text(
                "📊 آمار مطالعه حرفه‌ای:\n\n"
                "📈 این بخش به زودی فعال خواهد شد...",
                reply_markup=stats_menu()
            )
        except Exception as e:
            logger.error(f"❌ خطا در نمایش منوی آمار مطالعه: {e}")
            await self._send_error_message(update, "خطا در نمایش منوی آمار مطالعه")

    async def show_admin_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش منوی مدیریت"""
        user = update.effective_user
        
        if user.id != ADMIN_ID:
            logger.warning(f"⚠️ دسترسی غیرمجاز به پنل مدیریت از کاربر: {user.id}")
            await update.message.reply_text("❌ دسترسی denied!")
            return
        
        logger.info(f"👑 ادمین {user.first_name} منوی مدیریت را انتخاب کرد")
        
        try:
            await update.message.reply_text(
                "👑 پنل مدیریت:\n\n"
                "🛠️ این بخش به زودی فعال خواهد شد...",
                reply_markup=admin_menu()
            )
        except Exception as e:
            logger.error(f"❌ خطا در نمایش منوی مدیریت: {e}")
            await self._send_error_message(update, "خطا در نمایش منوی مدیریت")

    async def back_to_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """بازگشت به منوی اصلی"""
        user = update.effective_user
        logger.info(f"🏠 کاربر {user.first_name} به منوی اصلی بازگشت")
        
        try:
            await update.message.reply_text(
                "🏠 منوی اصلی:",
                reply_markup=main_menu()
            )
        except Exception as e:
            logger.error(f"❌ خطا در بازگشت به منوی اصلی: {e}")
            await self._send_error_message(update, "خطا در بازگشت به منوی اصلی")

    async def handle_unknown_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت پیام‌های متنی ناشناخته"""
        user = update.effective_user
        text = update.message.text
        
        logger.info(f"📝 پیام ناشناخته از {user.first_name}: {text}")
        
        try:
            await update.message.reply_text(
                "🤔 متوجه نشدم!\n\n"
                "لطفاً از دکمه‌های منو استفاده کنید:",
                reply_markup=main_menu()
            )
        except Exception as e:
            logger.error(f"❌ خطا در پاسخ به پیام ناشناخته: {e}")

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت کلیک روی دکمه‌های اینلاین"""
        query = update.callback_query
        await query.answer()
        
        user = query.from_user
        data = query.data
        
        logger.info(f"🔘 کلیک اینلاین از {user.first_name}: {data}")
        
        try:
            if data.startswith("exam_"):
                exam_key = data.replace("exam_", "")
                await self._send_exam_countdown(query, exam_key)
            elif data == "back_to_main":
                await query.edit_message_text("🏠 منوی اصلی:", reply_markup=main_menu())
            elif data == "show_all_exams":
                await self._show_all_exams_countdown(query)
            elif data == "refresh_all":
                await self._refresh_all_exams(query)
            else:
                await query.edit_message_text("❌ دستور نامعتبر!")
                
        except Exception as e:
            logger.error(f"❌ خطا در پردازش کال‌بک: {e}")
            await query.edit_message_text("❌ خطا در پردازش درخواست!")

    async def _send_exam_countdown(self, query, exam_key: str):
        """ارسال شمارش معکوس برای یک کنکور"""
        if exam_key not in EXAMS_1405:
            await query.edit_message_text("❌ آزمون مورد نظر یافت نشد.")
            return

        exam = EXAMS_1405[exam_key]
        countdown_info = self._calculate_countdown(exam)
        
        message = self._format_exam_message(exam, countdown_info)
        
        await query.edit_message_text(
            message, 
            reply_markup=countdown_actions(exam_key), 
            parse_mode='HTML'
        )

    async def _show_all_exams_countdown(self, query):
        """نمایش زمان تمامی کنکورها"""
        message = "⏳ <b>زمان باقی‌مانده تا کنکورهای ۱۴۰۵</b>\n\n"
        
        for exam_key, exam in EXAMS_1405.items():
            countdown_info = self._calculate_countdown(exam)
            
            message += f"🎯 <b>{exam['name']}</b>\n"
            message += f"📅 {exam['persian_date']} - 🕒 {exam['time']}\n"
            message += f"⏳ {countdown_info['simple_countdown']}\n"
            message += "─" * 30 + "\n\n"
        
        message += f"💫 <i>{random.choice(MOTIVATIONAL_MESSAGES)}</i>"
        
        await query.edit_message_text(
            message, 
            reply_markup=countdown_actions(), 
            parse_mode='HTML'
        )

    async def _refresh_all_exams(self, query):
        """بروزرسانی همه کنکورها"""
        await query.edit_message_text(
            "🔄 در حال بروزرسانی اطلاعات...",
            reply_markup=exams_menu()
        )

    def _calculate_countdown(self, exam: Dict) -> Dict[str, Any]:
        """محاسبه زمان باقی‌مانده تا کنکور"""
        now = datetime.now()
        dates = exam["date"] if isinstance(exam["date"], list) else [exam["date"]]
        future_dates = [datetime(*d) for d in dates if datetime(*d) > now]

        if not future_dates:
            return {
                "has_passed": True,
                "simple_countdown": "✅ برگزار شده",
                "detailed_countdown": "⛳ همه‌ی مراحل این آزمون برگزار شده‌اند."
            }

        target = min(future_dates)
        delta = target - now
        
        return {
            "has_passed": False,
            "target_date": target,
            "simple_countdown": self._format_simple_countdown(delta),
            "detailed_countdown": self._format_detailed_countdown(delta)
        }

    def _format_exam_message(self, exam: Dict, countdown_info: Dict) -> str:
        """قالب‌بندی پیام کنکور"""
        if countdown_info["has_passed"]:
            countdown_text = countdown_info["detailed_countdown"]
        else:
            countdown_text = countdown_info["detailed_countdown"]

        motivation = f"\n\n🎯 {random.choice(MOTIVATIONAL_MESSAGES)}"

        return f"""
📘 <b>{exam['name']}</b>
📅 تاریخ: {exam['persian_date']}
🕒 ساعت: {exam['time']}

{countdown_text}
{motivation}
"""

    def _format_detailed_countdown(self, delta) -> str:
        """قالب‌بندی دقیق شمارش معکوس"""
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

    def _format_simple_countdown(self, delta) -> str:
        """قالب ساده برای نمایش همه کنکورها"""
        days = delta.days
        hours = delta.seconds // 3600
        return f"{days} روز و {hours} ساعت"

    def _generate_welcome_message(self, user) -> str:
        """تولید پیام خوشآمدگویی"""
        return f"""
👋 سلام <b>{user.first_name}</b> عزیز!
به ربات برنامه‌ریزی و شمارش معکوس <b>کنکور ۱۴۰۵</b> خوش آمدی! 🎯

📚 <b>امکانات ربات:</b>
• ⏳ شمارش معکوس کنکورها
• 📅 برنامه مطالعاتی پیشرفته  
• 📊 آمار مطالعه حرفه‌ای
• 💫 پیام‌های انگیزشی

از منوی زیر یکی از گزینه‌ها رو انتخاب کن:
"""

    def _init_user_session(self, user_id: int):
        """ایجاد سشن جدید برای کاربر"""
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                'first_seen': datetime.now(),
                'message_count': 0,
                'last_activity': datetime.now()
            }
        else:
            self.user_sessions[user_id]['last_activity'] = datetime.now()
            self.user_sessions[user_id]['message_count'] += 1

    async def _send_error_message(self, update: Update, error_msg: str):
        """ارسال پیام خطا"""
        try:
            if update.message:
                await update.message.reply_text(
                    f"❌ {error_msg}\n\n"
                    "لطفاً بعداً مجدداً تلاش کنید.",
                    reply_markup=main_menu()
                )
            elif update.callback_query:
                await update.callback_query.edit_message_text(
                    f"❌ {error_msg}"
                )
        except Exception as e:
            logger.error(f"💥 خطا در ارسال پیام خطا: {e}")

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت خطاهای全局"""
        logger.error(f"💥 خطا در پردازش آپدیت: {context.error}")
        
        try:
            if update and update.effective_user:
                await self._send_error_message(update, "خطای داخلی ربات")
        except Exception as e:
            logger.critical(f"🔥 خطا در مدیریت خطا: {e}")

# تابع برای app.py
def get_application():
    """ایجاد و بازگرداندن instance ربات"""
    return KonkourBot().application
