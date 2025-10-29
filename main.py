import logging
import os
import asyncio
import functools
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی
load_dotenv()

# تنظیمات لاگ بهینه
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# کش global برای داده‌های پرکاربرد
_CACHE = {}

# Lazy imports با کش
@functools.lru_cache(maxsize=1)
def get_config():
    from config import BOT_TOKEN, ADMIN_ID
    return BOT_TOKEN, ADMIN_ID

@functools.lru_cache(maxsize=1)  
def get_bot():
    BOT_TOKEN, _ = get_config()
    return Bot(token=BOT_TOKEN)

@functools.lru_cache(maxsize=1)
def get_dispatcher():
    return Dispatcher()

# ایمپورت‌های سنگین فقط وقتی نیاز هستن
def get_exam_data():
    if 'exam_data' not in _CACHE:
        from exam_data import EXAMS_1405
        _CACHE['exam_data'] = EXAMS_1405
    return _CACHE['exam_data']

def get_database():
    if 'db' not in _CACHE:
        from database import Database
        _CACHE['db'] = Database()
    return _CACHE['db']

# هندلرهای سریع - ایمپورت وقتی نیاز هست
async def start_handler(message: types.Message):
    from handlers.main_handlers import start_handler as _start_handler
    return await _start_handler(message, get_bot())

async def exam_callback_handler(callback: types.CallbackQuery):
    from handlers.exam_handlers import exam_callback_handler as _handler
    return await _handler(callback)

# بقیه هندلرها به همین شکل...

# ایجاد ربات و دیسپچر
bot = get_bot()
dp = get_dispatcher()

# --- میدلور سریع‌تر ---
@dp.update.middleware()
async def fast_membership_middleware(handler, event, data):
    if event.message:
        user_id = event.message.from_user.id
        user = event.message.from_user
        
        db = get_database()
        db.add_user(user_id, user.username or "", user.first_name, user.last_name or "")
        
        if (event.message.text != "/start" and 
            not event.message.text.startswith("/") and
            event.message.text != "✅ بررسی عضویت"):
            
            from utils import check_user_membership
            is_member = await check_user_membership(bot, user_id)
            if not is_member:
                from utils import create_membership_keyboard
                channels = db.get_mandatory_channels()
                if channels:
                    channel_list = "\n".join([f"• {ch['channel_title']}" for ch in channels])
                    await event.message.answer(
                        f"🚫 برای استفاده از ربات باید در کانال‌ها عضو باشید.",
                        reply_markup=create_membership_keyboard(),
                        parse_mode="HTML"
                    )
                    return
    
    return await handler(event, data)

# --- ثبت هندلرهای اصلی ---
@dp.message(CommandStart())
async def start_wrapper(message: types.Message):
    await start_handler(message)

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

# --- هندلر سلامت ---
async def health_check(request):
    return web.Response(text="✅ ربات کنکور ۱۴۰۵ فعال است!")

# --- Keep Alive ---
async def keep_alive():
    """پینگ دوره‌ای برای جلوگیری از sleep"""
    import aiohttp
    while True:
        await asyncio.sleep(300)  # هر 5 دقیقه
        try:
            webhook_url = os.environ.get("WEBHOOK_URL", "").replace('/webhook', '')
            if webhook_url:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f'{webhook_url}/health', timeout=10) as resp:
                        logger.info("🔄 Keep alive ping sent")
        except Exception as e:
            logger.warning(f"⚠️ Keep alive failed: {e}")

# --- راه‌اندازی ---
async def on_startup(app: web.Application):
    webhook_url = os.environ.get("WEBHOOK_URL", "").replace('/webhook', '') + '/webhook'
    if not webhook_url.startswith('http'):
        webhook_url = f"https://{os.environ.get('RENDER_SERVICE_NAME', '')}.onrender.com/webhook"
    
    logger.info(f"🔄 تنظیم وب‌هوک: {webhook_url}")
    await bot.set_webhook(webhook_url)
    logger.info("✅ وب‌هوک تنظیم شد")
    
    # شروع keep alive
    asyncio.create_task(keep_alive())

async def on_shutdown(app: web.Application):
    await bot.delete_webhook()
    logger.info("❌ وب‌هوک حذف شد")

def main():
    app = web.Application()
    
    # وب‌هوک
    webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_requests_handler.register(app, path="/webhook")
    
    # routes
    app.router.add_get('/', health_check)
    app.router.add_get('/health', health_check)
    
    # events
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    
    # راه‌اندازی
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"🚀 سرور روی پورت {port}")
    web.run_app(app, host="0.0.0.0", port=port, access_log=None)  # غیرفعال کردن access log برای سرعت

if __name__ == "__main__":
    main()
