import logging
import os
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی
load_dotenv()

# ایمپورت سیستم مقاوم‌سازی
from error_handlers import register_error_handlers
from health_monitor import health_monitor, health_check_handler, readiness_check_handler
from circuit_breaker import database_breaker, webhook_breaker

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# کش global
_CACHE = {}

# ایجاد ربات و دیسپچر
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8381121739:AAFB2YBMomBh9xhoI3Qn0VVuGaGlpea9fx8")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ثبت هندلرهای خطا
register_error_handlers(dp)

# --- ایمپورت و ثبت هندلرها ---
# (همانند قبل، اما با استفاده از circuit breaker)

async def safe_startup():
    """راه‌اندازی ایمن با Circuit Breaker"""
    try:
        # راه‌اندازی وب‌هوک با محافظت
        webhook_url = os.environ.get("WEBHOOK_URL", "").replace('/webhook', '') + '/webhook'
        if not webhook_url.startswith('http'):
            webhook_url = f"https://{os.environ.get('RENDER_SERVICE_NAME', '')}.onrender.com/webhook"
        
        await webhook_breaker.call(bot.set_webhook, webhook_url)
        logger.info(f"✅ وب‌هوک تنظیم شد: {webhook_url}")
        
        # شروع مانیتورینگ سلامت
        asyncio.create_task(health_monitor.periodic_health_check())
        logger.info("✅ مانیتور سلامت فعال شد")
        
    except Exception as e:
        logger.critical(f"❌ راه‌اندازی ناموفق: {e}")
        raise

async def safe_shutdown():
    """خاموشی ایمن"""
    try:
        await webhook_breaker.call(bot.delete_webhook)
        logger.info("✅ وب‌هوک حذف شد")
    except Exception as e:
        logger.error(f"⚠️ خطا در خاموشی: {e}")

# --- توابع اصلی ---
async def on_startup(app: web.Application):
    """هندلر راه‌اندازی"""
    await safe_startup()

async def on_shutdown(app: web.Application):
    """هندلر خاموشی"""
    await safe_shutdown()

def main():
    """تابع اصلی"""
    app = web.Application()
    
    # وب‌هوک
    webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_requests_handler.register(app, path="/webhook")
    
    # routes سلامت
    app.router.add_get('/', health_check_handler)
    app.router.add_get('/health', health_check_handler)
    app.router.add_get('/ready', readiness_check_handler)
    app.router.add_get('/metrics', health_check_handler)
    
    # events
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    
    # راه‌اندازی
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"🚀 سرور مقاوم‌سازی شده روی پورت {port}")
    
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
