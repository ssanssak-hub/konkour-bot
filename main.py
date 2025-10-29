import logging
import asyncio
import random
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiohttp import web
import os
import sqlite3

from config import BOT_TOKEN, MOTIVATIONAL_MESSAGES, ADMIN_ID
from exam_data import EXAMS_1405
from keyboards import (
    main_menu, exams_menu, exam_actions_menu, 
    study_plan_menu, stats_menu, admin_menu,
    back_button_menu, confirm_cancel_menu
)
from database import Database
from utils import (
    check_user_membership, format_time_remaining, 
    format_time_remaining_detailed, create_membership_keyboard,
    get_subject_emoji, get_study_tips, calculate_study_progress,
    format_study_time, get_motivational_quote, create_study_plan_keyboard,
    create_stats_keyboard, calculate_streak, get_next_exam,
    create_admin_stats_message
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

# حالت‌های FSM
class StudySession(StatesGroup):
    waiting_for_subject = State()
    waiting_for_duration = State()
    waiting_for_topic = State()

class AdminStates(StatesGroup):
    waiting_for_channel_info = State()
    waiting_for_broadcast = State()

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
            event.message.text != "✅ بررسی عضویت" and
            not event.message.text.startswith("🏠")):
            
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
• 🎯 نکات طلایی مطالعه

از منوی زیر یکی از گزینه‌ها رو انتخاب کن:
"""
    await message.answer(welcome, reply_markup=main_menu(), parse_mode="HTML")

@dp.message(Command("test"))
async def test_handler(message: types.Message):
    logger.info(f"🧪 دریافت /test از {message.from_user.id}")
    await message.answer("✅ ربات با aiogram + webhook کار می‌کند! تست موفق.")

@dp.message(Command("stats"))
async def stats_command_handler(message: types.Message):
    """دستور سریع برای مشاهده آمار"""
    user_stats = db.get_user_progress(message.from_user.id)
    progress = calculate_study_progress(user_stats['total_minutes'])
    
    await message.answer(
        f"📊 <b>آمار سریع شما</b>\n\n"
        f"🕒 کل زمان مطالعه: {user_stats['total_hours']} ساعت\n"
        f"📖 تعداد جلسات: {user_stats['total_sessions']} جلسه\n"
        f"📅 روزهای فعال: {user_stats['active_days']} روز\n"
        f"📈 پیشرفت کلی: {progress['percentage']}%\n"
        f"{progress['progress_bar']}\n\n"
        f"💪 {random.choice(MOTIVATIONAL_MESSAGES)}",
        reply_markup=create_stats_keyboard(),
        parse_mode="HTML"
    )

# --- هندلرهای منوی اصلی ---

@dp.message(F.text == "⏳ زمان‌سنجی کنکورها")
async def exams_menu_handler(message: types.Message):
    logger.info(f"⏰ کاربر {message.from_user.id} منوی کنکورها را انتخاب کرد")
    await message.answer("🎯 انتخاب کنکور مورد نظر:", reply_markup=exams_menu())

@dp.message(F.text == "📅 برنامه مطالعاتی پیشرفته")
async def study_plan_handler(message: types.Message):
    logger.info(f"📅 کاربر {message.from_user.id} منوی برنامه مطالعاتی را انتخاب کرد")
    
    user_stats = db.get_user_progress(message.from_user.id)
    progress = calculate_study_progress(user_stats['total_minutes'])
    
    await message.answer(
        f"📅 <b>برنامه مطالعاتی پیشرفته</b>\n\n"
        f"📊 آمار کلی شما:\n"
        f"• 🕒 کل زمان مطالعه: {user_stats['total_hours']} ساعت\n"
        f"• 📖 تعداد جلسات: {user_stats['total_sessions']} جلسه\n"
        f"• 📅 روزهای فعال: {user_stats['active_days']} روز\n"
        f"• 📈 پیشرفت کلی: {progress['percentage']}%\n"
        f"{progress['progress_bar']}\n\n"
        f"💡 <b>نکته طلایی:</b>\n{get_study_tips()}\n\n"
        f"از گزینه‌های زیر استفاده کنید:",
        reply_markup=create_study_plan_keyboard(),
        parse_mode="HTML"
    )

@dp.message(F.text == "📊 آمار مطالعه حرفه‌ای")
async def stats_handler(message: types.Message):
    logger.info(f"📊 کاربر {message.from_user.id} منوی آمار مطالعه را انتخاب کرد")
    
    today_stats = db.get_today_study_stats(message.from_user.id)
    weekly_stats = db.get_weekly_stats(message.from_user.id)
    user_stats = db.get_user_progress(message.from_user.id)
    
    total_weekly = sum(day['total_minutes'] for day in weekly_stats)
    study_days = [day['date'] for day in weekly_stats if day['total_minutes'] > 0]
    current_streak = calculate_streak(study_days)
    
    await message.answer(
        f"📊 <b>آمار مطالعه حرفه‌ای</b>\n\n"
        f"📈 <b>امروز:</b>\n"
        f"• 🕒 زمان مطالعه: {today_stats['total_minutes']} دقیقه\n"
        f"• 📖 جلسات: {today_stats['sessions_count']} جلسه\n"
        f"• 📚 دروس: {today_stats['subjects']}\n\n"
        f"📅 <b>هفته جاری:</b>\n"
        f"• 🕒 کل زمان: {format_study_time(total_weekly)}\n"
        f"• 📊 میانگین روزانه: {total_weekly // 7 if weekly_stats else 0} دقیقه\n"
        f"• 🔥 streak فعلی: {current_streak} روز\n\n"
        f"📊 <b>کلی:</b>\n"
        f"• 🕒 کل زمان: {user_stats['total_hours']} ساعت\n"
        f"• 📖 کل جلسات: {user_stats['total_sessions']} جلسه\n\n"
        f"برای مشاهده جزئیات بیشتر از گزینه‌های زیر استفاده کنید:",
        reply_markup=create_stats_keyboard(),
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

# --- هندلرهای کال‌بک کنکورها ---

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
        total_days = 0
    else:
        target = min(future_dates)
        countdown, total_days = format_time_remaining(target)
    
    message = f"""
