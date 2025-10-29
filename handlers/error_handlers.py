"""
هندلرهای全局 خطا برای ربات
"""
import logging
import traceback
from typing import Any
from aiogram import Dispatcher, types
from aiogram.exceptions import (
    TelegramAPIError, TelegramNetworkError, 
    TelegramRetryAfter, TelegramBadRequest,
    TelegramConflictError, TelegramForbiddenError,
    TelegramNotFound, TelegramUnauthorizedError,
    TelegramMigrateToChat, TelegramEntityTooLarge
)

logger = logging.getLogger(__name__)

async def global_error_handler(update: types.Update, exception: Exception) -> bool:
    """
    هندلر全局 برای تمام خطاهای ربات
    """
    try:
        # لاگ کامل خطا
        error_info = {
            "error_type": type(exception).__name__,
            "error_message": str(exception),
            "update_type": update.update_type if update else "Unknown",
            "traceback": traceback.format_exc()
        }
        
        logger.error(f"🔥 خطای全局: {error_info}")
        
        # مدیریت خطاهای خاص تلگرام
        if isinstance(exception, TelegramRetryAfter):
            retry_after = exception.retry_after
            logger.warning(f"⏳ محدودیت Rate Limit - انتظار {retry_after} ثانیه")
            return True
            
        elif isinstance(exception, TelegramBadRequest):
            logger.error(f"❌ درخواست نامعتبر: {exception}")
            # معمولاً مشکل از سمت ماست - نیاز به fix داره
            return True
            
        elif isinstance(exception, TelegramForbiddenError):
            logger.warning(f"🚫 دسترسی ممنوع - ربات از گروه/کانال حذف شده")
            return True
            
        elif isinstance(exception, TelegramNotFound):
            logger.warning(f"🔍 منبع یافت نشد - ممکن است کاربر ربات را بلاک کرده باشد")
            return True
            
        elif isinstance(exception, TelegramUnauthorizedError):
            logger.critical(f"🔐 توکن نامعتبر - نیاز به بررسی فوری")
            return True
            
        elif isinstance(exception, TelegramNetworkError):
            logger.warning(f"🌐 خطای شبکه - احتمالاً موقتی است")
            return True
            
        elif isinstance(exception, TelegramEntityTooLarge):
            logger.error(f"📦 داده بسیار حجیم - نیاز به تقسیم")
            return True
            
        # خطاهای دیتابیس
        elif "database" in str(exception).lower() or "sql" in str(exception).lower():
            logger.critical(f"🗄️ خطای دیتابیس: {exception}")
            # تلاش برای reconnect
            await handle_database_error()
            return True
            
        # خطاهای memory
        elif "memory" in str(exception).lower() or "out of memory" in str(exception).lower():
            logger.critical(f"💾 خطای حافظه - پاکسازی کش‌ها")
            await handle_memory_error()
            return True
            
        # سایر خطاها
        else:
            logger.error(f"❓ خطای ناشناخته: {exception}")
            return True
            
    except Exception as fatal_error:
        # اگر خود هندلر خطا crash کند
        logger.critical(f"💥 خطای بحرانی در هندلر خطا: {fatal_error}")
        return False

async def handle_database_error():
    """مدیریت خطاهای دیتابیس"""
    try:
        from database import Database
        db = Database()
        # تلاش برای reconnect
        db.get_connection().close()
        logger.info("🔄 تلاش برای reconnect به دیتابیس")
    except Exception as e:
        logger.error(f"❌ reconnect دیتابیس ناموفق: {e}")

async def handle_memory_error():
    """مدیریت خطاهای حافظه"""
    try:
        # پاکسازی کش‌های global
        from main import _CACHE
        _CACHE.clear()
        logger.info("🧹 کش‌های حافظه پاکسازی شدند")
        
        # جمع‌آوری حافظه
        import gc
        gc.collect()
        logger.info("🔧 GC اجرا شد")
    except Exception as e:
        logger.error(f"❌ پاکسازی حافظه ناموفق: {e}")

async def message_error_handler(update: types.Update, exception: Exception) -> bool:
    """هندلر مخصوص خطاهای مربوط به پیام‌ها"""
    if update.message:
        try:
            await update.message.answer(
                "❌ متأسفانه در پردازش درخواست شما خطایی رخ داد.\n"
                "لطفاً稍后 مجدداً尝试 کنید یا با پشتیبانی تماس بگیرید."
            )
        except:
            pass  # اگر حتی ارسال پیام خطا هم fail شد
    return True

def register_error_handlers(dp: Dispatcher) -> None:
    """ثبت تمام هندلرهای خطا"""
    dp.errors.register(global_error_handler)
    dp.errors.register(message_error_handler)
    
    logger.info("✅ هندلرهای خطا ثبت شدند")
