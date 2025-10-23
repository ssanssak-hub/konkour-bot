import logging
from typing import List, Optional
from datetime import datetime
from sqlalchemy import and_
from database.base import db
from database.models import User

logger = logging.getLogger(__name__)

class UserRepository:
    def __init__(self):
        self.db = db
    
    def add_user(self, user_id: int, username: str = None, first_name: str = None, 
                 last_name: str = None, phone_number: str = None) -> User:
        """افزودن کاربر جدید"""
        session = self.db.get_session()
        try:
            user = session.query(User).filter_by(user_id=user_id).first()
            if not user:
                user = User(
                    user_id=user_id,
                    username=username,
                    first_name=first_name or "Unknown",
                    last_name=last_name,
                    phone_number=phone_number
                )
                session.add(user)
                session.commit()
                logger.info(f"✅ کاربر جدید اضافه شد: {user_id}")
            else:
                # بروزرسانی اطلاعات کاربر
                user.username = username or user.username
                user.first_name = first_name or user.first_name
                user.last_name = last_name or user.last_name
                user.phone_number = phone_number or user.phone_number
                user.last_active = datetime.now()
                session.commit()
                logger.debug(f"🔁 اطلاعات کاربر بروزرسانی شد: {user_id}")
            
            return user
        except Exception as e:
            session.rollback()
            logger.error(f"❌ خطا در افزودن کاربر: {e}")
            raise
        finally:
            self.db.close_session()
    
    def get_user(self, user_id: int) -> Optional[User]:
        """دریافت کاربر بر اساس user_id"""
        session = self.db.get_session()
        try:
            return session.query(User).filter_by(user_id=user_id).first()
        except Exception as e:
            logger.error(f"❌ خطا در دریافت کاربر: {e}")
            return None
        finally:
            self.db.close_session()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """دریافت کاربر بر اساس username"""
        session = self.db.get_session()
        try:
            return session.query(User).filter_by(username=username).first()
        except Exception as e:
            logger.error(f"❌ خطا در دریافت کاربر: {e}")
            return None
        finally:
            self.db.close_session()
    
    def get_all_users(self, active_only: bool = True) -> List[User]:
        """دریافت تمام کاربران"""
        session = self.db.get_session()
        try:
            query = session.query(User)
            if active_only:
                query = query.filter_by(is_active=True)
            return query.order_by(User.join_date.desc()).all()
        except Exception as e:
            logger.error(f"❌ خطا در دریافت کاربران: {e}")
            return []
        finally:
            self.db.close_session()
    
    def update_user_last_active(self, user_id: int) -> bool:
        """بروزرسانی زمان آخرین فعالیت کاربر"""
        session = self.db.get_session()
        try:
            user = session.query(User).filter_by(user_id=user_id).first()
            if user:
                user.last_active = datetime.now()
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"❌ خطا در بروزرسانی فعالیت کاربر: {e}")
            return False
        finally:
            self.db.close_session()
    
    def deactivate_user(self, user_id: int) -> bool:
        """غیرفعال کردن کاربر"""
        session = self.db.get_session()
        try:
            user = session.query(User).filter_by(user_id=user_id).first()
            if user:
                user.is_active = False
                session.commit()
                logger.info(f"✅ کاربر غیرفعال شد: {user_id}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"❌ خطا در غیرفعال کردن کاربر: {e}")
            return False
        finally:
            self.db.close_session()
    
    def activate_user(self, user_id: int) -> bool:
        """فعال کردن کاربر"""
        session = self.db.get_session()
        try:
            user = session.query(User).filter_by(user_id=user_id).first()
            if user:
                user.is_active = True
                session.commit()
                logger.info(f"✅ کاربر فعال شد: {user_id}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"❌ خطا در فعال کردن کاربر: {e}")
            return False
        finally:
            self.db.close_session()
    
    def update_user_settings(self, user_id: int, settings: dict) -> bool:
        """بروزرسانی تنظیمات کاربر"""
        session = self.db.get_session()
        try:
            user = session.query(User).filter_by(user_id=user_id).first()
            if user:
                user.settings = {**(user.settings or {}), **settings}
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"❌ خطا در بروزرسانی تنظیمات کاربر: {e}")
            return False
        finally:
            self.db.close_session()
    
    def get_inactive_users(self, days: int = 30) -> List[User]:
        """دریافت کاربران غیرفعال"""
        session = self.db.get_session()
        try:
            cutoff_date = datetime.now().replace(day=datetime.now().day - days)
            return session.query(User).filter(
                and_(
                    User.last_active < cutoff_date,
                    User.is_active == True
                )
            ).all()
        except Exception as e:
            logger.error(f"❌ خطا در دریافت کاربران غیرفعال: {e}")
            return []
        finally:
            self.db.close_session()
    
    def get_user_count(self) -> int:
        """دریافت تعداد کل کاربران"""
        session = self.db.get_session()
        try:
            return session.query(User).count()
        except Exception as e:
            logger.error(f"❌ خطا در دریافت تعداد کاربران: {e}")
            return 0
        finally:
            self.db.close_session()
    
    def get_active_user_count(self) -> int:
        """دریافت تعداد کاربران فعال"""
        session = self.db.get_session()
        try:
            return session.query(User).filter_by(is_active=True).count()
        except Exception as e:
            logger.error(f"❌ خطا در دریافت تعداد کاربران فعال: {e}")
            return 0
        finally:
            self.db.close_session()
