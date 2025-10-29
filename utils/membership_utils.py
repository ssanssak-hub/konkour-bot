"""
توابع مربوط به سیستم عضویت اجباری
"""
import logging
from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database import Database

logger = logging.getLogger(__name__)
db = Database()

async def check_user_membership(bot: Bot, user_id: int) -> bool:
    """
    بررسی عضویت کاربر در تمام کانال‌های اجباری
    
    Args:
        bot: نمونه ربات
        user_id: آیدی عددی کاربر
    
    Returns:
        bool: True اگر کاربر در همه کانال‌ها عضو باشد
    """
    channels = db.get_mandatory_channels()
    
    if not channels:
        logger.info("هیچ کانال اجباری تعریف نشده است")
        return True  # اگر کانال اجباری وجود ندارد
    
    logger.info(f"بررسی عضویت کاربر {user_id} در {len(channels)} کانال")
    
    for channel in channels:
        try:
            member = await bot.get_chat_member(channel['channel_id'], user_id)
            is_member = member.status in ['member', 'administrator', 'creator']
            
            # بروزرسانی وضعیت در دیتابیس
            db.update_channel_membership(user_id, channel['channel_id'], is_member)
            
            if not is_member:
                logger.warning(f"کاربر {user_id} در کانال {channel['channel_title']} عضو نیست")
                return False
                
            logger.info(f"کاربر {user_id} در کانال {channel['channel_title']} عضو است")
            
        except Exception as e:
            logger.error(f"خطا در بررسی عضویت کاربر {user_id} در کانال {channel['channel_title']}: {e}")
            return False
    
    logger.info(f"کاربر {user_id} در تمام کانال‌های اجباری عضو است")
    return True

def create_membership_keyboard():
    """
    ایجاد کیبورد برای عضویت در کانال‌های اجباری
    
    Returns:
        InlineKeyboardMarkup: کیبورد با لینک‌های عضویت
    """
    channels = db.get_mandatory_channels()
    keyboard = []
    
    if not channels:
        logger.warning("هیچ کانال اجباری برای ایجاد کیبورد وجود ندارد")
        # بازگشت کیبورد خالی
        return InlineKeyboardMarkup(inline_keyboard=[])
    
    logger.info(f"ایجاد کیبورد عضویت برای {len(channels)} کانال")
    
    for channel in channels:
        # پاک کردن @ از ابتدای یوزرنیم اگر وجود دارد
        username = channel['channel_username'].lstrip('@')
        keyboard.append([
            InlineKeyboardButton(
                text=f"📢 {channel['channel_title']}",
                url=f"https://t.me/{username}"
            )
        ])
    
    # دکمه بررسی عضویت
    keyboard.append([
        InlineKeyboardButton(text="✅ بررسی عضویت", callback_data="check_membership")
    ])
    
    logger.info("کیبورد عضویت با موفقیت ایجاد شد")
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

async def get_membership_status(bot: Bot, user_id: int) -> dict:
    """
    دریافت وضعیت دقیق عضویت کاربر در هر کانال
    
    Args:
        bot: نمونه ربات
        user_id: آیدی عددی کاربر
    
    Returns:
        dict: وضعیت عضویت در هر کانال
    """
    channels = db.get_mandatory_channels()
    status = {
        'user_id': user_id,
        'total_channels': len(channels),
        'joined_channels': 0,
        'channel_details': []
    }
    
    for channel in channels:
        try:
            member = await bot.get_chat_member(channel['channel_id'], user_id)
            is_member = member.status in ['member', 'administrator', 'creator']
            
            status['channel_details'].append({
                'channel_id': channel['channel_id'],
                'channel_title': channel['channel_title'],
                'is_member': is_member,
                'member_status': member.status
            })
            
            if is_member:
                status['joined_channels'] += 1
                
        except Exception as e:
            status['channel_details'].append({
                'channel_id': channel['channel_id'],
                'channel_title': channel['channel_title'],
                'is_member': False,
                'error': str(e)
            })
    
    status['all_joined'] = status['joined_channels'] == status['total_channels']
    return status
