import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiohttp import web
import random
from datetime import datetime
import os

from config import BOT_TOKEN, MOTIVATIONAL_MESSAGES, ADMIN_ID
from exam_data import EXAMS_1405
from keyboards import (
    main_menu, exams_menu, exam_actions_menu, 
    study_plan_menu, stats_menu, admin_menu,
    back_button_menu, confirm_cancel_menu
)
from database import Database
from utils import check_user_membership, format_time_remaining, create_membership_keyboard, get_subject_emoji

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

# تنظیمات وب‌هوک
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "https://konkour-bot-4i5p.onrender.com") + WEBHOOK_PATH

# --- میدلور بررسی عضویت ---
@dp.update.middleware()
async def membership_middleware(handler, event, data):
    """میان‌افزار برای بررسی عضویت کاربر"""
    if event.message:
        user_id = event.message.from_user.id
        user = event.message.from_user
        
        # افزودن/بروزرسانی کاربر در دیتابیس
        db.add_user(user_id, user.username or "", user.first_name, user.last_name or "")
        
        # بررسی عضویت (به جز برای دستور /start و دکمه بررسی عضویت)
        if (event.message.text != "/start" and 
            not event.message.text.startswith("/") and
            event.message.text != "✅ بررسی عضویت"):
            
            is_member = await check_user_membership(bot, user_id)
            if not is_member:
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

# --- هندلرهای اصلی ---

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    user = message.from_user
    logger.info(f"🎯 دریافت /start از {user.first_name} ({user.id})")
    
    # بررسی عضویت
    is_member = await check_user_membership(bot, user.id)
    
    if not is_member:
        channels = db.get_mandatory_channels()
        if channels:
            channel_list = "\n".join([f"• {ch['channel_title']}" for ch in channels])
            
            await message.answer(
                f"👋 سلام {user.first_name} عزیز!\n\n"
                f"🚫 <b>برای استفاده از ربات باید در کانال‌های زیر عضو باشید:</b>\n\n"
                f"{channel_list}\n\n"
                f"پس از عضویت، دکمه '✅ بررسی عضویت' را بزنید.",
                reply_markup=create_membership_keyboard(),
                parse_mode="HTML"
            )
            return
    
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
    
    user_stats = db.get_user_progress(message.from_user.id)
    
    await message.answer(
        f"📅 <b>برنامه مطالعاتی پیشرفته</b>\n\n"
        f"📊 آمار کلی شما:\n"
        f"• 🕒 کل زمان مطالعه: {user_stats['total_hours']} ساعت\n"
        f"• 📖 تعداد جلسات: {user_stats['total_sessions']} جلسه\n"
        f"• 📅 روزهای فعال: {user_stats['active_days']} روز\n\n"
        f"از گزینه‌های زیر استفاده کنید:",
        reply_markup=study_plan_menu(),
        parse_mode="HTML"
    )

@dp.message(F.text == "📊 آمار مطالعه حرفه‌ای")
async def stats_handler(message: types.Message):
    logger.info(f"📊 کاربر {message.from_user.id} منوی آمار مطالعه را انتخاب کرد")
    
    today_stats = db.get_today_study_stats(message.from_user.id)
    weekly_stats = db.get_weekly_stats(message.from_user.id)
    
    total_weekly = sum(day['total_minutes'] for day in weekly_stats)
    
    await message.answer(
        f"📊 <b>آمار مطالعه حرفه‌ای</b>\n\n"
        f"📈 <b>امروز:</b>\n"
        f"• 🕒 زمان مطالعه: {today_stats['total_minutes']} دقیقه\n"
        f"• 📖 جلسات: {today_stats['sessions_count']} جلسه\n"
        f"• 📚 دروس: {today_stats['subjects']}\n\n"
        f"📅 <b>هفته جاری:</b>\n"
        f"• 🕒 کل زمان: {total_weekly} دقیقه\n"
        f"• 📊 میانگین روزانه: {total_weekly // 7 if weekly_stats else 0} دقیقه\n\n"
        f"برای مشاهده جزئیات بیشتر از گزینه‌های زیر استفاده کنید:",
        reply_markup=stats_menu(),
        parse_mode="HTML"
    )

