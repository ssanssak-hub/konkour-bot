import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import jdatetime
from sqlalchemy import and_, func
from database.base import db
from database.models import StudyPlan, StudySession, StudyTimer

logger = logging.getLogger(__name__)

class StudyRepository:
    def __init__(self):
        self.db = db
    
    # ==================== STUDY PLAN OPERATIONS ====================
    
    def add_study_plan(self, user_id: int, title: str, subject: str, plan_type: str,
                      target_hours: float, deadline: str = None, priority: int = 1,
                      color: str = '#3498db', tags: List[str] = None) -> StudyPlan:
        """افزودن برنامه مطالعه جدید"""
        session = self.db.get_session()
        try:
            plan = StudyPlan(
                user_id=user_id,
                title=title,
                subject=subject,
                plan_type=plan_type,
                target_hours=target_hours,
                deadline=deadline,
                priority=priority,
                color=color,
                tags=tags or []
            )
            session.add(plan)
            session.commit()
            logger.info(f"✅ برنامه مطالعه اضافه شد برای کاربر: {user_id}")
            return plan
        except Exception as e:
            session.rollback()
            logger.error(f"❌ خطا در افزودن برنامه مطالعه: {e}")
            raise
        finally:
            self.db.close_session()
    
    def get_user_study_plans(self, user_id: int, active_only: bool = True) -> List[StudyPlan]:
        """دریافت برنامه‌های مطالعه کاربر"""
        session = self.db.get_session()
        try:
            query = session.query(StudyPlan).filter_by(user_id=user_id)
            if active_only:
                query = query.filter_by(is_completed=False)
            return query.order_by(StudyPlan.priority.desc(), StudyPlan.created_at.desc()).all()
        except Exception as e:
            logger.error(f"❌ خطا در دریافت برنامه‌های مطالعه: {e}")
            return []
        finally:
            self.db.close_session()
    
    def get_study_plan(self, plan_id: int) -> Optional[StudyPlan]:
        """دریافت برنامه مطالعه بر اساس ID"""
        session = self.db.get_session()
        try:
            return session.query(StudyPlan).filter_by(id=plan_id).first()
        except Exception as e:
            logger.error(f"❌ خطا در دریافت برنامه مطالعه: {e}")
            return None
        finally:
            self.db.close_session()
    
    def update_study_plan_progress(self, plan_id: int, completed_hours: float) -> bool:
        """بروزرسانی پیشرفت برنامه مطالعه"""
        session = self.db.get_session()
        try:
            plan = session.query(StudyPlan).filter_by(id=plan_id).first()
            if plan:
                plan.completed_hours = completed_hours
                if completed_hours >= plan.target_hours:
                    plan.is_completed = True
                plan.updated_at = datetime.now()
                session.commit()
                logger.info(f"✅ پیشرفت برنامه مطالعه بروزرسانی شد: {plan_id}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"❌ خطا در بروزرسانی پیشرفت برنامه: {e}")
            return False
        finally:
            self.db.close_session()
    
    def delete_study_plan(self, plan_id: int) -> bool:
        """حذف برنامه مطالعه"""
        session = self.db.get_session()
        try:
            plan = session.query(StudyPlan).filter_by(id=plan_id).first()
            if plan:
                session.delete(plan)
                session.commit()
                logger.info(f"✅ برنامه مطالعه حذف شد: {plan_id}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"❌ خطا در حذف برنامه مطالعه: {e}")
            return False
        finally:
            self.db.close_session()
    
    # ==================== STUDY SESSION OPERATIONS ====================
    
    def add_study_session(self, user_id: int, subject: str, duration: float,
                         date: str = None, start_time: str = None, end_time: str = None,
                         notes: str = None, mood: int = None, productivity: int = None) -> StudySession:
        """افزودن جلسه مطالعه"""
        session = self.db.get_session()
        try:
            if not date:
                date = jdatetime.datetime.now().strftime("%Y-%m-%d")
            
            session_obj = StudySession(
                user_id=user_id,
                subject=subject,
                duration=duration,
                date=date,
                start_time=start_time,
                end_time=end_time,
                notes=notes,
                mood=mood,
                productivity=productivity
            )
            session.add(session_obj)
            session.commit()
            logger.info(f"✅ جلسه مطالعه اضافه شد برای کاربر: {user_id}")
            return session_obj
        except Exception as e:
            session.rollback()
            logger.error(f"❌ خطا در افزودن جلسه مطالعه: {e}")
            raise
        finally:
            self.db.close_session()
    
    def get_user_study_sessions(self, user_id: int, days: int = 30) -> List[StudySession]:
        """دریافت جلسات مطالعه کاربر"""
        session = self.db.get_session()
        try:
            start_date = (jdatetime.datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            return session.query(StudySession).filter(
                StudySession.user_id == user_id,
                StudySession.date >= start_date
            ).order_by(StudySession.date.desc(), StudySession.created_at.desc()).all()
        except Exception as e:
            logger.error(f"❌ خطا در دریافت جلسات مطالعه: {e}")
            return []
        finally:
            self.db.close_session()
    
    def get_study_session(self, session_id: int) -> Optional[StudySession]:
        """دریافت جلسه مطالعه بر اساس ID"""
        session = self.db.get_session()
        try:
            return session.query(StudySession).filter_by(id=session_id).first()
        except Exception as e:
            logger.error(f"❌ خطا در دریافت جلسه مطالعه: {e}")
            return None
        finally:
            self.db.close_session()
    
    def delete_study_session(self, session_id: int) -> bool:
        """حذف جلسه مطالعه"""
        session = self.db.get_session()
        try:
            session_obj = session.query(StudySession).filter_by(id=session_id).first()
            if session_obj:
                session.delete(session_obj)
                session.commit()
                logger.info(f"✅ جلسه مطالعه حذف شد: {session_id}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"❌ خطا در حذف جلسه مطالعه: {e}")
            return False
        finally:
            self.db.close_session()
    
    # ==================== STUDY TIME CALCULATIONS ====================
    
    def get_daily_study_time(self, user_id: int, date: str = None) -> float:
        """دریافت مدت مطالعه روزانه"""
        session = self.db.get_session()
        try:
            if not date:
                date = jdatetime.datetime.now().strftime("%Y-%m-%d")
            
            result = session.query(func.sum(StudySession.duration)).filter(
                StudySession.user_id == user_id,
                StudySession.date == date
            ).scalar()
            
            return float(result) if result else 0.0
        except Exception as e:
            logger.error(f"❌ خطا در دریافت مدت مطالعه روزانه: {e}")
            return 0.0
        finally:
            self.db.close_session()
    
    def get_weekly_study_time(self, user_id: int) -> float:
        """دریافت مدت مطالعه هفتگی"""
        session = self.db.get_session()
        try:
            today = jdatetime.datetime.now()
            start_of_week = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
            
            result = session.query(func.sum(StudySession.duration)).filter(
                StudySession.user_id == user_id,
                StudySession.date >= start_of_week
            ).scalar()
            
            return float(result) if result else 0.0
        except Exception as e:
            logger.error(f"❌ خطا در دریافت مدت مطالعه هفتگی: {e}")
            return 0.0
        finally:
            self.db.close_session()
    
    def get_monthly_study_time(self, user_id: int) -> float:
        """دریافت مدت مطالعه ماهانه"""
        session = self.db.get_session()
        try:
            today = jdatetime.datetime.now()
            start_of_month = today.replace(day=1).strftime("%Y-%m-%d")
            
            result = session.query(func.sum(StudySession.duration)).filter(
                StudySession.user_id == user_id,
                StudySession.date >= start_of_month
            ).scalar()
            
            return float(result) if result else 0.0
        except Exception as e:
            logger.error(f"❌ خطا در دریافت مدت مطالعه ماهانه: {e}")
            return 0.0
        finally:
            self.db.close_session()
    
    def get_study_time_by_subject(self, user_id: int, days: int = 30) -> Dict[str, float]:
        """دریافت مدت مطالعه بر اساس درس"""
        session = self.db.get_session()
        try:
            start_date = (jdatetime.datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            
            results = session.query(
                StudySession.subject,
                func.sum(StudySession.duration)
            ).filter(
                StudySession.user_id == user_id,
                StudySession.date >= start_date
            ).group_by(StudySession.subject).all()
            
            return {subject: float(total) for subject, total in results}
        except Exception as e:
            logger.error(f"❌ خطا در دریافت مدت مطالعه بر اساس درس: {e}")
            return {}
        finally:
            self.db.close_session()
    
    # ==================== STUDY TIMER OPERATIONS ====================
    
    def add_study_timer(self, user_id: int, title: str, target_hours: float, subject: str = None) -> StudyTimer:
        """افزودن تایمر مطالعه"""
        session = self.db.get_session()
        try:
            timer = StudyTimer(
                user_id=user_id,
                title=title,
                subject=subject,
                target_hours=target_hours,
                remaining_hours=target_hours
            )
            session.add(timer)
            session.commit()
            logger.info(f"✅ تایمر مطالعه اضافه شد برای کاربر: {user_id}")
            return timer
        except Exception as e:
            session.rollback()
            logger.error(f"❌ خطا در افزودن تایمر مطالعه: {e}")
            raise
        finally:
            self.db.close_session()
    
    def get_user_timers(self, user_id: int, active_only: bool = True) -> List[StudyTimer]:
        """دریافت تایمرهای کاربر"""
        session = self.db.get_session()
        try:
            query = session.query(StudyTimer).filter_by(user_id=user_id)
            if active_only:
                query = query.filter_by(is_active=True)
            return query.order_by(StudyTimer.start_time.desc()).all()
        except Exception as e:
            logger.error(f"❌ خطا در دریافت تایمرها: {e}")
            return []
        finally:
            self.db.close_session()
    
    def get_study_timer(self, timer_id: int) -> Optional[StudyTimer]:
        """دریافت تایمر بر اساس ID"""
        session = self.db.get_session()
        try:
            return session.query(StudyTimer).filter_by(id=timer_id).first()
        except Exception as e:
            logger.error(f"❌ خطا در دریافت تایمر: {e}")
            return None
        finally:
            self.db.close_session()
    
    def update_timer_progress(self, timer_id: int, remaining_hours: float) -> bool:
        """بروزرسانی پیشرفت تایمر"""
        session = self.db.get_session()
        try:
            timer = session.query(StudyTimer).filter_by(id=timer_id).first()
            if timer:
                timer.remaining_hours = remaining_hours
                if remaining_hours <= 0:
                    timer.is_active = False
                    timer.end_time = datetime.now()
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"❌ خطا در بروزرسانی تایمر: {e}")
            return False
        finally:
            self.db.close_session()
    
    def pause_timer(self, timer_id: int) -> bool:
        """توقف تایمر"""
        session = self.db.get_session()
        try:
            timer = session.query(StudyTimer).filter_by(id=timer_id).first()
            if timer and not timer.is_paused:
                timer.is_paused = True
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"❌ خطا در توقف تایمر: {e}")
            return False
        finally:
            self.db.close_session()
    
    def resume_timer(self, timer_id: int) -> bool:
        """ادامه تایمر"""
        session = self.db.get_session()
        try:
            timer = session.query(StudyTimer).filter_by(id=timer_id).first()
            if timer and timer.is_paused:
                timer.is_paused = False
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"❌ خطا در ادامه تایمر: {e}")
            return False
        finally:
            self.db.close_session()
    
    def complete_timer(self, timer_id: int) -> bool:
        """اتمام تایمر"""
        session = self.db.get_session()
        try:
            timer = session.query(StudyTimer).filter_by(id=timer_id).first()
            if timer:
                timer.is_active = False
                timer.remaining_hours = 0
                timer.end_time = datetime.now()
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"❌ خطا در اتمام تایمر: {e}")
            return False
        finally:
            self.db.close_session()
