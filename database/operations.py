import logging
from typing import List, Dict, Any, Optional
from .base import db
from .repositories import (
    UserRepository,
    StudyRepository,
    ReminderRepository,
    AttendanceRepository,
    MessageRepository
)

logger = logging.getLogger(__name__)

class DatabaseOperations:
    def __init__(self):
        self.user_repo = UserRepository()
        self.study_repo = StudyRepository()
        self.reminder_repo = ReminderRepository()
        self.attendance_repo = AttendanceRepository()
        self.message_repo = MessageRepository()
    
    # ==================== USER OPERATIONS ====================
    
    def add_user(self, user_id: int, username: str = None, first_name: str = None, 
                 last_name: str = None, phone_number: str = None):
        return self.user_repo.add_user(user_id, username, first_name, last_name, phone_number)
    
    def get_user(self, user_id: int):
        return self.user_repo.get_user(user_id)
    
    def get_all_users(self, active_only: bool = True):
        return self.user_repo.get_all_users(active_only)
    
    def update_user_last_active(self, user_id: int):
        return self.user_repo.update_user_last_active(user_id)
    
    def deactivate_user(self, user_id: int):
        return self.user_repo.deactivate_user(user_id)
    
    # ==================== ATTENDANCE OPERATIONS ====================
    
    def record_attendance(self, user_id: int, check_in_time: str = None, 
                         check_out_time: str = None, notes: str = None):
        return self.attendance_repo.record_attendance(user_id, check_in_time, check_out_time, notes)
    
    def get_today_attendance_count(self):
        return self.attendance_repo.get_today_attendance_count()
    
    def get_user_attendance_stats(self, user_id: int, days: int = 30):
        return self.attendance_repo.get_user_attendance_stats(user_id, days)
    
    # ==================== STUDY OPERATIONS ====================
    
    def add_study_plan(self, user_id: int, title: str, subject: str, plan_type: str,
                      target_hours: float, deadline: str = None, priority: int = 1,
                      color: str = '#3498db', tags: List[str] = None):
        return self.study_repo.add_study_plan(user_id, title, subject, plan_type, target_hours, 
                                            deadline, priority, color, tags)
    
    def get_user_study_plans(self, user_id: int, active_only: bool = True):
        return self.study_repo.get_user_study_plans(user_id, active_only)
    
    def update_study_plan_progress(self, plan_id: int, completed_hours: float):
        return self.study_repo.update_study_plan_progress(plan_id, completed_hours)
    
    def add_study_session(self, user_id: int, subject: str, duration: float,
                         date: str = None, start_time: str = None, end_time: str = None,
                         notes: str = None, mood: int = None, productivity: int = None):
        return self.study_repo.add_study_session(user_id, subject, duration, date, 
                                               start_time, end_time, notes, mood, productivity)
    
    def get_user_study_sessions(self, user_id: int, days: int = 30):
        return self.study_repo.get_user_study_sessions(user_id, days)
    
    def get_daily_study_time(self, user_id: int, date: str = None):
        return self.study_repo.get_daily_study_time(user_id, date)
    
    def get_weekly_study_time(self, user_id: int):
        return self.study_repo.get_weekly_study_time(user_id)
    
    def get_monthly_study_time(self, user_id: int):
        return self.study_repo.get_monthly_study_time(user_id)
    
    # ==================== REMINDER OPERATIONS ====================
    
    def add_reminder(self, user_id: int, reminder_type: str, reminder_time: str,
                    title: str = None, exam_name: str = None, custom_message: str = None,
                    days_of_week: List[int] = None, is_recurring: bool = True):
        return self.reminder_repo.add_reminder(user_id, reminder_type, reminder_time, title,
                                             exam_name, custom_message, days_of_week, is_recurring)
    
    def get_user_reminders(self, user_id: int, active_only: bool = True):
        return self.reminder_repo.get_user_reminders(user_id, active_only)
    
    def get_active_reminders(self):
        return self.reminder_repo.get_active_reminders()
    
    def toggle_reminder(self, reminder_id: int):
        return self.reminder_repo.toggle_reminder(reminder_id)
    
    def delete_reminder(self, reminder_id: int):
        return self.reminder_repo.delete_reminder(reminder_id)
    
    # ==================== MESSAGE OPERATIONS ====================
    
    def add_user_message(self, user_id: int, message_text: str, message_type: str = 'general'):
        return self.message_repo.add_user_message(user_id, message_text, message_type)
    
    def get_pending_messages(self):
        return self.message_repo.get_pending_messages()
    
    def get_user_messages(self, user_id: int):
        return self.message_repo.get_user_messages(user_id)
    
    # ==================== TIMER OPERATIONS ====================
    
    def add_study_timer(self, user_id: int, title: str, target_hours: float, subject: str = None):
        return self.study_repo.add_study_timer(user_id, title, target_hours, subject)
    
    def get_user_timers(self, user_id: int, active_only: bool = True):
        return self.study_repo.get_user_timers(user_id, active_only)
    
    def update_timer_progress(self, timer_id: int, remaining_hours: float):
        return self.study_repo.update_timer_progress(timer_id, remaining_hours)
    
    # ==================== STATISTICS OPERATIONS ====================
    
    def get_user_statistics(self, user_id: int):
        """دریافت آمار کامل کاربر"""
        try:
            attendance_stats = self.get_user_attendance_stats(user_id, 30)
            daily_time = self.get_daily_study_time(user_id)
            weekly_time = self.get_weekly_study_time(user_id)
            monthly_time = self.get_monthly_study_time(user_id)
            
            study_sessions = self.get_user_study_sessions(user_id, 30)
            total_sessions = len(study_sessions)
            total_study_time = sum(session.duration for session in study_sessions)
            
            study_plans = self.get_user_study_plans(user_id, active_only=True)
            completed_plans = len([p for p in study_plans if p.is_completed])
            total_plans = len(study_plans)
            
            return {
                'attendance': attendance_stats,
                'study_time': {
                    'daily': daily_time,
                    'weekly': weekly_time,
                    'monthly': monthly_time,
                    'total_30_days': total_study_time
                },
                'sessions': {
                    'total': total_sessions,
                    'average_duration': total_study_time / total_sessions if total_sessions > 0 else 0
                },
                'plans': {
                    'total': total_plans,
                    'completed': completed_plans,
                    'completion_rate': (completed_plans / total_plans * 100) if total_plans > 0 else 0
                }
            }
        except Exception as e:
            logger.error(f"❌ خطا در دریافت آمار کاربر: {e}")
            return {}
    
    def get_system_statistics(self):
        """دریافت آمار کلی سیستم"""
        try:
            total_users = len(self.get_all_users(active_only=False))
            active_users = len(self.get_all_users(active_only=True))
            today_attendance = self.get_today_attendance_count()
            
            # سایر آمارها...
            return {
                'total_users': total_users,
                'active_users': active_users,
                'today_attendance': today_attendance
            }
        except Exception as e:
            logger.error(f"❌ خطا در دریافت آمار سیستم: {e}")
            return {}
    
    def close(self):
        """بستن اتصال به دیتابیس"""
        db.close()

# ایجاد نمونه global
database = DatabaseOperations()
