import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# تنظیمات ساده لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ایجاد Application
application = Application.builder().token("8381121739:AAFB2YBMomBh9xhoI3Qn0VVuGaGlpea9fx8").build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("🎯 تابع start اجرا شد!")
    await update.message.reply_text("✅ ربات کار می‌کند! تست موفق.")

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("🧪 تابع test اجرا شد!")
    await update.message.reply_text("🧪 تست موفق! همه چیز درست است.")

# ثبت فقط دو هندلر ساده
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("test", test))

logger.info("✅ هندلرهای ساده ثبت شدند")

def get_application():
    return application
