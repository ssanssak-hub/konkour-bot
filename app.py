import os
import logging
import requests
from flask import Flask, request, jsonify
import sqlite3
import json
from datetime import datetime

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

def send_telegram_message(chat_id, text, reply_markup=None):
    """ارسال پیام به تلگرام"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    
    if reply_markup:
        payload["reply_markup"] = reply_markup
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        logger.error(f"❌ خطا در ارسال پیام: {e}")
        return None

def edit_telegram_message(chat_id, message_id, text, reply_markup=None):
    """ویرایش پیام تلگرام"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "HTML"
    }
    
    if reply_markup:
        payload["reply_markup"] = reply_markup
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        logger.error(f"❌ خطا در ویرایش پیام: {e}")
        return None

def answer_callback_query(callback_query_id, text=None):
    """پاسخ به callback query"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery"
    payload = {
        "callback_query_id": callback_query_id
    }
    
    if text:
        payload["text"] = text
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        logger.error(f"❌ خطا در پاسخ به callback: {e}")
        return None

def create_main_menu_keyboard():
    """ایجاد کیبورد منوی اصلی"""
    keyboard = {
        "inline_keyboard": [
            [{"text": "⏳ چند روز تا کنکور؟", "callback_data": "countdown"}],
            [{"text": "📅 تقویم و رویدادها", "callback_data": "calendar"}],
            [{"text": "🔔 مدیریت یادآوری‌ها", "callback_data": "reminders"}],
            [{"text": "📨 ارسال پیام", "callback_data": "send_message"}],
            [{"text": "✅ اعلام حضور", "callback_data": "attendance"}],
            [{"text": "📚 اهداف و برنامه‌ریزی", "callback_data": "study_plan"}],
            [{"text": "📊 آمار و گزارش", "callback_data": "statistics"}],
            [{"text": "❓ راهنما", "callback_data": "help"}],
            [{"text": "🔧 پنل مدیریت", "callback_data": "admin_panel"}]
        ]
    }
    return keyboard

def create_back_keyboard():
    """ایجاد کیبورد بازگشت"""
    keyboard = {
        "inline_keyboard": [
            [{"text": "🏠 بازگشت به منو", "callback_data": "main_menu"}]
        ]
    }
    return keyboard

def init_database():
    """راه‌اندازی دیتابیس"""
    try:
        conn = sqlite3.connect('konkur_bot.db')
        cursor = conn.cursor()
        
        # ایجاد جدول کاربران
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')
        
        # ایجاد جدول حضور و غیاب
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                check_in_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ دیتابیس راه‌اندازی شد")
        return True
    except Exception as e:
        logger.error(f"❌ خطا در راه‌اندازی دیتابیس: {e}")
        return False

def add_user(user_id, username, first_name, last_name):
    """افزودن کاربر به دیتابیس"""
    try:
        conn = sqlite3.connect('konkur_bot.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, username, first_name, last_name, last_active, is_active)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, TRUE)
        ''', (user_id, username, first_name, last_name))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"❌ خطا در افزودن کاربر: {e}")
        return False

def record_attendance(user_id):
    """ثبت حضور کاربر"""
    try:
        conn = sqlite3.connect('konkur_bot.db')
        cursor = conn.cursor()
        
        # بررسی آیا امروز حضور ثبت شده
        cursor.execute('''
            SELECT COUNT(*) FROM attendance 
            WHERE user_id = ? AND DATE(check_in_time) = DATE('now')
        ''', (user_id,))
        
        count = cursor.fetchone()[0]
        
        if count == 0:
            cursor.execute('''
                INSERT INTO attendance (user_id) VALUES (?)
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False  # امروز قبلاً حضور ثبت شده
    except Exception as e:
        logger.error(f"❌ خطا در ثبت حضور: {e}")
        return False

def get_today_attendance_count():
    """دریافت تعداد حضورهای امروز"""
    try:
        conn = sqlite3.connect('konkur_bot.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(DISTINCT user_id) FROM attendance 
            WHERE DATE(check_in_time) = DATE('now')
        ''')
        
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        logger.error(f"❌ خطا در دریافت آمار حضور: {e}")
        return 0

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
                process_message(update_data['message'])
            elif 'callback_query' in update_data:
                process_callback_query(update_data['callback_query'])
            
            return jsonify({"status": "success"})
            
        except Exception as e:
            logger.error(f"❌ خطا در پردازش وب‌هوک: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500
    
    return jsonify({"status": "error", "message": "Method not allowed"}), 405

def process_message(message):
    """پردازش پیام دریافتی"""
    chat_id = message['chat']['id']
    user_id = message['from']['id']
    text = message.get('text', '')
    
    # ثبت کاربر
    add_user(
        user_id=user_id,
        username=message['from'].get('username'),
        first_name=message['from'].get('first_name', ''),
        last_name=message['from'].get('last_name', '')
    )
    
    if text == '/start':
        send_welcome_message(chat_id, message['from']['first_name'])
    elif text == '/menu':
        send_main_menu(chat_id)
    else:
        send_unknown_message(chat_id)

def process_callback_query(callback_query):
    """پردازش callback query"""
    chat_id = callback_query['message']['chat']['id']
    message_id = callback_query['message']['message_id']
    callback_data = callback_query['data']
    callback_id = callback_query['id']
    
    # پاسخ به callback
    answer_callback_query(callback_id)
    
    if callback_data == 'main_menu':
        send_main_menu(chat_id, message_id)
    elif callback_data == 'countdown':
        send_countdown_menu(chat_id, message_id)
    elif callback_data == 'calendar':
        send_calendar_menu(chat_id, message_id)
    elif callback_data == 'reminders':
        send_reminders_menu(chat_id, message_id)
    elif callback_data == 'attendance':
        process_attendance(chat_id, message_id, callback_query['from']['id'])
    elif callback_data == 'study_plan':
        send_study_plan_menu(chat_id, message_id)
    elif callback_data == 'statistics':
        send_statistics_menu(chat_id, message_id)
    elif callback_data == 'help':
        send_help_menu(chat_id, message_id)
    elif callback_data == 'admin_panel':
        send_admin_panel(chat_id, message_id, callback_query['from']['id'])
    elif callback_data.startswith('countdown_'):
        show_countdown(chat_id, message_id, callback_data.replace('countdown_', ''))

def send_welcome_message(chat_id, first_name):
    """ارسال پیام خوشآمدگویی"""
    text = f"""
