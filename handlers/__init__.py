"""
🎮 handlers package برای ربات کنکور
"""
from .main_menu import *
from .countdown import *
from .calendar import *
from .reminders import *
from .attendance import *
from .study_plan import *
from .statistics import *
from .help import *
from .admin import *

__all__ = [
    'setup_main_handlers',
    'countdown_handler',
    'calendar_handler', 
    'reminder_handler',
    'attendance_handler',
    'study_plan_handler',
    'statistics_handler',
    'help_handler',
    'admin_handler'
]
