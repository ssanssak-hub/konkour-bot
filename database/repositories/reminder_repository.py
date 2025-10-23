import logging
from typing import List, Optional
from datetime import datetime
from database.base import db
from database.models import Reminder

logger = logging.getLogger(__name__)

class ReminderRepository:
    def __init__(self):
        self.db = db
    
    def add_reminder(self, user_id: int, reminder_type: str, reminder_time: str,
                    title: str = None, exam_name: str = None, custom_message: str = None,
                    days_of_week: List[int] = None, is_recurring: bool = True) -> Reminder:
        """افزودن یادآوری"""
        session = self.db.get_session()
        try:
            reminder = Reminder(
                user_id=user_id,
                reminder_type=reminder_type,
                title=title,
                exam_name=exam_name,
                custom_message=custom_message,
                reminder_time=reminder_time,
                days_of_week=days_of_week or list(range(7)),
                is_recurring=is_recurring
            )
            session.add(reminder)
            session.commit()
            logger.info(f"✅ یادآوری اضافه شد برای کاربر: {user_id}")
            return reminder
        except Exception as e:
            session.rollback()
            logger.error(f"❌ خطا در افزودن یادآوری: {e}")
            raise
        finally:
            self.db.close_session()
    
    def get_user_reminders(self, user_id: int, active_only: bool = True) -> List[Reminder]:
        """دریافت یادآوری‌های کاربر"""
        session = self.db.get_session()
        try:
            query = session.query(Reminder).filter_by(user_id=user_id)
            if active_only:
                query = query.filter_by(is_active=True)
            return query.order_by(Reminder.reminder_time).all()
        except Exception as e:
            logger.error(f"❌ خطا در دریافت یادآوری‌ها: {e}")
            return []
        finally:
            self.db.close_session()
    
    def get_reminder(self, reminder_id: int) -> Optional[Reminder]:
        """دریافت یادآوری بر اساس ID"""
        session = self.db.get_session()
        try:
            return session.query(Reminder).filter_by(id=reminder_id).first()
        except Exception as e:
            logger.error(f"❌ خطا در دریافت یادآوری: {e}")
            return None
        finally:
            self.db.close_session()
    
    def get_active_reminders(self) -> List[Reminder]:
        """دریافت تمام یادآوری‌های فعال"""
        session = self.db.get_session()
        try:
            return session.query(Reminder).filter_by(is_active=True).all()
        except Exception as e:
            logger.error(f"❌ خطا در دریافت یادآوری‌های فعال: {e}")
            return []
        finally:
            self.db.close_session()
    
    def get_reminders_by_type(self, reminder_type: str, active_only: bool = True) -> List[Reminder]:
        """دریافت یادآوری‌ها بر اساس نوع"""
        session = self.db.get_session()
        try:
            query = session.query(Reminder).filter_by(reminder_type=reminder_type)
            if active_only:
                query = query.filter_by(is_active=True)
            return query.all()
        except Exception as e:
            logger.error(f"❌ خطا در دریافت یادآوری‌ها بر اساس نوع: {e}")
            return []
        finally:
            self.db.close_session()
    
    def toggle_reminder(self, reminder_id: int) -> bool:
        """تغییر وضعیت فعال/غیرفعال یادآوری"""
        session = self.db.get_session()
        try:
            reminder = session.query(Reminder).filter_by(id=reminder_id).first()
            if reminder:
                reminder.is_active = not reminder.is_active
                session.commit()
                logger.info(f"✅ وضعیت یادآوری تغییر کرد: {reminder_id}")
                return reminder.is_active
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"❌ خطا در تغییر وضعیت یادآوری: {e}")
            return False
        finally:
            self.db.close_session()
    
    def activate_reminder(self, reminder_id: int) -> bool:
        """فعال کردن یادآوری"""
        session = self.db.get_session()
        try:
            reminder = session.query(Reminder).filter_by(id=reminder_id).first()
            if reminder:
                reminder.is_active = True
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"❌ خطا در فعال کردن یادآوری: {e}")
            return False
        finally:
            self.db.close_session()
    
    def deactivate_reminder(self, reminder_id: int) -> bool:
        """غیرفعال کردن یادآوری"""
        session = self.db.get_session()
        try:
            reminder = session.query(Reminder).filter_by(id=reminder_id).first()
            if reminder:
                reminder.is_active = False
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"❌ خطا در غیرفعال کردن یادآوری: {e}")
            return False
        finally:
            self.db.close_session()
    
    def delete_reminder(self, reminder_id: int) -> bool:
        """حذف یادآوری"""
        session = self.db.get_session()
        try:
            reminder = session.query(Reminder).filter_by(id=reminder_id).first()
            if reminder:
                session.delete(reminder)
                session.commit()
                logger.info(f"✅ یادآوری حذف شد: {reminder_id}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"❌ خطا در حذف یادآوری: {e}")
            return False
        finally:
            self.db.close_session()
    
    def update_reminder_time(self, reminder_id: int, new_time: str) -> bool:
        """بروزرسانی زمان یادآوری"""
        session = self.db.get_session()
        try:
            reminder = session.query(Reminder).filter_by(id=reminder_id).first()
            if reminder:
                reminder.reminder_time = new_time
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"❌ خطا در بروزرسانی زمان یادآوری: {e}")
            return False
        finally:
            self.db.close_session()
    
    def update_reminder_message(self, reminder_id: int, new_message: str) -> bool:
        """بروزرسانی پیام یادآوری"""
        session = self.db.get_session()
        try:
            reminder = session.query(Reminder).filter_by(id=reminder_id).first()
            if reminder:
                reminder.custom_message = new_message
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"❌ خطا در بروزرسانی پیام یادآوری: {e}")
            return False
        finally:
            self.db.close_session()
    
    def mark_reminder_triggered(self, reminder_id: int) -> bool:
        """علامت‌گذاری یادآوری به عنوان اجرا شده"""
        session = self.db.get_session()
        try:
            reminder = session.query(Reminder).filter_by(id=reminder_id).first()
            if reminder:
                reminder.last_triggered = datetime.now()
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"❌ خطا در علامت‌گذاری یادآوری: {e}")
            return False
        finally:
            self.db.close_session()
    
    def get_due_reminders(self, current_time: str) -> List[Reminder]:
        """دریافت یادآوری‌های زمان رسیده"""
        session = self.db.get_session()
        try:
            return session.query(Reminder).filter(
                Reminder.reminder_time == current_time,
                Reminder.is_active == True
            ).all()
        except Exception as e:
            logger.error(f"❌ خطا در دریافت یادآوری‌های زمان رسیده: {e}")
            return []
        finally:
            self.db.close_session()
    
    def get_user_reminder_count(self, user_id: int, active_only: bool = True) -> int:
        """دریافت تعداد یادآوری‌های کاربر"""
        session = self.db.get_session()
        try:
            query = session.query(Reminder).filter_by(user_id=user_id)
            if active_only:
                query = query.filter_by(is_active=True)
            return query.count()
        except Exception as e:
            logger.error(f"❌ خطا در دریافت تعداد یادآوری‌ها: {e}")
            return 0
        finally:
            self.db.close_session()
