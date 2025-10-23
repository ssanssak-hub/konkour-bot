import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool

# تنظیمات لاگ
logger = logging.getLogger(__name__)

# ایجاد Base
Base = declarative_base()

class DatabaseManager:
    def __init__(self, database_url=None):
        # ✅ استفاده مستقیم از متغیر محیطی - تضمین شده
        self.database_url = database_url or os.getenv("DATABASE_URL", "sqlite:///konkur_bot.db")
        self.engine = self._create_engine()
        self.Session = self._create_session()
        
    def _create_engine(self):
        """ایجاد engine دیتابیس"""
        try:
            if 'sqlite' in self.database_url:
                engine = create_engine(
                    self.database_url,
                    poolclass=StaticPool,
                    connect_args={'check_same_thread': False}
                )
            else:
                engine = create_engine(self.database_url)
            
            logger.info("✅ Engine دیتابیس ایجاد شد")
            return engine
        except Exception as e:
            logger.error(f"❌ خطا در ایجاد engine دیتابیس: {e}")
            raise
    
    def _create_session(self):
        """ایجاد session factory"""
        return scoped_session(sessionmaker(bind=self.engine))
    
    def create_tables(self):
        """ایجاد جداول در دیتابیس"""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("✅ جداول دیتابیس با موفقیت ایجاد شدند")
        except Exception as e:
            logger.error(f"❌ خطا در ایجاد جداول دیتابیس: {e}")
            raise
    
    def get_session(self):
        """دریافت session جدید"""
        return self.Session()
    
    def close_session(self):
        """بستن session"""
        self.Session.remove()
    
    def close(self):
        """بستن اتصال به دیتابیس"""
        try:
            self.Session.remove()
            self.engine.dispose()
            logger.info("✅ اتصال دیتابیس بسته شد")
        except Exception as e:
            logger.error(f"❌ خطا در بستن اتصال دیتابیس: {e}")

# ایجاد نمونه global از دیتابیس
db = DatabaseManager()
