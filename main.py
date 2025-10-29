import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import random
from datetime import datetime

from config import MOTIVATIONAL_MESSAGES
from exam_data import EXAMS_1405

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ایجاد ربات و دیسپچر
bot = Bot(token="8381121739:AAFB2YBMomBh9xhoI3Qn0VVuGaGlpea9fx8")
dp = Dispatcher()

# منوی اصلی
def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⏳ زمان‌سنجی کنکورها")],
            [KeyboardButton(text="📅 برنامه مطالعاتی پیشرفته")],
            [KeyboardButton(text="📊 آمار مطالعه حرفه‌ای")],
            [KeyboardButton(text="👑 پنل مدیریت")]
        ],
        resize_keyboard=True
    )

# منوی کنکورها
def exams_menu():
    keyboard = []
    keys = list(EXAMS_1405.keys())
    for i in range(0, len(keys), 2):
        row = []
        for j in range(2):
            if i + j < len(keys):
                key = keys[i + j]
                label = EXAMS_1405[key]["name"]
                row.append(InlineKeyboardButton(text=f"🎓 {label}", callback_data=f"exam_{key}"))
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton(text="📋 همه کنکورها", callback_data="show_all_exams")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# هندلر start
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    user = message.from_user
    logger.info(f"🎯 دریافت /start از {user.first_name} ({user.id})")
    
    welcome = f"""
👋 سلام {user.first_name} عزیز!
به ربات کنکور ۱۴۰۵ خوش آمدی! 🎯

از منوی زیر استفاده کن:
"""
    await message.answer(welcome, reply_markup=main_menu())

# هندلر test
@dp.message(Command("test"))
async def test_handler(message: types.Message):
    logger.info(f"🧪 دریافت /test از {message.from_user.id}")
    await message.answer("✅ ربات با aiogram کار می‌کند! تست موفق.")

# هندلر منوی کنکورها
@dp.message(F.text == "⏳ زمان‌سنجی کنکورها")
async def exams_menu_handler(message: types.Message):
    logger.info(f"⏰ کاربر {message.from_user.id} منوی کنکورها را انتخاب کرد")
    await message.answer("🎯 انتخاب کنکور مورد نظر:", reply_markup=exams_menu())

# هندلر سایر منوها (موقت)
@dp.message(F.text.in_(["📅 برنامه مطالعاتی پیشرفته", "📊 آمار مطالعه حرفه‌ای", "👑 پنل مدیریت"]))
async def other_menus_handler(message: types.Message):
    await message.answer("🛠️ این بخش به زودی فعال خواهد شد...")

# هندلر پیام‌های ناشناخته
@dp.message()
async def unknown_handler(message: types.Message):
    logger.info(f"📝 پیام ناشناخته از {message.from_user.id}: {message.text}")
    await message.answer("🤔 لطفاً از دکمه‌های منو استفاده کنید:", reply_markup=main_menu())

# هندلر کلیک دکمه‌های اینلاین
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
        countdown = f"⏳ {days} روز و {hours} ساعت باقی مانده"
    
    message = f"""
📘 <b>{exam['name']}</b>
📅 {exam['persian_date']} - 🕒 {exam['time']}

{countdown}

🎯 {random.choice(MOTIVATIONAL_MESSAGES)}
"""
    await callback.message.edit_text(message, parse_mode="HTML")

@dp.callback_query(F.data == "show_all_exams")
async def all_exams_handler(callback: types.CallbackQuery):
    logger.info(f"📋 کاربر {callback.from_user.id} همه کنکورها را انتخاب کرد")
    
    message = "⏳ <b>کنکورهای ۱۴۰۵</b>\n\n"
    
    for exam_key, exam in EXAMS_1405.items():
        now = datetime.now()
        dates = exam["date"] if isinstance(exam["date"], list) else [exam["date"]]
        future_dates = [datetime(*d) for d in dates if datetime(*d) > now]
        
        if future_dates:
            target = min(future_dates)
            delta = target - now
            countdown = f"{delta.days} روز باقی مانده"
        else:
            countdown = "✅ برگزار شده"
        
        message += f"🎯 {exam['name']}\n"
        message += f"📅 {exam['persian_date']} - {countdown}\n"
        message += "─" * 20 + "\n\n"
    
    await callback.message.edit_text(message, parse_mode="HTML")

# تابع اصلی
async def main():
    logger.info("🚀 راه‌اندازی ربات با aiogram...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
