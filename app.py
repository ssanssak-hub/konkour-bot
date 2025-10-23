import os
import logging
import requests
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

def get_status_html():
    """تولید HTML وضعیت"""
    bot_token_status = "✅ ست شده" if BOT_TOKEN and BOT_TOKEN != "your_telegram_bot_token_here" else "❌ تنظیم نشده"
    admin_id_status = "✅ ست شده" if ADMIN_ID else "❌ تنظیم نشده"
    status_div = '<div class="status">✅ سرویس فعال و در حال اجرا</div>' if BOT_TOKEN and BOT_TOKEN != "your_telegram_bot_token_here" else '<div class="error">❌ BOT_TOKEN تنظیم نشده است</div>'
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ربات کنکور ۱۴۰۵</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
            .container {{ max-width: 600px; margin: 0 auto; background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; backdrop-filter: blur(10px); }}
            h1 {{ font-size: 2.5em; margin-bottom: 20px; }}
            .status {{ background: #4CAF50; padding: 10px; border-radius: 5px; margin: 20px 0; }}
            .error {{ background: #f44336; padding: 10px; border-radius: 5px; margin: 20px 0; }}
            .links {{ margin-top: 30px; }}
            .links a {{ color: white; text-decoration: none; margin: 0 10px; padding: 10px 20px; border: 1px solid white; border-radius: 5px; transition: all 0.3s; }}
            .links a:hover {{ background: white; color: #667eea; }}
            .config {{ text-align: left; background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin: 15px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 ربات کنکور ۱۴۰۵</h1>
            <p>ربات مدیریت و برنامه‌ریزی کنکور ۱۴۰۵</p>
            
            <div class="config">
                <h3>📋 وضعیت تنظیمات:</h3>
                <p><strong>BOT_TOKEN:</strong> {bot_token_status}</p>
                <p><strong>ADMIN_ID:</strong> {admin_id_status}</p>
                <p><strong>ENVIRONMENT:</strong> {ENVIRONMENT}</p>
                <p><strong>WEBHOOK_URL:</strong> {WEBHOOK_URL or "❌ تنظیم نشده"}</p>
            </div>
            
            {status_div}
            
            <div class="links">
                <a href="/health">بررسی سلامت</a>
                <a href="/config">تنظیمات</a>
                <a href="/test">تست</a>
                <a href="/setup_webhook">تنظیم وب‌هوک</a>
                <a href="https://t.me/{BOT_TOKEN.split(':')[0] if BOT_TOKEN and ':' in BOT_TOKEN else 'your_bot'}">ربات تلگرام</a>
            </div>
        </div>
    </html>
    """

@app.route('/')
def home():
    return get_status_html()

@app.route('/health')
def health():
    """بررسی سلامت"""
    return jsonify({
        "status": "healthy" if BOT_TOKEN and BOT_TOKEN != "your_telegram_bot_token_here" else "unhealthy",
        "service": "Konkur 1405 Bot",
        "environment": ENVIRONMENT,
        "bot_token_configured": bool(BOT_TOKEN and BOT_TOKEN != "your_telegram_bot_token_here"),
        "admin_id_configured": bool(ADMIN_ID),
        "webhook_url": WEBHOOK_URL or "NOT_SET"
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
        "environment": ENVIRONMENT,
        "bot_ready": bool(BOT_TOKEN and BOT_TOKEN != "your_telegram_bot_token_here")
    })

def set_telegram_webhook():
    """تنظیم وب‌هوک در تلگرام"""
    try:
        webhook_url = f"{WEBHOOK_URL}/webhook"
        
        # حذف وب‌هوک قبلی
        delete_url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
        requests.get(delete_url)
        
        # تنظیم وب‌هوک جدید
        set_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
        payload = {
            "url": webhook_url,
            "max_connections": 40,
            "allowed_updates": ["message", "callback_query"]
        }
        
        response = requests.post(set_url, json=payload)
        result = response.json()
        
        if result.get('ok'):
            logger.info(f"✅ وب‌هوک با موفقیت تنظیم شد: {webhook_url}")
            return True, result
        else:
            logger.error(f"❌ خطا در تنظیم وب‌هوک: {result}")
            return False, result
            
    except Exception as e:
        logger.error(f"❌ خطا در تنظیم وب‌هوک: {e}")
        return False, {"error": str(e)}

@app.route('/setup_webhook')
def setup_webhook():
    """تنظیم واقعی وب‌هوک"""
    try:
        if not BOT_TOKEN or BOT_TOKEN == "your_telegram_bot_token_here":
            return jsonify({"status": "error", "message": "BOT_TOKEN not set"}), 400
        
        if not WEBHOOK_URL:
            return jsonify({"status": "error", "message": "WEBHOOK_URL not set"}), 400
        
        success, result = set_telegram_webhook()
        
        if success:
            return jsonify({
                "status": "success",
                "message": "✅ وب‌هوک با موفقیت تنظیم شد!",
                "webhook_url": f"{WEBHOOK_URL}/webhook",
                "result": result
            })
        else:
            return jsonify({
                "status": "error",
                "message": "❌ خطا در تنظیم وب‌هوک",
                "result": result
            }), 500
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    """وب‌هوک تلگرام"""
    if not BOT_TOKEN or BOT_TOKEN == "your_telegram_bot_token_here":
        return jsonify({
            "status": "error",
            "message": "BOT_TOKEN not configured"
        }), 400
    
    try:
        data = request.get_json()
        logger.info(f"📨 دریافت وب‌هوک: {data}")
        
        # پردازش اولیه پیام
        if 'message' in data:
            message = data['message']
            chat_id = message['chat']['id']
            text = message.get('text', '')
            
            # پاسخ به دستور /start
            if text == '/start':
                response_text = """
                🤖 به ربات کنکور ۱۴۰۵ خوش آمدید!

                🎯 امکانات ربات:
                • ⏳ شمارش معکوس کنکور
                • 📅 تقویم مطالعاتی  
                • ⏰ مدیریت یادآوری
                • 📚 برنامه مطالعاتی
                • ✅ ثبت حضور و مطالعه
                • 📊 آمار و گزارش‌گیری

                برای شروع از دکمه‌های زیر استفاده کنید:
                """
                
                # ارسال پاسخ به کاربر
                send_message_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                payload = {
                    "chat_id": chat_id,
                    "text": response_text,
                    "reply_markup": {
                        "keyboard": [
                            ["⏳ شمارش معکوس", "📅 تقویم مطالعاتی"],
                            ["⏰ مدیریت یادآوری", "📚 برنامه مطالعاتی"],
                            ["✅ ثبت حضور", "📊 آمار"]
                        ],
                        "resize_keyboard": True
                    }
                }
                
                requests.post(send_message_url, json=payload)
            
            # پاسخ به پیام‌های دیگر
            else:
                send_message_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                payload = {
                    "chat_id": chat_id,
                    "text": "🤔 لطفاً از منوی ربات استفاده کنید یا دستور /start را وارد کنید."
                }
                requests.post(send_message_url, json=payload)
        
        return jsonify({"status": "success"})
        
    except Exception as e:
        logger.error(f"❌ خطا در پردازش وب‌هوک: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/remove_webhook')
def remove_webhook():
    """حذف وب‌هوک"""
    try:
        if not BOT_TOKEN or BOT_TOKEN == "your_telegram_bot_token_here":
            return jsonify({"status": "error", "message": "BOT_TOKEN not set"}), 400
        
        delete_url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
        response = requests.get(delete_url)
        result = response.json()
        
        if result.get('ok'):
            return jsonify({
                "status": "success", 
                "message": "✅ وب‌هوک با موفقیت حذف شد"
            })
        else:
            return jsonify({
                "status": "error",
                "message": "❌ خطا در حذف وب‌هوک",
                "result": result
            }), 500
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

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
    
    if not WEBHOOK_URL:
        logger.warning("⚠️ WEBHOOK_URL تنظیم نشده است")
    else:
        logger.info(f"✅ WEBHOOK_URL: {WEBHOOK_URL}")
    
    app.run(host='0.0.0.0', port=port, debug=ENVIRONMENT == 'development')

# این برای Gunicorn لازمه
application = app