سلام {first_name}! 👋

به ربات کنکور ۱۴۰۵ خوش آمدید! 🎓

من می‌تونم در زمینه‌های زیر بهت کمک کنم:
• ⏳ شمارش معکوس تا کنکور
• 📅 مدیریت زمان و برنامه‌ریزی
• 🔔 تنظیم یادآوری‌های هوشمند
• 📚 ثبت اهداف و پیشرفت مطالعه
• 📊 تحلیل آمار و عملکرد

لطفاً یکی از گزینه‌های زیر را انتخاب کنید:
"""
    
    send_telegram_message(chat_id, text, create_main_menu_keyboard())

def send_main_menu(chat_id, message_id=None):
    """ارسال منوی اصلی"""
    text = "🏠 منوی اصلی\n\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:"
    
    if message_id:
        edit_telegram_message(chat_id, message_id, text, create_main_menu_keyboard())
    else:
        send_telegram_message(chat_id, text, create_main_menu_keyboard())

def send_countdown_menu(chat_id, message_id):
    """ارسال منوی شمارش معکوس"""
    keyboard = {
        "inline_keyboard": [
            [{"text": "🔬 علوم تجربی", "callback_data": "countdown_علوم تجربی"}],
            [{"text": "📐 ریاضی‌وفنی", "callback_data": "countdown_ریاضی‌وفنی"}],
            [{"text": "📚 علوم انسانی", "callback_data": "countdown_علوم انسانی"}],
            [{"text": "👨‍🏫 فرهنگیان", "callback_data": "countdown_فرهنگیان"}],
            [{"text": "🎨 هنر", "callback_data": "countdown_هنر"}],
            [{"text": "🌍 زبان‌وگروه‌های‌خارجه", "callback_data": "countdown_زبان‌وگروه‌های‌خارجه"}],
            [{"text": "🏠 بازگشت به منو", "callback_data": "main_menu"}]
        ]
    }
    
    text = "🎯 انتخاب کنکور برای نمایش زمان باقی‌مانده\n\nلطفاً کنکور مورد نظر خود را انتخاب کنید:"
    edit_telegram_message(chat_id, message_id, text, keyboard)

def show_countdown(chat_id, message_id, exam_name):
    """نمایش زمان باقی‌مانده تا کنکور"""
    exam_dates = {
        "علوم تجربی": "1405-04-12",
        "ریاضی‌وفنی": "1405-04-11",
        "علوم انسانی": "1405-04-11",
        "فرهنگیان": "1405-02-17 و 1405-02-18",
        "هنر": "1405-04-12",
        "زبان‌وگروه‌های‌خارجه": "1405-04-12"
    }
    
    days_remaining = {
        "علوم تجربی": 260,
        "ریاضی‌وفنی": 259,
        "علوم انسانی": 259,
        "فرهنگیان": 180,
        "هنر": 260,
        "زبان‌وگروه‌های‌خارجه": 260
    }
    
    date = exam_dates.get(exam_name, "نامشخص")
    days = days_remaining.get(exam_name, 0)
    
    text = f"""
