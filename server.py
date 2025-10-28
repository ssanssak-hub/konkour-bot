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

# ایمپورت ربات بعد از راه‌اندازی
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
        
        global bot
        if not bot:
            logger.error("❌ Bot not available for webhook setup")
            return
            
        try:
            # دریافت توکن از محیط
            bot_token = os.environ.get('BOT_TOKEN')
            if not bot_token or bot_token == "YOUR_BOT_TOKEN_HERE":
                logger.error("❌ BOT_TOKEN not found in environment variables")
                return

            # ساخت آدرس وب‌هوک - اینبار بدون توکن در URL
            railway_url = os.environ.get('RAILWAY_STATIC_URL')
            if railway_url:
                webhook_url = f"{railway_url}/webhook"
            else:
                webhook_url = f"https://konkoor-bot.up.railway.app/webhook"

            logger.info(f"🔄 Setting webhook to: {webhook_url}")

            async def set_webhook_task():
                try:
                    # حذف وب‌هوک قبلی
                    await bot.application.bot.delete_webhook()
                    time.sleep(2)
                    
                    # تنظیم وب‌هوک جدید - بدون توکن در URL
                    result = await bot.application.bot.set_webhook(
                        url=webhook_url,  # فقط /webhook
                        allowed_updates=["message", "callback_query"],
                        drop_pending_updates=True,
                        secret_token=bot_token  # استفاده از secret_token برای امنیت
                    )
                    self.webhook_set = True
                    logger.info(f"✅ Webhook set successfully!")
                    
                    # بررسی وضعیت وب‌هوک
                    webhook_info = await bot.application.bot.get_webhook_info()
                    logger.info(f"📊 Webhook info: {webhook_info.url}")
                    
                except Exception as e:
                    logger.error(f"❌ Error setting webhook: {e}")

            # اجرای غیرهمزمان
            asyncio.run(set_webhook_task())
            
        except Exception as e:
            logger.error(f"❌ Webhook setup failed: {e}")

# ایجاد مدیر وب‌هوک
webhook_manager = WebhookManager()

def initialize_app():
    """راه‌اندازی برنامه"""
    global bot
    try:
        # چک کردن توکن قبل از ایمپورت
        bot_token = os.environ.get('BOT_TOKEN')
        if not bot_token or bot_token == "YOUR_BOT_TOKEN_HERE":
            logger.error("❌ BOT_TOKEN not set.")
            return
            
        from main import bot as main_bot
        bot = main_bot
        logger.info("✅ Bot imported successfully")
        
        # راه‌اندازی وب‌هوک در پس‌زمینه
        time.sleep(5)
        webhook_manager.setup_webhook()
        
    except ImportError as e:
        logger.error(f"❌ Failed to import bot: {e}")
    except Exception as e:
        logger.error(f"❌ Error initializing app: {e}")

# راه‌اندازی هنگام شروع
@app.before_request
def before_first_request():
    """جایگزین before_first_request در Flask جدید"""
    if not hasattr(app, 'initialized'):
        logger.info("🚀 Initializing application...")
        threading.Thread(target=initialize_app, daemon=True).start()
        app.initialized = True

