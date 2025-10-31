# handlers/main_handlers.py
import logging
from aiogram import Bot, types
from aiogram.fsm.context import FSMContext

logger = logging.getLogger(__name__)

async def start_handler(message: types.Message, bot: Bot = None):
    """هندلر دستور /start"""
    try:
        welcome_text = """
        🤖 **به ربات مدیریت کنکور خوش آمدید!**

        📚 **امکانات ربات:**
        • ⏳ زمان‌سنجی کنکورها
        • 📅 برنامه مطالعاتی پیشرفته  
        • 📊 آمار مطالعه حرفه‌ای
        • ⏰ سیستم یادآوری هوشمند

        🔧 از منوی زیر انتخاب کنید:
        """
        
        keyboard = [
            [types.KeyboardButton(text="⏳ زمان‌سنجی کنکورها")],
            [types.KeyboardButton(text="📅 برنامه مطالعاتی پیشرفته")],
            [types.KeyboardButton(text="📊 آمار مطالعه حرفه‌ای")],
            [types.KeyboardButton(text="⏰ یادآوری کنکورها")],
            [types.KeyboardButton(text="📝 یادآوری شخصی")]
        ]
        reply_markup = types.ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True,
            input_field_placeholder="یک گزینه انتخاب کنید..."
        )
        
        await message.answer(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")
        logger.info(f"کاربر {message.from_user.id} ربات را شروع کرد")
        
    except Exception as e:
        logger.error(f"خطا در start_handler: {e}")
        await message.answer("❌ خطا در راه‌اندازی ربات. لطفاً مجدداً تلاش کنید.")

async def test_handler(message: types.Message):
    """هندلر دستور /test"""
    await message.answer("✅ ربات فعال است! همه چیز OK است.")

async def stats_command_handler(message: types.Message):
    """هندلر دستور /stats"""
    stats_text = """
    📊 **آمار ربات:**
    
    • کاربران فعال: در حال بارگذاری...
    • ریمایندرهای فعال: در حال بارگذاری...
    • وضعیت سیستم: ✅ فعال
    
    🔧 برای آمار دقیق‌تر از منوی اصلی استفاده کنید.
    """
    await message.answer(stats_text, parse_mode="Markdown")

async def handle_back_to_main(message: types.Message):
    """بازگشت به منوی اصلی"""
    try:
        welcome_text = """
        🏠 **منوی اصلی**

        🔧 گزینه مورد نظر را انتخاب کنید:
        """
        
        keyboard = [
            [types.KeyboardButton(text="⏳ زمان‌سنجی کنکورها")],
            [types.KeyboardButton(text="📅 برنامه مطالعاتی پیشرفته")],
            [types.KeyboardButton(text="📊 آمار مطالعه حرفه‌ای")],
            [types.KeyboardButton(text="⏰ یادآوری کنکورها")],
            [types.KeyboardButton(text="📝 یادآوری شخصی")]
        ]
        reply_markup = types.ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True,
            input_field_placeholder="یک گزینه انتخاب کنید..."
        )
        
        await message.answer(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"خطا در handle_back_to_main: {e}")
        await message.answer("❌ خطا در بازگشت به منوی اصلی.")

async def handle_auto_reminders(message: types.Message):
    """هندلر منوی یادآوری خودکار"""
    try:
        auto_text = """
        🤖 **یادآوری خودکار**

        این سیستم به صورت خودکار یادآوری‌های کنکور را برای شما ارسال می‌کند.

        🔧 گزینه مورد نظر را انتخاب کنید:
        """
        
        keyboard = [
            [types.KeyboardButton(text="📋 لیست یادآوری‌ها")],
            [types.KeyboardButton(text="✅ فعال کردن")],
            [types.KeyboardButton(text="❌ غیرفعال کردن")],
            [types.KeyboardButton(text="🔙 بازگشت به منوی اصلی")]
        ]
        reply_markup = types.ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True,
            input_field_placeholder="یک گزینه انتخاب کنید..."
        )
        
        await message.answer(auto_text, reply_markup=reply_markup, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"خطا در handle_auto_reminders: {e}")
        await message.answer("❌ خطا در نمایش منوی یادآوری خودکار.")
