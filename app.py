import os
import logging
import asyncio
import threading
import json
import requests
from datetime import datetime
from flask import Flask, request, jsonify

# تنظیمات اصلی
BOT_TOKEN = "8381121739:AAFB2YBMomBh9xhoI3Qn0VVuGaGlpea9fx8"
WEBHOOK_URL = "https://konkour-bot.onrender.com"
WEBHOOK_SECRET = "konkur1405_secret_key_2024"
ADMIN_ID = 7703677187

app = Flask(__name__)

# ==================== سیستم لاگینگ ساده ====================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== مدیریت ربات ====================

class KonkurBot:
    def __init__(self):
        self.initialized = False
        self.bot = None
        self.start_time = datetime.now()
        
    def initialize(self):
        """راه‌اندازی مطمئن ربات"""
        try:
            logger.info("🚀 شروع راه‌اندازی ربات...")
            
            # تست اتصال به تلگرام
            test_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
            response = requests.get(test_url, timeout=10)
            result = response.json()
            
            if not result.get('ok'):
                logger.error(f"❌ توکن نامعتبر: {result}")
                return False
                
            logger.info(f"✅ توکن معتبر: @{result['result']['username']}")
            
            # ایجاد session برای ربات
            self.bot = {
                'token': BOT_TOKEN,
                'username': result['result']['username'],
                'first_name': result['result']['first_name']
            }
            
            self.initialized = True
            logger.info("✅ ربات با موفقیت راه‌اندازی شد")
            return True
            
        except Exception as e:
            logger.error(f"❌ خطا در راه‌اندازی: {e}")
            return False
    
    async def send_message(self, chat_id, text, reply_markup=None):
        """ارسال پیام به کاربر"""
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }
            
            if reply_markup:
                data['reply_markup'] = json.dumps(reply_markup)
                
            response = requests.post(url, json=data, timeout=10)
            return response.json().get('ok', False)
            
        except Exception as e:
            logger.error(f"❌ خطا در ارسال پیام: {e}")
            return False
    
    async def edit_message(self, chat_id, message_id, text, reply_markup=None):
        """ویرایش پیام"""
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
            data = {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': text,
                'parse_mode': 'HTML'
            }
            
            if reply_markup:
                data['reply_markup'] = json.dumps(reply_markup)
                
            response = requests.post(url, json=data, timeout=10)
            return response.json().get('ok', False)
            
        except Exception as e:
            logger.error(f"❌ خطا در ویرایش پیام: {e}")
            return False
    
    async def answer_callback(self, callback_id):
        """پاسخ به callback"""
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery"
            data = {'callback_query_id': callback_id}
            requests.post(url, json=data, timeout=5)
        except:
            pass

# ==================== سیستم منو و محتوا ====================

