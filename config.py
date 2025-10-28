import os
from exam_data import EXAMS_1405, MOTIVATIONAL_MESSAGES, EXAM_GROUPS

BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# جملات انگیزشی
MOTIVATIONAL_MESSAGES = [
    "🎯 هر روز یک قدم نزدیک‌تر به هدف! تو می‌تونی!",
    "💪 همین لحظه‌هایی که درس می‌خونی، آینده‌تو می‌سازه!",
    "🚀 رقبای تو همین الان در حال مطالعه‌اند! تو هم ادامه بده!",
    "⭐ موفقیت ترکیبی از عشق، تلاش و پشتکار است!",
    "📚 این روزها می‌گذرد، اما نتیجه‌اش همیشه با تو می‌ماند!",
    "🔥 تو استعدادشو داری، فقط کافیه باور داشته باشی!",
    "🌈 بعد از هر تلاش سخت، نتیجۀ شیرین می‌رسد!",
    "🎓 به خودت ایمان داشته باش، تو قابلیت رسیدن به بهترین‌ها رو داری!",
]

# تنظیمات وب‌هوک
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
WEBAPP_HOST = os.environ.get("WEBAPP_HOST", "0.0.0.0")
WEBAPP_PORT = int(os.environ.get("PORT", 5000))
