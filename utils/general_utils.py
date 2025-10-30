"""
ابزارهای عمومی و کمکی
"""
from exam_data import EXAMS_1405
from datetime import datetime

def get_subject_emoji(subject: str) -> str:
    """
    دریافت ایموجی مناسب برای هر درس
    """
    emoji_map = {
        "ریاضی": "📐",
        "فیزیک": "⚡", 
        "شیمی": "🧪",
        "زیست": "🔬",
        "ادبیات": "📖",
        "عربی": "🕌",
        "دینی": "📿",
        "زبان": "🔠",
        "هنر": "🎨",
        "تاریخ": "📜",
        "جغرافیا": "🗺️",
        "فلسفه": "💭",
        "اقتصاد": "💹",
        "جامعه": "👥",
        "روانشناسی": "🧠",
        "مدیریت": "📊"
    }
    return emoji_map.get(subject, "📚")

def get_next_exam():
    """
    پیدا کردن نزدیک‌ترین آزمون آینده و بازگشت دیکشنری کامل
    """
    now = datetime.now()
    next_exam = None
    min_delta = None
    
    for exam_key, exam in EXAMS_1405.items():
        dates = exam["date"] if isinstance(exam["date"], list) else [exam["date"]]
        
        for date_tuple in dates:
            exam_date = datetime(*date_tuple)
            if exam_date > now:
                delta = exam_date - now
                if min_delta is None or delta < min_delta:
                    min_delta = delta
                    next_exam = {
                        'key': exam_key,
                        'name': exam['name'],
                        'date': exam_date,
                        'persian_date': exam['persian_date'],
                        'time': exam['time']
                    }
    
    return next_exam

def create_admin_stats_message() -> str:
    """
    ایجاد پیام آمار برای پنل مدیریت
    """
    return (
        "👑 <b>آمار مدیریتی ربات</b>\n\n"
        "📊 آمار کلی:\n"
        "• 👥 کاربران فعال: در حال بارگذاری...\n"
        "• 📚 جلسات مطالعه: در حال بارگذاری...\n"
        "• 🕒 زمان کل مطالعه: در حال بارگذاری...\n\n"
        "⚙️ سیستم عضویت اجباری:\n"
        "• 📢 کانال‌های فعال: در حال بارگذاری...\n"
        "• ✅ کاربران تأیید شده: در حال بارگذاری...\n"
        "• ❌ کاربران bloque شده: در حال بارگذاری..."
    )