@dp.message(F.text == "👑 پنل مدیریت")
async def admin_handler(message: types.Message):
    user = message.from_user
    logger.info(f"👑 کاربر {user.first_name} منوی مدیریت را انتخاب کرد")
    
    if user.id != ADMIN_ID:
        await message.answer("❌ دسترسی denied!")
        return
        
    channels = db.get_mandatory_channels()
    channel_count = len(channels)
    
    await message.answer(
        f"👑 <b>پنل مدیریت</b>\n\n"
        f"📊 آمار سیستم:\n"
        f"• 👥 کانال‌های اجباری: {channel_count} کانال\n"
        f"• ⚙️ سیستم عضویت اجباری: {'فعال' if channel_count > 0 else 'غیرفعال'}\n\n"
        f"از گزینه‌های زیر برای مدیریت استفاده کنید:",
        reply_markup=admin_menu(),
        parse_mode="HTML"
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
        countdown = format_time_remaining(target)
    
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
            countdown = format_time_remaining(target)
            message += f"{countdown}\n"
        else:
            message += "✅ برگزار شده\n"
        
        message += "─" * 30 + "\n\n"
    
    message += f"💫 <i>{random.choice(MOTIVATIONAL_MESSAGES)}</i>"
    
    await callback.message.edit_text(
        message, 
        reply_markup=exam_actions_menu(), 
        parse_mode="HTML"
    )

# --- هندلرهای برنامه مطالعاتی ---

@dp.callback_query(F.data == "create_plan")
async def create_plan_handler(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📝 <b>ایجاد برنامه مطالعاتی جدید</b>\n\n"
        "این بخش به زودی فعال خواهد شد...\n"
        "در حال حاضر می‌توانید جلسات مطالعه را از بخش '⏱️ ثبت مطالعه' اضافه کنید.",
        reply_markup=back_button_menu("🔙 بازگشت به برنامه مطالعاتی", "back_to_study_plan"),
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "log_study")
async def log_study_handler(callback: types.CallbackQuery):
    # لیست دروس برای انتخاب
    subjects = [
        ("ریاضی", "ریاضی"),
        ("فیزیک", "فیزیک"), 
        ("شیمی", "شیمی"),
        ("زیست", "زیست"),
        ("ادبیات", "ادبیات"),
        ("عربی", "عربی"),
        ("دینی", "دینی"),
        ("زبان", "زبان")
    ]
    
    keyboard = []
    for subject_name, subject_code in subjects:
        emoji = get_subject_emoji(subject_name)
        keyboard.append([
            InlineKeyboardButton(
                text=f"{emoji} {subject_name}", 
                callback_data=f"log_subject_{subject_code}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_to_stats")
    ])
    
    await callback.message.edit_text(
        "⏱️ <b>ثبت جلسه مطالعه</b>\n\n"
        "لطفاً درس مورد نظر را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode="HTML"
    )

@dp.callback_query(F.data.startswith("log_subject_"))
async def log_subject_handler(callback: types.CallbackQuery):
    subject = callback.data.replace("log_subject_", "")
    subject_name = {
        "ریاضی": "ریاضی", "فیزیک": "فیزیک", "شیمی": "شیمی", 
        "زیست": "زیست", "ادبیات": "ادبیات", "عربی": "عربی",
        "دینی": "دینی", "زبان": "زبان"
    }.get(subject, "نامشخص")
    
    # ذخیره موضوع در state (در اینجا ساده شده)
    await callback.message.edit_text(
        f"⏱️ <b>ثبت مطالعه {subject_name}</b>\n\n"
        f"مدت زمان مطالعه را به دقیقه وارد کنید:\n"
        f"مثال: 120 (برای ۲ ساعت)",
        reply_markup=back_button_menu("🔙 بازگشت به انتخاب درس", "log_study"),
        parse_mode="HTML"
    )
    
    # در اینجا باید state مدیریت شود که کاربر زمان را وارد کند

# --- هندلرهای مدیریت ---

@dp.callback_query(F.data == "admin_mandatory_channels")
async def admin_channels_handler(callback: types.CallbackQuery):
    channels = db.get_mandatory_channels()
    
    if not channels:
        message = "👑 <b>مدیریت کانال‌های اجباری</b>\n\n❌ هیچ کانال اجباری تعریف نشده است."
    else:
        message = "👑 <b>مدیریت کانال‌های اجباری</b>\n\n📋 کانال‌های فعلی:\n"
        for i, channel in enumerate(channels, 1):
            message += f"{i}. {channel['channel_title']} (@{channel['channel_username']})\n"
    
    keyboard = [
        [InlineKeyboardButton(text="➕ افزودن کانال", callback_data="admin_add_channel")],
        [InlineKeyboardButton(text="🗑️ حذف کانال", callback_data="admin_remove_channel")],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_to_admin")]
    ]
    
    await callback.message.edit_text(
        message,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "admin_add_channel")
async def admin_add_channel_handler(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "👑 <b>افزودن کانال اجباری</b>\n\n"
        "لطفاً اطلاعات کانال را به فرمت زیر ارسال کنید:\n"
        "<code>آیدی_عددی @username عنوان_کانال</code>\n\n"
        "مثال:\n"
        "<code>-1001234567890 @konkour_channel کانال کنکور ۱۴۰۵</code>",
        reply_markup=back_button_menu("🔙 بازگشت", "admin_mandatory_channels"),
        parse_mode="HTML"
    )
    
    # در اینجا باید state مدیریت شود که ادمین اطلاعات کانال را وارد کند

# --- هندلر عضویت ---

@dp.callback_query(F.data == "check_membership")
async def check_membership_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    is_member = await check_user_membership(bot, user_id)
    
    if is_member:
        await callback.message.edit_text(
            "✅ <b>تبریک! شما در تمام کانال‌ها عضو هستید.</b>\n\n"
            "اکنون می‌توانید از تمام امکانات ربات استفاده کنید.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="🏠 منوی اصلی", callback_data="back_to_main")
            ]]),
            parse_mode="HTML"
        )
    else:
        await callback.answer("❌ هنوز در برخی کانال‌ها عضو نیستید!", show_alert=True)

