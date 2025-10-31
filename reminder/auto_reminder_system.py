"""
سیستم ریمایندر خودکار برای همه کاربران
"""
import logging
import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
import pytz

from exam_data import EXAMS_1405
from utils.time_utils import get_current_persian_datetime, format_time_remaining

logger = logging.getLogger(__name__)
TEHRAN_TIMEZONE = pytz.timezone('Asia/Tehran')

class AutoReminderSystem:
    def __init__(self, db_path="konkour_bot.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """ایجاد جداول ریمایندرهای خودکار"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # ابتدا جدول رو حذف کن (اگر وجود داره)
            cursor.execute('DROP TABLE IF EXISTS auto_reminders')
            cursor.execute('DROP TABLE IF EXISTS user_auto_reminders')
            
            # حالا جدول رو با ساختار جدید ایجاد کن
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS auto_reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    days_before_exam INTEGER NOT NULL,
                    exam_keys TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    is_global BOOLEAN DEFAULT TRUE,
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
                    FOREIGN KEY (auto_reminder_id) REFERENCES auto_reminders (id) ON DELETE CASCADE,
                    UNIQUE(user_id, auto_reminder_id)
                )
            ''')
            
            # ایجاد ریمایندرهای پیش‌فرض
            self.create_default_reminders()

    def create_default_reminders(self):
        """ایجاد ریمایندرهای خودکار پیش‌فرض"""
        default_reminders = [
            {
                "title": "شروع فصل طلایی",
                "message": "فصل طلایی مطالعه شروع شده! فقط ۹۰ روز تا کنکور باقی مانده. 💪",
                "days_before_exam": 90,
                "exam_keys": ["ریاضی_فنی", "علوم_تجربی", "علوم_انسانی", "هنر", "زبان_خارجه"]
            },
            {
                "title": "شروع جمع‌بندی", 
                "message": "زمان جمع‌بندی فرا رسیده! ۳۰ روز تا کنکور باقی مانده. 📚",
                "days_before_exam": 30,
                "exam_keys": ["ریاضی_فنی", "علوم_تجربی", "علوم_انسانی", "هنر", "زبان_خارجه"]
            },
            {
                "title": "دو هفته پایانی",
                "message": "فقط ۱۵ روز تا کنکور! این روزها رو هوشمندانه مدیریت کنید. ⏳",
                "days_before_exam": 15,
                "exam_keys": ["ریاضی_فنی", "علوم_تجربی", "علوم_انسانی", "هنر", "زبان_خارجه"]
            },
            {
                "title": "هفته آخر",
                "message": "هفته آخر کنکور! آرامش خود را حفظ کنید و مرورهای سبک انجام دهید. 🧘",
                "days_before_exam": 7,
                "exam_keys": ["ریاضی_فنی", "علوم_تجربی", "علوم_انسانی", "هنر", "زبان_خارجه"]
            },
            {
                "title": "آماده‌سازی نهایی",
                "message": "فقط ۳ روز تا کنکور! وسایل مورد نیاز را آماده کنید. 🎒",
                "days_before_exam": 3,
                "exam_keys": ["ریاضی_فنی", "علوم_تجربی", "علوم_انسانی", "هنر", "زبان_خارجه"]
            },
            {
                "title": "روز قبل کنکور",
                "message": "فردا روز بزرگه! استراحت کنید و اعتماد به نفس داشته باشید. 🌟",
                "days_before_exam": 1,
                "exam_keys": ["ریاضی_فنی", "علوم_تجربی", "علوم_انسانی", "هنر", "زبان_خارجه"]
            }
        ]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for reminder in default_reminders:
                # بررسی وجود ریمایندر
                cursor.execute(
                    'SELECT id FROM auto_reminders WHERE title = ? AND days_before_exam = ?',
                    (reminder['title'], reminder['days_before_exam'])
                )
                if not cursor.fetchone():
                    cursor.execute('''
                        INSERT INTO auto_reminders (title, message, days_before_exam, exam_keys, created_by_admin, is_global)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        reminder['title'],
                        reminder['message'],
                        reminder['days_before_exam'],
                        json.dumps(reminder['exam_keys']),
                        1,  # ادمین اصلی
                        True
                    ))
            
            conn.commit()

    def add_auto_reminder(self, title: str, message: str, days_before_exam: int, 
                         exam_keys: List[str], admin_id: int, is_global: bool = True) -> int:
        """افزودن ریمایندر خودکار جدید"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO auto_reminders (title, message, days_before_exam, exam_keys, created_by_admin, is_global)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (title, message, days_before_exam, json.dumps(exam_keys), admin_id, is_global))
            return cursor.lastrowid

    def get_all_auto_reminders(self) -> List[Dict[str, Any]]:
        """دریافت همه ریمایندرهای خودکار"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM auto_reminders ORDER BY days_before_exam DESC')
            
            reminders = []
            for row in cursor.fetchall():
                reminders.append({
                    'id': row['id'],
                    'title': row['title'],
                    'message': row['message'],
                    'days_before_exam': row['days_before_exam'],
                    'exam_keys': json.loads(row['exam_keys']),
                    'is_active': bool(row['is_active']),
                    'is_global': bool(row['is_global']),
                    'created_by_admin': row['created_by_admin'],
                    'created_at': row['created_at']
                })
            return reminders

    def get_active_auto_reminders(self) -> List[Dict[str, Any]]:
        """دریافت ریمایندرهای خودکار فعال"""
        reminders = self.get_all_auto_reminders()
        return [r for r in reminders if r['is_active']]

    def update_auto_reminder(self, reminder_id: int, **kwargs) -> bool:
        """ویرایش ریمایندر خودکار"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            update_fields = []
            params = []
            
            for key, value in kwargs.items():
                if key == 'exam_keys' and isinstance(value, list):
                    update_fields.append("exam_keys = ?")
                    params.append(json.dumps(value))
                elif key in ['title', 'message', 'days_before_exam', 'is_active', 'is_global']:
                    update_fields.append(f"{key} = ?")
                    params.append(value)
            
            if not update_fields:
                return False
                
            params.append(reminder_id)
            cursor.execute(f'''
                UPDATE auto_reminders 
                SET {', '.join(update_fields)} 
                WHERE id = ?
            ''', params)
            
            return cursor.rowcount > 0

    def delete_auto_reminder(self, reminder_id: int) -> bool:
        """حذف ریمایندر خودکار"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM auto_reminders WHERE id = ?', (reminder_id,))
            return cursor.rowcount > 0

    def get_user_auto_reminders(self, user_id: int) -> List[Dict[str, Any]]:
        """دریافت ریمایندرهای خودکار کاربر"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT uar.*, ar.title, ar.message, ar.days_before_exam, ar.exam_keys
                FROM user_auto_reminders uar
                JOIN auto_reminders ar ON uar.auto_reminder_id = ar.id
                WHERE uar.user_id = ?
            ''', (user_id,))
            
            return [dict(row) for row in cursor.fetchall()]

    def toggle_user_auto_reminder(self, user_id: int, reminder_id: int) -> bool:
        """تغییر وضعیت ریمایندر خودکار برای کاربر"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # بررسی وجود رکورد
            cursor.execute(
                'SELECT * FROM user_auto_reminders WHERE user_id = ? AND auto_reminder_id = ?',
                (user_id, reminder_id)
            )
            existing = cursor.fetchone()
            
            if existing:
                # تغییر وضعیت
                new_status = not bool(existing[3])  # ایندکس 3 مربوط به is_active هست
                cursor.execute(
                    'UPDATE user_auto_reminders SET is_active = ? WHERE user_id = ? AND auto_reminder_id = ?',
                    (new_status, user_id, reminder_id)
                )
            else:
                # افزودن جدید
                cursor.execute(
                    'INSERT INTO user_auto_reminders (user_id, auto_reminder_id, is_active) VALUES (?, ?, ?)',
                    (user_id, reminder_id, True)
                )
            
            conn.commit()
            return True

    def get_users_for_auto_reminder(self, reminder_id: int) -> List[int]:
        """دریافت لیست کاربرانی که این ریمایندر برایشان فعال است"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT user_id FROM user_auto_reminders 
                WHERE auto_reminder_id = ? AND is_active = TRUE
            ''', (reminder_id,))
            
            return [row[0] for row in cursor.fetchall()]

# ایجاد instance اصلی
auto_reminder_system = AutoReminderSystem()
