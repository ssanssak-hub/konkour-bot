"""
پکیج سیستم ریمایندر - نسخه کامل و یکپارچه
"""

# =============================================================================
# ایمپورت ماژول‌های اصلی ریمایندر
# =============================================================================

from .reminder_database import reminder_db
from .reminder_scheduler import reminder_scheduler, ReminderScheduler, init_reminder_scheduler
from .auto_reminder_system import auto_reminder_system
from .auto_reminder_scheduler import auto_reminder_scheduler
from .advanced_reminder_scheduler import advanced_reminder_scheduler

# =============================================================================
# ایمپورت هندلرهای ریمایندر
# =============================================================================

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

# =============================================================================
# ایمپورت هندلرهای ریمایندر خودکار
# =============================================================================

from .auto_reminder_handlers import (
    user_auto_reminders_list,
    toggle_user_auto_reminder,
    handle_auto_reminder_user_callback
)

from .auto_reminder_admin import (
    auto_reminders_admin_handler,
    list_auto_reminders_admin,
    start_add_auto_reminder,
    delete_auto_reminder_handler,
    toggle_auto_reminder_status,
    process_add_title,
    process_add_message,
    process_add_days,
    process_admin_exam_selection,
    process_admin_confirmation,
    handle_auto_reminder_admin_callback,
    AutoReminderAdminStates
)

# =============================================================================
# ایمپورت هندلرهای ریمایندر پیشرفته
# =============================================================================

from .advanced_reminder_handlers import (
    advanced_reminders_admin_handler,
    start_add_advanced_reminder,
    process_advanced_title,
    process_advanced_message,
    process_start_time,
    process_start_date as process_advanced_start_date,
    process_end_time,
    process_end_date as process_advanced_end_date,
    process_days_of_week,
    process_repeat_count,
    process_repeat_interval,
    process_advanced_confirmation,
    list_advanced_reminders_admin,
    edit_advanced_reminder_handler,
    delete_advanced_reminder_handler,
    toggle_advanced_reminder_handler,
    handle_advanced_reminder_callback,
    show_advanced_reminder_details,
    edit_advanced_reminder,
    delete_advanced_reminder,
    toggle_advanced_reminder,
    show_advanced_reminder_stats
)

from .advanced_reminder_states import AdvancedReminderStates

# =============================================================================
# ایمپورت کیبوردها
# =============================================================================

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

from .advanced_reminder_keyboards import (
    create_advanced_reminder_admin_menu,
    create_start_time_menu,
    create_start_date_menu,
    create_end_time_menu,
    create_end_date_menu,
    create_days_of_week_menu,
    create_repeat_count_menu,
    create_repeat_interval_menu,
    create_advanced_reminder_list_keyboard,
    create_advanced_reminder_actions_keyboard
)

# =============================================================================
# ایمپورت ابزارها
# =============================================================================

from .reminder_utils import (
    validator,
    formatter,
    time_converter,
    analyzer
)

# =============================================================================
# توابع اصلی
# =============================================================================

def setup_reminder_system(bot):
    """راه‌اندازی کلی سیستم ریمایندر"""
    from .reminder_scheduler import ReminderScheduler
    return ReminderScheduler(bot)

# =============================================================================
# لیست همه exportها
# =============================================================================

__all__ = [
    # دیتابیس
    'reminder_db',
    
    # سیستم‌های زمان‌بندی
    'reminder_scheduler',
    'ReminderScheduler',
    'init_reminder_scheduler',
    'auto_reminder_system',
    'auto_reminder_scheduler', 
    'advanced_reminder_scheduler',
    
    # هندلرهای اصلی ریمایندر
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
    
    # هندلرهای ریمایندر خودکار
    'user_auto_reminders_list',
    'toggle_user_auto_reminder',
    'handle_auto_reminder_user_callback',
    'auto_reminders_admin_handler',
    'list_auto_reminders_admin',
    'start_add_auto_reminder',
    'delete_auto_reminder_handler',
    'toggle_auto_reminder_status',
    'process_add_title',
    'process_add_message',
    'process_add_days',
    'process_admin_exam_selection',
    'process_admin_confirmation',
    'handle_auto_reminder_admin_callback',
    
    # هندلرهای ریمایندر پیشرفته
    'advanced_reminders_admin_handler',
    'start_add_advanced_reminder',
    'process_advanced_title',
    'process_advanced_message',
    'process_start_time',
    'process_advanced_start_date',
    'process_end_time',
    'process_advanced_end_date',
    'process_days_of_week',
    'process_repeat_count',
    'process_repeat_interval',
    'process_advanced_confirmation',
    'list_advanced_reminders_admin',
    'edit_advanced_reminder_handler',
    'delete_advanced_reminder_handler',
    'toggle_advanced_reminder_handler',
    'handle_advanced_reminder_callback',
    'show_advanced_reminder_details',
    'edit_advanced_reminder',
    'delete_advanced_reminder',
    'toggle_advanced_reminder',
    'show_advanced_reminder_stats',
    
    # States
    'ExamReminderStates',
    'PersonalReminderStates',
    'ManagementStates',
    'AutoReminderAdminStates',
    'AdvancedReminderStates',
    
    # کیبوردهای اصلی
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
    
    # کیبوردهای پیشرفته
    'create_advanced_reminder_admin_menu',
    'create_start_time_menu',
    'create_start_date_menu',
    'create_end_time_menu',
    'create_end_date_menu',
    'create_days_of_week_menu',
    'create_repeat_count_menu',
    'create_repeat_interval_menu',
    'create_advanced_reminder_list_keyboard',
    'create_advanced_reminder_actions_keyboard',
    
    # ابزارها
    'validator',
    'formatter',
    'time_converter',
    'analyzer',
    'setup_reminder_system'
]
