"""
🎮 handlers package برای ربات کنکور
"""

from .main_menu import setup_main_menu_handlers
from .countdown import setup_countdown_handlers
from .calendar import setup_calendar_handlers
from .reminders import setup_reminders_handlers
from .messages import setup_messages_handlers
from .attendance import setup_attendance_handlers
from .study_plan import setup_study_plan_handlers
from .statistics import setup_statistics_handlers
from .help import setup_help_handlers
from .admin import setup_admin_handlers

__all__ = [
    'setup_main_menu_handlers',
    'setup_countdown_handlers',
    'setup_calendar_handlers', 
    'setup_reminders_handlers',
    'setup_messages_handlers',
    'setup_attendance_handlers',
    'setup_study_plan_handlers',
    'setup_statistics_handlers',
    'setup_help_handlers',
    'setup_admin_handlers'
]
