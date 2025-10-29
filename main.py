import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token="8381121739:AAFB2YBMomBh9xhoI3Qn0VVuGaGlpea9fx8")
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    logger.info(f"🎯 start اجرا شد برای کاربر {message.from_user.id}")
    await message.answer("✅ ربات با aiogram کار می‌کند!")

@dp.message(Command("test"))
async def test_handler(message: types.Message):
    logger.info(f"🧪 test اجرا شد برای کاربر {message.from_user.id}")
    await message.answer("🧪 تست aiogram موفق!")

async def main():
    logger.info("🚀 راه‌اندازی ربات با aiogram...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
