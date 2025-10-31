"""
سیستم دیتابیس تخصصی برای ریمایندرها - نسخه کامل با تاریخ میلادی
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
                    start_date TEXT NOT NULL,  -- ذخیره به صورت میلادی YYYY-MM-DD
                    end_date TEXT NOT NULL,    -- ذخیره به صورت میلادی YYYY-MM-DD
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
                    start_date TEXT NOT NULL,  -- ذخیره به صورت میلادی YYYY-MM-DD
                    end_date TEXT,             -- ذخیره به صورت میلادی YYYY-MM-DD
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
            
            # 🔥 جدول جدید برای ریمایندرهای پیشرفته ادمین
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admin_advanced_reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    admin_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    start_time TEXT NOT NULL,      -- ساعت شروع (مثلا 14:30)
                    start_date TEXT NOT NULL,      -- تاریخ شروع میلادی
                    end_time TEXT NOT NULL,        -- ساعت پایان
                    end_date TEXT NOT NULL,        -- تاریخ پایان میلادی
                    days_of_week TEXT NOT NULL,    -- روزهای هفته به صورت JSON
                    repeat_count INTEGER DEFAULT 1,-- تعداد تکرار (&)
                    repeat_interval INTEGER DEFAULT 0, -- فاصله زمانی (@)
                    is_active BOOLEAN DEFAULT TRUE,
                    total_sent INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_admin_advanced_active 
                ON admin_advanced_reminders(is_active, admin_id)
            ''')
            
            conn.commit()
            logger.info("✅ دیتابیس ریمایندرها راه‌اندازی شد")

    # --- توابع جدید برای ریمایندرهای پیشرفته ادمین ---
    
    def add_admin_advanced_reminder(self, admin_id: int, title: str, message: str,
                                  start_time: str, start_date: str, 
                                  end_time: str, end_date: str,
                                  days_of_week: List[int], 
                                  repeat_count: int, repeat_interval: int) -> int:
        """افزودن ریمایندر پیشرفته توسط ادمین"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO admin_advanced_reminders 
                (admin_id, title, message, start_time, start_date, end_time, end_date, 
                 days_of_week, repeat_count, repeat_interval)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                admin_id,
                title,
                message,
                start_time,
                start_date,  # تاریخ میلادی
                end_time,
                end_date,    # تاریخ میلادی
                json.dumps(days_of_week),
                repeat_count,
                repeat_interval
            ))
            
            reminder_id = cursor.lastrowid
            logger.info(f"✅ ریمایندر پیشرفته ادمین {reminder_id} ایجاد شد")
            return reminder_id

    def get_admin_advanced_reminders(self, admin_id: int = None) -> List[Dict[str, Any]]:
        """دریافت ریمایندرهای پیشرفته ادمین"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if admin_id:
                cursor.execute(
                    '''SELECT * FROM admin_advanced_reminders 
                       WHERE admin_id = ? 
                       ORDER BY created_at DESC''',
                    (admin_id,)
                )
            else:
                cursor.execute('''SELECT * FROM admin_advanced_reminders ORDER BY created_at DESC''')
            
            reminders = []
            for row in cursor.fetchall():
                reminders.append({
                    'id': row['id'],
                    'admin_id': row['admin_id'],
                    'title': row['title'],
                    'message': row['message'],
                    'start_time': row['start_time'],
                    'start_date': row['start_date'],
                    'end_time': row['end_time'],
                    'end_date': row['end_date'],
                    'days_of_week': json.loads(row['days_of_week']),
                    'repeat_count': row['repeat_count'],
                    'repeat_interval': row['repeat_interval'],
                    'is_active': bool(row['is_active']),
                    'total_sent': row['total_sent'],
                    'created_at': row['created_at']
                })
            
            return reminders

    def update_admin_advanced_reminder(self, reminder_id: int, **kwargs) -> bool:
        """ویرایش ریمایندر پیشرفته ادمین"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            update_fields = []
            params = []
            
            for key, value in kwargs.items():
                if key in ['title', 'message', 'start_time', 'start_date', 'end_time', 'end_date', 
                          'repeat_count', 'repeat_interval', 'is_active']:
                    update_fields.append(f"{key} = ?")
                    params.append(value)
                elif key == 'days_of_week' and isinstance(value, list):
                    update_fields.append("days_of_week = ?")
                    params.append(json.dumps(value))
            
            if not update_fields:
                return False
                
            params.append(reminder_id)
            cursor.execute(f'''
                UPDATE admin_advanced_reminders 
                SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', params)
            
            success = cursor.rowcount > 0
            if success:
                logger.info(f"✅ ریمایندر پیشرفته {reminder_id} آپدیت شد")
            
            return success

    def delete_admin_advanced_reminder(self, reminder_id: int) -> bool:
        """حذف ریمایندر پیشرفته ادمین"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM admin_advanced_reminders WHERE id = ?', (reminder_id,))
            
            success = cursor.rowcount > 0
            if success:
                logger.info(f"🗑️ ریمایندر پیشرفته {reminder_id} حذف شد")
            
            return success

    def toggle_admin_advanced_reminder(self, reminder_id: int) -> bool:
        """تغییر وضعیت فعال/غیرفعال ریمایندر پیشرفته"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # دریافت وضعیت فعلی
            cursor.execute('SELECT is_active FROM admin_advanced_reminders WHERE id = ?', (reminder_id,))
            result = cursor.fetchone()
            
            if not result:
                return False
                
            new_status = not bool(result[0])
            
            cursor.execute(
                'UPDATE admin_advanced_reminders SET is_active = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (new_status, reminder_id)
            )
            
            success = cursor.rowcount > 0
            if success:
                status_text = "فعال" if new_status else "غیرفعال"
                logger.info(f"✅ ریمایندر پیشرفته {reminder_id} {status_text} شد")
            
            return success

    # --- توابع ریمایندر کنکور ---
    
    def add_exam_reminder(self, user_id: int, exam_keys: List[str], 
                         days_of_week: List[int], specific_times: List[str],
                         start_date: str, end_date: str,  # تاریخ شمسی از کاربر
                         specific_dates: List[str] = None) -> int:
        """افزودن ریمایندر کنکور - ذخیره تاریخ‌ها به صورت میلادی"""
        
        from utils.time_utils import persian_to_gregorian_string
        
        # تبدیل تاریخ‌های شمسی به میلادی
        start_date_gregorian = persian_to_gregorian_string(start_date)
        end_date_gregorian = persian_to_gregorian_string(end_date)
        
        specific_dates_gregorian = []
        if specific_dates:
            for date in specific_dates:
                specific_dates_gregorian.append(persian_to_gregorian_string(date))
        
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
                json.dumps(specific_dates_gregorian),
                start_date_gregorian,  # ذخیره میلادی
                end_date_gregorian     # ذخیره میلادی
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
                    'start_date': row['start_date'],  # میلادی
                    'end_date': row['end_date'],      # میلادی
                    'is_active': bool(row['is_active']),
                    'last_sent': row['last_sent'],
                    'total_sent': row['total_sent'],
                    'created_at': row['created_at']
                })
            
            return reminders

    # --- توابع ریمایندر شخصی ---
    
    def add_personal_reminder(self, user_id: int, title: str, message: str,
                            repetition_type: str, specific_time: str,
                            start_date: str, days_of_week: List[int] = None,  # تاریخ شمسی از کاربر
                            custom_days_interval: int = None, 
                            end_date: str = None, max_occurrences: int = None) -> int:
        """افزودن ریمایندر شخصی - ذخیره تاریخ‌ها به صورت میلادی"""
        
        from utils.time_utils import persian_to_gregorian_string
        
        # تبدیل تاریخ‌های شمسی به میلادی
        start_date_gregorian = persian_to_gregorian_string(start_date)
        end_date_gregorian = persian_to_gregorian_string(end_date) if end_date else None
        
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
                start_date_gregorian,  # ذخیره میلادی
                end_date_gregorian,    # ذخیره میلادی
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
                    'start_date': row['start_date'],  # میلادی
                    'end_date': row['end_date'],      # میلادی
                    'max_occurrences': row['max_occurrences'],
                    'is_active': bool(row['is_active']),
                    'last_sent': row['last_sent'],
                    'total_sent': row['total_sent'],
                    'created_at': row['created_at']
                )
            
            return reminders

    # --- توابع اصلی برای سیستم زمان‌بندی ---
    
    def get_due_reminders(self, target_date: str, target_time: str, target_weekday: int) -> List[Dict[str, Any]]:
        """دریافت ریمایندرهای due برای تاریخ و زمان مشخص - با تاریخ میلادی"""
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
                
                # 🔥 حالا target_date خودش میلادی هست (از سیستم)
                # پس نیاز به تبدیل نداریم!
                
                logger.info(f"🔍 جستجوی ریمایندر برای تاریخ میلادی: {target_date}, زمان: {target_time_english}")
                
                # دریافت ریمایندرهای کنکور - با تاریخ میلادی
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
                    target_date,  # تاریخ میلادی
                    target_date   # تاریخ میلادی
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
                
                # دریافت ریمایندرهای شخصی - با تاریخ میلادی
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
                
                # 🔥 دریافت ریمایندرهای پیشرفته ادمین - با تاریخ میلادی
                cursor.execute('''
                    SELECT * FROM admin_advanced_reminders 
                    WHERE is_active = TRUE 
                    AND json_extract(days_of_week, '$') LIKE ?
                    AND start_time = ?
                    AND start_date <= ? 
                    AND end_date >= ?
                ''', (
                    f'%{target_weekday}%',
                    target_time_english,
                    target_date,  # تاریخ میلادی
                    target_date   # تاریخ میلادی
                ))
                
                for row in cursor.fetchall():
                    reminders.append({
                        'id': row['id'],
                        'admin_id': row['admin_id'],
                        'title': row['title'],
                        'message': row['message'],
                        'start_time': row['start_time'],
                        'start_date': row['start_date'],
                        'end_time': row['end_time'],
                        'end_date': row['end_date'],
                        'days_of_week': json.loads(row['days_of_week']),
                        'repeat_count': row['repeat_count'],
                        'repeat_interval': row['repeat_interval'],
                        'is_active': bool(row['is_active']),
                        'reminder_type': 'admin_advanced'
                    })
                
                logger.info(f"✅ پیدا شد {len(reminders)} ریمایندر برای ارسال")
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
            'auto': 'user_auto_reminders',
            'admin_advanced': 'admin_advanced_reminders'
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
            'personal': 'personal_reminders',
            'admin_advanced': 'admin_advanced_reminders'
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
                    'personal': 'personal_reminders',
                    'admin_advanced': 'admin_advanced_reminders'
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
                        UNION ALL
                        SELECT id, is_active FROM admin_advanced_reminders
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
