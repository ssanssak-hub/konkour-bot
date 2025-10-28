import logging
from main import bot
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    logger.info("🚀 شروع ربات در حالت Polling...")
    await bot.application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
