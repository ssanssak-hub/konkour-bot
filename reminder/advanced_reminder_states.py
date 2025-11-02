"""
حالت‌های FSM برای ریمایندرهای پیشرفته ادمین
"""
from aiogram.fsm.state import State, StatesGroup

class AdvancedReminderStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_message = State()
    waiting_for_start_time = State()
    waiting_for_start_date = State()
    waiting_for_repetition_mode = State()  # جدید
    waiting_for_end_time = State()
    waiting_for_end_date = State()
    waiting_for_daily_max_occurrences = State()  # جدید
    waiting_for_days_of_week = State()
    waiting_for_repeat_count = State()
    waiting_for_repeat_interval = State()
    waiting_for_confirmation = State()
