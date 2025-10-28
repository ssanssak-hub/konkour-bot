from flask import Flask, request, jsonify
import os
import asyncio
import logging
import threading
import time

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ایمپورت ربات
try:
    from main import bot
    logger.info("✅ ربات کنکور راه‌اندازی شد")
except Exception as e:
    logger.error(f"❌ خطا در ایمپورت ربات: {e}")
    bot = None

class WebhookManager:
    def __init__(self):
        self.webhook_set = False
    
    def setup_webhook(self):
        """تنظیم وب‌هوک برای Render"""
        if not bot:
            logger.error("❌ ربات در دسترس نیست")
            return False
            
        try:
            bot_token = os.environ.get('BOT_TOKEN')
            if not bot_token:
                logger.error("❌ BOT_TOKEN تنظیم نشده")
                return False

            # آدرس Render - بعد از deploy معلوم میشه
            render_url = os.environ.get('RENDER_EXTERNAL_URL')
            if render_url:
                webhook_url = f"{render_url}/webhook"
            else:
                # حالت fallback
                webhook_url = "https://konkour-bot.onrender.com/webhook"

            logger.info(f"🔄 در حال تنظیم وب‌هوک: {webhook_url}")

            async def set_webhook_task():
                try:
                    # حذف وب‌هوک قبلی
                    await bot.application.bot.delete_webhook()
                    time.sleep(2)
                    
                    # تنظیم وب‌هوک جدید
                    result = await bot.application.bot.set_webhook(
                        url=webhook_url,
                        allowed_updates=["message", "callback_query"],
                        drop_pending_updates=True,
                        max_connections=40
                    )
                    self.webhook_set = True
                    logger.info(f"✅ وب‌هوک با موفقیت تنظیم شد!")
                    
                    # بررسی وضعیت
                    webhook_info = await bot.application.bot.get_webhook_info()
                    logger.info(f"📊 وضعیت وب‌هوک: {webhook_info.url}")
                    return True
                    
                except Exception as e:
                    logger.error(f"❌ خطا در تنظیم وب‌هوک: {e}")
                    return False

            return asyncio.run(set_webhook_task())
            
        except Exception as e:
            logger.error(f"❌ خطا در راه‌اندازی وب‌هوک: {e}")
            return False

# ایجاد مدیر وب‌هوک
webhook_manager = WebhookManager()

def initialize_webhook():
    """راه‌اندازی وب‌هوک در پس‌زمینه"""
    time.sleep(10)  # صبر کن سرور کامل راه‌اندازی بشه
    webhook_manager.setup_webhook()

# راه‌اندازی وب‌هوک هنگام شروع
@app.before_request
def initialize():
    if not hasattr(app, 'initialized'):
        logger.info("🚀 راه‌اندازی برنامه...")
        threading.Thread(target=initialize_webhook, daemon=True).start()
        app.initialized = True

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>ربات کنکور ۱۴۰۵</title>
        <style>
            body {
                font-family: 'Tahoma', 'Arial', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                color: #333;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                text-align: center;
                max-width: 500px;
                width: 90%;
            }
            h1 {
                color: #4a5568;
                margin-bottom: 20px;
                font-size: 24px;
            }
            .status {
                padding: 10px 20px;
                border-radius: 25px;
                font-weight: bold;
                margin: 10px 0;
            }
            .status-ok {
                background: #48bb78;
                color: white;
            }
            .status-waiting {
                background: #ed8936;
                color: white;
            }
            .emoji {
                font-size: 48px;
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="emoji">🤖</div>
            <h1>ربات کنکور ۱۴۰۵</h1>
            
            <div class="status {'status-ok' if webhook_manager.webhook_set else 'status-waiting'}">
                {'✅ وب‌هوک فعال' if webhook_manager.webhook_set else '🔄 در حال تنظیم وب‌هوک'}
            </div>
            
            <p>Platform: Render</p>
            <p>سرویس: Webhook</p>
            
            <div style="margin-top: 20px;">
                <a href="/health" style="margin: 10px; padding: 10px; background: #007bff; color: white; text-decoration: none; border-radius: 5px;">بررسی سلامت</a>
                <a href="/set_webhook" style="margin: 10px; padding: 10px; background: #28a745; color: white; text-decoration: none; border-radius: 5px;">تنظیم وب‌هوک</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "konkour-bot",
        "platform": "render",
        "webhook_set": webhook_manager.webhook_set,
        "bot_loaded": bot is not None,
        "timestamp": time.time()
    })

@app.route('/set_webhook', methods=['GET'])
def set_webhook_manual():
    """تنظیم دستی وب‌هوک"""
    success = webhook_manager.setup_webhook()
    if success:
        return jsonify({
            "status": "success",
            "message": "وب‌هوک با موفقیت تنظیم شد"
        })
    else:
        return jsonify({
            "status": "error", 
            "message": "خطا در تنظیم وب‌هوک"
        }), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    """دریافت آپدیت‌های تلگرام"""
    logger.info("📨 دریافت درخواست وب‌هوک")
    
    if not bot:
        logger.error("❌ ربات در دسترس نیست")
        return jsonify({"error": "ربات در دسترس نیست"}), 500
        
    try:
        if not request.is_json:
            logger.error("❌ فرمت JSON نیست")
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        update_data = request.get_json()
        if not update_data:
            logger.error("❌ داده‌ای دریافت نشد")
            return jsonify({"error": "No data received"}), 400
            
        update_id = update_data.get('update_id', 'unknown')
        logger.info(f"📝 پردازش آپدیت: {update_id}")
        
        # پردازش غیرهمزمان آپدیت
        async def process_update():
            try:
                await bot.application.process_update(update_data)
                logger.info(f"✅ آپدیت {update_id} با موفقیت پردازش شد")
            except Exception as e:
                logger.error(f"❌ خطا در پردازش آپدیت {update_id}: {e}")
        
        asyncio.run(process_update())
        
        return jsonify({"status": "ok", "update_id": update_id}), 200
        
    except Exception as e:
        logger.error(f"❌ خطا در پردازش وب‌هوک: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"🚀 راه‌اندازی سرور روی پورت {port}")
    
    # راه‌اندازی وب‌هوک
    threading.Thread(target=initialize_webhook, daemon=True).start()
    
    app.run(host='0.0.0.0', port=port, debug=False)
