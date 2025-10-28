from flask import Flask, request
import os
import asyncio
from threading import Thread

from main import bot

app = Flask(__name__)

# تنظیم وب‌هوک هنگام راه‌اندازی
def setup_webhook():
    with app.app_context():
        webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME', '')}/{os.environ.get('BOT_TOKEN')}"
        print(f"🔄 Setting webhook to: {webhook_url}")
        
        async def set_webhook():
            await bot.application.bot.set_webhook(
                url=webhook_url,
                allowed_updates=["message", "callback_query"]
            )
            print("✅ Webhook set successfully!")
        
        # اجرای غیرهمزمان
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(set_webhook())

# راه‌اندازی وب‌هوک در پس‌زمینه
Thread(target=setup_webhook).start()

@app.route('/')
def home():
    return "🤖 ربات کنکور ۱۴۰۵ در حال اجرا است! 🎓"

@app.route(f'/{os.environ.get("BOT_TOKEN")}', methods=['POST'])
def webhook():
    """دریافت آپدیت‌های تلگرام"""
    update = request.get_json()
    
    async def process_update():
        await bot.application.process_update(update)
    
    # پردازش غیرهمزمان آپدیت
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(process_update())
    
    return "OK"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
