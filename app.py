from flask import Flask, request, jsonify
import os
import asyncio
import logging
import threading
import traceback

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ساخت اپلیکیشن Flask
app = Flask(__name__)

# وضعیت ربات
application = None
bot_initialized = False

# راه‌اندازی async ربات
async def initialize_bot():
    global application, bot_initialized
    try:
        from main import get_application
        application = get_application()

        await application.initialize()
        await application.start()
        logger.info("✅ ربات initialize و start شد")

        # راه‌حل موقت: ساخت خودکار WEBHOOK_URL
        render_service_url = "https://konkour-bot-4i5p.onrender.com"
        webhook_url = f"{render_service_url}/webhook"
        
        logger.info(f"🔧 تنظیم وب‌هوک روی: {webhook_url}")
        
        # تنظیم وب‌هوک
        await application.bot.set_webhook(
            webhook_url,
            allowed_updates=["message", "callback_query", "chat_member", "inline_query"],
            drop_pending_updates=True,
            max_connections=40
        )

        # بررسی وضعیت وب‌هوک
        webhook_info = await application.bot.get_webhook_info()
        logger.info(f"📊 وضعیت وب‌هوک: {webhook_info.url} - pending: {webhook_info.pending_update_count}")

        if webhook_info.url != webhook_url:
            logger.error(f"❌ وب‌هوک تنظیم نشد! انتظار: {webhook_url}, واقعی: {webhook_info.url}")
        else:
            logger.info("✅ وب‌هوک با موفقیت تنظیم شد")

        bot_initialized = True
        logger.info("🎉 ربات با وب‌هوک فعال شد")
        return True

    except Exception as e:
        logger.error(f"❌ خطا در راه‌اندازی ربات: {e}")
        logger.error(traceback.format_exc())
        return False

# اجرای async در thread جداگانه
def run_async_init():
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(initialize_bot())
        if success:
            logger.info("🎉 ربات با موفقیت راه‌اندازی شد")
        else:
            logger.error("💥 خطا در راه‌اندازی ربات")
    except Exception as e:
        logger.error(f"❌ خطا در اجرای async: {e}")

# راه‌اندازی اولیه هنگام اولین درخواست
@app.before_request
def startup():
    global bot_initialized
    if not bot_initialized:
        logger.info("🚀 شروع راه‌اندازی ربات...")
        thread = threading.Thread(target=run_async_init)
        thread.daemon = True
        thread.start()
        bot_initialized = True

# صفحه اصلی
@app.route('/')
def home():
    return "🤖 ربات کنکور ۱۴۰۵ - فعال ✅"

# بررسی سلامت سرویس
@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "bot_initialized": bot_initialized,
        "service": "konkour-bot"
    })

# دریافت آپدیت‌های تلگرام
@app.route('/webhook', methods=['POST'])
def webhook():
    logger.info("📨 دریافت درخواست وب‌هوک")

    if not application:
        logger.error("❌ ربات آماده نیست")
        return jsonify({"error": "ربات آماده نیست"}), 500

    try:
        update_data = request.get_json()
        if not update_data:
            logger.error("❌ داده‌ای دریافت نشد")
            return jsonify({"error": "No data received"}), 400

        update_id = update_data.get('update_id', 'unknown')
        logger.info(f"📝 پردازش آپدیت: {update_id}")
        
        # لاگ جزئیات بیشتر برای دیباگ
        if 'message' in update_data:
            message = update_data['message']
            chat_id = message.get('chat', {}).get('id')
            text = message.get('text', '')
            logger.info(f"💬 پیام از {chat_id}: {text}")
        elif 'callback_query' in update_data:
            callback = update_data['callback_query']
            data = callback.get('data', '')
            logger.info(f"🔘 کال‌بک: {data}")

        async def process_update():
            try:
                await application.process_update(update_data)
                logger.info(f"✅ آپدیت {update_id} با موفقیت پردازش شد")
            except Exception as e:
                logger.error(f"❌ خطا در پردازش آپدیت {update_id}: {e}")
                logger.error(traceback.format_exc())
                raise

        asyncio.run(process_update())
        return jsonify({"status": "ok", "update_id": update_id}), 200

    except Exception as e:
        logger.error(f"❌ خطا در پردازش وب‌هوک: {e}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "Internal server error"}), 500

# صفحه دیباگ
@app.route('/debug')
def debug():
    return jsonify({
        "application_exists": application is not None,
        "bot_initialized": bot_initialized,
        "status": "debug"
    })