⏰ زمان باقی‌مانده تا کنکور {exam_name}:

📅 تاریخ: {date}
⏳ روزهای باقی‌مانده: {days} روز

💡 توصیه: {get_study_recommendation(days)}
"""
    
    keyboard = {
        "inline_keyboard": [
            [{"text": "🔄 بروزرسانی", "callback_data": f"countdown_{exam_name}"}],
            [{"text": "📊 همه کنکورها", "callback_data": "countdown"}],
            [{"text": "🏠 بازگشت به منو", "callback_data": "main_menu"}]
        ]
    }
    
    edit_telegram_message(chat_id, message_id, text, keyboard)

def get_study_recommendation(days):
    """دریافت توصیه مطالعه"""
    if days > 180:
        return "📅 زمان کافی داری! با برنامه‌ریزی منظم پیش برو."
    elif days > 90:
        return "⏳ نیمه راهی! روی نقاط ضعف تمرکز کن."
    elif days > 30:
        return "🚀 زمان محدود! تست‌زنی رو بیشتر کن."
    elif days > 7:
        return "🔥 فاز آخر! مرور سریع و تست زمان‌دار."
    else:
        return "🎯 نزدیک کنکوری! استراحت کن و آروم باش."

def send_calendar_menu(chat_id, message_id):
    """ارسال منوی تقویم"""
    text = """
📅 تقویم و رویدادها

امکانات تقویم:
• نمایش تقویم شمسی
• مناسبت‌های مهم
• رویدادهای کنکور
• مدیریت رویدادهای شخصی
"""
    
    keyboard = {
        "inline_keyboard": [
            [{"text": "📅 تقویم جاری", "callback_data": "current_calendar"}],
            [{"text": "🔍 مشاهده رویدادها", "callback_data": "view_events"}],
            [{"text": "🏠 بازگشت به منو", "callback_data": "main_menu"}]
        ]
    }
    
    edit_telegram_message(chat_id, message_id, text, keyboard)

def send_reminders_menu(chat_id, message_id):
    """ارسال منوی یادآوری‌ها"""
    text = """
🔔 مدیریت یادآوری‌ها

با این قابلیت می‌توانید:
• ⏰ یادآوری کنکور تنظیم کنید
• 📝 یادآوری متفرقه ایجاد کنید
• 📚 یادآوری مطالعه تنظیم کنید
"""
    
    keyboard = {
        "inline_keyboard": [
            [{"text": "⏰ یادآوری کنکور", "callback_data": "exam_reminder"}],
            [{"text": "📝 یادآوری متفرقه", "callback_data": "custom_reminder"}],
            [{"text": "📚 یادآوری مطالعه", "callback_data": "study_reminder"}],
            [{"text": "🏠 بازگشت به منو", "callback_data": "main_menu"}]
        ]
    }
    
    edit_telegram_message(chat_id, message_id, text, keyboard)

def process_attendance(chat_id, message_id, user_id):
    """پردازش ثبت حضور"""
    success = record_attendance(user_id)
    today_count = get_today_attendance_count()
    
    if success:
        text = f"""
✅ حضور شما با موفقیت ثبت شد!

📅 امروز: {datetime.now().strftime('%Y/%m/%d')}
👥 تعداد حاضرین امروز: {today_count} نفر

📊 آمار شما:
• 📅 روزهای حضور این ماه: در حال محاسبه...
• ⏰ مجموع مطالعه: در حال محاسبه...
"""
    else:
        text = """
⚠️ شما امروز قبلاً حضور خود را ثبت کرده‌اید!

💡 می‌توانید فردا دوباره حضور خود را ثبت کنید.
"""
    
    keyboard = {
        "inline_keyboard": [
            [{"text": "📊 نمایش اعلام حضورها", "callback_data": "show_attendance"}],
            [{"text": "📈 آمار حضور من", "callback_data": "my_attendance_stats"}],
            [{"text": "🔄 بروزرسانی", "callback_data": "attendance"}],
            [{"text": "🏠 بازگشت به منو", "callback_data": "main_menu"}]
        ]
    }
    
    edit_telegram_message(chat_id, message_id, text, keyboard)

def send_study_plan_menu(chat_id, message_id):
    """ارسال منوی مطالعه"""
    text = """
📚 اهداف و برنامه‌ریزی و ثبت مطالعه

