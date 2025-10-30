"""
سیستم دیتابیس تخصصی برای ریمایندرها - نسخه پیشرفته
"""
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import json
import pytz

logger = logging.getLogger(__name__)

# تنظیم تایم‌زون تهران
TEHRAN_TIMEZONE = pytz.timezone('Asia/Tehran')

class ReminderDatabase:
    def __init__(self, db_path="konkour_bot.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """ایجاد جداول ریمایندرها با بهینه‌سازی"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # فعال کردن ویژگی‌های پیشرفته SQLite
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute("PRAGMA journal_mode = WAL")
            cursor.execute("PRAGMA synchronous = NORMAL")
            cursor.execute("PRAGMA cache_size = -64000")  # 64MB cache
            
            # جدول ریمایندرهای کنکور
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS exam_reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    exam_keys TEXT NOT NULL,
                    days_of_week TEXT NOT NULL,
                    specific_times TEXT NOT NULL,
                    specific_dates TEXT,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    timezone TEXT DEFAULT 'Asia/Tehran',
                    is_active BOOLEAN DEFAULT TRUE,
                    last_sent TIMESTAMP,
                    total_sent INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # جدول ریمایندرهای شخصی
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS personal_reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    repetition_type TEXT NOT NULL,
                    days_of_week TEXT,
                    specific_time TEXT NOT NULL,
                    custom_days_interval INTEGER,
                    start_date TEXT NOT NULL,
                    end_date TEXT,
                    max_occurrences INTEGER,
                    timezone TEXT DEFAULT 'Asia/Tehran',
                    is_active BOOLEAN DEFAULT TRUE,
                    last_sent TIMESTAMP,
                    total_sent INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # جدول ریمایندرهای خودکار
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS auto_reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    days_before_exam INTEGER NOT NULL,
                    exam_keys TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_by_admin INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # جدول فعال‌سازی ریمایندرهای خودکار توسط کاربران
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_auto_reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    auto_reminder_id INTEGER NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (auto_reminder_id) REFERENCES auto_reminders (id) ON DELETE CASCADE
                )
            ''')
            
            # جدول لاگ ارسال ریمایندرها
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reminder_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    reminder_id INTEGER NOT NULL,
                    reminder_type TEXT NOT NULL,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'sent',
                    error_message TEXT,
                    delivery_time_ms INTEGER
                )
            ''')
            
            # ایجاد ایندکس‌های بهینه
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_exam_reminders_active 
                ON exam_reminders(is_active, user_id)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_personal_reminders_active 
                ON personal_reminders(is_active, user_id)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_reminder_logs_user_date 
                ON reminder_logs(user_id, sent_at)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_exam_reminders_dates 
                ON exam_reminders(start_date, end_date)
            ''')
            
            conn.commit()
            logger.info("✅ دیتابیس ریمایندرها راه‌اندازی شد")

    # --- توابع ریمایندر کنکور ---
    
    def add_exam_reminder(self, user_id: int, exam_keys: List[str], 
                         days_of_week: List[int], specific_times: List[str],
                         start_date: str, end_date: str, 
                         specific_dates: List[str] = None) -> int:
        """افزودن ریمایندر کنکور"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO exam_reminders 
                (user_id, exam_keys, days_of_week, specific_times, specific_dates, start_date, end_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                json.dumps(exam_keys),
                json.dumps(days_of_week),
                json.dumps(specific_times),
                json.dumps(specific_dates or []),
                start_date,
                end_date
            ))
            
            reminder_id = cursor.lastrowid
            logger.info(f"✅ ریمایندر کنکور {reminder_id} برای کاربر {user_id} ایجاد شد")
            return reminder_id

    def get_user_exam_reminders(self, user_id: int) -> List[Dict[str, Any]]:
        """دریافت ریمایندرهای کنکور کاربر"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                '''SELECT * FROM exam_reminders 
                   WHERE user_id = ? 
                   ORDER BY created_at DESC''',
                (user_id,)
            )
            
            reminders = []
            for row in cursor.fetchall():
                reminders.append({
                    'id': row['id'],
                    'user_id': row['user_id'],
                    'exam_keys': json.loads(row['exam_keys']),
                    'days_of_week': json.loads(row['days_of_week']),
                    'specific_times': json.loads(row['specific_times']),
                    'specific_dates': json.loads(row['specific_dates']),
                    'start_date': row['start_date'],
                    'end_date': row['end_date'],
                    'is_active': bool(row['is_active']),
                    'last_sent': row['last_sent'],
                    'total_sent': row['total_sent'],
                    'created_at': row['created_at']
                })
            
            return reminders

    # --- توابع ریمایندر شخصی ---
    
    def add_personal_reminder(self, user_id: int, title: str, message: str,
                            repetition_type: str, specific_time: str,
                            start_date: str, days_of_week: List[int] = None,
                            custom_days_interval: int = None, 
                            end_date: str = None, max_occurrences: int = None) -> int:
        """افزودن ریمایندر شخصی"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO personal_reminders 
                (user_id, title, message, repetition_type, days_of_week, 
                 specific_time, custom_days_interval, start_date, end_date, max_occurrences)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                title,
                message,
                repetition_type,
                json.dumps(days_of_week or []),
                specific_time,
                custom_days_interval,
                start_date,
                end_date,
                max_occurrences
            ))
            
            reminder_id = cursor.lastrowid
            logger.info(f"✅ ریمایندر شخصی {reminder_id} برای کاربر {user_id} ایجاد شد")
            return reminder_id

    def get_user_personal_reminders(self, user_id: int) -> List[Dict[str, Any]]:
        """دریافت ریمایندرهای شخصی کاربر"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                '''SELECT * FROM personal_reminders 
                   WHERE user_id = ? 
                   ORDER BY created_at DESC''',
                (user_id,)
            )
            
            reminders = []
            for row in cursor.fetchall():
                reminders.append({
                    'id': row['id'],
                    'user_id': row['user_id'],
                    'title': row['title'],
                    'message': row['message'],
                    'repetition_type': row['repetition_type'],
                    'days_of_week': json.loads(row['days_of_week']),
                    'specific_time': row['specific_time'],
                    'custom_days_interval': row['custom_days_interval'],
                    'start_date': row['start_date'],
                    'end_date': row['end_date'],
                    'max_occurrences': row['max_occurrences'],
                    'is_active': bool(row['is_active']),
                    'last_sent': row['last_sent'],
                    'total_sent': row['total_sent'],
                    'created_at': row['created_at']
                })
            
            return reminders

    # --- توابع اصلی برای سیستم زمان‌بندی ---
    
    def get_due_reminders(self, target_date: str, target_time: str, target_weekday: int) -> List[Dict[str, Any]]:
        """دریافت ریمایندرهای due برای تاریخ و زمان مشخص"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # تبدیل زمان فارسی به انگلیسی
                time_map = {
                    "۸:۰۰": "08:00", "۱۰:۰۰": "10:00", "۱۲:۰۰": "12:00", 
                    "۱۴:۰۰": "14:00", "۱۶:۰۰": "16:00", "۱۸:۰۰": "18:00",
                    "۲۰:۰۰": "20:00", "۲۲:۰۰": "22:00"
                }
                
                target_time_english = time_map.get(target_time, target_time)
                
                # دریافت ریمایندرهای کنکور
                cursor.execute('''
                    SELECT * FROM exam_reminders 
                    WHERE is_active = TRUE 
                    AND json_extract(days_of_week, '$') LIKE ?
                    AND json_extract(specific_times, '$') LIKE ?
                    AND start_date <= ? 
                    AND end_date >= ?
                ''', (
                    f'%{target_weekday}%',
                    f'%"{target_time_english}"%',
                    target_date,
                    target_date
                ))
                
                reminders = []
                for row in cursor.fetchall():
                    reminders.append({
                        'id': row['id'],
                        'user_id': row['user_id'],
                        'exam_keys': json.loads(row['exam_keys']),
                        'days_of_week': json.loads(row['days_of_week']),
                        'specific_times': json.loads(row['specific_times']),
                        'specific_dates': json.loads(row['specific_dates']),
                        'start_date': row['start_date'],
                        'end_date': row['end_date'],
                        'is_active': bool(row['is_active']),
                        'reminder_type': 'exam'
                    })
                
                # دریافت ریمایندرهای شخصی
                cursor.execute('''
                    SELECT * FROM personal_reminders 
                    WHERE is_active = TRUE 
                    AND specific_time = ?
                    AND start_date <= ? 
                    AND (end_date >= ? OR end_date IS NULL)
                ''', (target_time_english, target_date, target_date))
                
                for row in cursor.fetchall():
                    reminders.append({
                        'id': row['id'],
                        'user_id': row['user_id'],
                        'title': row['title'],
                        'message': row['message'],
                        'repetition_type': row['repetition_type'],
                        'days_of_week': json.loads(row['days_of_week']),
                        'specific_time': row['specific_time'],
                        'custom_days_interval': row['custom_days_interval'],
                        'start_date': row['start_date'],
                        'end_date': row['end_date'],
                        'max_occurrences': row['max_occurrences'],
                        'is_active': bool(row['is_active']),
                        'reminder_type': 'personal'
                    })
                
                return reminders
                
        except Exception as e:
            logger.error(f"خطا در دریافت ریمایندرهای due: {e}")
            return []

    def get_active_exam_reminders(self) -> List[Dict[str, Any]]:
        """دریافت همه ریمایندرهای کنکور فعال"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM exam_reminders 
                WHERE is_active = TRUE
            ''')
            
            reminders = []
            for row in cursor.fetchall():
                reminders.append({
                    'id': row['id'],
                    'user_id': row['user_id'],
                    'exam_keys': json.loads(row['exam_keys']),
                    'days_of_week': json.loads(row['days_of_week']),
                    'specific_times': json.loads(row['specific_times']),
                    'specific_dates': json.loads(row['specific_dates']),
                    'start_date': row['start_date'],
                    'end_date': row['end_date'],
                    'is_active': bool(row['is_active']),
                    'reminder_type': 'exam'
                })
            
            return reminders

    def update_reminder_status(self, reminder_type: str, reminder_id: int, is_active: bool):
        """به‌روزرسانی وضعیت ریمایندر"""
        table_map = {
            'exam': 'exam_reminders',
            'personal': 'personal_reminders',
            'auto': 'user_auto_reminders'
        }
        
        table = table_map.get(reminder_type)
        if not table:
            return False
            
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f'UPDATE {table} SET is_active = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (is_active, reminder_id)
            )
            
            success = cursor.rowcount > 0
            if success:
                logger.info(f"✅ وضعیت ریمایندر {reminder_id} به {'فعال' if is_active else 'غیرفعال'} تغییر کرد")
            
            return success

    def delete_reminder(self, reminder_type: str, reminder_id: int):
        """حذف ریمایندر"""
        table_map = {
            'exam': 'exam_reminders',
            'personal': 'personal_reminders'
        }
        
        table = table_map.get(reminder_type)
        if not table:
            return False
            
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f'DELETE FROM {table} WHERE id = ?', (reminder_id,))
            
            success = cursor.rowcount > 0
            if success:
                logger.info(f"🗑️ ریمایندر {reminder_id} حذف شد")
            
            return success

    def log_reminder_sent(self, user_id: int, reminder_id: int, reminder_type: str, 
                         status: str = 'sent', error_message: str = None, 
                         delivery_time_ms: int = None):
        """ثبت لاگ ارسال ریمایندر"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO reminder_logs 
                    (user_id, reminder_id, reminder_type, status, error_message, delivery_time_ms)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, reminder_id, reminder_type, status, error_message, delivery_time_ms))
                
                # آپدیت آمار ارسال در جدول اصلی
                table_map = {
                    'exam': 'exam_reminders',
                    'personal': 'personal_reminders'
                }
                table = table_map.get(reminder_type)
                if table:
                    cursor.execute(f'''
                        UPDATE {table} 
                        SET last_sent = CURRENT_TIMESTAMP, 
                            total_sent = total_sent + 1 
                        WHERE id = ?
                    ''', (reminder_id,))
                
        except Exception as e:
            logger.error(f"خطا در ثبت لاگ ریمایندر: {e}")

    def get_reminder_stats(self, user_id: int = None) -> Dict[str, Any]:
        """دریافت آمار ریمایندرها"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # آمار کلی
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_reminders,
                        SUM(CASE WHEN is_active THEN 1 ELSE 0 END) as active_reminders
                    FROM (
                        SELECT id, is_active FROM exam_reminders
                        UNION ALL
                        SELECT id, is_active FROM personal_reminders
                    )
                ''')
                row = cursor.fetchone()
                stats['total_reminders'] = row[0]
                stats['active_reminders'] = row[1]
                
                # آمار ارسال‌ها
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_sent,
                        COUNT(CASE WHEN status = 'sent' THEN 1 END) as successful_sent,
                        COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_sent
                    FROM reminder_logs
                ''')
                row = cursor.fetchone()
                stats['total_sent'] = row[0]
                stats['successful_sent'] = row[1]
                stats['failed_sent'] = row[2]
                
                # آمار کاربر خاص
                if user_id:
                    cursor.execute('''
                        SELECT COUNT(*) FROM (
                            SELECT id FROM exam_reminders WHERE user_id = ?
                            UNION ALL
                            SELECT id FROM personal_reminders WHERE user_id = ?
                        )
                    ''', (user_id, user_id))
                    stats['user_total_reminders'] = cursor.fetchone()[0]
                    
                    cursor.execute('''
                        SELECT COUNT(*) FROM reminder_logs WHERE user_id = ?
                    ''', (user_id,))
                    stats['user_total_sent'] = cursor.fetchone()[0]
                
                return stats
                
        except Exception as e:
            logger.error(f"خطا در دریافت آمار ریمایندرها: {e}")
            return {}

    def cleanup_old_logs(self, days_old: int = 30):
        """پاک کردن لاگ‌های قدیمی"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM reminder_logs 
                    WHERE sent_at < datetime('now', ?)
                ''', (f'-{days_old} days',))
                
                deleted_count = cursor.rowcount
                if deleted_count > 0:
                    logger.info(f"🧹 {deleted_count} لاگ قدیمی پاک شد")
                
                return deleted_count
                
        except Exception as e:
            logger.error(f"خطا در پاک کردن لاگ‌های قدیمی: {e}")
            return 0

# ایجاد instance اصلی
reminder_db = ReminderDatabase()
