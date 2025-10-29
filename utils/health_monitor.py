"""
سیستم مانیتورینگ سلامت و منابع ربات
"""
import logging
import asyncio
import psutil
import os
from datetime import datetime, timedelta
from typing import Dict, Any
from aiohttp import web

logger = logging.getLogger(__name__)

class HealthMonitor:
    """
    مانیتور سلامت ربات و منابع سیستم
    """
    
    def __init__(self):
        self.start_time = datetime.now()
        self.metrics = {
            "requests_total": 0,
            "errors_total": 0,
            "database_errors": 0,
            "memory_warnings": 0
        }
        self.alerts = []
    
    async def check_system_health(self) -> Dict[str, Any]:
        """بررسی سلامت سیستم"""
        process = psutil.Process(os.getpid())
        
        # مموری
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        
        # CPU
        cpu_percent = process.cpu_percent()
        
        # دیتابیس
        db_health = await self.check_database_health()
        
        # وضعیت کلی
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "system": {
                "memory_usage_mb": round(memory_mb, 2),
                "cpu_percent": round(cpu_percent, 2),
                "memory_percent": round(process.memory_percent(), 2)
            },
            "application": {
                "requests_total": self.metrics["requests_total"],
                "errors_total": self.metrics["errors_total"],
                "database_errors": self.metrics["database_errors"]
            },
            "components": {
                "database": db_health,
                "webhook": await self.check_webhook_health(),
                "cache": await self.check_cache_health()
            },
            "alerts": self.alerts[-5:]  # 5 alert آخر
        }
        
        # بررسی thresholdها
        if memory_mb > 400:  # 400MB
            health_status["status"] = "warning"
            self.metrics["memory_warnings"] += 1
            self.add_alert("⚠️ مصرف حافظه بالا", f"حافظه: {memory_mb:.1f}MB")
            
        if self.metrics["errors_total"] > 10:
            health_status["status"] = "warning"
            self.add_alert("⚠️ خطاهای زیاد", f"تعداد خطاها: {self.metrics['errors_total']}")
        
        if memory_mb > 450:  # 450MB - بحرانی
            health_status["status"] = "critical"
            await self.handle_memory_critical()
            
        return health_status
    
    async def check_database_health(self) -> str:
        """بررسی سلامت دیتابیس"""
        try:
            # ایمپورت داخل تابع برای جلوگیری از circular import
            from database import Database
            db = Database()
            with db.get_connection() as conn:
                conn.execute("SELECT 1")
            return "healthy"
        except Exception as e:
            self.metrics["database_errors"] += 1
            logger.error(f"❌ سلامت دیتابیس: {e}")
            return "unhealthy"
    
    async def check_webhook_health(self) -> str:
        """بررسی سلامت وب‌هوک"""
        try:
            from main import bot  # ایمپورت داخل تابع
            webhook_info = await bot.get_webhook_info()
            if webhook_info.url:
                return "healthy"
            return "unhealthy"
        except Exception as e:
            logger.error(f"❌ سلامت وب‌هوک: {e}")
            return "unhealthy"
    
    async def check_cache_health(self) -> str:
        """بررسی سلامت کش"""
        try:
            from main import _CACHE  # ایمپورت داخل تابع
            cache_size = len(_CACHE)
            if cache_size < 1000:  # حداکثر 1000 آیتم در کش
                return "healthy"
            return "warning"
        except Exception as e:
            logger.error(f"❌ سلامت کش: {e}")
            return "unhealthy"
    
    async def handle_memory_critical(self):
        """مدیریت وضعیت بحرانی حافظه"""
        logger.critical("💥 وضعیت بحرانی حافظه - پاکسازی اضطراری")
        
        # پاکسازی کش‌ها
        try:
            from main import _CACHE
            _CACHE.clear()
            logger.info("🧹 کش‌ها پاکسازی شدند")
        except:
            pass
        
        # اجرای GC
        import gc
        gc.collect()
        
        self.add_alert("🚨 وضعیت بحرانی حافظه", "پاکسازی اضطراری انجام شد")
    
    def add_alert(self, title: str, message: str):
        """افزودن alert جدید"""
        alert = {
            "title": title,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.alerts.append(alert)
        
        # حفظ فقط 20 alert آخر
        if len(self.alerts) > 20:
            self.alerts = self.alerts[-20:]
    
    def increment_metric(self, metric_name: str, value: int = 1):
        """افزایش متریک"""
        if metric_name in self.metrics:
            self.metrics[metric_name] += value
    
    async def periodic_health_check(self):
        """بررسی دوره‌ی سلامت"""
        while True:
            try:
                health_status = await self.check_system_health()
                
                if health_status["status"] != "healthy":
                    logger.warning(f"🔍 گزارش سلامت: {health_status['status']}")
                    
                # لاگ هر 5 دقیقه
                if datetime.now().minute % 5 == 0:
                    logger.info(f"📊 گزارش سلامت دوره‌ای: {health_status}")
                    
            except Exception as e:
                logger.error(f"❌ خطا در بررسی سلامت: {e}")
            
            await asyncio.sleep(60)  # هر 1 دقیقه

# نمونه全局
health_monitor = HealthMonitor()

# هندلر HTTP برای سلامت
async def health_check_handler(request):
    """هندلر بررسی سلامت برای HTTP"""
    health_status = await health_monitor.check_system_health()
    
    status_code = 200
    if health_status["status"] == "critical":
        status_code = 503
    elif health_status["status"] == "warning":
        status_code = 200  # Still OK but with warnings
    
    return web.json_response(health_status, status=status_code)

async def readiness_check_handler(request):
    """هندلر بررسی آمادگی سرویس"""
    health_status = await health_monitor.check_system_health()
    
    if health_status["status"] in ["healthy", "warning"]:
        return web.Response(text="READY", status=200)
    else:
        return web.Response(text="NOT READY", status=503)
