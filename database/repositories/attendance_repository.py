import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import jdatetime
from sqlalchemy import func
from database.base import db
from database.models import Attendance

logger = logging.getLogger(__name__)

class AttendanceRepository:
    def __init__(self):
        self.db = db
    
    def record_attendance(self, user_id: int, check_in_time: str = None, 
                         check_out_time: str = None, notes: str = None) -> Attendance:
        """ثبت حضور کاربر"""
        session = self.db.get_session()
        try:
            today = jdatetime.datetime.now().strftime("%Y-%m-%d")
            current_time = datetime.now().strftime("%H:%M:%S")
            
            # بررسی آیا کاربر امروز حضور داشته یا نه
            existing = session.query(Attendance).filter_by(
                user_id=user_id, date=today
            ).first()
            
            if existing:
                # بروزرسانی خروج
                if check_out_time:
                    existing.check_out_time = check_out_time
                else:
                    existing.check_out_time = current_time
                
                # محاسبه مدت زمان
                if existing.check_in_time and existing.check_out_time:
                    check_in = datetime.strptime(existing.check_in_time, "%H:%M:%S")
                    check_out = datetime.strptime(existing.check_out_time, "%H:%M:%S")
                    existing.duration_minutes = int((check_out - check_in).total_seconds() / 60)
                
                existing.notes = notes or existing.notes
                attendance = existing
            else:
                # ثبت حضور جدید
                attendance = Attendance(
                    user_id=user_id,
                    date=today,
                    check_in_time=check_in_time or current_time,
                    check_out_time=check_out_time,
                    notes=notes
                )
                session.add(attendance)
            
            session.commit()
            logger.info(f"✅ حضور ثبت شد برای کاربر: {user_id}")
            return attendance
        except Exception as e:
            session.rollback()
            logger.error(f"❌ خطا در ثبت حضور: {e}")
            raise
        finally:
            self.db.close_session()
    
    def get_today_attendance_count(self) -> int:
        """دریافت تعداد حضورهای امروز"""
        session = self.db.get_session()
        try:
            today = jdatetime.datetime.now().strftime("%Y-%m-%d")
            return session.query(Attendance).filter_by(date=today).count()
        except Exception as e:
            logger.error(f"❌ خطا در دریافت تعداد حضور: {e}")
            return 0
        finally:
            self.db.close_session()
    
    def get_user_attendance_stats(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """دریافت آمار حضور کاربر"""
        session = self.db.get_session()
        try:
            start_date = (jdatetime.datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            
            # تعداد روزهای حضور
            attendance_days = session.query(Attendance).filter(
                Attendance.user_id == user_id,
                Attendance.date >= start_date
            ).distinct(Attendance.date).count()
            
            # مجموع دقایق مطالعه
            total_minutes_result = session.query(func.sum(Attendance.duration_minutes)).filter(
                Attendance.user_id == user_id,
                Attendance.date >= start_date
            ).scalar()
            total_minutes = total_minutes_result or 0
            
            # آخرین حضور
            last_attendance = session.query(Attendance).filter(
                Attendance.user_id == user_id
            ).order_by(Attendance.date.desc()).first()
            
            # بیشترین مدت مطالعه در یک روز
            max_daily_minutes_result = session.query(func.max(Attendance.duration_minutes)).filter(
                Attendance.user_id == user_id,
                Attendance.date >= start_date
            ).scalar()
            max_daily_minutes = max_daily_minutes_result or 0
            
            # میانگین مدت مطالعه روزانه
            avg_daily_minutes = total_minutes / attendance_days if attendance_days > 0 else 0
            
            return {
                'attendance_days': attendance_days,
                'total_minutes': total_minutes,
                'total_hours': round(total_minutes / 60, 2),
                'last_attendance': last_attendance.date if last_attendance else None,
                'attendance_rate': round((attendance_days / days) * 100, 2) if days > 0 else 0,
                'max_daily_minutes': max_daily_minutes,
                'avg_daily_minutes': round(avg_daily_minutes, 2)
            }
        except Exception as e:
            logger.error(f"❌ خطا در دریافت آمار حضور: {e}")
            return {}
        finally:
            self.db.close_session()
    
    def get_user_attendance_history(self, user_id: int, days: int = 30) -> List[Attendance]:
        """دریافت تاریخچه حضور کاربر"""
        session = self.db.get_session()
        try:
            start_date = (jdatetime.datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            return session.query(Attendance).filter(
                Attendance.user_id == user_id,
                Attendance.date >= start_date
            ).order_by(Attendance.date.desc()).all()
        except Exception as e:
            logger.error(f"❌ خطا در دریافت تاریخچه حضور: {e}")
            return []
        finally:
            self.db.close_session()
    
    def get_attendance_by_date(self, user_id: int, date: str) -> Optional[Attendance]:
        """دریافت حضور کاربر در تاریخ مشخص"""
        session = self.db.get_session()
        try:
            return session.query(Attendance).filter_by(
                user_id=user_id,
                date=date
            ).first()
        except Exception as e:
            logger.error(f"❌ خطا در دریافت حضور: {e}")
            return None
        finally:
            self.db.close_session()
    
    def get_todays_attendance(self, user_id: int) -> Optional[Attendance]:
        """دریافت حضور امروز کاربر"""
        session = self.db.get_session()
        try:
            today = jdatetime.datetime.now().strftime("%Y-%m-%d")
            return session.query(Attendance).filter_by(
                user_id=user_id,
                date=today
            ).first()
        except Exception as e:
            logger.error(f"❌ خطا در دریافت حضور امروز: {e}")
            return None
        finally:
            self.db.close_session()
    
    def get_attendance_count_by_date(self, date: str) -> int:
        """دریافت تعداد حضورها در تاریخ مشخص"""
        session = self.db.get_session()
        try:
            return session.query(Attendance).filter_by(date=date).count()
        except Exception as e:
            logger.error(f"❌ خطا در دریافت تعداد حضور: {e}")
            return 0
        finally:
            self.db.close_session()
    
    def get_daily_attendance_stats(self, days: int = 7) -> Dict[str, int]:
        """دریافت آمار حضور روزانه"""
        session = self.db.get_session()
        try:
            stats = {}
            for i in range(days):
                date = (jdatetime.datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                count = session.query(Attendance).filter_by(date=date).count()
                stats[date] = count
            return stats
        except Exception as e:
            logger.error(f"❌ خطا در دریافت آمار حضور روزانه: {e}")
            return {}
        finally:
            self.db.close_session()
    
    def get_top_attendance_users(self, days: int = 30, limit: int = 10) -> List[Dict[str, Any]]:
        """دریافت کاربران برتر از نظر حضور"""
        session = self.db.get_session()
        try:
            start_date = (jdatetime.datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            
            from database.models import User
            results = session.query(
                User.user_id,
                User.first_name,
                User.username,
                func.count(Attendance.id).label('attendance_count')
            ).join(
                Attendance, User.user_id == Attendance.user_id
            ).filter(
                Attendance.date >= start_date
            ).group_by(
                User.user_id, User.first_name, User.username
            ).order_by(
                func.count(Attendance.id).desc()
            ).limit(limit).all()
            
            return [
                {
                    'user_id': user_id,
                    'first_name': first_name,
                    'username': username,
                    'attendance_count': attendance_count
                }
                for user_id, first_name, username, attendance_count in results
            ]
        except Exception as e:
            logger.error(f"❌ خطا در دریافت کاربران برتر: {e}")
            return []
        finally:
            self.db.close_session()
    
    def delete_attendance(self, attendance_id: int) -> bool:
        """حذف رکورد حضور"""
        session = self.db.get_session()
        try:
            attendance = session.query(Attendance).filter_by(id=attendance_id).first()
            if attendance:
                session.delete(attendance)
                session.commit()
                logger.info(f"✅ رکورد حضور حذف شد: {attendance_id}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"❌ خطا در حذف رکورد حضور: {e}")
            return False
        finally:
            self.db.close_session()
    
    def update_attendance_notes(self, attendance_id: int, notes: str) -> bool:
        """بروزرسانی یادداشت‌های حضور"""
        session = self.db.get_session()
        try:
            attendance = session.query(Attendance).filter_by(id=attendance_id).first()
            if attendance:
                attendance.notes = notes
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"❌ خطا در بروزرسانی یادداشت‌ها: {e}")
            return False
        finally:
            self.db.close_session()
