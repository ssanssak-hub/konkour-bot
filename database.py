"""
دیتابیس SQLite برای ربات کنکور
"""
import sqlite3
import logging
from datetime import datetime, date
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path="konkour_bot.db"):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_db(self):
        """ایجاد جداول دیتابیس"""
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
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
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
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # جدول کانال‌های اجباری
            conn.execute('''
                CREATE TABLE IF NOT EXISTS mandatory_channels (
                    channel_id INTEGER PRIMARY KEY,
                    channel_username TEXT,
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
                    PRIMARY KEY (user_id, channel_id)
                )
            ''')
            
            conn.commit()
        logger.info("✅ دیتابیس راه‌اندازی شد")
    
    def add_user(self, user_id: int, username: str, first_name: str, last_name: str = ""):
        """افزودن کاربر جدید"""
        with self.get_connection() as conn:
            conn.execute('''
                INSERT OR REPLACE INTO users (user_id, username, first_name, last_name, last_active)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, username, first_name, last_name))
            conn.commit()
    
    def update_user_activity(self, user_id: int):
        """بروزرسانی زمان فعالیت کاربر"""
        with self.get_connection() as conn:
            conn.execute('''
                UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE user_id = ?
            ''', (user_id,))
            conn.commit()
    
    def add_study_session(self, user_id: int, subject: str, topic: str, duration_minutes: int, study_date: str = None):
        """افزودن جلسه مطالعه"""
        if study_date is None:
            study_date = date.today().isoformat()
        
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO study_plans (user_id, subject, topic, duration_minutes, study_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, subject, topic, duration_minutes, study_date))
            conn.commit()
    
    def get_today_study_stats(self, user_id: int) -> Dict[str, Any]:
        """دریافت آمار مطالعه امروز"""
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
    
    def get_weekly_stats(self, user_id: int) -> List[Dict[str, Any]]:
        """دریافت آمار مطالعه هفته جاری"""
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
    
    def add_mandatory_channel(self, channel_id: int, channel_username: str, channel_title: str, admin_id: int):
        """افزودن کانال اجباری"""
        with self.get_connection() as conn:
            conn.execute('''
                INSERT OR REPLACE INTO mandatory_channels (channel_id, channel_username, channel_title, added_by)
                VALUES (?, ?, ?, ?)
            ''', (channel_id, channel_username, channel_title, admin_id))
            conn.commit()
    
    def get_mandatory_channels(self) -> List[Dict[str, Any]]:
        """دریافت لیست کانال‌های اجباری"""
        with self.get_connection() as conn:
            cursor = conn.execute('''
                SELECT channel_id, channel_username, channel_title 
                FROM mandatory_channels
            ''')
            
            return [
                {'channel_id': row[0], 'channel_username': row[1], 'channel_title': row[2]}
                for row in cursor.fetchall()
            ]
    
    def check_channel_membership(self, user_id: int, channel_id: int) -> bool:
        """بررسی عضویت کاربر در کانال"""
        with self.get_connection() as conn:
            cursor = conn.execute('''
                SELECT is_member FROM channel_memberships 
                WHERE user_id = ? AND channel_id = ?
            ''', (user_id, channel_id))
            
            result = cursor.fetchone()
            return result[0] if result else False
    
    def update_channel_membership(self, user_id: int, channel_id: int, is_member: bool):
        """بروزرسانی وضعیت عضویت کاربر"""
        with self.get_connection() as conn:
            conn.execute('''
                INSERT OR REPLACE INTO channel_memberships (user_id, channel_id, is_member, last_checked)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, channel_id, is_member))
            conn.commit()
    
    def get_user_progress(self, user_id: int) -> Dict[str, Any]:
        """دریافت پیشرفت کلی کاربر"""
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
            
            return {
                'total_minutes': total_minutes,
                'total_hours': round(total_minutes / 60, 1),
                'total_sessions': total_sessions,
                'active_days': active_days
            }