📘 <b>{exam['name']}</b>
📅 تاریخ: {exam['persian_date']}
🕒 ساعت: {exam['time']}

{countdown}
📆 تعداد کل روزهای باقی‌مانده: {total_days} روز

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
            countdown, total_days = format_time_remaining(target)
            message += f"{countdown}\n"
            message += f"📆 کل روزهای باقی‌مانده: {total_days} روز\n"
        else:
            message += "✅ برگزار شده\n"
        
        message += "─" * 30 + "\n\n"
    
    message += f"💫 <i>{random.choice(MOTIVATIONAL_MESSAGES)}</i>"
    
    await callback.message.edit_text(
        message, 
        reply_markup=exam_actions_menu(), 
        parse_mode="HTML"
    )

@dp.callback_query(F.data.startswith("refresh_"))
async def refresh_exam_handler(callback: types.CallbackQuery):
    """هندلر دکمه بروزرسانی"""
    if callback.data == "refresh_exams":
        # بروزرسانی لیست همه آزمون‌ها
        await all_exams_handler(callback)
    elif callback.data.startswith("refresh_"):
        # بروزرسانی آزمون خاص
        exam_key = callback.data.replace("refresh_", "")
        await exam_callback_handler(callback)
    
    await callback.answer("🔄 اطلاعات بروزرسانی شد")

@dp.callback_query(F.data == "next_exam")
async def next_exam_handler(callback: types.CallbackQuery):
    """هندلر دکمه آزمون بعدی"""
    next_exam = get_next_exam()
    
    if next_exam:
        # ایجاد یک callback data مصنوعی برای استفاده از هندلر موجود
        callback.data = f"exam_{next_exam['key']}"
        await exam_callback_handler(callback)
    else:
        await callback.answer("❌ هیچ آزمون آینده‌ای پیدا نشد", show_alert=True)

