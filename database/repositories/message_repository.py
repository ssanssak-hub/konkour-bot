import logging
from typing import List, Optional
from datetime import datetime
from database.base import db
from database.models import UserMessage

logger = logging.getLogger(__name__)

class MessageRepository:
    def __init__(self):
        self.db = db
    
    def add_user_message(self, user_id: int, message_text: str, message_type: str = 'general') -> UserMessage:
        """افزودن پیام کاربر"""
        session = self.db.get_session()
        try:
            message = UserMessage(
                user_id=user_id,
                message_text=message_text,
                message_type=message_type
            )
            session.add(message)
            session.commit()
            logger.info(f"✅ پیام کاربر اضافه شد: {user_id}")
            return message
        except Exception as e:
            session.rollback()
            logger.error(f"❌ خطا در افزودن پیام کاربر: {e}")
            raise
        finally:
            self.db.close_session()
    
    def get_user_messages(self, user_id: int) -> List[UserMessage]:
        """دریافت پیام‌های کاربر"""
        session = self.db.get_session()
        try:
            return session.query(UserMessage).filter_by(user_id=user_id).order_by(UserMessage.created_at.desc()).all()
        except Exception as e:
            logger.error(f"❌ خطا در دریافت پیام‌های کاربر: {e}")
            return []
        finally:
            self.db.close_session()
    
    def get_pending_messages(self) -> List[UserMessage]:
        """دریافت پیام‌های در انتظار پاسخ"""
        session = self.db.get_session()
        try:
            return session.query(UserMessage).filter_by(status='pending').order_by(UserMessage.created_at).all()
        except Exception as e:
            logger.error(f"❌ خطا در دریافت پیام‌های در انتظار: {e}")
            return []
        finally:
            self.db.close_session()
    
    def get_message(self, message_id: int) -> Optional[UserMessage]:
        """دریافت پیام بر اساس ID"""
        session = self.db.get_session()
        try:
            return session.query(UserMessage).filter_by(id=message_id).first()
        except Exception as e:
            logger.error(f"❌ خطا در دریافت پیام: {e}")
            return None
        finally:
            self.db.close_session()
    
    def get_messages_by_type(self, message_type: str) -> List[UserMessage]:
        """دریافت پیام‌ها بر اساس نوع"""
        session = self.db.get_session()
        try:
            return session.query(UserMessage).filter_by(message_type=message_type).order_by(UserMessage.created_at.desc()).all()
        except Exception as e:
            logger.error(f"❌ خطا در دریافت پیام‌ها بر اساس نوع: {e}")
            return []
        finally:
            self.db.close_session()
    
    def update_message_status(self, message_id: int, status: str, admin_reply: str = None) -> bool:
        """بروزرسانی وضعیت پیام"""
        session = self.db.get_session()
        try:
            message = session.query(UserMessage).filter_by(id=message_id).first()
            if message:
                message.status = status
                if admin_reply:
                    message.admin_reply = admin_reply
                    message.reply_date = datetime.now()
                message.updated_at = datetime.now()
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"❌ خطا در بروزرسانی وضعیت پیام: {e}")
            return False
        finally:
            self.db.close_session()
    
    def mark_message_replied(self, message_id: int, admin_reply: str) -> bool:
        """علامت‌گذاری پیام به عنوان پاسخ داده شده"""
        session = self.db.get_session()
        try:
            message = session.query(UserMessage).filter_by(id=message_id).first()
            if message:
                message.status = 'replied'
                message.admin_reply = admin_reply
                message.reply_date = datetime.now()
                message.updated_at = datetime.now()
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"❌ خطا در علامت‌گذاری پیام: {e}")
            return False
        finally:
            self.db.close_session()
    
    def mark_message_resolved(self, message_id: int) -> bool:
        """علامت‌گذاری پیام به عنوان حل شده"""
        session = self.db.get_session()
        try:
            message = session.query(UserMessage).filter_by(id=message_id).first()
            if message:
                message.status = 'resolved'
                message.updated_at = datetime.now()
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"❌ خطا در علامت‌گذاری پیام: {e}")
            return False
        finally:
            self.db.close_session()
    
    def delete_message(self, message_id: int) -> bool:
        """حذف پیام"""
        session = self.db.get_session()
        try:
            message = session.query(UserMessage).filter_by(id=message_id).first()
            if message:
                session.delete(message)
                session.commit()
                logger.info(f"✅ پیام حذف شد: {message_id}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"❌ خطا در حذف پیام: {e}")
            return False
        finally:
            self.db.close_session()
    
    def get_message_stats(self) -> dict:
        """دریافت آمار پیام‌ها"""
        session = self.db.get_session()
        try:
            total_messages = session.query(UserMessage).count()
            pending_messages = session.query(UserMessage).filter_by(status='pending').count()
            replied_messages = session.query(UserMessage).filter_by(status='replied').count()
            resolved_messages = session.query(UserMessage).filter_by(status='resolved').count()
            
            return {
                'total': total_messages,
                'pending': pending_messages,
                'replied': replied_messages,
                'resolved': resolved_messages
            }
        except Exception as e:
            logger.error(f"❌ خطا در دریافت آمار پیام‌ها: {e}")
            return {}
        finally:
            self.db.close_session()
    
    def get_recent_messages(self, limit: int = 10) -> List[UserMessage]:
        """دریافت آخرین پیام‌ها"""
        session = self.db.get_session()
        try:
            return session.query(UserMessage).order_by(UserMessage.created_at.desc()).limit(limit).all()
        except Exception as e:
            logger.error(f"❌ خطا در دریافت آخرین پیام‌ها: {e}")
            return []
        finally:
            self.db.close_session()