class MenuSystem:
    def __init__(self):
        self.exam_dates = {
            "علوم تجربی": "1405-04-12",
            "ریاضی و فنی": "1405-04-11", 
            "علوم انسانی": "1405-04-11",
            "فرهنگیان": "1405-02-17",
            "هنر": "1405-04-12",
            "زبان و گروه‌های خارجه": "1405-04-12"
        }
    
    def create_main_menu(self):
        """ایجاد منوی اصلی"""
        return {
            'inline_keyboard': [
                [{'text': '⏳ چند روز تا کنکور؟', 'callback_data': 'countdown'}],
                [{'text': '📅 تقویم و رویدادها', 'callback_data': 'calendar'}],
                [{'text': '🔔 مدیریت یادآوری‌ها', 'callback_data': 'reminders'}],
                [{'text': '📊 آمار و گزارش', 'callback_data': 'statistics'}],
                [{'text': '❓ راهنما', 'callback_data': 'help'}]
            ]
        }
    
    def create_countdown_menu(self):
        """منوی شمارش معکوس"""
        import jdatetime
        
        keyboard = []
        for exam_name, exam_date in self.exam_dates.items():
            # محاسبه روزهای باقی‌مانده
            today = jdatetime.datetime.now()
            exam_jdate = jdatetime.datetime.strptime(exam_date, "%Y-%m-%d")
            days_remaining = (exam_jdate - today).days
            
            keyboard.append([{
                'text': f'🎯 {exam_name} ({days_remaining} روز)',
                'callback_data': f'show_{exam_name}'
            }])
        
        keyboard.append([{'text': '🏠 منوی اصلی', 'callback_data': 'main_menu'}])
        
        return {'inline_keyboard': keyboard}
    
    def get_exam_info(self, exam_name):
        """دریافت اطلاعات کنکور"""
        import jdatetime
        
        exam_date = self.exam_dates.get(exam_name, "1405-04-12")
        today = jdatetime.datetime.now()
        exam_jdate = jdatetime.datetime.strptime(exam_date, "%Y-%m-%d")
        days_remaining = (exam_jdate - today).days
        
        info = f"""
⏰ **شمارش معکوس کنکور {exam_name}**

🕐 **زمان باقی‌مانده:** {days_remaining} روز
📅 **تاریخ کنکور:** {exam_date.replace('-', '/')}
🕒 **ساعت برگزاری:** ۰۸:۰۰ صبح

"""
        
        if days_remaining > 60:
            info += "🎯 **وضعیت:** فرصت خوبی داری! برنامه‌ریزی کن"
        elif days_remaining > 30:
            info += "🔥 **وضعیت:** زمان جدی‌تر شدن!"
        elif days_remaining > 0:
            info += "⚡ **وضعیت:** روزهای پایانی! تمرکزت رو حفظ کن"
        else:
            info += "✅ **وضعیت:** کنکور برگزار شد"
        
        info += """

💡 **توصیه مطالعاتی:**
📚 برنامه‌ریزی منظم روزانه داشته باش
🎯 روی نقاط ضعف تمرکز کن  
⏱️ زمانت رو هوشمندانه مدیریت کن
🧘 استراحت و سلامت روان رو فراموش نکن
"""
        
        return info
    
    def get_calendar_info(self):
        """اطلاعات تقویم"""
        import jdatetime
        
        today = jdatetime.datetime.now()
        
        return f"""
📅 **تقویم کنکور ۱۴۰۵**

🕒 **امروز:** {today.strftime('%A %Y/%m/%d')}
📆 **تاریخ دقیق:** {today.strftime('%Y/%m/%d %H:%M:%S')}

🎯 **تاریخ‌های مهم کنکور:**
• ریاضی و فنی: ۱۴۰۵/۰۴/۱۱
• علوم انسانی: ۱۴۰۵/۰۴/۱۱
• علوم تجربی: ۱۴۰۵/۰۴/۱۲  
• هنر: ۱۴۰۵/۰۴/۱۲
• زبان: ۱۴۰۵/۰۴/۱۲

💡 **نکته:** تاریخ‌ها بر اساس اعلام سازمان سنجش می‌باشد
"""
    
    def get_help_text(self):
        """متن راهنما"""
        return """
❓ **راهنمای ربات کنکور ۱۴۰۵**

🎯 **دستورات اصلی:**
/start - شروع کار با ربات

⏳ **شمارش معکوس:**
• مشاهده زمان باقی‌مانده تا کنکور
• تاریخ دقیق هر رشته
• توصیه‌های مطالعاتی

📅 **تقویم:**
• نمایش تاریخ شمسی
• تاریخ‌های مهم کنکوری
• مناسبت‌ها

🔔 **یادآوری:**
• تنظیم یادآوری کنکور
• یادآوری مطالعه

📊 **آمار:**
• مشاهده عملکرد ربات
• آمار کاربران

💡 **برای شروع از /start استفاده کنید**
"""

# ==================== ایجاد نمونه‌ها ====================

bot = KonkurBot()
menu_system = MenuSystem()

