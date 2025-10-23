# utils/memory_manager.py
import psutil
import logging
from typing import Optional

class MemoryManager:
    """مدیریت حافظه برای کتابخانه‌های سنگین مثل pandas"""
    
    @staticmethod
    def optimize_memory_usage():
        """بهینه‌سازی مصرف حافظه"""
        try:
            import pandas as pd
            # تنظیمات بهینه pandas
            pd.set_option('mode.chained_assignment', None)
        except ImportError:
            pass
    
    @staticmethod
    def get_memory_usage() -> str:
        """دریافت میزان مصرف حافظه"""
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        return f"{memory_mb:.2f} MB"
