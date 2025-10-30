"""
سیستم دیتابیس تخصصی برای ریمایندرها
"""
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json

logger = logging.getLogger(__name__)

class ReminderDatabase:
    def __init__(self, db_path="konkour_bot.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """ایجاد جداول ریمایندرها"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # جدول ریمایندرهای کنکور
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS exam_reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    exam_keys TEXT NOT NULL, -- JSON list of exam keys
                    days_of_week TEXT NOT NULL, -- JSON list [0,1,2,3,4,5,6]
                    specific_times TEXT NOT NULL, -- JSON list of times ["08:00", "14:30"]
                    specific_dates TEXT, -- JSON list of specific dates
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # جدول ریمایندرهای شخصی
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS personal_reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    repetition_type TEXT NOT NULL, -- once, daily, weekly, monthly, custom
                    days_of_week TEXT, -- JSON list for weekly
                    specific_time TEXT NOT NULL,
                    custom_days_interval INTEGER, -- for custom repetition
                    start_date TEXT NOT NULL,
                    end_date TEXT,
                    max_occurrences INTEGER,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # جدول ریمایندرهای خودکار
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS auto_reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    days_before_exam INTEGER NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_by_admin INTEGER NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # جدول فعال‌سازی ریمایندرهای خودکار توسط کاربران
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_auto_reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    auto_reminder_id INTEGER NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (auto_reminder_id) REFERENCES auto_reminders (id)
                )
            ''')
            
            # جدول لاگ ارسال ریمایندرها
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reminder_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    reminder_id INTEGER NOT NULL,
                    reminder_type TEXT NOT NULL, -- exam, personal, auto
                    sent_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'sent' -- sent, failed
                )
            ''')
            
            conn.commit()

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
            
            return cursor.lastrowid

    def get_user_exam_reminders(self, user_id: int) -> List[Dict[str, Any]]:
        """دریافت ریمایندرهای کنکور کاربر"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM exam_reminders WHERE user_id = ? ORDER BY created_at DESC',
                (user_id,)
            )
            
            reminders = []
            for row in cursor.fetchall():
                reminders.append({
                    'id': row[0],
                    'user_id': row[1],
                    'exam_keys': json.loads(row[2]),
                    'days_of_week': json.loads(row[3]),
                    'specific_times': json.loads(row[4]),
                    'specific_dates': json.loads(row[5]),
                    'start_date': row[6],
                    'end_date': row[7],
                    'is_active': bool(row[8]),
                    'created_at': row[9]
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
            
            return cursor.lastrowid

    def get_user_personal_reminders(self, user_id: int) -> List[Dict[str, Any]]:
        """دریافت ریمایندرهای شخصی کاربر"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM personal_reminders WHERE user_id = ? ORDER BY created_at DESC',
                (user_id,)
            )
            
            reminders = []
            for row in cursor.fetchall():
                reminders.append({
                    'id': row[0],
                    'user_id': row[1],
                    'title': row[2],
                    'message': row[3],
                    'repetition_type': row[4],
                    'days_of_week': json.loads(row[5]),
                    'specific_time': row[6],
                    'custom_days_interval': row[7],
                    'start_date': row[8],
                    'end_date': row[9],
                    'max_occurrences': row[10],
                    'is_active': bool(row[11]),
                    'created_at': row[12]
                })
            
            return reminders

    # --- توابع عمومی ---
    
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
            
            return cursor.rowcount > 0

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
            return cursor.rowcount > 0

    def get_due_reminders(self, target_date: str, target_time: str) -> List[Dict[str, Any]]:
        """دریافت ریمایندرهای due برای تاریخ و زمان مشخص"""
        # این تابع رو بعداً کامل می‌کنم
        return []

# ایجاد instance اصلی
reminder_db = ReminderDatabase()