# راه‌اندازی اولیه ربات
logger.info("🔧 راه‌اندازی اولیه سیستم...")
if bot.initialize():
    logger.info("✅ سیستم آماده است")
else:
    logger.info("⚠️ سیستم با محدودیت راه‌اندازی شد")

# ==================== وب‌هوک و API ====================

@app.route('/')
def home():
    """صفحه اصلی"""
    return jsonify({
        "status": "active",
        "service": "Konkur 1405 Bot",
        "version": "2.0.0",
        "bot_initialized": bot.initialized,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/health')
def health():
    """بررسی سلامت"""
    return jsonify({
        "status": "healthy",
        "bot_initialized": bot.initialized,
        "uptime": str(datetime.now() - bot.start_time).split('.')[0],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/set_webhook')
def set_webhook():
    """تنظیم وب‌هوک"""
    try:
        webhook_url = f"{WEBHOOK_URL}/webhook"
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
        
        params = {
            'url': webhook_url,
            'secret_token': WEBHOOK_SECRET,
            'max_connections': 40
        }
        
        response = requests.get(url, params=params, timeout=10)
        result = response.json()
        
        return jsonify({
            "status": "success" if result.get('ok') else "error",
            "result": result
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# ==================== پردازش پیام‌ها ====================

async def process_start(chat_id, user_name):
    """پردازش دستور start"""
    welcome_text = f"""
👋 **سلام {user_name} عزیز!**

🎓 **به ربات کنکور ۱۴۰۵ خوش آمدید!**

🤖 **من یک دستیار هوشمندم که می‌تونم در مسیر کنکورت کمکت کنم:**

⏳ **شمارش معکوس هوشمند کنکور**
📅 **تقویم و برنامه‌ریزی پیشرفته**  
🔔 **سیستم یادآوری هوشمند**
📚 **مدیریت برنامه مطالعه**
📊 **آنالیز پیشرفت درسی**

💡 **برای شروع، از منوی زیر انتخاب کن:**
"""
    return await bot.send_message(chat_id, welcome_text, menu_system.create_main_menu())

async def process_callback(chat_id, message_id, callback_data, user_name):
    """پردازش callback‌ها"""
    await bot.answer_callback(callback_data['id'])
    
    if callback_data['data'] == 'main_menu':
        text = f"🏠 **منوی اصلی ربات کنکور**\n\nلطفاً بخش مورد نظر خود را انتخاب کنید:"
        return await bot.edit_message(chat_id, message_id, text, menu_system.create_main_menu())
    
    elif callback_data['data'] == 'countdown':
        text = "⏳ **سیستم شمارش معکوس کنکور ۱۴۰۵**\n\n🎯 لطفاً کنکور مورد نظر خود را انتخاب کنید:"
        return await bot.edit_message(chat_id, message_id, text, menu_system.create_countdown_menu())
    
    elif callback_data['data'] == 'calendar':
        text = menu_system.get_calendar_info()
        keyboard = {
            'inline_keyboard': [
                [{'text': '⏳ شمارش معکوس', 'callback_data': 'countdown'}],
                [{'text': '🏠 منوی اصلی', 'callback_data': 'main_menu'}]
            ]
        }
        return await bot.edit_message(chat_id, message_id, text, keyboard)
    
    elif callback_data['data'] == 'help':
        text = menu_system.get_help_text()
        keyboard = {
            'inline_keyboard': [
                [{'text': '🏠 منوی اصلی', 'callback_data': 'main_menu'}]
            ]
        }
        return await bot.edit_message(chat_id, message_id, text, keyboard)
    
    elif callback_data['data'].startswith('show_'):
        exam_name = callback_data['data'].replace('show_', '')
        text = menu_system.get_exam_info(exam_name)
        keyboard = {
            'inline_keyboard': [
                [{'text': '📊 همه کنکورها', 'callback_data': 'countdown'}],
                [{'text': '🏠 منوی اصلی', 'callback_data': 'main_menu'}]
            ]
        }
        return await bot.edit_message(chat_id, message_id, text, keyboard)
    
    elif callback_data['data'] in ['reminders', 'statistics']:
        text = "🔧 **این بخش به زودی فعال خواهد شد**\n\nدر حال حاضر می‌توانید از بخش‌های دیگر استفاده کنید."
        keyboard = {
            'inline_keyboard': [
                [{'text': '🏠 منوی اصلی', 'callback_data': 'main_menu'}]
            ]
        }
        return await bot.edit_message(chat_id, message_id, text, keyboard)

async def process_text_message(chat_id, text, user_name):
    """پردازش پیام متنی"""
    responses = {
        "سلام": "سلام! 👋 چطور می‌تونم کمکت کنم?",
        "خداحافظ": "خداحافظ! 🫡 موفق باشی در مسیر کنکور!",
        "تشکر": "خواهش می‌کنم! 😊 خوشحالم می‌تونم کمک کنم",
        "کنکور": "آماده‌ای برای کنکور? از منوی اصلی می‌تونی زمان‌بندی رو ببینی 🎯"
    }
    
    response = responses.get(text, 
        "🤔 **متوجه پیام شما نشدم!**\n\n"
        "💡 لطفاً از منوی اصلی استفاده کنید یا دستور /start را وارد کنید."
    )
    
    return await bot.send_message(chat_id, response, menu_system.create_main_menu())

# ==================== endpoint اصلی وب‌هوک ====================

@app.route('/webhook', methods=['POST'])
def webhook():
    """دریافت وب‌هوک از تلگرام"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"status": "success"}), 200
        
        # اگر ربات راه‌اندازی نشده، تلاش برای راه‌اندازی
        if not bot.initialized:
            bot.initialize()
        
        # پردازش غیرهمزمان
        def process_async():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(process_update(data))
                loop.close()
            except Exception as e:
                logger.error(f"❌ خطا در پردازش: {e}")
        
        thread = threading.Thread(target=process_async)
        thread.daemon = True
        thread.start()
        
        return jsonify({"status": "success"}), 200
        
    except Exception as e:
        logger.error(f"💥 خطای کلی: {e}")
        return jsonify({"status": "success"}), 200

async def process_update(data):
    """پردازش آپدیت دریافتی"""
    update_id = data.get('update_id', 'unknown')
    logger.info(f"📨 پردازش آپدیت: {update_id}")
    
    # پیام متنی
    if 'message' in data and 'text' in data['message']:
        message = data['message']
        chat_id = message['chat']['id']
        text = message['text']
        user_name = message['from'].get('first_name', 'کاربر')
        
        if text == '/start':
            await process_start(chat_id, user_name)
        else:
            await process_text_message(chat_id, text, user_name)
    
    # callback query
    elif 'callback_query' in data:
        callback = data['callback_query']
        chat_id = callback['message']['chat']['id']
        message_id = callback['message']['message_id']
        user_name = callback['from'].get('first_name', 'کاربر')
        
        await process_callback(chat_id, message_id, callback, user_name)

# ==================== اجرای برنامه ====================

if __name__ == '__main__':
    logger.info("=" * 50)
    logger.info("🤖 ربات کنکور ۱۴۰۵ - فعال")
    logger.info("=" * 50)
    
    # تنظیم وب‌هوک
    try:
        webhook_url = f"{WEBHOOK_URL}/webhook"
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
        params = {'url': webhook_url, 'secret_token': WEBHOOK_SECRET}
        requests.get(url, params=params, timeout=10)
        logger.info("✅ وب‌هوک تنظیم شد")
    except Exception as e:
        logger.warning(f"⚠️ خطا در تنظیم وب‌هوک: {e}")
    
    # اجرای سرور
    app.run(host='0.0.0.0', port=10000, debug=False)
