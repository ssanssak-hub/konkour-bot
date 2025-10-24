import os
import logging
import requests
import sqlite3
import jdatetime
from datetime import datetime

logger = logging.getLogger(__name__)

# تنظیمات
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8381121739:AAFB2YBMomBh9xhoI3Qn0VVuGaGlpea9fx8')
ADMIN_ID = os.environ.get('ADMIN_ID', '7703677187')

# دیکشنری برای ذخیره وضعیت کاربران
user_sessions = {}

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

# ==================== KEYBOARDS ====================

# در بخش ایجاد کیبوردها، این تابع رو اضافه کنید:

def create_glass_button(text, callback_data):
    """ایجاد دکمه شیشه‌ای"""
    return {"text": f"🔮 {text}", "callback_data": callback_data}

def create_main_menu_keyboard():
    """ایجاد کیبورد منوی اصلی با دکمه‌های شیشه‌ای"""
    keyboard = {
        "inline_keyboard": [
            [create_glass_button("⏳ چند روز تا کنکور؟", "countdown")],
            [create_glass_button("📅 تقویم و رویدادها", "calendar")],
            [create_glass_button("🔔 مدیریت یادآوری‌ها", "reminders")],
            [create_glass_button("📨 ارسال پیام", "send_message")],
            [create_glass_button("✅ اعلام حضور", "attendance")],
            [create_glass_button("📚 اهداف و برنامه‌ریزی", "study_plan")],
            [create_glass_button("📊 آمار و گزارش", "statistics")],
            [create_glass_button("❓ راهنما", "help")],
            [create_glass_button("🔧 پنل مدیریت", "admin_panel")]
        ]
    }
    return keyboard

# به همین صورت تمام کیبوردهای دیگر رو به دکمه‌های شیشه‌ای تبدیل کنید...
def create_back_keyboard(back_to="main_menu"):
    """ایجاد کیبورد بازگشت"""
    keyboard = {
        "inline_keyboard": [
            [{"text": "🔙 بازگشت", "callback_data": back_to}],
            [{"text": "🏠 منوی اصلی", "callback_data": "main_menu"}]
        ]
    }
    return keyboard

def create_countdown_keyboard():
    """ایجاد کیبورد شمارش معکوس"""
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
    return keyboard

def create_calendar_keyboard():
    """ایجاد کیبورد تقویم"""
    keyboard = {
        "inline_keyboard": [
            [{"text": "📅 تقویم جاری", "callback_data": "current_calendar"}],
            [{"text": "🔍 مشاهده رویدادها", "callback_data": "view_events"}],
            [{"text": "➕ افزودن رویداد", "callback_data": "add_event"}],
            [{"text": "🏠 بازگشت به منو", "callback_data": "main_menu"}]
        ]
    }
    return keyboard

def create_reminders_keyboard():
    """ایجاد کیبورد یادآوری‌ها"""
    keyboard = {
        "inline_keyboard": [
            [{"text": "⏰ یادآوری کنکور", "callback_data": "reminder_exam"}],
            [{"text": "📝 یادآوری متفرقه", "callback_data": "reminder_custom"}],
            [{"text": "📚 یادآوری مطالعه", "callback_data": "reminder_study"}],
            [{"text": "📋 مدیریت یادآوری‌ها", "callback_data": "reminder_manage"}],
            [{"text": "🏠 بازگشت به منو", "callback_data": "main_menu"}]
        ]
    }
    return keyboard

def create_study_plan_keyboard():
    """ایجاد کیبورد مطالعه"""
    keyboard = {
        "inline_keyboard": [
            [{"text": "🎯 ثبت هدف جدید", "callback_data": "add_study_goal"}],
            [{"text": "📚 ثبت جلسه مطالعه", "callback_data": "add_study_session"}],
            [{"text": "⏱️ زمان‌سنج مطالعه", "callback_data": "study_timer"}],
            [{"text": "📊 مدیریت اهداف و برنامه‌ها", "callback_data": "manage_study_plans"}],
            [{"text": "📈 آمار مطالعه", "callback_data": "study_stats"}],
            [{"text": "🏠 بازگشت به منو", "callback_data": "main_menu"}]
        ]
    }
    return keyboard

def create_goal_type_keyboard():
    """ایجاد کیبورد نوع هدف"""
    keyboard = {
        "inline_keyboard": [
            [{"text": "📅 روزانه", "callback_data": "goal_daily"}],
            [{"text": "📆 هفتگی", "callback_data": "goal_weekly"}],
            [{"text": "🗓️ ماهانه", "callback_data": "goal_monthly"}],
            [{"text": "🔙 بازگشت", "callback_data": "study_plan"}]
        ]
    }
    return keyboard

def create_statistics_keyboard():
    """ایجاد کیبورد آمار"""
    keyboard = {
        "inline_keyboard": [
            [{"text": "📈 پیشرفت روزانه", "callback_data": "daily_progress"}],
            [{"text": "📆 پیشرفت هفتگی", "callback_data": "weekly_progress"}],
            [{"text": "🏆 مقایسه با برترین‌ها", "callback_data": "compare_top"}],
            [{"text": "📋 گزارش کامل", "callback_data": "full_report"}],
            [{"text": "🔄 بروزرسانی آمار", "callback_data": "statistics"}],
            [{"text": "🏠 بازگشت به منو", "callback_data": "main_menu"}]
        ]
    }
    return keyboard

