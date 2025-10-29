import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import random
from datetime import datetime
import os

from config import BOT_TOKEN, MOTIVATIONAL_MESSAGES, ADMIN_ID
from exam_data import EXAMS_1405
from keyboards import (
    main_menu, exams_menu, exam_actions_menu, 
    study_plan_menu, stats_menu, admin_menu,
    back_button_menu
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

# تنظیمات وب‌هوک
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "https://konkour-bot-4i5p.onrender.com") + WEBHOOK_PATH

# --- هندلرهای اصلی ---

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    user = message.from_user
    logger.info(f"🎯 دریافت /start از {user.first_name} ({user.id})")
    
    welcome = f"""
👋 سلام {user.first_name} عزیز!
به ربات کنکور ۱۴۰۵ خوش آمدی! 🎯

📚 <b>امکانات ربات:</b>
• ⏳ شمارش معکوس کنکورها
• 📅 برنامه مطالعاتی پیشرفته  
• 📊 آمار مطالعه حرفه‌ای
• 💫 پیام‌های انگیزشی

از منوی زیر یکی از گزینه‌ها رو انتخاب کن:
"""
    await message.answer(welcome, reply_markup=main_menu(), parse_mode="HTML")

@dp.message(Command("test"))
async def test_handler(message: types.Message):
    logger.info(f"🧪 دریافت /test از {message.from_user.id}")
    await message.answer("✅ ربات با aiogram + webhook کار می‌کند! تست موفق.")

# --- هندلرهای منوی اصلی ---

@dp.message(F.text == "⏳ زمان‌سنجی کنکورها")
async def exams_menu_handler(message: types.Message):
    logger.info(f"⏰ کاربر {message.from_user.id} منوی کنکورها را انتخاب کرد")
    await message.answer("🎯 انتخاب کنکور مورد نظر:", reply_markup=exams_menu())

@dp.message(F.text == "📅 برنامه مطالعاتی پیشرفته")
async def study_plan_handler(message: types.Message):
    logger.info(f"📅 کاربر {message.from_user.id} منوی برنامه مطالعاتی را انتخاب کرد")
    await message.answer(
        "📅 برنامه مطالعاتی پیشرفته:\n\n"
        "🎯 این بخش به زودی فعال خواهد شد...",
        reply_markup=study_plan_menu()
    )

@dp.message(F.text == "📊 آمار مطالعه حرفه‌ای")
async def stats_handler(message: types.Message):
    logger.info(f"📊 کاربر {message.from_user.id} منوی آمار مطالعه را انتخاب کرد")
    await message.answer(
        "📊 آمار مطالعه حرفه‌ای:\n\n"
        "📈 این بخش به زودی فعال خواهد شد...",
        reply_markup=stats_menu()
    )

@dp.message(F.text == "👑 پنل مدیریت")
async def admin_handler(message: types.Message):
    user = message.from_user
    logger.info(f"👑 کاربر {user.first_name} منوی مدیریت را انتخاب کرد")
    
    if user.id != ADMIN_ID:
        await message.answer("❌ دسترسی denied!")
        return
        
    await message.answer(
        "👑 پنل مدیریت:\n\n"
        "🛠️ این بخش به زودی فعال خواهد شد...",
        reply_markup=admin_menu()
    )

# --- هندلرهای کال‌بک ---

@dp.callback_query(F.data.startswith("exam_"))
async def exam_callback_handler(callback: types.CallbackQuery):
    exam_key = callback.data.replace("exam_", "")
    logger.info(f"🔘 کلیک روی کنکور: {exam_key}")
    
    if exam_key not in EXAMS_1405:
        await callback.answer("❌ آزمون یافت نشد")
        return
    
    exam = EXAMS_1405[exam_key]
    now = datetime.now()
    
    dates = exam["date"] if isinstance(exam["date"], list) else [exam["date"]]
    future_dates = [datetime(*d) for d in dates if datetime(*d) > now]
    
    if not future_dates:
        countdown = "✅ برگزار شده"
    else:
        target = min(future_dates)
        delta = target - now
        days = delta.days
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        countdown = f"⏳ {days} روز و {hours} ساعت و {minutes} دقیقه باقی مانده"
    
    message = f"""
📘 <b>{exam['name']}</b>
📅 تاریخ: {exam['persian_date']}
🕒 ساعت: {exam['time']}

{countdown}

🎯 {random.choice(MOTIVATIONAL_MESSAGES)}
"""
    await callback.message.edit_text(
        message, 
        reply_markup=exam_actions_menu(exam_key), 
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "show_all_exams")
async def all_exams_handler(callback: types.CallbackQuery):
    logger.info(f"📋 کاربر {callback.from_user.id} همه کنکورها را انتخاب کرد")
    
    message = "⏳ <b>زمان باقی‌مانده تا کنکورهای ۱۴۰۵</b>\n\n"
    
    for exam_key, exam in EXAMS_1405.items():
        now = datetime.now()
        dates = exam["date"] if isinstance(exam["date"], list) else [exam["date"]]
        future_dates = [datetime(*d) for d in dates if datetime(*d) > now]
        
        message += f"🎯 <b>{exam['name']}</b>\n"
        message += f"📅 {exam['persian_date']} - 🕒 {exam['time']}\n"
        
        if future_dates:
            target = min(future_dates)
            delta = target - now
            message += f"⏳ {delta.days} روز و {delta.seconds // 3600} ساعت باقی مانده\n"
        else:
            message += "✅ برگزار شده\n"
        
        message += "─" * 30 + "\n\n"
    
    message += f"💫 <i>{random.choice(MOTIVATIONAL_MESSAGES)}</i>"
    
    await callback.message.edit_text(
        message, 
        reply_markup=exam_actions_menu(), 
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "back_to_main")
async def back_to_main_handler(callback: types.CallbackQuery):
    logger.info(f"🏠 کاربر {callback.from_user.id} به منوی اصلی بازگشت")
    await callback.message.edit_text(
        "🏠 منوی اصلی:",
        reply_markup=main_menu()
    )

# --- هندلر پیام‌های ناشناخته ---
@dp.message()
async def unknown_handler(message: types.Message):
    logger.info(f"📝 پیام ناشناخته از {message.from_user.id}: {message.text}")
    await message.answer(
        "🤔 متوجه نشدم!\n\nلطفاً از دکمه‌های منو استفاده کنید:",
        reply_markup=main_menu()
    )

# --- توابع راه‌اندازی وب‌هوک ---
async def on_startup(bot: Bot):
    """تنظیم وب‌هوک هنگام راه‌اندازی"""
    webhook_url = os.environ.get("WEBHOOK_URL", "https://konkour-bot-4i5p.onrender.com") + "/webhook"
    await bot.set_webhook(webhook_url)
    logger.info(f"✅ وب‌هوک تنظیم شد: {webhook_url}")

async def on_shutdown(bot: Bot):
    """پاک کردن وب‌هوک هنگام خاموشی"""
    await bot.delete_webhook()
    logger.info("❌ وب‌هوک حذف شد")

def main():
    """تابع اصلی راه‌اندازی"""
    app = web.Application()
    
    # ثبت هندلر وب‌هوک
    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    ).register(app, path="/webhook")
    
    # تنظیم startup/shutdown
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    
    # راه‌اندازی سرور
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"🚀 سرور در حال راه‌اندازی روی پورت {port}...")
    
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
