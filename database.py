"""
دیتابیس SQLite برای ربات کنکور - نسخه بهینه شده برای Render
"""
import os
import sqlite3
import logging
from datetime import datetime, date
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path=None):
        """مقداردهی دیتابیس با پشتیبانی از Environment Variables"""
        # استفاده از DATABASE_URL از environment یا مسیر پیش‌فرض
        if db_path is None:
            db_path = os.environ.get("DATABASE_URL", "konkour_bot.db")
        
        # تبدیل فرمت sqlite:/// به مسیر معمولی
        if db_path.startswith('sqlite:///'):
            db_path = db_path.replace('sqlite:///', '')
        
        self.db_path = db_path
        logger.info(f"📁 دیتابیس در مسیر: {self.db_path}")
        self.init_db()
    
    def get_connection(self):
        """اتصال به دیتابیس با هندلینگ خطا"""
        try:
            conn = sqlite3.connect(self.db_path)
            # فعال کردن foreign keys و بهبود عملکرد
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA journal_mode = WAL")  # بهبود کارایی
            conn.execute("PRAGMA synchronous = NORMAL")
            return conn
        except Exception as e:
            logger.error(f"❌ خطا در اتصال به دیتابیس {self.db_path}: {e}")
            raise
    
    def init_db(self):
        """ایجاد جداول دیتابیس"""
        logger.info("🔧 در حال راه‌اندازی دیتابیس...")
        
        try:
            with self.get_connection() as conn:
                # جدول کاربران
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # جدول برنامه مطالعاتی
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS study_plans (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        subject TEXT,
                        topic TEXT,
                        duration_minutes INTEGER,
                        completed BOOLEAN DEFAULT FALSE,
                        study_date DATE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
                    )
                ''')
                
                # جدول آمار مطالعه
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS study_stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        study_date DATE DEFAULT CURRENT_DATE,
                        total_minutes INTEGER DEFAULT 0,
                        subjects TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
                        UNIQUE(user_id, study_date)
                    )
                ''')
                
                # جدول کانال‌های اجباری
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS mandatory_channels (
                        channel_id INTEGER PRIMARY KEY,
                        channel_username TEXT UNIQUE,
                        channel_title TEXT,
                        added_by INTEGER,
                        added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # جدول عضویت کاربران در کانال‌ها
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS channel_memberships (
                        user_id INTEGER,
                        channel_id INTEGER,
                        is_member BOOLEAN DEFAULT FALSE,
                        last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (user_id, channel_id),
                        FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
                        FOREIGN KEY (channel_id) REFERENCES mandatory_channels (channel_id) ON DELETE CASCADE
                    )
                ''')
                
                # جدول لاگ خطاها برای عیب‌یابی
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS error_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        error_type TEXT,
                        error_message TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 🔥 اضافه کردن جدول ریمایندرهای پیشرفته
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS advanced_reminders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        title TEXT NOT NULL,
                        message_text TEXT NOT NULL,
                        scheduled_date TEXT NOT NULL,
                        scheduled_time TEXT NOT NULL,
                        repeat_count INTEGER DEFAULT 1,
                        repeat_interval INTEGER DEFAULT 1,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
                    )
                ''')
                
                # ایجاد ایندکس برای بهبود عملکرد
                conn.execute('CREATE INDEX IF NOT EXISTS idx_study_plans_user_date ON study_plans(user_id, study_date)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_study_plans_completed ON study_plans(completed)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_users_active ON users(last_active)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_advanced_reminders_user ON advanced_reminders(user_id)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_advanced_reminders_date ON advanced_reminders(scheduled_date)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_advanced_reminders_active ON advanced_reminders(is_active)')
                
                conn.commit()
            logger.info("✅ دیتابیس راه‌اندازی شد")
            
        except Exception as e:
            logger.error(f"❌ خطا در راه‌اندازی دیتابیس: {e}")
            raise
    
    def add_user(self, user_id: int, username: str, first_name: str, last_name: str = ""):
        """افزودن کاربر جدید"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO users (user_id, username, first_name, last_name, last_active)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (user_id, username, first_name, last_name))
                conn.commit()
            logger.debug(f"✅ کاربر {user_id} افزوده/آپدیت شد")
        except Exception as e:
            logger.error(f"❌ خطا در افزودن کاربر {user_id}: {e}")
            self.log_error(user_id, "add_user", str(e))

    def get_active_users(self):
        """دریافت کاربران فعال"""
        query = """
        SELECT user_id, username, first_name, last_name, created_at 
        FROM users 
        WHERE is_active = 1
        ORDER BY created_at DESC
        """
        return self.execute_query(query, fetch_all=True)

    def update_user_activity(self, user_id: int):
        """بروزرسانی زمان فعالیت کاربر"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE user_id = ?
                ''', (user_id,))
                conn.commit()
        except Exception as e:
            logger.error(f"❌ خطا در آپدیت فعالیت کاربر {user_id}: {e}")
    
    def add_study_session(self, user_id: int, subject: str, topic: str, duration_minutes: int, study_date: str = None):
        """افزودن جلسه مطالعه"""
        if study_date is None:
            study_date = date.today().isoformat()
        
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT INTO study_plans (user_id, subject, topic, duration_minutes, study_date)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, subject, topic, duration_minutes, study_date))
                conn.commit()
            logger.debug(f"✅ جلسه مطالعه برای کاربر {user_id} افزوده شد")
        except Exception as e:
            logger.error(f"❌ خطا در افزودن جلسه مطالعه: {e}")
            self.log_error(user_id, "add_study_session", str(e))
    
    def mark_session_completed(self, session_id: int, user_id: int):
        """علامت‌گذاری جلسه به عنوان کامل شده"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    UPDATE study_plans SET completed = TRUE 
                    WHERE id = ? AND user_id = ?
                ''', (session_id, user_id))
                conn.commit()
            logger.debug(f"✅ جلسه {session_id} کامل شد")
        except Exception as e:
            logger.error(f"❌ خطا در کامل کردن جلسه: {e}")
    
    def get_today_study_stats(self, user_id: int) -> Dict[str, Any]:
        """دریافت آمار مطالعه امروز"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('''
                    SELECT 
                        SUM(duration_minutes) as total_minutes,
                        COUNT(*) as sessions_count,
                        GROUP_CONCAT(DISTINCT subject) as subjects
                    FROM study_plans 
                    WHERE user_id = ? AND study_date = DATE('now') AND completed = TRUE
                ''', (user_id,))
                
                result = cursor.fetchone()
                return {
                    'total_minutes': result[0] or 0,
                    'sessions_count': result[1] or 0,
                    'subjects': result[2] or 'هیچ'
                }
        except Exception as e:
            logger.error(f"❌ خطا در دریافت آمار امروز: {e}")
            return {'total_minutes': 0, 'sessions_count': 0, 'subjects': 'خطا'}
    
    def get_weekly_stats(self, user_id: int) -> List[Dict[str, Any]]:
        """دریافت آمار مطالعه هفته جاری"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('''
                    SELECT 
                        study_date,
                        SUM(duration_minutes) as total_minutes,
                        COUNT(*) as sessions_count
                    FROM study_plans 
                    WHERE user_id = ? 
                    AND study_date >= DATE('now', '-6 days')
                    AND completed = TRUE
                    GROUP BY study_date
                    ORDER BY study_date
                ''', (user_id,))
                
                return [
                    {'date': row[0], 'total_minutes': row[1] or 0, 'sessions_count': row[2] or 0}
                    for row in cursor.fetchall()
                ]
        except Exception as e:
            logger.error(f"❌ خطا در دریافت آمار هفتگی: {e}")
            return []
    
    def add_mandatory_channel(self, channel_id: int, channel_username: str, channel_title: str, admin_id: int):
        """افزودن کانال اجباری"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO mandatory_channels (channel_id, channel_username, channel_title, added_by)
                    VALUES (?, ?, ?, ?)
                ''', (channel_id, channel_username, channel_title, admin_id))
                conn.commit()
            logger.info(f"✅ کانال {channel_username} افزوده شد")
        except Exception as e:
            logger.error(f"❌ خطا در افزودن کانال: {e}")
    
    def get_mandatory_channels(self) -> List[Dict[str, Any]]:
        """دریافت لیست کانال‌های اجباری"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('''
                    SELECT channel_id, channel_username, channel_title 
                    FROM mandatory_channels
                ''')
                
                return [
                    {'channel_id': row[0], 'channel_username': row[1], 'channel_title': row[2]}
                    for row in cursor.fetchall()
                ]
        except Exception as e:
            logger.error(f"❌ خطا در دریافت کانال‌ها: {e}")
            return []
    
    def check_channel_membership(self, user_id: int, channel_id: int) -> bool:
        """بررسی عضویت کاربر در کانال"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('''
                    SELECT is_member FROM channel_memberships 
                    WHERE user_id = ? AND channel_id = ?
                ''', (user_id, channel_id))
                
                result = cursor.fetchone()
                return result[0] if result else False
        except Exception as e:
            logger.error(f"❌ خطا در بررسی عضویت: {e}")
            return False
    
    def update_channel_membership(self, user_id: int, channel_id: int, is_member: bool):
        """بروزرسانی وضعیت عضویت کاربر"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO channel_memberships (user_id, channel_id, is_member, last_checked)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ''', (user_id, channel_id, is_member))
                conn.commit()
        except Exception as e:
            logger.error(f"❌ خطا در آپدیت عضویت: {e}")
    
    def get_user_progress(self, user_id: int) -> Dict[str, Any]:
        """دریافت پیشرفت کلی کاربر"""
        try:
            with self.get_connection() as conn:
                # کل زمان مطالعه
                cursor = conn.execute('''
                    SELECT SUM(duration_minutes) FROM study_plans 
                    WHERE user_id = ? AND completed = TRUE
                ''', (user_id,))
                total_minutes = cursor.fetchone()[0] or 0
                
                # تعداد جلسات
                cursor = conn.execute('''
                    SELECT COUNT(*) FROM study_plans 
                    WHERE user_id = ? AND completed = TRUE
                ''', (user_id,))
                total_sessions = cursor.fetchone()[0] or 0
                
                # روزهای فعال
                cursor = conn.execute('''
                    SELECT COUNT(DISTINCT study_date) FROM study_plans 
                    WHERE user_id = ? AND completed = TRUE
                ''', (user_id,))
                active_days = cursor.fetchone()[0] or 0
                
                # میانگین روزانه
                avg_daily = round(total_minutes / max(active_days, 1), 1)
                
                return {
                    'total_minutes': total_minutes,
                    'total_hours': round(total_minutes / 60, 1),
                    'total_sessions': total_sessions,
                    'active_days': active_days,
                    'avg_daily_minutes': avg_daily
                }
        except Exception as e:
            logger.error(f"❌ خطا در دریافت پیشرفت کاربر: {e}")
            return {'total_minutes': 0, 'total_hours': 0, 'total_sessions': 0, 'active_days': 0, 'avg_daily_minutes': 0}

    def get_active_users(self, days_active: int = 30) -> List[Dict[str, Any]]:
        """دریافت کاربران فعال (اختیاری - برای ریمایندرهای عمومی)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
SELECT DISTINCT user_id 
FROM users 
WHERE last_activity >= datetime('now', ?)
OR created_at >= datetime('now', ?)
''', (f'-{days_active} days', f'-{days_active} days'))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def log_error(self, user_id: int, error_type: str, error_message: str):
        """لاگ کردن خطاها برای عیب‌یابی"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT INTO error_logs (user_id, error_type, error_message)
                    VALUES (?, ?, ?)
                ''', (user_id, error_type, error_message))
                conn.commit()
        except Exception as e:
            logger.error(f"❌ خطا در لاگ کردن خطا: {e}")
    
    def get_database_info(self) -> Dict[str, Any]:
        """دریافت اطلاعات کلی دیتابیس"""
        try:
            with self.get_connection() as conn:
                # تعداد کاربران
                cursor = conn.execute('SELECT COUNT(*) FROM users')
                user_count = cursor.fetchone()[0]
                
                # تعداد جلسات مطالعه
                cursor = conn.execute('SELECT COUNT(*) FROM study_plans')
                session_count = cursor.fetchone()[0]
                
                # حجم فایل دیتابیس
                db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
                
                return {
                    'user_count': user_count,
                    'session_count': session_count,
                    'db_size_mb': round(db_size / (1024 * 1024), 2),
                    'db_path': self.db_path
                }
        except Exception as e:
            logger.error(f"❌ خطا در دریافت اطلاعات دیتابیس: {e}")
            return {'user_count': 0, 'session_count': 0, 'db_size_mb': 0, 'db_path': self.db_path}

    # 🔥 اضافه کردن متدهای ضروری برای ریمایندر پیشرفته
    def execute_query(self, query: str, params: tuple = (), fetch_all: bool = False):
        """اجرای کوئری و بازگرداندن نتایج - برای سازگاری با کدهای موجود"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                
                if query.strip().upper().startswith('SELECT'):
                    if fetch_all:
                        result = cursor.fetchall()
                    else:
                        result = cursor.fetchone()
                else:
                    conn.commit()
                    result = None
                
                return result
        except Exception as e:
            logger.error(f"❌ خطا در اجرای کوئری: {e}")
            return None

    def execute_many(self, query: str, params_list: list):
        """اجرای دستورات bulk"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(query, params_list)
                conn.commit()
        except Exception as e:
            logger.error(f"❌ خطا در اجرای دستورات bulk: {e}")

    # 🔥 متدهای مخصوص ریمایندرهای پیشرفته
    def add_advanced_reminder(self, user_id: int, title: str, message_text: str, 
                            scheduled_date: str, scheduled_time: str, 
                            repeat_count: int = 1, repeat_interval: int = 1):
        """افزودن ریمایندر پیشرفته جدید"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT INTO advanced_reminders 
                    (user_id, title, message_text, scheduled_date, scheduled_time, repeat_count, repeat_interval)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, title, message_text, scheduled_date, scheduled_time, repeat_count, repeat_interval))
                conn.commit()
            logger.info(f"✅ ریمایندر پیشرفته برای کاربر {user_id} افزوده شد")
            return True
        except Exception as e:
            logger.error(f"❌ خطا در افزودن ریمایندر پیشرفته: {e}")
            return False

    def get_user_advanced_reminders(self, user_id: int):
        """دریافت ریمایندرهای پیشرفته کاربر"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('''
                    SELECT id, title, message_text, scheduled_date, scheduled_time, 
                           repeat_count, repeat_interval, is_active, created_at
                    FROM advanced_reminders 
                    WHERE user_id = ? AND is_active = TRUE
                    ORDER BY scheduled_date, scheduled_time
                ''', (user_id,))
                
                return [
                    {
                        'id': row[0],
                        'title': row[1],
                        'message_text': row[2],
                        'scheduled_date': row[3],
                        'scheduled_time': row[4],
                        'repeat_count': row[5],
                        'repeat_interval': row[6],
                        'is_active': row[7],
                        'created_at': row[8]
                    }
                    for row in cursor.fetchall()
                ]
        except Exception as e:
            logger.error(f"❌ خطا در دریافت ریمایندرهای کاربر: {e}")
            return []

    def get_today_advanced_reminders(self):
        """دریافت ریمایندرهای پیشرفته امروز"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('''
                    SELECT id, user_id, title, message_text, scheduled_time, repeat_count
                    FROM advanced_reminders 
                    WHERE scheduled_date = DATE('now') 
                    AND is_active = TRUE
                    ORDER BY scheduled_time
                ''')
                
                return [
                    {
                        'id': row[0],
                        'user_id': row[1],
                        'title': row[2],
                        'message_text': row[3],
                        'scheduled_time': row[4],
                        'repeat_count': row[5]
                    }
                    for row in cursor.fetchall()
                ]
        except Exception as e:
            logger.error(f"❌ خطا در دریافت ریمایندرهای امروز: {e}")
            return []

    def deactivate_reminder(self, reminder_id: int):
        """غیرفعال کردن ریمایندر"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    UPDATE advanced_reminders 
                    SET is_active = FALSE 
                    WHERE id = ?
                ''', (reminder_id,))
                conn.commit()
            logger.info(f"✅ ریمایندر {reminder_id} غیرفعال شد")
            return True
        except Exception as e:
            logger.error(f"❌ خطا در غیرفعال کردن ریمایندر: {e}")
            return False

    def delete_reminder(self, reminder_id: int):
        """حذف ریمایندر"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    DELETE FROM advanced_reminders 
                    WHERE id = ?
                ''', (reminder_id,))
                conn.commit()
            logger.info(f"✅ ریمایندر {reminder_id} حذف شد")
            return True
        except Exception as e:
            logger.error(f"❌ خطا در حذف ریمایندر: {e}")
            return False

# ایجاد instance جهانی دیتابیس
database = Database()
