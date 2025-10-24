import os
import logging
import requests
from flask import Flask, request, jsonify
from handlers.bot_handlers import process_message_handler, process_callback_handler, init_database

# تنظیمات اولیه
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# تنظیمات مستقیم از محیط
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8381121739:AAFB2YBMomBh9xhoI3Qn0VVuGaGlpea9fx8')
ADMIN_ID = os.environ.get('ADMIN_ID', '7703677187')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', 'https://konkour-bot.onrender.com')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'production')

@app.route('/')
def home():
    """صفحه اصلی"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ربات کنکور ۱۴۰۵</title>
        <meta charset="utf-8">
        <style>
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                text-align: center; 
                padding: 50px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; 
            }
            .container { 
                max-width: 600px; 
                margin: 0 auto; 
                background: rgba(255,255,255,0.1); 
                padding: 30px; 
                border-radius: 15px; 
                backdrop-filter: blur(10px); 
            }
            h1 { 
                font-size: 2.5em; 
                margin-bottom: 20px; 
            }
            .status { 
                background: #4CAF50; 
                padding: 10px; 
                border-radius: 5px; 
                margin: 20px 0; 
            }
            .links { 
                margin-top: 30px; 
            }
            .links a { 
                color: white; 
                text-decoration: none; 
                margin: 0 10px; 
                padding: 10px 20px; 
                border: 1px solid white; 
                border-radius: 5px; 
                transition: all 0.3s; 
            }
            .links a:hover { 
                background: white; 
                color: #667eea; 
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 ربات کنکور ۱۴۰۵</h1>
            <p>ربات مدیریت و برنامه‌ریزی کنکور ۱۴۰۵</p>
            
            <div class="status">
                ✅ سرویس فعال و در حال اجرا
            </div>
            
            <p>ربات با موفقیت deploy شده و آماده دریافت پیام‌هاست.</p>
            
            <div class="links">
                <a href="/health">بررسی سلامت</a>
                <a href="/setup_webhook">تنظیم وب‌هوک</a>
                <a href="https://t.me/konkur1405_bot">ربات تلگرام</a>
            </div>
        </div>
    </html>
    """

@app.route('/health')
def health():
    """بررسی سلامت سرویس"""
    return jsonify({
        "status": "healthy",
        "service": "Konkur 1405 Bot",
        "environment": ENVIRONMENT,
        "bot_configured": bool(BOT_TOKEN and BOT_TOKEN != "your_telegram_bot_token_here"),
        "webhook_url": WEBHOOK_URL,
        "database_initialized": True
    })

@app.route('/setup_webhook')
def setup_webhook():
    """تنظیم وب‌هوک تلگرام"""
    try:
        webhook_url = f"{WEBHOOK_URL}/webhook"
        
        # حذف وب‌هوک قبلی
        delete_url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
        delete_response = requests.get(delete_url, timeout=10)
        
        # تنظیم وب‌هوک جدید
        set_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
        payload = {
            "url": webhook_url,
            "max_connections": 40,
            "allowed_updates": ["message", "callback_query", "chat_member"]
        }
        
        response = requests.post(set_url, json=payload, timeout=10)
        result = response.json()
        
        if result.get('ok'):
            logger.info(f"✅ وب‌هوک با موفقیت تنظیم شد: {webhook_url}")
            return jsonify({
                "status": "success",
                "message": "✅ وب‌هوک با موفقیت تنظیم شد!",
                "webhook_url": webhook_url,
                "result": result
            })
        else:
            logger.error(f"❌ خطا در تنظیم وب‌هوک: {result}")
            return jsonify({
                "status": "error",
                "message": "❌ خطا در تنظیم وب‌هوک",
                "result": result
            }), 500
            
    except Exception as e:
        logger.error(f"❌ خطا در تنظیم وب‌هوک: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    """دریافت وب‌هوک از تلگرام"""
    if request.method == 'POST':
        try:
            update_data = request.get_json()
            logger.info(f"📨 دریافت وب‌هوک")
            
            # پردازش پیام
            if 'message' in update_data:
                process_message_handler(update_data['message'])
            elif 'callback_query' in update_data:
                process_callback_handler(update_data['callback_query'])
            
            return jsonify({"status": "success"})
            
        except Exception as e:
            logger.error(f"❌ خطا در پردازش وب‌هوک: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500
    
    return jsonify({"status": "error", "message": "Method not allowed"}), 405

@app.route('/remove_webhook')
def remove_webhook():
    """حذف وب‌هوک"""
    try:
        delete_url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
        response = requests.get(delete_url, timeout=10)
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

@app.route('/get_webhook_info')
def get_webhook_info():
    """دریافت اطلاعات وب‌هوک"""
    try:
        info_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
        response = requests.get(info_url, timeout=10)
        result = response.json()
        
        return jsonify({
            "status": "success",
            "webhook_info": result
        })
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# برای اجرای مستقیم با Flask
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 شروع سرویس روی پورت {port}")
    
    if not BOT_TOKEN or BOT_TOKEN == "your_telegram_bot_token_here":
        logger.error("❌ BOT_TOKEN تنظیم نشده است!")
    else:
        logger.info("✅ BOT_TOKEN تنظیم شده است")
    
    app.run(host='0.0.0.0', port=port, debug=ENVIRONMENT == 'development')

# این برای Gunicorn لازمه
application = app
