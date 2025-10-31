"""
پکیج سیستم ریمایندر
"""

from .reminder_database import reminder_db
from .reminder_handlers import (
    reminder_main_handler,
    start_exam_reminder,
    process_exam_selection,
    process_days_selection,
    process_time_input,
    process_start_date,
    process_end_date,
    process_confirmation,
    start_personal_reminder,
    process_personal_title,
    process_personal_message,
    start_auto_reminders,
    list_auto_reminders,
    manage_reminders_handler,
    view_all_reminders,
    ExamReminderStates,
    PersonalReminderStates,
    ManagementStates
)
from .reminder_keyboards import (
    create_reminder_main_menu,
    create_exam_selection_menu,
    create_days_selection_menu,
    create_time_input_menu,
    create_date_input_menu,
    create_repetition_type_menu,
    create_confirmation_menu,
    create_management_menu,
    create_auto_reminders_menu,
    create_back_only_menu,
    remove_menu
)
from .reminder_scheduler import ReminderScheduler, init_reminder_scheduler
from .reminder_utils import (
    validator,
    formatter,
    time_converter,
    analyzer,
    setup_reminder_system
)

__all__ = [
    # دیتابیس
    'reminder_db',
    
    # هندلرها
    'reminder_main_handler',
    'start_exam_reminder',
    'process_exam_selection', 
    'process_days_selection',
    'process_time_input',
    'process_start_date',
    'process_end_date',
    'process_confirmation',
    'start_personal_reminder',
    'process_personal_title',
    'process_personal_message',
    'start_auto_reminders',
    'list_auto_reminders',
    'manage_reminders_handler',
    'view_all_reminders',
    'ExamReminderStates',
    'PersonalReminderStates',
    'ManagementStates',
    
    # کیبوردها
    'create_reminder_main_menu',
    'create_exam_selection_menu',
    'create_days_selection_menu',
    'create_time_input_menu',
    'create_date_input_menu',
    'create_repetition_type_menu',
    'create_confirmation_menu',
    'create_management_menu',
    'create_auto_reminders_menu',
    'create_back_only_menu',
    'remove_menu',
    
    # زمان‌بندی
    'ReminderScheduler',
    'init_reminder_scheduler',
    
    # ابزارها
    'validator',
    'formatter', 
    'time_converter',
    'analyzer',
    'setup_reminder_system'
]

"""
پکیج سیستم ریمایندر - شامل همه ماژول‌های ریمایندر
"""

from .reminder_database import reminder_db
from .reminder_scheduler import reminder_scheduler
from .auto_reminder_system import auto_reminder_system
from .auto_reminder_scheduler import auto_reminder_scheduler
from .advanced_reminder_scheduler import advanced_reminder_scheduler

def setup_reminder_system(bot):
    """راه‌اندازی کلی سیستم ریمایندر"""
    from .reminder_scheduler import ReminderScheduler
    return ReminderScheduler(bot)

__all__ = [
    'reminder_db',
    'reminder_scheduler', 
    'auto_reminder_system',
    'auto_reminder_scheduler',
    'advanced_reminder_scheduler',
    'setup_reminder_system'
]
