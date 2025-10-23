# utils/error_handler.py
import traceback
from telegram import Update
from telegram.ext import ContextTypes
from .logger import setup_logger

logger = setup_logger()

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر متمرکز برای خطاها"""
    logger.error(f"Exception while handling an update: {context.error}")
    
    # لاگ کردن traceback کامل
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)
    logger.error(f"Traceback: {tb_string}")
    
    # اطلاع به کاربر
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ خطایی رخ داد. لطفاً دوباره تلاش کنید."
        )
