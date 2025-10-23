import logging
import os
import shutil
from datetime import datetime, timedelta
from typing import Dict, Any
from database.base import db
from database.models import SystemLog

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.db = db
    
    def backup_database(self, backup_path: str = None) -> bool:
        """پشتیبان‌گیری از دیتابیس"""
        try:
            if not backup_path:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = f"backups/konkur_bot_backup_{timestamp}.db"
            
            # ایجاد پوشه backups اگر وجود ندارد
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            # برای SQLite می‌توان از کپی فایل استفاده کرد
            if 'sqlite' in self.db.database_url:
                original_db = self.db.database_url.replace('sqlite:///', '')
                if os.path.exists(original_db):
                    shutil.copy2(original_db, backup_path)
                    self._log_system_event('BACKUP', f"پشتیبان‌گیری انجام شد: {backup_path}")
                    logger.info(f"✅ پشتیبان‌گیری انجام شد: {backup_path}")
                    return True
                else:
                    logger.error("❌ فایل دیتابیس اصلی یافت نشد")
                    return False
            else:
                logger.warning("⚠️ پشتیبان‌گیری برای این نوع دیتابیس پیاده‌سازی نشده است")
                return False
        except Exception as e:
            logger.error(f"❌ خطا در پشتیبان‌گیری: {e}")
            self._log_system_event('BACKUP_ERROR', f"خطا در پشتیبان‌گیری: {e}")
            return False
    
    def cleanup_old_data(self, days: int = 90) -> Dict[str, int]:
        """پاکسازی داده‌های قدیمی"""
        session = self.db.get_session()
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            from database.models import StudySession, Attendance, SystemLog
            
            # پاکسازی session های قدیمی
            old_sessions = session.query(StudySession).filter(StudySession.date < cutoff_date).delete()
            
            # پاکسازی حضور و غیاب قدیمی
            old_attendance = session.query(Attendance).filter(Attendance.date < cutoff_date).delete()
            
            # پاکسازی لاگ‌های قدیمی (نگهداری 30 روز)
            log_cutoff = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            old_logs = session.query(SystemLog).filter(SystemLog.created_at < log_cutoff).delete()
            
            session.commit()
            
            result = {
                'old_sessions_deleted': old_sessions,
                'old_attendance_deleted': old_attendance,
                'old_logs_deleted': old_logs
            }
            
            self._log_system_event('CLEANUP', f"پاکسازی داده‌های قدیمی: {result}")
            logger.info(f"✅ پاکسازی داده‌های قدیمی انجام شد: {result}")
            return result
        except Exception as e:
            session.rollback()
            logger.error(f"❌ خطا در پاکسازی داده‌های قدیمی: {e}")
            self._log_system_event('CLEANUP_ERROR', f"خطا در پاکسازی: {e}")
            return {}
        finally:
            self.db.close_session()
    
    def optimize_database(self) -> bool:
        """بهینه‌سازی دیتابیس"""
        try:
            if 'sqlite' in self.db.database_url:
                session = self.db.get_session()
                session.execute("VACUUM;")
                session.commit()
                self.db.close_session()
                
                self._log_system_event('OPTIMIZE', "دیتابیس بهینه‌سازی شد")
                logger.info("✅ دیتابیس بهینه‌سازی شد")
                return True
            else:
                logger.info("⚠️ بهینه‌سازی برای این نوع دیتابیس لازم نیست")
                return True
        except Exception as e:
            logger.error(f"❌ خطا در بهینه‌سازی دیتابیس: {e}")
            self._log_system_event('OPTIMIZE_ERROR', f"خطا در بهینه‌سازی: {e}")
            return False
    
    def get_database_info(self) -> Dict[str, Any]:
        """دریافت اطلاعات دیتابیس"""
        try:
            session = self.db.get_session()
            
            from database.models import User, StudySession, Attendance, Reminder, UserMessage
            
            info = {
                'total_users': session.query(User).count(),
                'active_users': session.query(User).filter_by(is_active=True).count(),
                'total_study_sessions': session.query(StudySession).count(),
                'total_attendance': session.query(Attendance).count(),
                'total_reminders': session.query(Reminder).count(),
                'total_messages': session.query(UserMessage).count(),
                'pending_messages': session.query(UserMessage).filter_by(status='pending').count(),
                'database_size': self._get_database_size()
            }
            
            self.db.close_session()
            return info
        except Exception as e:
            logger.error(f"❌ خطا در دریافت اطلاعات دیتابیس: {e}")
            return {}
    
    def _get_database_size(self) -> str:
        """دریافت حجم دیتابیس"""
        try:
            if 'sqlite' in self.db.database_url:
                db_file = self.db.database_url.replace('sqlite:///', '')
                if os.path.exists(db_file):
                    size_bytes = os.path.getsize(db_file)
                    size_mb = size_bytes / (1024 * 1024)
                    return f"{size_mb:.2f} MB"
            return "نامشخص"
        except Exception as e:
            logger.error(f"❌ خطا در دریافت حجم دیتابیس: {e}")
            return "نامشخص"
    
    def _log_system_event(self, level: str, message: str, user_id: int = None):
        """ثبت رویداد سیستم"""
        session = self.db.get_session()
        try:
            log = SystemLog(
                level=level,
                module='DATABASE_MANAGER',
                message=message,
                user_id=user_id
            )
            session.add(log)
            session.commit()
        except Exception as e:
            logger.error(f"❌ خطا در ثبت رویداد سیستم: {e}")
        finally:
            self.db.close_session()
    
    def health_check(self) -> Dict[str, Any]:
        """بررسی سلامت دیتابیس"""
        try:
            session = self.db.get_session()
            
            # تست اتصال با یک query ساده
            user_count = session.query(User).count()
            
            # بررسی وجود جداول اصلی
            from sqlalchemy import inspect
            inspector = inspect(self.db.engine)
            tables = inspector.get_table_names()
            
            required_tables = ['users', 'study_sessions', 'attendance', 'reminders']
            missing_tables = [table for table in required_tables if table not in tables]
            
            health_status = {
                'database_connection': 'healthy',
                'total_tables': len(tables),
                'missing_tables': missing_tables,
                'user_count': user_count,
                'timestamp': datetime.now().isoformat()
            }
            
            if missing_tables:
                health_status['database_connection'] = 'degraded'
                health_status['message'] = f'جداول مفقوده: {missing_tables}'
            
            self.db.close_session()
            return health_status
        except Exception as e:
            logger.error(f"❌ خطا در بررسی سلامت دیتابیس: {e}")
            return {
                'database_connection': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

# ایجاد نمونه global
db_manager = DatabaseManager()
