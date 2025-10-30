"""
سیستم مدیریت ریمایندرهای خودکار برای ادمین
"""
import logging
from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from typing import List, Dict, Any

from reminder.reminder_database import reminder_db
from reminder.reminder_keyboards import (
    create_back_only_menu,
    create_auto_reminders_admin_menu
)

logger = logging.getLogger(__name__)

# حالت‌های FSM برای مدیریت ریمایندرهای خودکار
class AutoReminderAdminStates(StatesGroup):
    adding_reminder = State()
    editing_reminder = State()
    deleting_reminder = State()

# --- توابع دیتابیس برای ریمایندرهای خودکار ---
def add_auto_reminder(title: str, message: str, days_before_exam: int, exam_keys: List[str], admin_id: int) -> int:
    """افزودن ریمایندر خودکار جدید"""
    try:
        with reminder_db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO auto_reminders (title, message, days_before_exam, exam_keys, created_by_admin)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, message, days_before_exam, json.dumps(exam_keys), admin_id))
            return cursor.lastrowid
    except Exception as e:
        logger.error(f"خطا در افزودن ریمایندر خودکار: {e}")
        return None

def get_all_auto_reminders() -> List[Dict[str, Any]]:
    """دریافت همه ریمایندرهای خودکار"""
    try:
        with reminder_db.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM auto_reminders ORDER BY days_before_exam DESC')
            
            reminders = []
            for row in cursor.fetchall():
                reminders.append({
                    'id': row['id'],
                    'title': row['title'],
                    'message': row['message'],
                    'days_before_exam': row['days_before_exam'],
                    'exam_keys': json.loads(row['exam_keys']),
                    'is_active': bool(row['is_active']),
                    'created_by_admin': row['created_by_admin'],
                    'created_at': row['created_at']
                })
            return reminders
    except Exception as e:
        logger.error(f"خطا در دریافت ریمایندرهای خودکار: {e}")
        return []

def update_auto_reminder(reminder_id: int, title: str = None, message: str = None, 
                        days_before_exam: int = None, exam_keys: List[str] = None, 
                        is_active: bool = None) -> bool:
    """ویرایش ریمایندر خودکار"""
    try:
        with reminder_db.get_connection() as conn:
            cursor = conn.cursor()
            
            update_fields = []
            params = []
            
            if title is not None:
                update_fields.append("title = ?")
                params.append(title)
            if message is not None:
                update_fields.append("message = ?")
                params.append(message)
            if days_before_exam is not None:
                update_fields.append("days_before_exam = ?")
                params.append(days_before_exam)
            if exam_keys is not None:
                update_fields.append("exam_keys = ?")
                params.append(json.dumps(exam_keys))
            if is_active is not None:
                update_fields.append("is_active = ?")
                params.append(is_active)
            
            if not update_fields:
                return False
                
            params.append(reminder_id)
            cursor.execute(f'''
                UPDATE auto_reminders 
                SET {', '.join(update_fields)} 
                WHERE id = ?
            ''', params)
            
            return cursor.rowcount > 0
    except Exception as e:
        logger.error(f"خطا در ویرایش ریمایندر خودکار: {e}")
        return False

def delete_auto_reminder(reminder_id: int) -> bool:
    """حذف ریمایندر خودکار"""
    try:
        with reminder_db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM auto_reminders WHERE id = ?', (reminder_id,))
            return cursor.rowcount > 0
    except Exception as e:
        logger.error(f"خطا در حذف ریمایندر خودکار: {e}")
        return False

# --- هندلرهای ادمین ---
async def auto_reminders_admin_handler(message: types.Message):
    """منوی مدیریت ریمایندرهای خودکار برای ادمین"""
    from config import ADMIN_ID
    
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ دسترسی denied!")
        return
        
    auto_reminders = get_all_auto_reminders()
    active_count = len([r for r in auto_reminders if r['is_active']])
    
    await message.answer(
        f"🤖 <b>مدیریت ریمایندرهای خودکار</b>\n\n"
        f"📊 آمار سیستم:\n"
        f"• 📝 کل ریمایندرها: {len(auto_reminders)}\n"
        f"• 🔔 فعال: {active_count}\n"
        f"• 🔕 غیرفعال: {len(auto_reminders) - active_count}\n\n"
        f"لطفاً عمل مورد نظر را انتخاب کنید:",
        reply_markup=create_auto_reminders_admin_menu(),
        parse_mode="HTML"
    )