@app.route('/')
def home():
    bot_token_set = bool(os.environ.get('BOT_TOKEN')) and os.environ.get('BOT_TOKEN') != "YOUR_BOT_TOKEN_HERE"
    
    return f"""
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>ربات کنکور ۱۴۰۵</title>
        <style>
            body {{ font-family: Tahoma; text-align: center; padding: 50px; }}
            .container {{ background: white; padding: 30px; border-radius: 10px; max-width: 600px; margin: 0 auto; }}
            .status-ok {{ color: green; font-weight: bold; }}
            .status-error {{ color: red; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 ربات کنکور ۱۴۰۵</h1>
            
            <p class="{'status-ok' if bot_token_set else 'status-error'}">
                {'✅ BOT_TOKEN تنظیم شده' if bot_token_set else '❌ BOT_TOKEN تنظیم نشده'}
            </p>
            
            <p class="{'status-ok' if webhook_manager.webhook_set else 'status-error'}">
                {'✅ وب‌هوک فعال' if webhook_manager.webhook_set else '❌ وب‌هوک غیرفعال'}
            </p>
            
            <p><strong>آدرس وب‌هوک:</strong></p>
            <code>https://konkoor-bot.up.railway.app/webhook</code>
            
            <div style="margin-top: 20px;">
                <a href="/health" style="margin: 10px; padding: 10px; background: #007bff; color: white; text-decoration: none; border-radius: 5px;">بررسی سلامت</a>
                <a href="/set_webhook" style="margin: 10px; padding: 10px; background: #28a745; color: white; text-decoration: none; border-radius: 5px;">تنظیم وب‌هوک</a>
                <a href="/delete_webhook" style="margin: 10px; padding: 10px; background: #dc3545; color: white; text-decoration: none; border-radius: 5px;">حذف وب‌هوک</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health_check():
    """بررسی سلامت سرویس"""
    bot_token_set = bool(os.environ.get('BOT_TOKEN')) and os.environ.get('BOT_TOKEN') != "YOUR_BOT_TOKEN_HERE"
    
    status = {
        "status": "healthy" if bot_token_set else "config_error",
        "bot_token_set": bot_token_set,
        "webhook_set": webhook_manager.webhook_set,
        "bot_loaded": bot is not None,
        "timestamp": time.time()
    }
    return jsonify(status)

@app.route('/set_webhook', methods=['GET'])
def manual_webhook_setup():
    """تنظیم دستی وب‌هوک"""
    webhook_manager.setup_webhook()
    return jsonify({"message": "Webhook setup initiated"})

@app.route('/delete_webhook', methods=['GET'])
def delete_webhook():
    """حذف وب‌هوک"""
    global bot
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

# مسیر اصلی وب‌هوک - بدون توکن در URL
@app.route('/webhook', methods=['POST'])
def webhook():
    """دریافت آپدیت‌های تلگرام"""
    return handle_webhook_request()

def handle_webhook_request():
    """پردازش درخواست وب‌هوک"""
    global bot
    if not bot:
        logger.error("❌ Bot not available for webhook processing")
        return jsonify({"error": "Bot not available"}), 500
        
    try:
        if not request.is_json:
            logger.warning("❌ Received non-JSON request")
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        update_data = request.get_json()
        if not update_data:
            logger.warning("❌ Empty request body received")
            return jsonify({"error": "Empty request body"}), 400
        
        update_id = update_data.get('update_id', 'unknown')
        
        # بررسی secret token (امنیت)
        secret_token = request.headers.get('X-Telegram-Bot-Api-Secret-Token')
        expected_token = os.environ.get('BOT_TOKEN')
        
        if secret_token and secret_token != expected_token:
            logger.warning(f"❌ Invalid secret token: {secret_token}")
            return jsonify({"error": "Invalid secret token"}), 403
        
        logger.info(f"📨 Received update: {update_id}")
        
        # پردازش غیرهمزمان آپدیت
        async def process_update():
            try:
                await bot.application.process_update(update_data)
                logger.info(f"✅ Successfully processed update: {update_id}")
            except Exception as e:
                logger.error(f"❌ Error processing update {update_id}: {e}")
        
        asyncio.run(process_update())
        
        return jsonify({"status": "ok", "update_id": update_id}), 200
        
    except Exception as e:
        logger.error(f"❌ Webhook processing error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/test', methods=['GET'])
def test_route():
    """مسیر تست"""
    return jsonify({"message": "Test route works!", "timestamp": time.time()})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    # راه‌اندازی اولیه
    logger.info("🚀 Starting server...")
    threading.Thread(target=initialize_app, daemon=True).start()
    
    app.run(host='0.0.0.0', port=port, debug=False)
