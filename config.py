import os
import datetime
from datetime import timedelta
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی
if os.path.exists('.env'):
    load_dotenv()
    print("✅ فایل .env بارگذاری شد")
else:
    print("ℹ️ فایل .env یافت نشد - استفاده از متغیرهای محیطی سیستم")

class PersianDateConverter:
    """کلاس تبدیل تاریخ میلادی به شمسی"""
    
    @staticmethod
    def gregorian_to_jalali(gy, gm, gd):
        """تبدیل تاریخ میلادی به شمسی"""
        g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
        if gm > 2:
            gy2 = gy + 1
        else:
            gy2 = gy
        days = 355666 + (365 * gy) + ((gy2 + 3) // 4) - ((gy2 + 99) // 100) + ((gy2 + 399) // 400) + gd + g_d_m[gm - 1]
        jy = -1595 + (33 * (days // 12053))
        days %= 12053
        jy += 4 * (days // 1461)
        days %= 1461
        if days > 365:
            jy += (days - 1) // 365
            days = (days - 1) % 365
        if days < 186:
            jm = 1 + (days // 31)
            jd = 1 + (days % 31)
        else:
            jm = 7 + ((days - 186) // 30)
            jd = 1 + ((days - 186) % 30)
        return jy, jm, jd
    
    @staticmethod
    def jalali_to_gregorian(jy, jm, jd):
        """تبدیل تاریخ شمسی به میلادی"""
        jy += 1595
        days = -355668 + (365 * jy) + ((jy // 33) * 8) + (((jy % 33) + 3) // 4) + jd
        if jm < 7:
            days += (jm - 1) * 31
        else:
            days += ((jm - 7) * 30) + 186
        gy = 400 * (days // 146097)
        days %= 146097
        if days > 36524:
            gy += 100 * (--days // 36524)
            days %= 36524
            if days >= 365:
                days += 1
        gy += 4 * (days // 1461)
        days %= 1461
        if days > 365:
            gy += (days - 1) // 365
            days = (days - 1) % 365
        gd = days + 1
        if (gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0):
            kab = 29
        else:
            kab = 28
        sal_a = [0, 31, kab, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        gm = 0
        while gm < 13 and gd > sal_a[gm]:
            gd -= sal_a[gm]
            gm += 1
        return gy, gm, gd

class PersianDateTime:
    """کلاس تاریخ و زمان شمسی"""
    
    def __init__(self, year=None, month=None, day=None, hour=0, minute=0, second=0):
        if year is None:
            # تاریخ فعلی
            now = datetime.datetime.now()
            jy, jm, jd = PersianDateConverter.gregorian_to_jalali(now.year, now.month, now.day)
            self.year = jy
            self.month = jm
            self.day = jd
            self.hour = now.hour
            self.minute = now.minute
            self.second = now.second
        else:
            self.year = year
            self.month = month
            self.day = day
            self.hour = hour
            self.minute = minute
            self.second = second
    
    def strftime(self, format_str):
        """قالب‌بندی تاریخ"""
        result = format_str
        result = result.replace('%Y', f"{self.year:04d}")
        result = result.replace('%m', f"{self.month:02d}")
        result = result.replace('%d', f"{self.day:02d}")
        result = result.replace('%H', f"{self.hour:02d}")
        result = result.replace('%M', f"{self.minute:02d}")
        result = result.replace('%S', f"{self.second:02d}")
        
        # نام ماه‌های شمسی
        month_names = {
            1: 'فروردین', 2: 'اردیبهشت', 3: 'خرداد',
            4: 'تیر', 5: 'مرداد', 6: 'شهریور',
            7: 'مهر', 8: 'آبان', 9: 'آذر',
            10: 'دی', 11: 'بهمن', 12: 'اسفند'
        }
        result = result.replace('%B', month_names.get(self.month, ''))
        
        return result
    
    @classmethod
    def now(cls):
        """تاریخ و زمان فعلی شمسی"""
        return cls()
    
    @classmethod
    def fromgregorian(cls, dt=None):
        """تبدیل از تاریخ میلادی"""
        if dt is None:
            dt = datetime.datetime.now()
        jy, jm, jd = PersianDateConverter.gregorian_to_jalali(dt.year, dt.month, dt.day)
        return cls(jy, jm, jd, dt.hour, dt.minute, dt.second)

# ایجاد alias برای سازگاری
jdatetime = type('jdatetime', (), {
    'datetime': PersianDateTime,
    'GregorianToJalali': PersianDateConverter.gregorian_to_jalali,
    'JalaliToGregorian': PersianDateConverter.jalali_to_gregorian
})()

class Config:
    # ==================== تنظیمات اصلی ربات ====================
    BOT_TOKEN = os.environ.get('BOT_TOKEN', "8381121739:AAFB2YBMomBh9xhoI3Qn0VVuGaGlpea9fx8")
    ADMIN_ID = int(os.environ.get('ADMIN_ID', 7703677187))
    BOT_USERNAME = os.environ.get('BOT_USERNAME', "konkur1405_bot")
    
    # ==================== تنظیمات Webhook ====================
    WEBHOOK_URL = os.environ.get('WEBHOOK_URL', "https://konkurcounting-3ga0.onrender.com")
    WEBHOOK_PATH = "/webhook"
    WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', "konkur1405_secret_key_2024")
    
    # ==================== تنظیمات سرور ====================
    PORT = int(os.environ.get('PORT', 5000))
    HOST = os.environ.get('HOST', '0.0.0.0')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # ==================== تنظیمات دیتابیس ====================
    DATABASE_URL = os.environ.get('DATABASE_URL', "sqlite:///konkur_bot.db")
    DATABASE_POOL_SIZE = 5
    DATABASE_MAX_OVERFLOW = 10
    DATABASE_POOL_RECYCLE = 3600
    
    # ==================== تنظیمات محیطی ====================
    ENVIRONMENT = os.environ.get('ENVIRONMENT', 'production')
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # ==================== تنظیمات امنیتی ====================
    SECRET_KEY = os.environ.get('SECRET_KEY', 'konkur1405_default_secret_key_2024')
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY', 'default_32_byte_encryption_key_2024_change_me')
    
    # ==================== تنظیمات توسعه ====================
    DEVELOPER_MODE = os.environ.get('DEVELOPER_MODE', 'False').lower() == 'true'
    ENABLE_DEBUG_FEATURES = os.environ.get('ENABLE_DEBUG_FEATURES', 'False').lower() == 'true'
    TEST_USER_ID = int(os.environ.get('TEST_USER_ID', '0'))
    
    # ==================== کنکورهای 1405 ====================
    EXAMS = {
        "علوم تجربی": {
            "date": "1405-04-12 08:00:00",
            "emoji": "🔬",
            "description": "کنکور رشته علوم تجربی"
        },
        "ریاضی‌وفنی": {
            "date": "1405-04-11 08:00:00",
            "emoji": "📐",
            "description": "کنکور رشته ریاضی و فنی"
        },
        "علوم انسانی": {
            "date": "1405-04-11 08:00:00", 
            "emoji": "📚",
            "description": "کنکور رشته علوم انسانی"
        },
        "فرهنگیان": {
            "date": ["1405-02-17 08:00:00", "1405-02-18 08:00:00"],
            "emoji": "👨‍🏫",
            "description": "کنکور دانشگاه فرهنگیان"
        },
        "هنر": {
            "date": "1405-04-12 14:30:00",
            "emoji": "🎨",
            "description": "کنکور رشته هنر"
        },
        "زبان‌وگروه‌های‌خارجه": {
            "date": "1405-04-12 14:30:00",
            "emoji": "🌍",
            "description": "کنکور زبان و گروه‌های خارجه"
        }
    }
    
    # ==================== تنظیمات تاریخ و زمان ====================
    TIMEZONE = 'Asia/Tehran'
    JALALI_YEAR = 1405
    EXAM_START_MONTH = 4  # تیرماه
    
    # ==================== تنظیمات یادآوری ====================
    REMINDER_HOURS = [f"{i:02d}:00" for i in range(24)]  # ساعات رند
    REMINDER_CHECK_INTERVAL = 300  # 5 دقیقه - چک کردن یادآوری‌ها
    MAX_REMINDERS_PER_USER = 10
    
    # ==================== تنظیمات مطالعه ====================
    STUDY_SESSION_MIN_DURATION = 0.25  # حداقل مدت جلسه مطالعه (15 دقیقه)
    STUDY_SESSION_MAX_DURATION = 8.0   # حداکثر مدت جلسه مطالعه (8 ساعت)
    DEFAULT_STUDY_TARGET_HOURS = {
        'daily': 4.0,
        'weekly': 25.0,
        'monthly': 100.0
    }
    
    # ==================== تنظیمات آمار و گزارش ====================
    STATS_UPDATE_INTERVAL = 3600  # 1 ساعت - بروزرسانی آمار
    TOP_USERS_COUNT = 20
    PROGRESS_LEVELS = {
        'excellent': 90,   # عالی
        'good': 75,        # خوب
        'average': 50,     # متوسط
        'weak': 25,        # ضعیف
        'poor': 0          # بسیار ضعیف
    }
    
    # ==================== تنظیمات مدیریت ====================
    MAX_BROADCAST_LENGTH = 4000  # حداکثر طول پیام همگانی
    BROADCAST_DELAY = 0.1        # تاخیر بین ارسال به کاربران (ثانیه)
    ADMIN_COMMANDS = ['/stats', '/broadcast', '/users', '/backup']
    
    # ==================== تنظیمات امنیتی ====================
    MAX_MESSAGE_LENGTH = 2000
    MAX_USER_MESSAGES_PER_DAY = 10
    RATE_LIMIT_PER_MINUTE = 30
    BLOCKED_USER_IDS = []  # لیست کاربران مسدود شده
    
    # ==================== تنظیمات لاگ ====================
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = 'bot.log'
    
    # ==================== تنظیمات کش ====================
    CACHE_TIMEOUT = 300  # 5 دقیقه
    MAX_CACHE_SIZE = 1000
    
    # ==================== مناسبت‌های مهم ====================
    PERSIAN_EVENTS = {
        "1405-01-01": "عید نوروز 🎉",
        "1405-01-02": "عید نوروز",
        "1405-01-03": "عید نوروز", 
        "1405-01-04": "عید نوروز",
        "1405-01-12": "روز جمهوری اسلامی",
        "1405-01-13": "سیزده بدر",
        "1405-02-14": "رحلت امام خمینی",
        "1405-03-14": "شهادت دکتر چمران",
        "1405-04-07": "شهادت دکتر بهشتی",
        "1405-06-30": "عید غدیر خم",
        "1405-08-22": "تاسوعا",
        "1405-08-23": "عاشورا",
        "1405-09-20": "اربعین حسینی",
        "1405-10-08": "شهادت امام رضا",
        "1405-11-10": "شهادت امام حسن عسکری",
        "1405-12-08": "ولادت امام زمان"
    }
    
    # ==================== متدهای کمکی ====================
    
    @classmethod
    def get_exam_date(cls, exam_name):
        """دریافت تاریخ کنکور"""
        exam = cls.EXAMS.get(exam_name)
        if exam:
            return exam["date"]
        return None
    
    @classmethod
    def get_exam_emoji(cls, exam_name):
        """دریافت ایموجی کنکور"""
        exam = cls.EXAMS.get(exam_name)
        if exam:
            return exam["emoji"]
        return "📝"
    
    @classmethod
    def get_all_exam_names(cls):
        """دریافت لیست تمام نام کنکورها"""
        return list(cls.EXAMS.keys())
    
    @classmethod
    def is_exam_date(cls, date_str):
        """بررسی آیا تاریخ مربوط به کنکور است"""
        for exam_name, exam_data in cls.EXAMS.items():
            exam_date = exam_data["date"]
            if isinstance(exam_date, list):
                if date_str in exam_date:
                    return True
            else:
                if date_str == exam_date:
                    return True
        return False
    
    @classmethod
    def get_exam_by_date(cls, date_str):
        """دریافت نام کنکور بر اساس تاریخ"""
        for exam_name, exam_data in cls.EXAMS.items():
            exam_date = exam_data["date"]
            if isinstance(exam_date, list):
                if date_str in exam_date:
                    return exam_name
            else:
                if date_str == exam_date:
                    return exam_name
        return None
    
    @classmethod
    def get_current_jalali_date(cls):
        """دریافت تاریخ شمسی فعلی"""
        return jdatetime.datetime.now().strftime("%Y-%m-%d")
    
    @classmethod
    def get_current_jalali_datetime(cls):
        """دریافت تاریخ و زمان شمسی فعلی"""
        return jdatetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    @classmethod
    def get_days_until_exam(cls, exam_name):
        """محاسبه روزهای باقی‌مانده تا کنکور"""
        exam_date = cls.get_exam_date(exam_name)
        if not exam_date:
            return None
        
        if isinstance(exam_date, list):
            # برای کنکورهای با چند تاریخ، اولین تاریخ را در نظر می‌گیریم
            exam_date = exam_date[0]
        
        try:
            # تجزیه تاریخ شمسی
            exam_parts = exam_date.split(' ')[0].split('-')
            exam_year = int(exam_parts[0])
            exam_month = int(exam_parts[1])
            exam_day = int(exam_parts[2])
            
            # تاریخ فعلی
            now = jdatetime.datetime.now()
            
            # محاسبه اختلاف (ساده‌سازی شده)
            days_diff = (exam_year - now.year) * 365 + (exam_month - now.month) * 30 + (exam_day - now.day)
            return max(days_diff, 0)
        except:
            # در صورت خطا، مقدار پیش‌فرض برگردان
            exam_default_days = {
                "علوم تجربی": 260,
                "ریاضی‌وفنی": 259,
                "علوم انسانی": 259,
                "فرهنگیان": 180,
                "هنر": 260,
                "زبان‌وگروه‌های‌خارجه": 260
            }
            return exam_default_days.get(exam_name, 0)
    
    @classmethod
    def is_exam_passed(cls, exam_name):
        """بررسی آیا کنکور گذشته است یا نه"""
        days_until = cls.get_days_until_exam(exam_name)
        return days_until is not None and days_until <= 0
    
    @classmethod
    def get_study_recommendation(cls, days_until):
        """دریافت توصیه مطالعه بر اساس روزهای باقی‌مانده"""
        if days_until > 180:
            return "📅 زمان کافی داری! با برنامه‌ریزی منظم پیش برو."
        elif days_until > 90:
            return "⏳ نیمه راهی! روی نقاط ضعف تمرکز کن."
        elif days_until > 30:
            return "🚀 زمان محدود! تست‌زنی رو بیشتر کن."
        elif days_until > 7:
            return "🔥 فاز آخر! مرور سریع و تست زمان‌دار."
        elif days_until > 0:
            return "🎯 فردا کنکور داری! استراحت کن و آروم باش."
        else:
            return "✅ کنکور تموم شد! به خودت افتخار کن."
    
    @classmethod
    def get_progress_emoji(cls, percentage):
        """دریافت ایموجی مناسب برای درصد پیشرفت"""
        if percentage >= 90:
            return "🎉"
        elif percentage >= 75:
            return "✅"
        elif percentage >= 50:
            return "📈"
        elif percentage >= 25:
            return "⚠️"
        else:
            return "🔴"
    
    @classmethod
    def get_progress_level(cls, percentage):
        """دریافت سطح پیشرفت"""
        if percentage >= cls.PROGRESS_LEVELS['excellent']:
            return "عالی"
        elif percentage >= cls.PROGRESS_LEVELS['good']:
            return "خوب"
        elif percentage >= cls.PROGRESS_LEVELS['average']:
            return "متوسط"
        elif percentage >= cls.PROGRESS_LEVELS['weak']:
            return "ضعیف"
        else:
            return "بسیار ضعیف"
    
    @classmethod
    def validate_time_format(cls, time_str):
        """اعتبارسنجی فرمت زمان"""
        try:
            hours, minutes = map(int, time_str.split(':'))
            return 0 <= hours <= 23 and 0 <= minutes <= 59
        except:
            return False
    
    @classmethod
    def is_development(cls):
        """بررسی آیا محیط توسعه است"""
        return cls.ENVIRONMENT == 'development'
    
    @classmethod
    def is_production(cls):
        """بررسی آیا محیط تولید است"""
        return cls.ENVIRONMENT == 'production'
    
    @classmethod
    def is_testing(cls):
        """بررسی آیا محیط تست است"""
        return cls.ENVIRONMENT == 'testing'
    
    @classmethod
    def get_database_url(cls):
        """دریافت آدرس دیتابیس با توجه به محیط"""
        if cls.is_production():
            return os.environ.get('DATABASE_URL', cls.DATABASE_URL)
        return cls.DATABASE_URL
    
    @classmethod
    def get_webhook_url(cls):
        """دریافت آدرس وب‌هوک"""
        if cls.is_development():
            return os.environ.get('WEBHOOK_URL_DEV', cls.WEBHOOK_URL)
        return cls.WEBHOOK_URL
    
    @classmethod
    def validate_config(cls):
        """اعتبارسنجی تنظیمات"""
        errors = []
        warnings = []
        
        # بررسی توکن ربات
        if not cls.BOT_TOKEN or cls.BOT_TOKEN == "your_telegram_bot_token_here":
            errors.append("❌ BOT_TOKEN تنظیم نشده است")
        elif len(cls.BOT_TOKEN) < 10:
            errors.append("❌ BOT_TOKEN نامعتبر است")
        
        # بررسی آیدی ادمین
        if cls.ADMIN_ID == 0:
            errors.append("❌ ADMIN_ID تنظیم نشده است")
        elif cls.ADMIN_ID < 1000:
            warnings.append("⚠️ ADMIN_ID ممکن است نامعتبر باشد")
        
        # بررسی محیط
        if cls.ENVIRONMENT not in ['development', 'production', 'testing']:
            errors.append("❌ ENVIRONMENT باید development, production یا testing باشد")
        
        return errors, warnings
    
    @classmethod
    def print_config_summary(cls):
        """چاپ خلاصه تنظیمات"""
        print("=" * 60)
        print("🤖 تنظیمات ربات کنکور ۱۴۰۵")
        print("=" * 60)
        print(f"🔧 محیط: {cls.ENVIRONMENT}")
        print(f"🐛 حالت دیباگ: {cls.DEBUG}")
        print(f"📊 سطح لاگ: {cls.LOG_LEVEL}")
        print(f"🤵 ادمین: {cls.ADMIN_ID}")
        print(f"🌐 Webhook: {cls.WEBHOOK_URL}")
        print(f"💾 دیتابیس: {cls.DATABASE_URL}")
        print(f"🔐 حالت توسعه: {cls.DEVELOPER_MODE}")
        print(f"📅 تاریخ فعلی: {cls.get_current_jalali_datetime()}")
        print("=" * 60)
        
        # بررسی خطاها و هشدارها
        errors, warnings = cls.validate_config()
        
        if errors:
            print("❌ خطاهای تنظیمات:")
            for error in errors:
                print(f"   {error}")
            print()
        
        if warnings:
            print("⚠️ هشدارهای تنظیمات:")
            for warning in warnings:
                print(f"   {warning}")
            print()
        
        if not errors and not warnings:
            print("✅ تمام تنظیمات معتبر هستند")
        
        # نمایش کنکورها
        print("🎯 کنکورهای پشتیبانی شده:")
        for exam_name in cls.get_all_exam_names():
            days = cls.get_days_until_exam(exam_name)
            status = "✅ فعال" if days and days > 0 else "❌ گذشته"
            print(f"   {cls.get_exam_emoji(exam_name)} {exam_name}: {days} روز باقی مانده - {status}")
        
        print("=" * 60)
    
    @classmethod
    def get_config_for_admin(cls):
        """دریافت تنظیمات برای نمایش در پنل مدیریت"""
        return {
            'environment': cls.ENVIRONMENT,
            'debug_mode': cls.DEBUG,
            'log_level': cls.LOG_LEVEL,
            'admin_id': cls.ADMIN_ID,
            'webhook_url': cls.WEBHOOK_URL,
            'database_url': cls.DATABASE_URL[:20] + '...' if len(cls.DATABASE_URL) > 20 else cls.DATABASE_URL,
            'total_exams': len(cls.EXAMS),
            'active_exams': len([exam for exam in cls.EXAMS if not cls.is_exam_passed(exam)]),
            'bot_username': cls.BOT_USERNAME,
            'current_time': cls.get_current_jalali_datetime(),
            'has_jdatetime': True  # همیشه True چون از پیاده‌سازی داخلی استفاده می‌کنیم
        }

# تست تنظیمات
if __name__ == "__main__":
    Config.print_config_summary()
    
    # تست متدهای کمکی
    print("\n🧪 تست متدهای کمکی:")
    print(f"تاریخ جاری: {Config.get_current_jalali_datetime()}")
    
    for exam in Config.get_all_exam_names():
        days = Config.get_days_until_exam(exam)
        print(f"{Config.get_exam_emoji(exam)} {exam}: {days} روز باقی مانده")
    
    print(f"توصیه مطالعه: {Config.get_study_recommendation(100)}")