@dp.callback_query(F.data.startswith("details_"))
async def exam_details_handler(callback: types.CallbackQuery):
    """هندلر دکمه جزئیات بیشتر"""
    exam_key = callback.data.replace("details_", "")
    
    if exam_key not in EXAMS_1405:
        await callback.answer("❌ آزمون یافت نشد")
        return
    
    exam = EXAMS_1405[exam_key]
    now = datetime.now()
    dates = exam["date"] if isinstance(exam["date"], list) else [exam["date"]]
    future_dates = [datetime(*d) for d in dates if datetime(*d) > now]
    
    if future_dates:
        target = min(future_dates)
        time_details = format_time_remaining_detailed(target)
        
        message = f"""
📘 <b>جزئیات کامل {exam['name']}</b>

📅 تاریخ: {exam['persian_date']}
🕒 ساعت: {exam['time']}

⏳ <b>زمان باقی‌مانده:</b>
• 📆 کل روزها: {time_details['total_days']} روز
• 🗓️ هفته: {time_details['weeks']} هفته
• 📅 روز: {time_details['days']} روز  
• 🕒 ساعت: {time_details['hours']} ساعت
• ⏰ دقیقه: {time_details['minutes']} دقیقه
• ⏱️ ثانیه: {time_details['seconds']} ثانیه

📊 <b>اطلاعات آماری:</b>
• 📈 کل ثانیه‌ها: {time_details['total_seconds']:,} ثانیه

💡 <b>نکته مطالعاتی:</b>
{get_study_tips()}
"""
    else:
        message = f"""
📘 <b>جزئیات کامل {exam['name']}</b>

📅 تاریخ: {exam['persian_date']}
🕒 ساعت: {exam['time']}

✅ این آزمون برگزار شده است.

🎯 {random.choice(MOTIVATIONAL_MESSAGES)}
"""
    
    await callback.message.edit_text(
        message,
        reply_markup=exam_actions_menu(exam_key),
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
async def log_study_handler(callback: types.CallbackQuery, state: FSMContext):
    """شروع فرآیند ثبت جلسه مطالعه"""
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
async def log_subject_handler(callback: types.CallbackQuery, state: FSMContext):
    """ذخیره درس انتخاب شده و درخواست مدت زمان"""
    subject = callback.data.replace("log_subject_", "")
    subject_name = {
        "ریاضی": "ریاضی", "فیزیک": "فیزیک", "شیمی": "شیمی", 
        "زیست": "زیست", "ادبیات": "ادبیات", "عربی": "عربی",
        "دینی": "دینی", "زبان": "زبان"
    }.get(subject, "نامشخص")
    
    await state.update_data(subject=subject, subject_name=subject_name)
    await state.set_state(StudySession.waiting_for_duration)
    
    await callback.message.edit_text(
        f"⏱️ <b>ثبت مطالعه {subject_name}</b>\n\n"
        f"مدت زمان مطالعه را به دقیقه وارد کنید:\n"
        f"مثال: <code>120</code> (برای ۲ ساعت)",
        reply_markup=back_button_menu("🔙 بازگشت به انتخاب درس", "log_study"),
        parse_mode="HTML"
    )

@dp.message(StudySession.waiting_for_duration)
async def process_study_duration(message: types.Message, state: FSMContext):
    """پردازش مدت زمان مطالعه"""
    try:
        duration = int(message.text)
        if duration <= 0 or duration > 1440:  # حداکثر 24 ساعت
            await message.answer("❌ لطفاً یک عدد معتبر بین 1 تا 1440 وارد کنید:")
            return
        
        data = await state.get_data()
        subject = data.get('subject')
        subject_name = data.get('subject_name')
        
        # ذخیره در دیتابیس
        db.add_study_session(
            user_id=message.from_user.id,
            subject=subject,
            topic=f"جلسه مطالعه {subject_name}",
            duration_minutes=duration
        )
        
        await state.clear()
        
        # نمایش نتیجه
        user_stats = db.get_today_study_stats(message.from_user.id)
        
        await message.answer(
            f"✅ <b>جلسه مطالعه ثبت شد!</b>\n\n"
            f"📚 درس: {subject_name}\n"
            f"⏰ مدت: {duration} دقیقه\n"
            f"📅 تاریخ: {datetime.now().strftime('%Y-%m-%d')}\n\n"
            f"📊 <b>آمار امروز:</b>\n"
            f"• 🕒 کل زمان: {user_stats['total_minutes']} دقیقه\n"
            f"• 📖 جلسات: {user_stats['sessions_count']} جلسه\n\n"
            f"🎯 {random.choice(MOTIVATIONAL_MESSAGES)}",
            reply_markup=create_stats_keyboard(),
            parse_mode="HTML"
        )
        
    except ValueError:
        await message.answer("❌ لطفاً یک عدد معتبر وارد کنید:")

# --- هندلرهای آمار مطالعه ---

@dp.callback_query(F.data == "today_stats")
async def today_stats_handler(callback: types.CallbackQuery):
    """نمایش آمار امروز"""
    today_stats = db.get_today_study_stats(callback.from_user.id)
    
    await callback.message.edit_text(
        f"📊 <b>آمار مطالعه امروز</b>\n\n"
        f"📅 تاریخ: {datetime.now().strftime('%Y-%m-%d')}\n\n"
        f"• 🕒 زمان مطالعه: {today_stats['total_minutes']} دقیقه\n"
        f"• 📖 تعداد جلسات: {today_stats['sessions_count']} جلسه\n"
        f"• 📚 دروس مطالعه شده: {today_stats['subjects']}\n\n"
        f"💪 {get_motivational_quote()}",
        reply_markup=create_stats_keyboard(),
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "weekly_stats")
async def weekly_stats_handler(callback: types.CallbackQuery):
    """نمایش آمار هفته جاری"""
    weekly_stats = db.get_weekly_stats(callback.from_user.id)
    total_weekly = sum(day['total_minutes'] for day in weekly_stats)
    
    stats_text = "📅 <b>آمار مطالعه هفته جاری</b>\n\n"
    
    for day in weekly_stats:
        stats_text += f"• {day['date']}: {day['total_minutes']} دقیقه ({day['sessions_count']} جلسه)\n"
    
    stats_text += f"\n📊 <b>جمع کل:</b> {format_study_time(total_weekly)}\n"
    stats_text += f"📈 <b>میانگین روزانه:</b> {total_weekly // 7 if weekly_stats else 0} دقیقه\n\n"
    stats_text += f"🎯 {random.choice(MOTIVATIONAL_MESSAGES)}"
    
    await callback.message.edit_text(
        stats_text,
        reply_markup=create_stats_keyboard(),
        parse_mode="HTML"
    )

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
async def admin_add_channel_handler(callback: types.CallbackQuery, state: FSMContext):
    """شروع فرآیند افزودن کانال اجباری"""
    await callback.message.edit_text(
        "👑 <b>افزودن کانال اجباری</b>\n\n"
        "لطفاً اطلاعات کانال را به فرمت زیر ارسال کنید:\n"
        "<code>آیدی_عددی @username عنوان_کانال</code>\n\n"
        "مثال:\n"
        "<code>-1001234567890 @konkour_channel کانال کنکور ۱۴۰۵</code>\n\n"
        "❕ توجه: ربات باید در کانال ادمین باشد.",
        reply_markup=back_button_menu("🔙 بازگشت", "admin_mandatory_channels"),
        parse_mode="HTML"
    )
    
    await state.set_state(AdminStates.waiting_for_channel_info)

@dp.message(AdminStates.waiting_for_channel_info)
async def process_channel_info(message: types.Message, state: FSMContext):
    """پردازش اطلاعات کانال وارد شده"""
    try:
        parts = message.text.split()
        if len(parts) < 3:
            await message.answer("❌ فرمت وارد شده صحیح نیست. لطفاً دوباره尝试 کنید:")
            return
        
        channel_id = int(parts[0])
        channel_username = parts[1].lstrip('@')
        channel_title = ' '.join(parts[2:])
        
        # بررسی اینکه ربات در کانال ادمین است
        try:
            chat_member = await bot.get_chat_member(channel_id, bot.id)
            if chat_member.status not in ['administrator', 'creator']:
                await message.answer(
                    "❌ ربات باید در کانال ادمین باشد. لطفاً ابتدا ربات را ادمین کنید.",
                    reply_markup=back_button_menu("🔙 بازگشت", "admin_mandatory_channels")
                )
                await state.clear()
                return
        except Exception as e:
            await message.answer(
                f"❌ خطا در بررسی وضعیت ربات: {e}",
                reply_markup=back_button_menu("🔙 بازگشت", "admin_mandatory_channels")
            )
            await state.clear()
            return
        
        # ذخیره کانال در دیتابیس
        db.add_mandatory_channel(
            channel_id=channel_id,
            channel_username=channel_username,
            channel_title=channel_title,
            admin_id=message.from_user.id
        )
        
        await state.clear()
        
        await message.answer(
            f"✅ <b>کانال با موفقیت اضافه شد!</b>\n\n"
            f"📢 عنوان: {channel_title}\n"
            f"🔗 آیدی: {channel_id}\n"
            f"👤 یوزرنیم: @{channel_username}\n\n"
            f"از این پس کاربران برای استفاده از ربات باید در این کانال عضو باشند.",
            reply_markup=admin_menu(),
            parse_mode="HTML"
        )
        
    except ValueError:
        await message.answer("❌ آیدی کانال باید عددی باشد. لطفاً دوباره尝试 کنید:")
    except Exception as e:
        await message.answer(f"❌ خطا: {e}")

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
