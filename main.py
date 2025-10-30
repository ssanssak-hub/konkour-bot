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

# ایمپورت سیستم مقاوم‌سازی از پوشه utils
from utils.error_handlers import register_error_handlers
from utils.health_monitor import health_monitor, health_check_handler, readiness_check_handler
from utils.circuit_breaker import database_breaker, webhook_breaker

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

# --- ایمپورت هندلرهای اصلی ---
@dp.message(CommandStart())
async def start_wrapper(message: types.Message):
    from handlers.main_handlers import start_handler
    await start_handler(message, bot)

@dp.message(Command("test"))
async def test_wrapper(message: types.Message):
    from handlers.main_handlers import test_handler
    await test_handler(message)

@dp.message(Command("stats"))
async def stats_wrapper(message: types.Message):
    from handlers.main_handlers import stats_command_handler
    await stats_command_handler(message)

# --- هندلرهای منو ---
@dp.message(F.text == "⏳ زمان‌سنجی کنکورها")
async def exams_wrapper(message: types.Message):
    from handlers.menu_handlers import exams_menu_handler
    await exams_menu_handler(message)

@dp.message(F.text == "📅 برنامه مطالعاتی پیشرفته")
async def study_wrapper(message: types.Message):
    from handlers.menu_handlers import study_plan_handler
    await study_plan_handler(message)

@dp.message(F.text == "📊 آمار مطالعه حرفه‌ای")
async def stats_menu_wrapper(message: types.Message):
    from handlers.menu_handlers import stats_handler
    await stats_handler(message)

@dp.message(F.text == "👑 پنل مدیریت")
async def admin_wrapper(message: types.Message):
    from handlers.menu_handlers import admin_handler
    await admin_handler(message)

# --- هندلرهای کنکور ---
@dp.callback_query(F.data.startswith("exam:"))
async def exam_wrapper(callback: types.CallbackQuery):
    from handlers.exam_handlers import exam_callback_handler
    await exam_callback_handler(callback)

@dp.callback_query(F.data == "exams:all")
async def all_exams_wrapper(callback: types.CallbackQuery):
    from handlers.exam_handlers import all_exams_handler
    await all_exams_handler(callback)

@dp.callback_query(F.data.startswith("refresh:"))
async def refresh_exam_wrapper(callback: types.CallbackQuery):
    from handlers.exam_handlers import refresh_exam_handler
    await refresh_exam_handler(callback)

@dp.callback_query(F.data == "exams:refresh")
async def refresh_all_wrapper(callback: types.CallbackQuery):
    from handlers.exam_handlers import refresh_all_exams_handler
    await refresh_all_exams_handler(callback)

@dp.callback_query(F.data == "exams:next")
async def next_exam_wrapper(callback: types.CallbackQuery):
    from handlers.exam_handlers import next_exam_handler
    await next_exam_handler(callback)

@dp.callback_query(F.data.startswith("details:"))
async def details_wrapper(callback: types.CallbackQuery):
    from handlers.exam_handlers import exam_details_handler
    await exam_details_handler(callback)

# --- هندلرهای بازگشت ---
@dp.callback_query(F.data == "main:back")
async def back_main_wrapper(callback: types.CallbackQuery):
    from handlers.back_handlers import back_to_main_handler
    await back_to_main_handler(callback)

# --- توابع اصلی ---
async def safe_startup():
    """راه‌اندازی ایمن با Circuit Breaker"""
    try:
        logger.info("🚀 شروع راه‌اندازی ربات...")
        
        # ۱. حذف وب‌هوک قبلی و پاکسازی پیام‌های pending
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("🗑️ وب‌هوک قبلی حذف شد + پیام‌های pending پاک شد")
        
        # ۲. ساخت آدرس وب‌هوک
        webhook_url = "https://8381121739.railway.app/webhook"
        logger.info(f"🔗 آدرس وب‌هوک: {webhook_url}")
        
        # ۳. تنظیم وب‌هوک جدید
        await bot.set_webhook(webhook_url)
        logger.info(f"✅ وب‌هوک تنظیم شد: {webhook_url}")
        
        # ۴. بررسی وضعیت وب‌هوک
        webhook_info = await bot.get_webhook_info()
        logger.info(f"📡 وضعیت وب‌هوک: {webhook_info}")
        
        # ۵. شروع مانیتورینگ سلامت
        asyncio.create_task(health_monitor.periodic_health_check())
        logger.info("✅ مانیتور سلامت فعال شد")
        
        logger.info("🎉 راه‌اندازی با موفقیت انجام شد")
        
    except Exception as e:
        logger.critical(f"❌ راه‌اندازی ناموفق: {e}")
        raise
        
async def safe_shutdown():
    """خاموشی ایمن"""
    try:
        await webhook_breaker.call(bot.delete_webhook)
        logger.info("✅ وب‌هوک حذف شد")
        
        # بستن session های باز
        await bot.session.close()
        logger.info("✅ sessionهای ربات بسته شدند")
        
    except Exception as e:
        logger.error(f"⚠️ خطا در خاموشی: {e}")

async def on_startup(app: web.Application):
    """هندلر راه‌اندازی"""
    await safe_startup()

async def on_shutdown(app: web.Application):
    """هندلر خاموشی"""
    await safe_shutdown()

# هندلرهای سلامت
async def home_handler(request):
    """هندلر صفحه اصلی"""
    return web.Response(text="🎯 ربات کنکور فعال است - Railway")

async def railway_check_handler(request):
    """هندلر مخصوص Railway برای بررسی سلامت"""
    return web.Response(text="🚀 Bot Server is Running on Railway!")

@dp.message()
async def debug_all_messages(message: types.Message):
    """هندلر دیباگ برای لاگ تمام پیام‌ها"""
    logger.info(f"🔔 پیام دریافت شد: user_id={message.from_user.id}, text='{message.text}'")
    await message.answer("🤖 ربات فعال است! پیام شما: " + message.text)

def main():
    """تابع اصلی"""
    app = web.Application()
    
    # اضافه کردن هندلر برای Railway
    app.router.add_get('/railway-check', railway_check_handler)
    app.router.add_get('/', home_handler)
    
    # 🔴 🔴 🔴 تصحیح این بخش - مشکل اصلی اینجا بود!
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot
    )
    webhook_requests_handler.register(app, path="/webhook")
    
    # routes سلامت
    app.router.add_get('/health', health_check_handler)
    app.router.add_get('/ready', readiness_check_handler)
    app.router.add_get('/metrics', health_check_handler)
    
    # events
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    
    # راه‌اندازی - Railway از پورت 8000 استفاده می‌کند
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"🚀 سرور مقاوم‌سازی شده روی پورت {port} (Railway)")
    
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
