"""
الگوی Circuit Breaker برای جلوگیری از crashهای آبشاری
"""
import asyncio
from datetime import datetime, timedelta
from typing import Any, Callable
import logging

logger = logging.getLogger(__name__)

class CircuitBreaker:
    """
    Circuit Breaker برای مدیریت خطاهای متوالی
    """
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60, name: str = "Unknown"):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.name = name
        self.failures = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.logger = logging.getLogger(f"CircuitBreaker.{name}")
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        اجرای تابع با محافظت Circuit Breaker
        """
        if self.state == "OPEN":
            if datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout):
                self.state = "HALF_OPEN"
                self.logger.info(f"🔵 Circuit Breaker {self.name} به حالت HALF_OPEN تغییر کرد")
            else:
                self.logger.warning(f"🔴 Circuit Breaker {self.name} باز است - درخواست مسدود شد")
                raise CircuitBreakerOpenError(f"Circuit breaker {self.name} is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            # عملیات موفق
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.logger.info(f"🟢 Circuit Breaker {self.name} به حالت CLOSED بازگشت")
            
            self.failures = 0
            return result
            
        except Exception as e:
            # عملیات ناموفق
            self.failures += 1
            self.last_failure_time = datetime.now()
            
            if self.failures >= self.failure_threshold:
                self.state = "OPEN"
                self.logger.error(f"🔴 Circuit Breaker {self.name} باز شد - خطاهای متوالی: {self.failures}")
            
            self.logger.warning(f"🟡 Circuit Breaker {self.name} - خطا: {e}")
            raise e
    
    def get_status(self) -> dict:
        """دریافت وضعیت فعلی"""
        return {
            "name": self.name,
            "state": self.state,
            "failures": self.failures,
            "last_failure": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "threshold": self.failure_threshold
        }

class CircuitBreakerOpenError(Exception):
    """خطای مخصوص Circuit Breaker باز"""
    pass

# نمونه‌های全局 برای کامپوننت‌های مختلف
database_breaker = CircuitBreaker(failure_threshold=3, timeout=30, name="Database")
webhook_breaker = CircuitBreaker(failure_threshold=2, timeout=60, name="Webhook")
external_api_breaker = CircuitBreaker(failure_threshold=5, timeout=120, name="ExternalAPI")
