import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.fsm.context import FSMContext
from aiohttp import web

from config import BOT_TOKEN
from database import Database

# ایمپورت هندلرها
from handlers.main_handlers import (
    start_handler, test_handler, stats_command_handler, unknown_handler
)
from handlers.menu_handlers import (
    exams_menu_handler, study_plan_handler, stats_handler, admin_handler
)
from handlers.exam_handlers import (
    exam_callback_handler, all_exams_handler, refresh_exam_handler,
    refresh_all_exams_handler, next_exam_handler, exam_details_handler
)
from handlers.study_handlers import (
    today_stats_handler, weekly_stats_handler, log_study_handler,
    log_subject_handler, process_study_duration
)
from handlers.admin_handlers import (
    admin_channels_handler, admin_add_channel_handler, process_channel_info
)
from handlers.membership_handlers import check_membership_handler
from handlers.back_handlers import (
    back_to_main_handler, back_to_stats_handler, 
    back_to_study_handler, back_to_admin_handler
)

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ایجاد ربات و دیسپچر
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
db = Database()

# --- میدلور بررسی عضویت ---
@dp.update.middleware()
async def membership_middleware(handler, event, data):
    """میان‌افزار برای بررسی عضویت کاربر"""
    from handlers.main_handlers import start_handler
    from utils import check_user_membership
    from database import Database
    
    db = Database()
    
    if event.message:
        user_id = event.message.from_user.id
        user = event.message.from_user
        
        # افزودن/بروزرسانی کاربر در دیتابیس
        db.add_user(user_id, user.username or "", user.first_name, user.last_name or "")
        
        # بررسی عضویت (به جز برای دستور /start و دکمه بررسی عضویت)
        if (event.message.text != "/start" and 
            not event.message.text.startswith("/") and
            event.message.text != "✅ بررسی عضویت" and
            not event.message.text.startswith("🏠")):
            
            is_member = await check_user_membership(bot, user_id)
            if not is_member:
                from utils import create_membership_keyboard
                from database import Database
                
                db = Database()
                channels = db.get_mandatory_channels()
                if channels:
                    channel_list = "\n".join([f"• {ch['channel_title']}" for ch in channels])
                    
                    await event.message.answer(
                        f"🚫 <b>برای استفاده از ربات باید در کانال‌های زیر عضو باشید:</b>\n\n"
                        f"{channel_list}\n\n"
                        f"پس از عضویت، دکمه '✅ بررسی عضویت' را بزنید.",
                        reply_markup=create_membership_keyboard(),
                        parse_mode="HTML"
                    )
                    return
    
    return await handler(event, data)

# --- ثبت هندلرهای اصلی ---
@dp.message(CommandStart())
async def start_wrapper(message: types.Message):
    await start_handler(message, bot)

@dp.message(Command("test"))
async def test_wrapper(message: types.Message):
    await test_handler(message)

@dp.message(Command("stats"))
async def stats_wrapper(message: types.Message):
    await stats_command_handler(message)

# --- ثبت هندلرهای منو ---
@dp.message(F.text == "⏳ زمان‌سنجی کنکورها")
async def exams_wrapper(message: types.Message):
    await exams_menu_handler(message)

@dp.message(F.text == "📅 برنامه مطالعاتی پیشرفته")
async def study_wrapper(message: types.Message):
    await study_plan_handler(message)

@dp.message(F.text == "📊 آمار مطالعه حرفه‌ای")
async def stats_menu_wrapper(message: types.Message):
    await stats_handler(message)

@dp.message(F.text == "👑 پنل مدیریت")
async def admin_wrapper(message: types.Message):
    await admin_handler(message)

# --- ثبت هندلرهای کنکور ---
@dp.callback_query(F.data.startswith("exam:"))
async def exam_wrapper(callback: types.CallbackQuery):
    await exam_callback_handler(callback)

@dp.callback_query(F.data == "exams:all")
async def all_exams_wrapper(callback: types.CallbackQuery):
    await all_exams_handler(callback)

