import os
import logging
from flask import Flask, request, jsonify

# تنظیمات اولیه
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# تنظیمات مستقیماً از محیط
BOT_TOKEN = os.environ.get('BOT_TOKEN', '')
ADMIN_ID = os.environ.get('ADMIN_ID', '')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', '')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'production')

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ربات کنکور ۱۴۰۵</title>
        <meta charset="utf-8">
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
            .container { max-width: 600px; margin: 0 auto; background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; backdrop-filter: blur(10px); }
            h1 { font-size: 2.5em; margin-bottom: 20px; }
            .status { background: #4CAF50; padding: 10px; border-radius: 5px; margin: 20px 0; }
            .error { background: #f44336; padding: 10px; border-radius: 5px; margin: 20px 0; }
            .links { margin-top: 30px; }
            .links a { color: white; text-decoration: none; margin: 0 10px; padding: 10px 20px; border: 1px solid white; border-radius: 5px; transition: all 0.3s; }
            .links a:hover { background: white; color: #667eea; }
            .config { text-align: left; background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 15px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 ربات کنکور ۱۴۰۵</h1>
            <p>ربات مدیریت و برنامه‌ریزی کنکور ۱۴۰۵</p>
            
            <div class="config">
                <h3>📋 وضعیت تنظیمات:</h3>
                <p><strong>BOT_TOKEN:</strong> {}</p>
                <p><strong>ADMIN_ID:</strong> {}</p>
                <p><strong>ENVIRONMENT:</strong> {}</p>
                <p><strong>WEBHOOK_URL:</strong> {}</p>
            </div>
            
            {}
            
            <div class="links">
                <a href="/health">بررسی سلامت</a>
                <a href="/config">تنظیمات</a>
                <a href="/test">تست</a>
            </div>
        </div>
    </html>
    """.format(
        "✅ ست شده" if BOT_TOKEN and BOT_TOKEN != "your_telegram_bot_token_here" else "❌ تنظیم نشده",
        "✅ ست شده" if ADMIN_ID else "❌ تنظیم نشده",
        ENVIRONMENT,
        WEBHOOK_URL or "❌ تنظیم نشده",
        '<div class="status">✅ سرویس فعال و در حال اجرا</div>' if BOT_TOKEN and BOT_TOKEN != "your_telegram_bot_token_here" else '<div class="error">❌ BOT_TOKEN تنظیم نشده است</div>'
    )

@app.route('/health')
def health():
    """بررسی سلامت"""
    return jsonify({
        "status": "healthy" if BOT_TOKEN and BOT_TOKEN != "your_telegram_bot_token_here" else "unhealthy",
        "service": "Konkur 1405 Bot",
        "environment": ENVIRONMENT,
        "bot_token_configured": bool(BOT_TOKEN and BOT_TOKEN != "your_telegram_bot_token_here"),
        "admin_id_configured": bool(ADMIN_ID)
    })

@app.route('/config')
def show_config():
    """نمایش تنظیمات"""
    return jsonify({
        "BOT_TOKEN": "***" + BOT_TOKEN[-4:] if BOT_TOKEN and BOT_TOKEN != "your_telegram_bot_token_here" else "NOT_SET",
        "ADMIN_ID": ADMIN_ID or "NOT_SET",
        "WEBHOOK_URL": WEBHOOK_URL or "NOT_SET",
        "ENVIRONMENT": ENVIRONMENT,
        "PORT": os.environ.get('PORT', '5000')
    })

@app.route('/test')
def test():
    """صفحه تست"""
    return jsonify({
        "message": "ربات کنکور ۱۴۰۵ فعال است",
        "status": "operational",
        "environment": ENVIRONMENT
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """وب‌هوک تلگرام (موقتاً غیرفعال)"""
    return jsonify({
        "status": "webhook_disabled",
        "message": "لطفاً ابتدا تنظیمات را کامل کنید"
    })

# تابع اصلی برای Gunicorn
def create_app():
    return app

# برای اجرای مستقیم
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 شروع سرویس روی پورت {port}")
    logger.info(f"🔧 محیط: {ENVIRONMENT}")
    
    if not BOT_TOKEN or BOT_TOKEN == "your_telegram_bot_token_here":
        logger.error("❌ BOT_TOKEN تنظیم نشده است!")
        logger.info("💡 لطفاً در Render.com → Environment Variables → BOT_TOKEN را تنظیم کنید")
    else:
        logger.info("✅ BOT_TOKEN تنظیم شده است")
    
    app.run(host='0.0.0.0', port=port, debug=ENVIRONMENT == 'development')

# این برای Gunicorn لازمه
application = app
