from flask import Flask, request, jsonify
import os
import asyncio
import logging
import threading
import time

# تنظیم لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ایمپورت ربات
try:
    from main import bot
    logger.info("✅ Bot imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import bot: {e}")
    bot = None

class WebhookManager:
    def __init__(self):
        self.webhook_set = False
        self.setup_attempted = False
    
    def setup_webhook(self):
        """تنظیم وب‌هوک برای Railway"""
        if self.setup_attempted:
            return
            
        self.setup_attempted = True
        
        if not bot:
            logger.error("❌ Bot not available for webhook setup")
            return
            
        try:
            # دریافت توکن از محیط
            bot_token = os.environ.get('BOT_TOKEN')
            if not bot_token:
                logger.error("❌ BOT_TOKEN not found in environment variables")
                return

            # ساخت آدرس وب‌هوک
            railway_url = os.environ.get('RAILWAY_STATIC_URL')
            if railway_url:
                webhook_url = f"{railway_url}/{bot_token}"
            else:
                # اگر RAILWAY_STATIC_URL موجود نبود، از آدرس عمومی استفاده می‌کنیم
                service_name = os.environ.get('RAILWAY_SERVICE_NAME', 'konkoor-bot')
                webhook_url = f"https://{service_name}.up.railway.app/{bot_token}"

            logger.info(f"🔄 Setting webhook to: {webhook_url}")

            async def set_webhook_task():
                try:
                    # حذف وب‌هوک قبلی
                    await bot.application.bot.delete_webhook()
                    time.sleep(1)  # تأثیر کمی قبل از تنظیم جدید
                    
                    # تنظیم وب‌هوک جدید
                    await bot.application.bot.set_webhook(
                        url=webhook_url,
                        allowed_updates=["message", "callback_query"],
                        drop_pending_updates=True
                    )
                    self.webhook_set = True
                    logger.info("✅ Webhook set successfully!")
                    
                except Exception as e:
                    logger.error(f"❌ Error setting webhook: {e}")

            # اجرای غیرهمزمان
            asyncio.run(set_webhook_task())
            
        except Exception as e:
            logger.error(f"❌ Webhook setup failed: {e}")

# ایجاد مدیر وب‌هوک
webhook_manager = WebhookManager()

def initialize_webhook():
    """تنظیم وب‌هوک در پس‌زمینه"""
    time.sleep(5)  # صبر کن سرور کامل راه‌اندازی بشه
    webhook_manager.setup_webhook()

# راه‌اندازی وب‌هوک هنگام شروع
@app.before_first_request
def startup():
    """عملیات راه‌اندازی"""
    logger.info("🚀 Starting Konkoor Bot on Railway...")
    # راه‌اندازی وب‌هوک در پس‌زمینه
    thread = threading.Thread(target=initialize_webhook)
    thread.daemon = True
    thread.start()

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
                background: #48bb78;
                color: white;
                padding: 10px 20px;
                border-radius: 25px;
                font-weight: bold;
                margin: 20px 0;
            }
            .info {
                background: #edf2f7;
                padding: 15px;
                border-radius: 10px;
                margin: 15px 0;
                border-right: 4px solid #667eea;
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
            <div class="status">✅ وضعیت: ربات در حال اجرا است</div>
            <div class="info">
                <strong>🚀 پلتفرم:</strong> Railway
            </div>
            <div class="info">
                <strong>📱 سرویس:</strong> ربات تلگرام
            </div>
            <div class="info">
                <strong>🔗 وب‌هوک:</strong> 
                """ + ("✅ فعال" if webhook_manager.webhook_set else "🔄 در حال تنظیم") + """
            </div>
            <p>برای استفاده از ربات، به اکانت تلگرام مراجعه کنید</p>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health_check():
    """بررسی سلامت سرویس"""
    status = {
        "status": "healthy",
        "service": "konkoor-bot",
        "timestamp": time.time(),
        "webhook_set": webhook_manager.webhook_set,
        "platform": "railway"
    }
    return jsonify(status)

@app.route('/set_webhook', methods=['GET', 'POST'])
def manual_webhook_setup():
    """تنظیم دستی وب‌هوک"""
    webhook_manager.setup_webhook()
    return jsonify({
        "message": "Webhook setup initiated",
        "webhook_set": webhook_manager.webhook_set
    })

@app.route('/delete_webhook', methods=['GET', 'POST'])
def delete_webhook():
    """حذف وب‌هوک"""
    if not bot:
        return jsonify({"error": "Bot not available"}), 500
        
    try:
        async def delete_webhook_task():
            await bot.application.bot.delete_webhook()
            webhook_manager.webhook_set = False
            webhook_manager.setup_attempted = False
            
        asyncio.run(delete_webhook_task())
        return jsonify({"message": "Webhook deleted successfully"})
        
    except Exception as e:
        logger.error(f"Error deleting webhook: {e}")
        return jsonify({"error": str(e)}), 500

# مسیر داینامیک برای وب‌هوک - مهم!
@app.route('/webhook', methods=['POST'])
@app.route('/webhook/<token>', methods=['POST'])
def webhook_general(token=None):
    """دریافت آپدیت‌های تلگرام - مسیر عمومی"""
    return handle_webhook_request()

# مسیر اصلی وب‌هوک با توکن
@app.route('/<token>', methods=['POST'])
def webhook_with_token(token):
    """دریافت آپدیت‌های تلگرام با توکن"""
    expected_token = os.environ.get('BOT_TOKEN')
    if token != expected_token:
        logger.warning(f"❌ Invalid token received: {token}")
        return jsonify({"error": "Invalid token"}), 403
    
    return handle_webhook_request()

def handle_webhook_request():
    """پردازش درخواست وب‌هوک"""
    if not bot:
        logger.error("❌ Bot not available for webhook processing")
        return jsonify({"error": "Bot not available"}), 500
        
    try:
        if not request.is_json:
            logger.warning("❌ Received non-JSON webhook request")
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        update_data = request.get_json()
        if not update_data:
            logger.warning("❌ Empty webhook request received")
            return jsonify({"error": "Empty request body"}), 400
        
        update_id = update_data.get('update_id', 'unknown')
        logger.info(f"📨 Received update: {update_id}")
        
        # پردازش غیرهمزمان آپدیت
        async def process_update():
            try:
                await bot.application.process_update(update_data)
                logger.info(f"✅ Processed update: {update_id}")
            except Exception as e:
                logger.error(f"❌ Error processing update {update_id}: {e}")
        
        asyncio.run(process_update())
        
        return jsonify({"status": "ok", "update_id": update_id}), 200
        
    except Exception as e:
        logger.error(f"❌ Webhook processing error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(404)
def not_found(error):
    """مدیریت خطای ۴۰۴"""
    return jsonify({"error": "Endpoint not found", "status": 404}), 404

@app.errorhandler(500)
def internal_error(error):
    """مدیریت خطای ۵۰۰"""
    return jsonify({"error": "Internal server error", "status": 500}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    logger.info(f"🚀 Starting Flask server on {host}:{port}")
    
    # راه‌اندازی وب‌هوک
    threading.Thread(target=initialize_webhook, daemon=True).start()
    
    app.run(host=host, port=port, debug=False)
