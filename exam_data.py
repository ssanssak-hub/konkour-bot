"""
اطلاعات کنکورهای ۱۴۰۵
تمامی تاریخ‌ها به صورت میلادی ذخیره شده‌اند
"""

EXAMS_1405 = {
    "علوم_انسانی": {
        "name": "کنکور علوم انسانی",
        "date": (2026, 6, 30),  # 11 تیر 1405
        "time": "08:00",
        "persian_date": "۱۱ تیر ۱۴۰۵",
        "group": "انسانی_ریاضی"
    },
    "ریاضی_فنی": {
        "name": "کنکور ریاضی و فنی",
        "date": (2026, 6, 30),  # 11 تیر 1405
        "time": "08:00",
        "persian_date": "۱۱ تیر ۱۴۰۵",
        "group": "انسانی_ریاضی"
    },
    "فرهنگیان": {
        "name": "کنکور فرهنگیان",
        "date": [(2026, 5, 6), (2026, 5, 7)],  # 17 و 18 اردیبهشت 1405
        "time": "08:00",
        "persian_date": "۱۷ و ۱۸ اردیبهشت ۱۴۰۵",
        "group": "فرهنگیان"
    },
    "علوم_تجربی": {
        "name": "کنکور علوم تجربی",
        "date": (2026, 7, 1),  # 12 تیر 1405
        "time": "08:00",
        "persian_date": "۱۲ تیر ۱۴۰۵",
        "group": "سایر"
    },
    "هنر": {
        "name": "کنکور هنر",
        "date": (2026, 7, 1),  # 12 تیر 1405
        "time": "08:00",
        "persian_date": "۱۲ تیر ۱۴۰۵",
        "group": "سایر"
    },
    "زبان_خارجه": {
        "name": "کنکور زبان و گروه‌های خارجه",
        "date": (2026, 7, 1),  # 12 تیر 1405
        "time": "14:30",
        "persian_date": "۱۲ تیر ۱۴۰۵",
        "group": "سایر"
    }
}

# گروه‌بندی کنکورها برای نمایش بهتر
EXAM_GROUPS = {
    "انسانی_ریاضی": {
        "name": "گروه علوم انسانی و ریاضی فنی",
        "exams": ["علوم_انسانی", "ریاضی_فنی"],
        "date": (2026, 6, 30),
        "time": "08:00",
        "persian_date": "۱۱ تیر ۱۴۰۵"
    },
    "فرهنگیان": {
        "name": "کنکور فرهنگیان",
        "exams": ["فرهنگیان"],
        "date": [(2026, 5, 6), (2026, 5, 7)],
        "time": "08:00",
        "persian_date": "۱۷ و ۱۸ اردیبهشت ۱۴۰۵"
    },
    "سایر": {
        "name": "سایر کنکورها (علوم تجربی، هنر، زبان)",
        "exams": ["علوم_تجربی", "هنر", "زبان_خارجه"],
        "date": (2026, 7, 1),
        "time": "08:00",  # توجه: زبان ساعت 14:30 است
        "persian_date": "۱۲ تیر ۱۴۰۵"
    }
}

# اطلاعات اضافی درباره کنکور
EXAM_INFO = {
    "سال": 1405,
    "مرجع": "سازمان سنجش آموزش کشور",
    "تاریخ_اعلام": "بهار ۱۴۰۴",
    "تعداد_گروه": 5,
    "تاریخ_ثبت_نام": "اسفند ۱۴۰۴ تا فروردین ۱۴۰۵",
    "تاریخ_اعلام_نتایج": "مرداد ۱۴۰۵"
}

def get_exam_by_name(persian_name: str) -> dict:
    """دریافت اطلاعات کنکور بر اساس نام فارسی"""
    name_mapping = {
        "علوم انسانی": "علوم_انسانی",
        "ریاضی": "ریاضی_فنی",
        "فرهنگیان": "فرهنگیان",
        "علوم تجربی": "علوم_تجربی",
        "هنر": "هنر",
        "زبان": "زبان_خارجه"
    }
    
    exam_key = name_mapping.get(persian_name)
    return EXAMS_1405.get(exam_key) if exam_key else None

def get_all_exams_list() -> list:
    """دریافت لیست تمامی کنکورها"""
    return [
        {
            "name": exam_data["name"],
            "date": exam_data["date"],
            "time": exam_data["time"],
            "persian_date": exam_data["persian_date"],
            "key": exam_key
        }
        for exam_key, exam_data in EXAMS_1405.items()
    ]

def get_upcoming_exams() -> list:
    """دریافت لیست کنکورهای آینده"""
    from datetime import datetime
    now = datetime.now()
    
    upcoming = []
    for exam_key, exam_data in EXAMS_1405.items():
        if isinstance(exam_data["date"], list):
            # برای کنکور فرهنگیان که دو تاریخ دارد
            for date_item in exam_data["date"]:
                exam_date = datetime(*date_item)
                if now < exam_date:
                    upcoming.append({
                        "name": exam_data["name"],
                        "date": exam_date,
                        "time": exam_data["time"],
                        "persian_date": exam_data["persian_date"]
                    })
        else:
            exam_date = datetime(*exam_data["date"])
            if now < exam_date:
                upcoming.append({
                    "name": exam_data["name"],
                    "date": exam_date,
                    "time": exam_data["time"],
                    "persian_date": exam_data["persian_date"]
                })
    
    # مرتب‌سازی بر اساس تاریخ
    upcoming.sort(key=lambda x: x["date"])
    return upcoming

def get_exam_group_info(group_key: str) -> dict:
    """دریافت اطلاعات گروه کنکور"""
    return EXAM_GROUPS.get(group_key, {})