async def list_auto_reminders_admin(message: types.Message):
    """نمایش لیست ریمایندرهای خودکار برای ادمین"""
    auto_reminders = get_all_auto_reminders()
    
    if not auto_reminders:
        await message.answer(
            "📭 <b>هیچ ریمایندر خودکاری پیدا نشد</b>",
            reply_markup=create_auto_reminders_admin_menu(),
            parse_mode="HTML"
        )
        return
    
    message_text = "📋 <b>لیست ریمایندرهای خودکار</b>\n\n"
    
    for reminder in auto_reminders:
        status = "✅" if reminder['is_active'] else "❌"
        exam_names = [EXAMS_1405[key]['name'] for key in reminder['exam_keys'] if key in EXAMS_1405]
        message_text += (
            f"{status} <b>کد {reminder['id']}</b>\n"
            f"📝 {reminder['title']}\n"
            f"⏰ {reminder['days_before_exam']} روز قبل از کنکور\n"
            f"🎯 {', '.join(exam_names)}\n"
            f"📅 ایجاد شده در: {reminder['created_at'][:10]}\n"
            f"────────────────────\n\n"
        )
    
    await message.answer(
        message_text,
        reply_markup=create_auto_reminders_admin_menu(),
        parse_mode="HTML"
    )

async def start_add_auto_reminder(message: types.Message, state: FSMContext):
    """شروع افزودن ریمایندر خودکار جدید"""
    from config import ADMIN_ID
    
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ دسترسی denied!")
        return
        
    await state.set_state(AutoReminderAdminStates.adding_reminder)
    await state.update_data(step="title")
    
    await message.answer(
        "➕ <b>افزودن ریمایندر خودکار جدید</b>\n\n"
        "لطفاً عنوان ریمایندر را وارد کنید:\n\n"
        "💡 <i>مثال: شروع فصل طلایی</i>\n\n"
        "یا برای بازگشت: 🔙 بازگشت",
        reply_markup=create_back_only_menu(),
        parse_mode="HTML"
    )

# --- هندلرهای کاربران عادی ---
async def user_auto_reminders_list(message: types.Message):
    """لیست ریمایندرهای خودکار برای کاربران عادی"""
    auto_reminders = get_all_auto_reminders()
    user_reminders = reminder_db.get_user_auto_reminders(message.from_user.id)
    
    # ایجاد مپ برای وضعیت فعال بودن هر ریمایندر برای کاربر
    user_reminders_map = {ur['auto_reminder_id']: ur['is_active'] for ur in user_reminders}
    
    message_text = "🤖 <b>ریمایندرهای خودکار</b>\n\n"
    message_text += "این ریمایندرها به صورت خودکار در زمان‌های مهم فعال می‌شوند:\n\n"
    
    for reminder in auto_reminders:
        if not reminder['is_active']:
            continue
            
        user_status = user_reminders_map.get(reminder['id'], False)
        status_icon = "✅" if user_status else "❌"
        status_text = "فعال" if user_status else "غیرفعال"
        
        message_text += (
            f"{status_icon} <b>{reminder['title']}</b>\n"
            f"⏰ {reminder['days_before_exam']} روز قبل از کنکور\n"
            f"📝 {reminder['message']}\n"
            f"🔔 وضعیت: {status_text}\n"
            f"────────────────────\n\n"
        )
    
    await message.answer(
        message_text,
        reply_markup=create_auto_reminders_menu(),
        parse_mode="HTML"
    )

async def toggle_user_auto_reminder(message: types.Message):
    """تغییر وضعیت ریمایندر خودکار برای کاربر"""
    auto_reminders = get_all_auto_reminders()
    active_reminders = [r for r in auto_reminders if r['is_active']]
    
    if not active_reminders:
        await message.answer(
            "❌ هیچ ریمایندر خودکار فعالی موجود نیست",
            reply_markup=create_auto_reminders_menu()
        )
        return
    
    # ایجاد کیبورد برای انتخاب ریمایندر
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = []
    for reminder in active_reminders:
        user_reminders = reminder_db.get_user_auto_reminders(message.from_user.id)
        user_status = any(ur['auto_reminder_id'] == reminder['id'] and ur['is_active'] for ur in user_reminders)
        status_text = "🔔 غیرفعال کن" if user_status else "✅ فعال کن"
        
        keyboard.append([
            InlineKeyboardButton(
                text=f"{reminder['title']} - {status_text}",
                callback_data=f"auto_toggle:{reminder['id']}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton(text="🔙 بازگشت", callback_data="auto_reminders:back")
    ])
    
    await message.answer(
        "🔔 <b>مدیریت ریمایندرهای خودکار</b>\n\n"
        "لطفاً ریمایندر مورد نظر را برای تغییر وضعیت انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode="HTML"
    )
