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
except Exception as e:
    logger.error(f"❌ Failed to import bot: {e}")
    bot = None

class WebhookManager:
    def __init__(self):
        self.webhook_set = False
    
    def setup_webhook(self):
        """تنظیم وب‌هوک"""
        if not bot:
            logger.error("❌ Bot not available")
            return False
            
        try:
            bot_token = os.environ.get('BOT_TOKEN')
            if not bot_token:
                logger.error("❌ BOT_TOKEN not set")
                return False

            webhook_url = "https://konkoor-bot.up.railway.app/webhook"
            logger.info(f"🔄 Setting webhook to: {webhook_url}")

            async def set_webhook_task():
                try:
                    # تنظیم وب‌هوک جدید
                    result = await bot.application.bot.set_webhook(
                        url=webhook_url,
                        allowed_updates=["message", "callback_query"],
                        drop_pending_updates=True,
                        max_connections=40
                    )
                    self.webhook_set = True
                    logger.info(f"✅ Webhook set successfully!")
                    return True
                    
                except Exception as e:
                    logger.error(f"❌ Error setting webhook: {e}")
                    return False

            return asyncio.run(set_webhook_task())
            
        except Exception as e:
            logger.error(f"❌ Webhook setup failed: {e}")
            return False

webhook_manager = WebhookManager()

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>ربات کنکور</title>
    </head>
    <body style="font-family: Tahoma; text-align: center; padding: 50px;">
        <h1>🤖 ربات کنکور ۱۴۰۵</h1>
        <p>✅ سرویس فعال</p>
        <p>آدرس وب‌هوک: <code>https://konkoor-bot.up.railway.app/webhook</code></p>
        <div style="margin-top: 20px;">
            <a href="/set_webhook" style="padding: 10px; background: green; color: white; text-decoration: none;">
                🔄 تنظیم وب‌هوک
            </a>
        </div>
    </body>
    </html>
    """

@app.route('/set_webhook', methods=['GET'])
def set_webhook_manual():
    """تنظیم دستی وب‌هوک"""
    success = webhook_manager.setup_webhook()
    if success:
        return jsonify({
            "status": "success",
            "message": "Webhook set successfully",
            "url": "https://konkoor-bot.up.railway.app/webhook"
        })
    else:
        return jsonify({
            "status": "error", 
            "message": "Failed to set webhook"
        }), 500

@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    """دریافت آپدیت‌های تلگرام"""
    logger.info("📨 Webhook received!")
    
    if request.method == 'GET':
        return jsonify({"message": "Webhook is ready!", "status": "active"})
    
    if not bot:
        logger.error("❌ Bot not available")
        return jsonify({"error": "Bot not available"}), 500
        
    try:
        update_data = request.get_json()
        if not update_data:
            logger.error("❌ No JSON data received")
            return jsonify({"error": "No data"}), 400
            
        update_id = update_data.get('update_id', 'unknown')
        logger.info(f"📝 Processing update: {update_id}")
        
        # پردازش آپدیت
        async def process_update():
            try:
                await bot.application.process_update(update_data)
                logger.info(f"✅ Update {update_id} processed successfully")
            except Exception as e:
                logger.error(f"❌ Error processing update {update_id}: {e}")
        
        asyncio.run(process_update())
        
        return jsonify({"status": "ok", "update_id": update_id}), 200
        
    except Exception as e:
        logger.error(f"❌ Webhook processing error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "webhook_set": webhook_manager.webhook_set,
        "bot_loaded": bot is not None,
        "timestamp": time.time()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 Starting server on port {port}")
    
    # راه‌اندازی وب‌هوک
    time.sleep(5)
    webhook_manager.setup_webhook()
    
    app.run(host='0.0.0.0', port=port, debug=False)
