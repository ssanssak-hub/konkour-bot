from flask import Flask, request
from main import create_app
import os

app = Flask(__name__)
bot = create_app()

@app.route('/' + os.environ.get('BOT_TOKEN'), methods=['POST'])
def webhook():
    return asyncio.run(bot.webhook_handler(request))

@app.route('/')
def index():
    return "🤖 ربات کنکور ۱۴۰۵ در حال اجرا است!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))