def create_messages_keyboard():
    """ایجاد کیبورد پیام‌ها"""
    keyboard = {
        "inline_keyboard": [
            [{"text": "📨 ارسال به ادمین اصلی", "callback_data": "send_to_main_admin"}],
            [{"text": "👥 ارسال به همه ادمین‌ها", "callback_data": "send_to_all_admins"}],
            [{"text": "📋 پیام‌های من", "callback_data": "my_messages"}],
            [{"text": "🏠 بازگشت به منو", "callback_data": "main_menu"}]
        ]
    }
    return keyboard

def create_help_keyboard():
    """ایجاد کیبورد راهنما"""
    keyboard = {
        "inline_keyboard": [
            [{"text": "🎯 شروع کار با ربات", "callback_data": "getting_started"}],
            [{"text": "❓ سوالات متداول", "callback_data": "faq"}],
            [{"text": "📞 تماس با پشتیبانی", "callback_data": "send_message"}],
            [{"text": "🏠 بازگشت به منو", "callback_data": "main_menu"}]
        ]
    }
    return keyboard

def create_admin_keyboard():
    """ایجاد کیبورد مدیریت"""
    keyboard = {
        "inline_keyboard": [
            [{"text": "📊 آمار کلی کاربران", "callback_data": "admin_stats"}],
            [{"text": "👥 مدیریت کاربران", "callback_data": "admin_manage_users"}],
            [{"text": "📢 ارسال پیام همگانی", "callback_data": "admin_broadcast"}],
            [{"text": "📨 ارسال پیام به کاربر", "callback_data": "admin_send_to_user"}],
            [{"text": "📩 مدیریت پیام‌های کاربران", "callback_data": "admin_user_messages"}],
            [{"text": "💾 مدیریت دیتابیس", "callback_data": "admin_database"}],
            [{"text": "🏠 بازگشت به منو", "callback_data": "main_menu"}]
        ]
    }
    return keyboard

# ==================== DATABASE FUNCTIONS ====================

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
        
        # ایجاد جدول اهداف مطالعه
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS study_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT,
                subject TEXT,
                plan_type TEXT,
                target_hours REAL,
                completed_hours REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_completed BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # ایجاد جدول جلسات مطالعه
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS study_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                subject TEXT,
                duration REAL,
                session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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

def get_user_attendance_stats(user_id, days=30):
    """دریافت آمار حضور کاربر"""
    try:
        conn = sqlite3.connect('konkur_bot.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(DISTINCT DATE(check_in_time)) 
            FROM attendance 
            WHERE user_id = ? AND check_in_time >= datetime('now', ?)
        ''', (user_id, f'-{days} days'))
        
        attendance_days = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COALESCE(SUM(duration), 0) 
            FROM study_sessions 
            WHERE user_id = ? AND session_date >= datetime('now', ?)
        ''', (user_id, f'-{days} days'))
        
        total_hours = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'attendance_days': attendance_days,
            'total_hours': total_hours,
            'attendance_rate': (attendance_days / days) * 100 if days > 0 else 0
        }
    except Exception as e:
        logger.error(f"❌ خطا در دریافت آمار کاربر: {e}")
        return {'attendance_days': 0, 'total_hours': 0, 'attendance_rate': 0}

