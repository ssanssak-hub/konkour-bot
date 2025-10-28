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
                logger.info("💡 Please set BOT_TOKEN in Railway dashboard")
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
                    time.sleep(1)
                    
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

def initialize_app():
    """راه‌اندازی برنامه"""
    global bot
    try:
        # چک کردن توکن قبل از ایمپورت
        bot_token = os.environ.get('BOT_TOKEN')
        if not bot_token or bot_token == "YOUR_BOT_TOKEN_HERE":
            logger.error("❌ BOT_TOKEN not set. Please add it in Railway Variables")
            return
            
        from main import bot as main_bot
        bot = main_bot
        logger.info("✅ Bot imported successfully")
        
        # راه‌اندازی وب‌هوک در پس‌زمینه
        time.sleep(3)
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
            
            <p>Platform: Railway</p>
            
            {'' if bot_token_set else '''
            <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3>⚠️ راهنمای تنظیم توکن:</h3>
                <ol style="text-align: right; direction: rtl;">
                    <li>به Dashboard Railway بروید</li>
                    <li>روی App خود کلیک کنید</li>
                    <li>به تب Variables بروید</li>
                    <li>New Variable اضافه کنید:
                        <br><strong>Key:</strong> BOT_TOKEN
                        <br><strong>Value:</strong> توکن ربات تلگرام شما
                    </li>
                </ol>
            </div>
            '''}
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
        "bot_loaded": bot is not None
    }
    return jsonify(status)

@app.route('/set_webhook', methods=['GET'])
def manual_webhook_setup():
    """تنظیم دستی وب‌هوک"""
    webhook_manager.setup_webhook()
    return jsonify({"message": "Webhook setup initiated"})

# مسیر اصلی وب‌هوک با توکن
@app.route('/<token>', methods=['POST'])
def webhook_with_token(token):
    """دریافت آپدیت‌های تلگرام با توکن"""
    expected_token = os.environ.get('BOT_TOKEN')
    if not expected_token or expected_token == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ BOT_TOKEN not configured")
        return jsonify({"error": "Bot token not configured"}), 500
        
    if token != expected_token:
        logger.warning(f"❌ Invalid token received: {token}")
        return jsonify({"error": "Invalid token"}), 403
    
    return handle_webhook_request()

def handle_webhook_request():
    """پردازش درخواست وب‌هوک"""
    global bot
    if not bot:
        logger.error("❌ Bot not available for webhook processing")
        return jsonify({"error": "Bot not available"}), 500
        
    try:
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        update_data = request.get_json()
        if not update_data:
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
        
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        logger.error(f"❌ Webhook processing error: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    # راه‌اندازی اولیه
    threading.Thread(target=initialize_app, daemon=True).start()
    
    logger.info(f"🚀 Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
