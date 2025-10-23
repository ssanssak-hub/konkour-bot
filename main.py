from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from handlers.main_menu import setup_main_menu_handlers
from handlers.countdown import setup_countdown_handlers
from handlers.calendar import setup_calendar_handlers
from handlers.reminders import setup_reminders_handlers
from handlers.messages import setup_messages_handlers
from handlers.attendance import setup_attendance_handlers
from handlers.study_plan import setup_study_plan_handlers
from handlers.statistics import setup_statistics_handlers
from handlers.help import setup_help_handlers
from handlers.admin import setup_admin_handlers
from database.base import db
import config
import logging

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

def setup_handlers(application):
    """تنظیم تمام هندلرهای ربات"""
    logger.info("🔧 در حال تنظیم هندلرها...")
    
    setup_main_menu_handlers(application)
    setup_countdown_handlers(application)
    setup_calendar_handlers(application)
    setup_reminders_handlers(application)
    setup_messages_handlers(application)
    setup_attendance_handlers(application)
    setup_study_plan_handlers(application)
    setup_statistics_handlers(application)
    setup_help_handlers(application)
    setup_admin_handlers(application)
    
    logger.info("✅ تمام هندلرها تنظیم شدند")
    
    # هندلر برای پیام‌های متنی عمومی
    async def handle_unknown_message(update, context):
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        keyboard = [
            [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🤔 متوجه پیام شما نشدم!\n\n"
            "لطفاً از منوی اصلی استفاده کنید یا دستور /start را وارد کنید.",
            reply_markup=reply_markup
        )
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_unknown_message), group=100)

def setup_error_handler(application):
    """تنظیم هندلر خطاها"""
    async def error_handler(update, context):
        logger.error(f"خطا رخ داد: {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ متأسفانه خطایی رخ داد!\n\n"
                "لطفاً دوباره تلاش کنید یا با ادمین تماس بگیرید."
            )
    
    application.add_error_handler(error_handler)

def initialize_database():
    """راه‌اندازی اولیه دیتابیس"""
    try:
        db.create_tables()
        logger.info("✅ جداول دیتابیس ایجاد شدند")
        return True
    except Exception as e:
        logger.error(f"❌ خطا در ایجاد جداول دیتابیس: {e}")
        return False

def main():
    """تابع اصلی برای اجرای ربات با Polling"""
    logger.info("🚀 در حال راه‌اندازی ربات با Polling...")
    
    # راه‌اندازی دیتابیس
    if not initialize_database():
        return

    # ایجاد اپلیکیشن
    application = Application.builder().token(config.Config.BOT_TOKEN).build()
    
    # تنظیم هندلرها
    setup_handlers(application)
    setup_error_handler(application)
    
    # شروع بات با Polling
    logger.info("🤖 ربات در حال راه‌اندازی با Polling...")
    logger.info("💡 برای تست محلی از این حالت استفاده کنید")
    logger.info("🌐 برای production از app.py با Webhook استفاده کنید")
    
    application.run_polling()

if __name__ == '__main__':
    main()