# --- هندلرهای بازگشت ---

@dp.callback_query(F.data == "back_to_main")
async def back_to_main_handler(callback: types.CallbackQuery):
    logger.info(f"🏠 کاربر {callback.from_user.id} به منوی اصلی بازگشت")
    await callback.message.edit_text(
        "🏠 منوی اصلی:",
        reply_markup=main_menu()
    )

@dp.callback_query(F.data == "back_to_study_plan")
async def back_to_study_plan_handler(callback: types.CallbackQuery):
    await study_plan_handler(callback.message)

@dp.callback_query(F.data == "back_to_stats")
async def back_to_stats_handler(callback: types.CallbackQuery):
    await stats_handler(callback.message)

@dp.callback_query(F.data == "back_to_admin")
async def back_to_admin_handler(callback: types.CallbackQuery):
    await admin_handler(callback.message)

# --- هندلر پیام‌های ناشناخته ---
@dp.message()
async def unknown_handler(message: types.Message):
    logger.info(f"📝 پیام ناشناخته از {message.from_user.id}: {message.text}")
    await message.answer(
        "🤔 متوجه نشدم!\n\nلطفاً از دکمه‌های منو استفاده کنید:",
        reply_markup=main_menu()
    )

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
    
    # تنظیم startup/shutdown - حالا app دریافت می‌شود
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    
    # راه‌اندازی سرور
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"🚀 سرور در حال راه‌اندازی روی پورت {port}...")
    
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