امکانات:
• 🎯 ثبت هدف مطالعه
• 📚 ثبت جلسات مطالعه
• ⏱️ زمان‌سنج مطالعه
• 📊 مدیریت اهداف
"""
    
    keyboard = {
        "inline_keyboard": [
            [{"text": "🎯 ثبت هدف جدید", "callback_data": "add_study_goal"}],
            [{"text": "📚 ثبت جلسه مطالعه", "callback_data": "add_study_session"}],
            [{"text": "📊 مدیریت اهداف", "callback_data": "manage_study_plans"}],
            [{"text": "🏠 بازگشت به منو", "callback_data": "main_menu"}]
        ]
    }
    
    edit_telegram_message(chat_id, message_id, text, keyboard)

def send_statistics_menu(chat_id, message_id):
    """ارسال منوی آمار"""
    text = """
📊 آمار و گزارش جامع

در این بخش می‌توانید:
• 📈 پیشرفت خود را مشاهده کنید
• 📆 آمار روزانه و هفتگی ببینید
• 🏆 با دیگران مقایسه کنید
• 📋 گزارش کامل دریافت کنید
"""
    
    keyboard = {
        "inline_keyboard": [
            [{"text": "📈 پیشرفت روزانه", "callback_data": "daily_progress"}],
            [{"text": "📆 پیشرفت هفتگی", "callback_data": "weekly_progress"}],
            [{"text": "🏆 مقایسه با برترین‌ها", "callback_data": "compare_top"}],
            [{"text": "🏠 بازگشت به منو", "callback_data": "main_menu"}]
        ]
    }
    
    edit_telegram_message(chat_id, message_id, text, keyboard)

def send_help_menu(chat_id, message_id):
    """ارسال منوی راهنما"""
    text = """
📚 راهنمای کامل ربات کنکور ۱۴۰۵

🎯 امکانات ربات:
• ⏳ شمارش معکوس کنکور
• 📅 تقویم و رویدادها
• 🔔 مدیریت یادآوری
• 📚 برنامه مطالعاتی
• ✅ ثبت حضور و مطالعه
• 📊 آمار و گزارش‌گیری

💡 برای شروع از منوی اصلی استفاده کنید.
"""
    
    keyboard = {
        "inline_keyboard": [
            [{"text": "🎯 شروع کار با ربات", "callback_data": "getting_started"}],
            [{"text": "❓ سوالات متداول", "callback_data": "faq"}],
            [{"text": "🏠 بازگشت به منو", "callback_data": "main_menu"}]
        ]
    }
    
    edit_telegram_message(chat_id, message_id, text, keyboard)

def send_admin_panel(chat_id, message_id, user_id):
    """ارسال پنل مدیریت"""
    if int(user_id) != int(ADMIN_ID):
        text = "❌ شما دسترسی به این بخش را ندارید."
        edit_telegram_message(chat_id, message_id, text, create_back_keyboard())
        return
    
    today_count = get_today_attendance_count()
    
    text = f"""
🔧 پنل مدیریت پیشرفته

📊 آمار سیستم:
• 👥 کاربران کل: در حال محاسبه...
• ✅ کاربران فعال: در حال محاسبه...
• 📅 حضور امروز: {today_count}
• 📩 پیام‌های pending: 0

💾 دیتابیس: فعال
"""
    
    keyboard = {
        "inline_keyboard": [
            [{"text": "📊 آمار کلی کاربران", "callback_data": "admin_stats"}],
            [{"text": "👥 مدیریت کاربران", "callback_data": "admin_manage_users"}],
            [{"text": "📢 ارسال پیام همگانی", "callback_data": "admin_broadcast"}],
            [{"text": "🏠 بازگشت به منو", "callback_data": "main_menu"}]
        ]
    }
    
    edit_telegram_message(chat_id, message_id, text, keyboard)

def send_unknown_message(chat_id):
    """ارسال پیام برای پیام‌های ناشناخته"""
    text = "🤔 متوجه پیام شما نشدم!\n\nلطفاً از منوی اصلی استفاده کنید یا دستور /start را وارد کنید."
    send_telegram_message(chat_id, text, create_back_keyboard())

# راه‌اندازی اولیه
if init_database():
    logger.info("✅ دیتابیس راه‌اندازی شد")
else:
    logger.error("❌ خطا در راه‌اندازی دیتابیس")

# برای اجرای مستقیم با Flask
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 شروع سرویس روی پورت {port}")
    app.run(host='0.0.0.0', port=port, debug=ENVIRONMENT == 'development')

# این برای Gunicorn لازمه
application = app
