# error_handlers.py
"""
هندلرهای全局 خطا برای ربات - سازگار با Aiogram 3.x
"""
import logging
import traceback
from aiogram import Dispatcher
from aiogram.types import ErrorEvent
from aiogram.exceptions import (
    TelegramAPIError, TelegramNetworkError, 
    TelegramRetryAfter, TelegramBadRequest,
    TelegramConflictError, TelegramForbiddenError,
    TelegramNotFound, TelegramUnauthorizedError,
    TelegramMigrateToChat, TelegramEntityTooLarge
)

logger = logging.getLogger(__name__)

async def global_error_handler(event: ErrorEvent) -> bool:
    """
    هندلر全局 برای تمام خطاهای ربات - Aiogram 3.x
    """
    try:
        exception = event.exception
        update = event.update
        
        # لاگ کامل خطا
        error_info = {
            "error_type": type(exception).__name__,
            "error_message": str(exception),
            "update_type": update.event_type if update else "Unknown",
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

def register_error_handlers(dp: Dispatcher) -> None:
    """ثبت تمام هندلرهای خطا"""
    dp.errors.register(global_error_handler)
    logger.info("✅ هندلرهای خطا ثبت شدند")
