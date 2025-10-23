import asyncio
import requests
import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def setup_webhook():
    """تنظیم خودکار وب‌هوک پس از deploy"""
    try:
        webhook_url = f"{config.WEBHOOK_URL}/webhook"
        
        # حذف وب‌هوک قبلی
        delete_url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/deleteWebhook"
        requests.get(delete_url)
        
        # تنظیم وب‌هوک جدید
        set_webhook_url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/setWebhook"
        payload = {
            "url": webhook_url,
            "max_connections": 40,
            "allowed_updates": ["message", "callback_query"]
        }
        
        response = requests.post(set_webhook_url, json=payload)
        result = response.json()
        
        if result.get("ok"):
            logger.info(f"✅ Webhook setup successful: {webhook_url}")
            
            # دریافت اطلاعات وب‌هوک
            webhook_info_url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/getWebhookInfo"
            info_response = requests.get(webhook_info_url)
            webhook_info = info_response.json()
            
            logger.info(f"📊 Webhook info: {webhook_info}")
            
            return True
        else:
            logger.error(f"❌ Webhook setup failed: {result}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error setting up webhook: {e}")
        return False

if __name__ == "__main__":
    # اجرای تنظیم وب‌هوک
    asyncio.run(setup_webhook())