@dp.callback_query(F.data.startswith("refresh:"))
async def refresh_exam_wrapper(callback: types.CallbackQuery):
    await refresh_exam_handler(callback)

@dp.callback_query(F.data == "exams:refresh")
async def refresh_all_wrapper(callback: types.CallbackQuery):
    await refresh_all_exams_handler(callback)

@dp.callback_query(F.data == "exams:next")
async def next_exam_wrapper(callback: types.CallbackQuery):
    await next_exam_handler(callback)

@dp.callback_query(F.data.startswith("details:"))
async def details_wrapper(callback: types.CallbackQuery):
    await exam_details_handler(callback)

# --- ثبت هندلرهای مطالعه ---
@dp.callback_query(F.data == "stats:today")
async def today_stats_wrapper(callback: types.CallbackQuery):
    await today_stats_handler(callback)

@dp.callback_query(F.data == "stats:weekly")
async def weekly_stats_wrapper(callback: types.CallbackQuery):
    await weekly_stats_handler(callback)

@dp.callback_query(F.data == "study:log")
async def log_study_wrapper(callback: types.CallbackQuery, state: FSMContext):
    await log_study_handler(callback, state)

@dp.callback_query(F.data.startswith("study:subject:"))
async def log_subject_wrapper(callback: types.CallbackQuery, state: FSMContext):
    await log_subject_handler(callback, state)

@dp.message(F.state == "waiting_for_duration")
async def process_duration_wrapper(message: types.Message, state: FSMContext):
    await process_study_duration(message, state)

# --- ثبت هندلرهای مدیریت ---
@dp.callback_query(F.data == "admin:channels")
async def admin_channels_wrapper(callback: types.CallbackQuery):
    await admin_channels_handler(callback)

@dp.callback_query(F.data == "admin:add_channel")
async def admin_add_channel_wrapper(callback: types.CallbackQuery, state: FSMContext):
    await admin_add_channel_handler(callback, state, bot)

@dp.message(F.state == "waiting_for_channel_info")
async def process_channel_wrapper(message: types.Message, state: FSMContext):
    await process_channel_info(message, state, bot)

# --- ثبت هندلرهای عضویت ---
@dp.callback_query(F.data == "check_membership")
async def check_membership_wrapper(callback: types.CallbackQuery):
    await check_membership_handler(callback, bot)

# --- ثبت هندلرهای بازگشت ---
@dp.callback_query(F.data == "main:back")
async def back_main_wrapper(callback: types.CallbackQuery):
    await back_to_main_handler(callback)

@dp.callback_query(F.data == "stats:back")
async def back_stats_wrapper(callback: types.CallbackQuery):
    await back_to_stats_handler(callback)

@dp.callback_query(F.data == "study:back")
async def back_study_wrapper(callback: types.CallbackQuery):
    await back_to_study_handler(callback)

@dp.callback_query(F.data == "admin:back")
async def back_admin_wrapper(callback: types.CallbackQuery):
    await back_to_admin_handler(callback)

# --- هندلر پیام‌های ناشناخته ---
@dp.message()
async def unknown_wrapper(message: types.Message):
    await unknown_handler(message)

# --- توابع راه‌اندازی وب‌هوک ---
async def on_startup(app: web.Application):
    """تنظیم وب‌هوک هنگام راه‌اندازی"""
    webhook_url = os.environ.get("WEBHOOK_URL", "https://konkour-bot-4i5p.onrender.com") + "/webhook"
    await bot.set_webhook(webhook_url)
    logger.info(f"✅ وب‌هوک تنظیم شد: {webhook_url}")

async def on_shutdown(app: web.Application):
    """پاک کردن وب‌هوک هنگام خاموشی"""
    await bot.delete_webhook()
    logger.info("❌ وب‌هوک حذف شد")

def main():
    """تابع اصلی راه‌اندازی"""
    app = web.Application()
    
    # ثبت هندلر وب‌هوک
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_requests_handler.register(app, path="/webhook")
    
    # تنظیم startup/shutdown
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    
    # راه‌اندازی سرور
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"🚀 سرور در حال راه‌اندازی روی پورت {port}...")
    
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
