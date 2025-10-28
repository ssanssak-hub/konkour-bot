from flask import Flask, request
import os
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

try:
    from main import bot
    print("✅ ربات لود شد")
except Exception as e:
    print(f"❌ خطا: {e}")
    bot = None

@app.route('/')
def home():
    return "🤖 ربات کنکور ۱۴۰۵ - فعال ✅"

@app.route('/webhook', methods=['POST'])
def webhook():
    if bot:
        try:
            data = request.get_json()
            async def process():
                await bot.application.process_update(data)
            asyncio.run(process())
            return "OK"
        except Exception as e:
            print(f"❌ خطا: {e}")
            return "ERROR", 500
    return "BOT NOT READY", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