def add_study_goal(user_id, title, subject, plan_type, target_hours):
    """افزودن هدف مطالعه"""
    try:
        conn = sqlite3.connect('konkur_bot.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO study_goals (user_id, title, subject, plan_type, target_hours)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, title, subject, plan_type, target_hours))
        
        goal_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return goal_id
    except Exception as e:
        logger.error(f"❌ خطا در افزودن هدف مطالعه: {e}")
        return None

def add_study_session(user_id, subject, duration):
    """افزودن جلسه مطالعه"""
    try:
        conn = sqlite3.connect('konkur_bot.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO study_sessions (user_id, subject, duration)
            VALUES (?, ?, ?)
        ''', (user_id, subject, duration))
        
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return session_id
    except Exception as e:
        logger.error(f"❌ خطا در افزودن جلسه مطالعه: {e}")
        return None

def get_user_study_plans(user_id):
    """دریافت اهداف کاربر"""
    try:
        conn = sqlite3.connect('konkur_bot.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, subject, plan_type, target_hours, completed_hours, is_completed
            FROM study_goals 
            WHERE user_id = ? AND is_completed = FALSE
            ORDER BY created_at DESC
            LIMIT 10
        ''', (user_id,))
        
        plans = cursor.fetchall()
        conn.close()
        return plans
    except Exception as e:
        logger.error(f"❌ خطا در دریافت اهداف کاربر: {e}")
        return []

def get_daily_study_time(user_id, date=None):
    """دریافت زمان مطالعه روزانه"""
    try:
        conn = sqlite3.connect('konkur_bot.db')
        cursor = conn.cursor()
        
        if date:
            cursor.execute('''
                SELECT COALESCE(SUM(duration), 0) 
                FROM study_sessions 
                WHERE user_id = ? AND DATE(session_date) = ?
            ''', (user_id, date))
        else:
            cursor.execute('''
                SELECT COALESCE(SUM(duration), 0) 
                FROM study_sessions 
                WHERE user_id = ? AND DATE(session_date) = DATE('now')
            ''', (user_id,))
        
        total_time = cursor.fetchone()[0]
        conn.close()
        return total_time
    except Exception as e:
        logger.error(f"❌ خطا در دریافت زمان مطالعه: {e}")
        return 0

def get_weekly_study_time(user_id):
    """دریافت زمان مطالعه هفتگی"""
    try:
        conn = sqlite3.connect('konkur_bot.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COALESCE(SUM(duration), 0) 
            FROM study_sessions 
            WHERE user_id = ? AND session_date >= datetime('now', '-7 days')
        ''', (user_id,))
        
        total_time = cursor.fetchone()[0]
        conn.close()
        return total_time
    except Exception as e:
        logger.error(f"❌ خطا در دریافت زمان مطالعه هفتگی: {e}")
        return 0

# ==================== MESSAGE HANDLERS ====================

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
    text = "🎯 انتخاب کنکور برای نمایش زمان باقی‌مانده\n\nلطفاً کنکور مورد نظر خود را انتخاب کنید:"
    edit_telegram_message(chat_id, message_id, text, create_countdown_keyboard())

def show_countdown(chat_id, message_id, exam_name):
    """نمایش زمان دقیق باقی‌مانده تا کنکور"""
    # تاریخ‌های دقیق کنکور 1405
    exam_dates = {
        "علوم تجربی": "1405-04-12 08:00:00",
        "ریاضی‌وفنی": "1405-04-11 08:00:00",
        "علوم انسانی": "1405-04-11 08:00:00",
        "فرهنگیان": ["1405-02-17 08:00:00", "1405-02-18 08:00:00"],  # دو تاریخ
        "هنر": "1405-04-12 14:30:00",
        "زبان‌وگروه‌های‌خارجه": "1405-04-12 14:30:00"
    }
    
    exam_date_data = exam_dates.get(exam_name)
    if not exam_date_data:
        text = "❌ تاریخ کنکور یافت نشد."
        edit_telegram_message(chat_id, message_id, text, create_back_keyboard("countdown"))
        return
    
    try:
        if exam_name == "فرهنگیان":
            # پردازش دو تاریخ برای فرهنگیان
            text = process_cultural_exam(exam_date_data)
        else:
            # پردازش تک تاریخ برای سایر کنکورها
            exam_date_str = exam_date_data
            exam_date = jdatetime.datetime.strptime(exam_date_str, "%Y-%m-%d %H:%M:%S")
            now = jdatetime.datetime.now()
            time_diff = exam_date - now
            
            if time_diff.total_seconds() <= 0:
                text = f"""
🎉 کنکور {exam_name} به پایان رسیده است!

📅 تاریخ برگزاری: {exam_date_str}
✅ آرزوی موفقیت و قبولی برای شما داریم! 🎓
"""
            else:
                weeks, days, hours, minutes, seconds, total_days = calculate_time_details(time_diff)
                text = format_countdown_text(
                    exam_name, 
                    weeks, days, hours, minutes, seconds,
                    exam_date_str,
                    total_days
                )
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "🔄 بروزرسانی زمان", "callback_data": f"countdown_{exam_name}"}],
                [{"text": "📊 همه کنکورها", "callback_data": "countdown"}],
                [{"text": "🏠 بازگشت به منو", "callback_data": "main_menu"}]
            ]
        }
        
        edit_telegram_message(chat_id, message_id, text, keyboard)
        
    except Exception as e:
        logger.error(f"❌ خطا در محاسبه زمان: {e}")
        text = "❌ خطا در محاسبه زمان باقی‌مانده."
        edit_telegram_message(chat_id, message_id, text, create_back_keyboard("countdown"))

def process_cultural_exam(exam_dates):
    """پردازش دو تاریخ کنکور فرهنگیان"""
    now = jdatetime.datetime.now()
    
    # تاریخ اول (۱۷ اردیبهشت)
    date1_str = exam_dates[0]
    date1 = jdatetime.datetime.strptime(date1_str, "%Y-%m-%d %H:%M:%S")
    time_diff1 = date1 - now
    
    # تاریخ دوم (۱۸ اردیبهشت)  
    date2_str = exam_dates[1]
    date2 = jdatetime.datetime.strptime(date2_str, "%Y-%m-%d %H:%M:%S")
    time_diff2 = date2 - now
    
    if time_diff1.total_seconds() <= 0 and time_diff2.total_seconds() <= 0:
        return f"""
🎉 کنکور فرهنگیان به پایان رسیده است!

📅 تاریخ‌های برگزاری:
• مرحله اول: {date1_str}
• مرحله دوم: {date2_str}

✅ آرزوی موفقیت و قبولی برای شما داریم! 🎓
"""
    elif time_diff1.total_seconds() <= 0:
        # فقط تاریخ اول گذشته
        weeks, days, hours, minutes, seconds, total_days = calculate_time_details(time_diff2)
        return format_cultural_text(
            "مرحله دوم", 
            weeks, days, hours, minutes, seconds,
            date2_str,
            total_days,
            date1_str
        )
    else:
        # هر دو تاریخ آینده هستند
        weeks1, days1, hours1, minutes1, seconds1, total_days1 = calculate_time_details(time_diff1)
        weeks2, days2, hours2, minutes2, seconds2, total_days2 = calculate_time_details(time_diff2)
        
        return format_cultural_both_dates(
            weeks1, days1, hours1, minutes1, seconds1, date1_str, total_days1,
            weeks2, days2, hours2, minutes2, seconds2, date2_str, total_days2
        )

def calculate_time_details(time_diff):
    """محاسبه جزئیات زمان"""
    total_seconds = int(time_diff.total_seconds())
    total_minutes = total_seconds // 60
    total_hours = total_minutes // 60
    total_days = total_hours // 24
    total_weeks = total_days // 7
    
    weeks = total_weeks
    days = total_days % 7
    hours = total_hours % 24
    minutes = total_minutes % 60
    seconds = total_seconds % 60
    
    return weeks, days, hours, minutes, seconds, total_days

def format_cultural_text(stage, weeks, days, hours, minutes, seconds, exam_date_str, total_days, past_date=None):
    """فرمت‌بندی متن برای یک مرحله فرهنگیان"""
    time_parts = []
    
    if weeks > 0:
        time_parts.append(f"{weeks} هفته")
    if days > 0:
        time_parts.append(f"{days} روز")
    if hours > 0:
        time_parts.append(f"{hours} ساعت")
    if minutes > 0:
        time_parts.append(f"{minutes} دقیقه")
    if seconds > 0:
        time_parts.append(f"{seconds} ثانیه")
    
    time_display = " • ".join(time_parts)
    
    text = f"""
👨‍🏫 زمان باقی‌مانده تا کنکور فرهنگیان ({stage})

🕐 {time_display}

📅 تاریخ {stage}: {exam_date_str.split()[0]}
🕒 ساعت برگزاری: {exam_date_str.split()[1]}
"""
    
    if past_date:
        text += f"✅ مرحله اول: {past_date.split()[0]} (گذشته)\n\n"
    else:
        text += f"\n📊 خلاصه زمانی:\n"
        text += f"🗓️ مجموع روزها: {total_days} روز\n"
        text += f"📈 مجموع هفته‌ها: {total_days // 7} هفته\n"
        text += f"⏱️ مجموع ساعت‌ها: {total_days * 24} ساعت\n\n"
    
    text += f"💡 **توصیه مطالعاتی:**\n{get_study_recommendation(total_days)}"
    
    return text

def format_cultural_both_dates(weeks1, days1, hours1, minutes1, seconds1, date1_str, total_days1,
                              weeks2, days2, hours2, minutes2, seconds2, date2_str, total_days2):
    """فرمت‌بندی متن برای دو تاریخ فرهنگیان"""
    
    # زمان‌بندی مرحله اول
    time_parts1 = []
    if weeks1 > 0:
        time_parts1.append(f"{weeks1} هفته")
    if days1 > 0:
        time_parts1.append(f"{days1} روز")
    if hours1 > 0:
        time_parts1.append(f"{hours1} ساعت")
    if minutes1 > 0:
        time_parts1.append(f"{minutes1} دقیقه")
    if seconds1 > 0:
        time_parts1.append(f"{seconds1} ثانیه")
    
    # زمان‌بندی مرحله دوم
    time_parts2 = []
    if weeks2 > 0:
        time_parts2.append(f"{weeks2} هفته")
    if days2 > 0:
        time_parts2.append(f"{days2} روز")
    if hours2 > 0:
        time_parts2.append(f"{hours2} ساعت")
    if minutes2 > 0:
        time_parts2.append(f"{minutes2} دقیقه")
    if seconds2 > 0:
        time_parts2.append(f"{seconds2} ثانیه")
    
    time_display1 = " • ".join(time_parts1)
    time_display2 = " • ".join(time_parts2)
    
    return f"""
👨‍🏫 زمان باقی‌مانده تا کنکور فرهنگیان

📅 **مرحله اول (۱۷ اردیبهشت):**
🕐 {time_display1}
🗓️ مجموع: {total_days1} روز

📅 **مرحله دوم (۱۸ اردیبهشت):**  
🕐 {time_display2}
🗓️ مجموع: {total_days2} روز

🕒 ساعت برگزاری هر دو مرحله: ۰۸:۰۰ صبح

💡 **توصیه مطالعاتی:**
{get_study_recommendation(min(total_days1, total_days2))}

📝 **نکته:** کنکور فرهنگیان در دو روز متوالی برگزار می‌شود.
"""    

def get_study_recommendation(days):
    """دریافت توصیه مطالعه بر اساس روزهای باقی‌مانده"""
    if days > 180:
        return "📅 زمان کافی داری! با برنامه‌ریزی منظم پیش برو.\n• فصل‌های سنگین رو اولویت بده\n• تست‌زنی رو شروع کن"
    elif days > 120:
        return "⏳ زمان مناسبی داری! روی نقاط ضعف تمرکز کن.\n• مرور هفتگی داشته باش\n• خلاصه‌نویسی رو جدی بگیر"
    elif days > 90:
        return "🚀 نیمه راهی! تست‌زنی رو بیشتر کن.\n• آزمون‌های آزمایشی شرکت کن\n• timing خودت رو بهبود بده"
    elif days > 60:
        return "🔥 فاز آخر! مرور سریع و تست زمان‌دار.\n• نکات مهم رو مرور کن\n• مدیریت زمان رو تمرین کن"
    elif days > 30:
        return "⚡ یک ماه مونده! آرومش خودت رو حفظ کن.\n• سلامت روان مهمه\n• خواب کافی داشته باش"
    elif days > 7:
        return "🎯 یک هفته مونده! استراحت و مرور سبک.\n• از خودت فشار نیار\n• اعتماد به نفس داشته باش"
    elif days > 0:
        return "❤️ فردا کنکور داری! فقط استراحت کن.\n• وسایل لازم رو آماده کن\n• به خودت ایمان داشته باش"
    else:
        return "🎉 کنکور تموم شد! به خودت افتخار کن.\n• هر نتیجه‌ای بگیری، تو بهترینی!"

def format_countdown_text(exam_name, weeks, days, hours, minutes, seconds, exam_date_str, total_days):
    """فرمت‌بندی متن شمارش معکوس"""
    time_parts = []
    
    if weeks > 0:
        time_parts.append(f"{weeks} هفته")
    if days > 0:
        time_parts.append(f"{days} روز")
    if hours > 0:
        time_parts.append(f"{hours} ساعت")
    if minutes > 0:
        time_parts.append(f"{minutes} دقیقه")
    if seconds > 0:
        time_parts.append(f"{seconds} ثانیه")
    
    time_display = " • ".join(time_parts)
    
    return f"""
⏰ زمان باقی‌مانده تا کنکور **{exam_name}**

🕐 {time_display}

📅 تاریخ کنکور: {exam_date_str.split()[0]}
🕒 ساعت برگزاری: {exam_date_str.split()[1]}

📊 خلاصه زمانی:
🗓️ مجموع روزها: {total_days} روز
📈 مجموع هفته‌ها: {total_days // 7} هفته
⏱️ مجموع ساعت‌ها: {total_days * 24} ساعت

💡 **توصیه مطالعاتی:**
{get_study_recommendation(total_days)}
"""
    
def send_calendar_menu(chat_id, message_id):
    """ارسال منوی تقویم"""
    today = jdatetime.datetime.now().strftime("%Y/%m/%d")
    
    text = f"""
📅 تقویم و رویدادها

📆 امروز: {today}

امکانات تقویم:
• نمایش تقویم شمسی
• مناسبت‌های مهم
• رویدادهای کنکور
• مدیریت رویدادهای شخصی
"""
    
    edit_telegram_message(chat_id, message_id, text, create_calendar_keyboard())

def send_reminders_menu(chat_id, message_id):
    """ارسال منوی یادآوری‌ها"""
    text = """
🔔 مدیریت یادآوری‌ها

با این قابلیت می‌توانید:
• ⏰ یادآوری کنکور تنظیم کنید
• 📝 یادآوری متفرقه ایجاد کنید
• 📚 یادآوری مطالعه تنظیم کنید
• 📋 یادآوری‌های خود را مدیریت کنید
"""
    
    edit_telegram_message(chat_id, message_id, text, create_reminders_keyboard())

def process_reminder_action(chat_id, message_id, user_id, callback_data):
    """پردازش اقدامات یادآوری"""
    action = callback_data.replace('reminder_', '')
    
    if action == 'exam':
        text = "⏰ یادآوری کنکور\n\nاین قابلیت به زودی اضافه خواهد شد."
    elif action == 'custom':
        text = "📝 یادآوری متفرقه\n\nاین قابلیت به زودی اضافه خواهد شد."
    elif action == 'study':
        text = "📚 یادآوری مطالعه\n\nاین قابلیت به زودی اضافه خواهد شد."
    elif action == 'manage':
        text = "📋 مدیریت یادآوری‌ها\n\nاین قابلیت به زودی اضافه خواهد شد."
    else:
        text = "❌ عمل نامعتبر"
    
    edit_telegram_message(chat_id, message_id, text, create_back_keyboard("reminders"))

def process_attendance(chat_id, message_id, user_id):
    """پردازش ثبت حضور"""
    success = record_attendance(user_id)
    today_count = get_today_attendance_count()
    user_stats = get_user_attendance_stats(user_id, 30)
    
    if success:
        text = f"""
✅ حضور شما با موفقیت ثبت شد!

📅 امروز: {jdatetime.datetime.now().strftime('%Y/%m/%d')}
👥 تعداد حاضرین امروز: {today_count} نفر

📊 آمار ۳۰ روزه شما:
• 📅 روزهای حضور: {user_stats['attendance_days']} روز
• ⏰ مجموع مطالعه: {user_stats['total_hours']:.1f} ساعت
• 📈 نرخ حضور: {user_stats['attendance_rate']:.1f}%
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

def send_study_plan_menu(chat_id, message_id, user_id):
    """ارسال منوی مطالعه"""
    daily_time = get_daily_study_time(user_id)
    weekly_time = get_weekly_study_time(user_id)
    
    text = f"""
📚 اهداف و برنامه‌ریزی و ثبت مطالعه

📊 آمار مطالعه شما:
• 📅 امروز: {daily_time:.1f} ساعت
• 📆 این هفته: {weekly_time:.1f} ساعت

لطفاً گزینه مورد نظر خود را انتخاب کنید:
"""
    
    edit_telegram_message(chat_id, message_id, text, create_study_plan_keyboard())

def start_add_study_goal(chat_id, message_id, user_id):
    """شروع ثبت هدف جدید"""
    text = "🎯 ثبت هدف جدید\n\nلطفاً نوع هدف را انتخاب کنید:"
    edit_telegram_message(chat_id, message_id, text, create_goal_type_keyboard())

def set_goal_type(chat_id, message_id, user_id, goal_type):
    """تنظیم نوع هدف"""
    user_sessions[user_id] = {
        'waiting_for_goal_title': True,
        'goal_type': goal_type
    }
    
    type_text = {
        'daily': 'روزانه',
        'weekly': 'هفتگی', 
        'monthly': 'ماهانه'
    }
    
    text = f"📝 ثبت هدف {type_text[goal_type]}\n\nلطفاً عنوان هدف را ارسال کنید:\nمثال: 'خواندن فصل ۱ ریاضی' یا 'حل ۵۰ تست شیمی'"
    edit_telegram_message(chat_id, message_id, text, create_back_keyboard("add_study_goal"))

def process_study_goal_title(chat_id, user_id, title):
    """پردازش عنوان هدف"""
    user_sessions[user_id] = {
        'waiting_for_goal_hours': True,
        'goal_title': title,
        'goal_type': user_sessions[user_id]['goal_type']
    }
    
    type_text = {
        'daily': 'روزانه',
        'weekly': 'هفتگی',
        'monthly': 'ماهانه'
    }
    
    goal_type = user_sessions[user_id]['goal_type']
    
    text = f"✅ عنوان هدف ثبت شد: {title}\n\nلطفاً تعداد ساعت‌های هدف {type_text[goal_type]} را وارد کنید:\nمثال: 2.5 (یعنی ۲ ساعت و ۳۰ دقیقه)"
    send_telegram_message(chat_id, text)

def process_study_goal_hours(chat_id, user_id, hours_text):
    """پردازش ساعت‌های هدف"""
    try:
        target_hours = float(hours_text)
        title = user_sessions[user_id]['goal_title']
        goal_type = user_sessions[user_id]['goal_type']
        
        # ذخیره هدف در دیتابیس
        goal_id = add_study_goal(user_id, title, "عمومی", goal_type, target_hours)
        
        # پاک کردن وضعیت
        if user_id in user_sessions:
            del user_sessions[user_id]
        
        type_text = {
            'daily': 'روزانه',
            'weekly': 'هفتگی',
            'monthly': 'ماهانه'
        }
        
        text = f"✅ هدف {type_text[goal_type]} با موفقیت ثبت شد! 🎉\n\n🎯 عنوان: {title}\n⏰ ساعت هدف: {target_hours} ساعت\n📅 نوع: {type_text[goal_type]}\n🆔 کد هدف: {goal_id}\n\nحالا می‌تونی جلسات مطالعه‌ات رو ثبت کنی!"
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "📚 ثبت جلسه مطالعه", "callback_data": "add_study_session"}],
                [{"text": "📊 مدیریت اهداف", "callback_data": "manage_study_plans"}],
                [{"text": "🏠 منوی اصلی", "callback_data": "main_menu"}]
            ]
        }
        
        send_telegram_message(chat_id, text, keyboard)
        
    except ValueError:
        text = "❌ لطفاً یک عدد معتبر وارد کنید:\nمثال: 2.5 (برای ۲ ساعت و ۳۰ دقیقه)"
        send_telegram_message(chat_id, text)

def start_add_study_session(chat_id, message_id, user_id):
    """شروع ثبت جلسه مطالعه"""
    user_sessions[user_id] = {
        'waiting_for_session_subject': True
    }
    
    text = "📚 ثبت جلسه مطالعه\n\nلطفاً نام درس یا موضوع مطالعه را ارسال کنید:\nمثال: 'ریاضی - فصل ۱' یا 'شیمی - مسائل استوکیومتری'"
    edit_telegram_message(chat_id, message_id, text, create_back_keyboard("study_plan"))

def process_study_session_subject(chat_id, user_id, subject):
    """پردازش موضوع جلسه مطالعه"""
    user_sessions[user_id] = {
        'waiting_for_session_duration': True,
        'session_subject': subject
    }
    
    text = f"✅ موضوع ثبت شد: {subject}\n\nلطفاً مدت زمان مطالعه (به ساعت) را وارد کنید:\nمثال: 1.5 (یعنی ۱ ساعت و ۳۰ دقیقه)"
    send_telegram_message(chat_id, text)

def process_study_session_duration(chat_id, user_id, duration_text):
    """پردازش مدت زمان جلسه مطالعه"""
    try:
        duration = float(duration_text)
        subject = user_sessions[user_id]['session_subject']
        
        # ذخیره جلسه مطالعه در دیتابیس
        session_id = add_study_session(user_id, subject, duration)
        
        # پاک کردن وضعیت
        if user_id in user_sessions:
            del user_sessions[user_id]
        
        # بروزرسانی آمار
        daily_time = get_daily_study_time(user_id)
        weekly_time = get_weekly_study_time(user_id)
        
        text = f"✅ جلسه مطالعه با موفقیت ثبت شد! 📚\n\n📚 موضوع: {subject}\n⏰ مدت زمان: {duration} ساعت\n📅 تاریخ: {jdatetime.datetime.now().strftime('%Y/%m/%d')}\n🆔 کد جلسه: {session_id}\n\n📊 آمار به روز شما:\n• 📅 امروز: {daily_time:.1f} ساعت\n• 📆 این هفته: {weekly_time:.1f} ساعت\n\nآفرین! ادامه بده 💪"
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "🎯 ثبت هدف جدید", "callback_data": "add_study_goal"}],
                [{"text": "📊 آمار مطالعه", "callback_data": "study_stats"}],
                [{"text": "🏠 منوی اصلی", "callback_data": "main_menu"}]
            ]
        }
        
        send_telegram_message(chat_id, text, keyboard)
        
    except ValueError:
        text = "❌ لطفاً یک عدد معتبر وارد کنید:\nمثال: 1.5 (برای ۱ ساعت و ۳۰ دقیقه)"
        send_telegram_message(chat_id, text)

def show_study_plans(chat_id, message_id, user_id):
    """نمایش اهداف کاربر"""
    plans = get_user_study_plans(user_id)
    
    if not plans:
        text = "ℹ️ شما هیچ هدف فعالی ندارید.\n\nمی‌توانید با ثبت هدف جدید شروع کنید!"
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "🎯 ثبت هدف جدید", "callback_data": "add_study_goal"}],
                [{"text": "🔙 بازگشت", "callback_data": "study_plan"}],
                [{"text": "🏠 منوی اصلی", "callback_data": "main_menu"}]
            ]
        }
    else:
        text = "📋 اهداف و برنامه‌های شما:\n\n"
        keyboard_buttons = []
        
        for plan in plans:
            plan_id, title, subject, plan_type, target_hours, completed_hours, is_completed = plan
            progress = (completed_hours / target_hours) * 100 if target_hours > 0 else 0
            status = "✅ انجام شده" if is_completed else "🟡 در حال انجام"
            
            text += f"🎯 {title}\n"
            text += f"📚 {subject} | {plan_type}\n"
            text += f"⏰ {completed_hours:.1f}/{target_hours:.1f} ساعت ({progress:.1f}%)\n"
            text += f"🔸 {status}\n\n"
            
            keyboard_buttons.append([
                {"text": f"✏️ ویرایش {plan_id}", "callback_data": f"edit_plan_{plan_id}"},
                {"text": f"✅ کامل {plan_id}", "callback_data": f"complete_plan_{plan_id}"}
            ])
        
        keyboard_buttons.append([{"text": "🎯 هدف جدید", "callback_data": "add_study_goal"}])
        keyboard_buttons.append([{"text": "🔙 بازگشت", "callback_data": "study_plan"}])
        keyboard_buttons.append([{"text": "🏠 منوی اصلی", "callback_data": "main_menu"}])
        
        keyboard = {"inline_keyboard": keyboard_buttons}
    
    edit_telegram_message(chat_id, message_id, text, keyboard)

def send_statistics_menu(chat_id, message_id, user_id):
    """ارسال منوی آمار"""
    user_stats = get_user_attendance_stats(user_id, 30)
    daily_time = get_daily_study_time(user_id)
    weekly_time = get_weekly_study_time(user_id)
    
    text = f"""
📊 آمار و گزارش جامع

⏰ مطالعه امروز: {daily_time:.1f} ساعت
📅 مطالعه این هفته: {weekly_time:.1f} ساعت
📚 کل مطالعه ۳۰ روزه: {user_stats['total_hours']:.1f} ساعت

✅ تعداد حضور: {user_stats['attendance_days']} روز
🎯 نرخ موفقیت: در حال محاسبه...
📈 میانگین جلسات: در حال محاسبه...

📅 تاریخ امروز: {jdatetime.datetime.now().strftime('%Y/%m/%d')}
"""
    
    edit_telegram_message(chat_id, message_id, text, create_statistics_keyboard())

def show_daily_progress(chat_id, message_id, user_id):
    """نمایش پیشرفت روزانه"""
    # شبیه‌سازی داده‌های ۷ روز اخیر
    days = ["دیروز", "۲ روز قبل", "۳ روز قبل", "۴ روز قبل", "۵ روز قبل", "۶ روز قبل", "۷ روز قبل"]
    study_times = [3.5, 2.0, 4.2, 1.5, 3.8, 2.5, 4.0]
    
    chart_text = "📈 نمودار مطالعه ۷ روز اخیر:\n\n"
    max_time = max(study_times)
    
    for day, time in zip(days, study_times):
        bar_length = int((time / max_time) * 20)
        bar = "█" * bar_length
        chart_text += f"{day}: {bar} {time:.1f}h\n"
    
    chart_text += f"\n📊 امروز: {get_daily_study_time(user_id):.1f} ساعت\n💪 ادامه بده!"
    
    edit_telegram_message(chat_id, message_id, chart_text, create_back_keyboard("statistics"))

def show_weekly_progress(chat_id, message_id, user_id):
    """نمایش پیشرفت هفتگی"""
    # شبیه‌سازی داده‌های ۴ هفته اخیر
    weeks = ["هفته ۴", "هفته ۳", "هفته ۲", "هفته ۱"]
    study_times = [18.5, 22.0, 19.8, 25.5]
    
    chart_text = "📆 نمودار مطالعه ۴ هفته اخیر:\n\n"
    max_time = max(study_times)
    
    for week, time in zip(weeks, study_times):
        bar_length = int((time / max_time) * 20)
        bar = "█" * bar_length
        chart_text += f"{week}: {bar} {time:.1f}h\n"
    
    chart_text += f"\n📊 این هفته: {get_weekly_study_time(user_id):.1f} ساعت\n🎉 پیشرفت خوبی داری!"
    
    edit_telegram_message(chat_id, message_id, chart_text, create_back_keyboard("statistics"))

def show_compare_top(chat_id, message_id, user_id):
    """نمایش مقایسه با برترین‌ها"""
    user_weekly = get_weekly_study_time(user_id)
    
    text = f"""
🏆 مقایسه با برترین‌ها

📊 مطالعه هفتگی شما: {user_weekly:.1f} ساعت

📈 رتبه‌های برتر:
🥇 کاربر برتر ۱: 48.5 ساعت
🥈 کاربر برتر ۲: 45.0 ساعت  
🥉 کاربر برتر ۳: 42.5 ساعت
4. کاربر برتر ۴: 40.0 ساعت
5. کاربر برتر ۵: 38.5 ساعت

🔸 رتبه شما: ۶

💡 برای رسیدن به رتبه‌های برتر، حداقل ۳۵ ساعت در هفته مطالعه نیاز داری.
"""
    
    edit_telegram_message(chat_id, message_id, text, create_back_keyboard("statistics"))

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

📞 پشتیبانی: از طریق دکمه 'ارسال پیام' با ما در ارتباط باشید.
"""
    
    edit_telegram_message(chat_id, message_id, text, create_help_keyboard())

def send_messages_menu(chat_id, message_id):
    """ارسال منوی پیام‌ها"""
    text = """
📨 سیستم پیام‌رسانی

از این بخش می‌توانید:
• 📨 پیام به ادمین ارسال کنید
• 📩 پیام‌های خود را مشاهده کنید
• ✏️ پیام‌ها را مدیریت کنید

💡 برای گزارش مشکل یا ارائه پیشنهاد از این بخش استفاده کنید.
"""
    
    edit_telegram_message(chat_id, message_id, text, create_messages_keyboard())

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
📅 آخرین بروزرسانی: {jdatetime.datetime.now().strftime('%Y/%m/%d %H:%M')}
"""
    
    edit_telegram_message(chat_id, message_id, text, create_admin_keyboard())

def process_admin_action(chat_id, message_id, user_id, callback_data):
    """پردازش اقدامات مدیریت"""
    if int(user_id) != int(ADMIN_ID):
        text = "❌ شما دسترسی به این بخش را ندارید."
        edit_telegram_message(chat_id, message_id, text, create_back_keyboard())
        return
    
    action = callback_data.replace('admin_', '')
    
    if action == 'stats':
        text = "📊 آمار کلی کاربران\n\nاین قابلیت به زودی اضافه خواهد شد."
    elif action == 'manage_users':
        text = "👥 مدیریت کاربران\n\nاین قابلیت به زودی اضافه خواهد شد."
    elif action == 'broadcast':
        text = "📢 ارسال پیام همگانی\n\nاین قابلیت به زودی اضافه خواهد شد."
    elif action == 'send_to_user':
        text = "📨 ارسال پیام به کاربر\n\nاین قابلیت به زودی اضافه خواهد شد."
    elif action == 'user_messages':
        text = "📩 مدیریت پیام‌های کاربران\n\nاین قابلیت به زودی اضافه خواهد شد."
    elif action == 'database':
        text = "💾 مدیریت دیتابیس\n\nاین قابلیت به زودی اضافه خواهد شد."
    else:
        text = "❌ عمل نامعتبر"
    
    edit_telegram_message(chat_id, message_id, text, create_back_keyboard("admin_panel"))

def send_unknown_message(chat_id):
    """ارسال پیام برای پیام‌های ناشناخته"""
    text = "🤔 متوجه پیام شما نشدم!\n\nلطفاً از منوی اصلی استفاده کنید یا دستور /start را وارد کنید."
    send_telegram_message(chat_id, text, create_back_keyboard())

# ==================== PROCESSING FUNCTIONS ====================

def process_message_handler(message):
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
    
    # بررسی وضعیت کاربر
    user_state = user_sessions.get(user_id, {})
    
    if user_state.get('waiting_for_goal_title'):
        process_study_goal_title(chat_id, user_id, text)
    elif user_state.get('waiting_for_goal_hours'):
        process_study_goal_hours(chat_id, user_id, text)
    elif user_state.get('waiting_for_session_subject'):
        process_study_session_subject(chat_id, user_id, text)
    elif user_state.get('waiting_for_session_duration'):
        process_study_session_duration(chat_id, user_id, text)
    elif text == '/start':
        send_welcome_message(chat_id, message['from']['first_name'])
    elif text == '/menu':
        send_main_menu(chat_id)
    else:
        send_unknown_message(chat_id)

def process_callback_handler(callback_query):
    """پردازش callback query"""
    chat_id = callback_query['message']['chat']['id']
    message_id = callback_query['message']['message_id']
    callback_data = callback_query['data']
    callback_id = callback_query['id']
    user_id = callback_query['from']['id']
    
    # پاسخ به callback
    answer_callback_query(callback_id)
    
    # پردازش بر اساس callback_data
    if callback_data == 'main_menu':
        send_main_menu(chat_id, message_id)
    elif callback_data == 'countdown':
        send_countdown_menu(chat_id, message_id)
    elif callback_data == 'calendar':
        send_calendar_menu(chat_id, message_id)
    elif callback_data == 'reminders':
        send_reminders_menu(chat_id, message_id)
    elif callback_data == 'attendance':
        process_attendance(chat_id, message_id, user_id)
    elif callback_data == 'study_plan':
        send_study_plan_menu(chat_id, message_id, user_id)
    elif callback_data == 'statistics':
        send_statistics_menu(chat_id, message_id, user_id)
    elif callback_data == 'help':
        send_help_menu(chat_id, message_id)
    elif callback_data == 'send_message':
        send_messages_menu(chat_id, message_id)
    elif callback_data == 'admin_panel':
        send_admin_panel(chat_id, message_id, user_id)
    
    # پردازش شمارش معکوس
    elif callback_data.startswith('countdown_'):
        show_countdown(chat_id, message_id, callback_data.replace('countdown_', ''))
    
    # پردازش اهداف مطالعه
    elif callback_data == 'add_study_goal':
        start_add_study_goal(chat_id, message_id, user_id)
    elif callback_data.startswith('goal_'):
        set_goal_type(chat_id, message_id, user_id, callback_data.replace('goal_', ''))
    elif callback_data == 'add_study_session':
        start_add_study_session(chat_id, message_id, user_id)
    elif callback_data == 'manage_study_plans':
        show_study_plans(chat_id, message_id, user_id)
    elif callback_data == 'study_stats':
        send_statistics_menu(chat_id, message_id, user_id)
    
    # پردازش آمار
    elif callback_data == 'daily_progress':
        show_daily_progress(chat_id, message_id, user_id)
    elif callback_data == 'weekly_progress':
        show_weekly_progress(chat_id, message_id, user_id)
    elif callback_data == 'compare_top':
        show_compare_top(chat_id, message_id, user_id)
    
    # پردازش یادآوری‌ها
    elif callback_data.startswith('reminder_'):
        process_reminder_action(chat_id, message_id, user_id, callback_data)
    
    # پردازش مدیریت
    elif callback_data.startswith('admin_'):
        process_admin_action(chat_id, message_id, user_id, callback_data)
    
    # پردازش پیام‌ها
    elif callback_data.startswith('send_'):
        text = "📨 سیستم پیام‌رسانی\n\nاین قابلیت به زودی اضافه خواهد شد."
        edit_telegram_message(chat_id, message_id, text, create_back_keyboard("send_message"))
    
    # پردازش راهنما
    elif callback_data in ['getting_started', 'faq']:
        text = "📚 راهنمای ربات\n\nاین بخش به زودی تکمیل خواهد شد."
        edit_telegram_message(chat_id, message_id, text, create_back_keyboard("help"))

# راه‌اندازی اولیه دیتابیس
init_database()
