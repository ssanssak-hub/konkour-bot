import os
from dotenv import load_dotenv
# بارگذاری متغیرهای محیطی
load_dotenv()


BOT_TOKEN = os.environ.get("BOT_TOKEN", "8381121739:AAFB2YBMomBh9xhoI3Qn0VVuGaGlpea9fx8")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "7703672187"))

def get_bot_token():
    global _BOT_TOKEN
    if _BOT_TOKEN is None:
        _BOT_TOKEN = os.environ.get("BOT_TOKEN", "default_token")
    return _BOT_TOKEN

def get_admin_id():
    global _ADMIN_ID  
    if _ADMIN_ID is None:
        _ADMIN_ID = int(os.environ.get("ADMIN_ID", 123456789))
    return _ADMIN_ID

MOTIVATIONAL_MESSAGES = [
    "🎯 هر روز یک قدم نزدیک‌تر به هدف! تو می‌تونی!",
    "💪 همین لحظه‌هایی که درس می‌خونی، آینده‌تو می‌سازه!",
    "🚀 رقبای تو همین الان در حال مطالعه‌اند! تو هم ادامه بده!",
    "⭐ موفقیت ترکیبی از عشق، تلاش و پشتکار است!",
    "📚 این روزها می‌گذرد، اما نتیجه‌اش همیشه با تو می‌ماند!",
    "⚙ فردایی اگر باشد باید از آن تو باشد ، امروز دیروزت نباش، برنده صحرا!",
    "🔥 تو استعدادشو داری، فقط کافیه باور داشته باشی!",
    "🌈 بعد از هر تلاش سخت، نتیجۀ شیرین می‌رسد!",
    "🎓 به خودت ایمان داشته باش، تو قابلیت رسیدن به بهترین‌ها رو داری!",
    "💪 تو قوی‌تر از آنی که فکر می‌کنی!",
    "🚀 هر روز یک قدم به موفقیت نزدیک‌تر شو!",
    "🌟 استعداد تو با تلاش تو معنا پیدا می‌کنه!",
    "🎯 تمرکزت رو حفظ کن، هدف نزدیکه!",
    "📚 هر صفحه‌ای که می‌خونی، یک قدم به رویاهات نزدیک‌تری!",
    "🔥 امروز رو از دست نده، فردا دیره!",
    "💎 تو الماسی که نیاز به تراش داره!",
    "🌈 بعد از هر طوفانی، آفتاب درخشنده‌تری می‌تابه!",
    "🎓 موفقیت تو حتمیه، فقط باید ادامه بدی!",
    "⏰ زمان طلاست، از هر ثانیه استفاده کن!",
    "💯 امروز تلاش کن، فردا نتیجه ببین!",
    "🌟 رویاهات رو با تلاش به واقعیت تبدیل کن!",
    "📈 پیشرفت روزانه، موفقیت قطعی!",
    "🎪 زندگی یه سیرکه، تو هم شعبون‌بازی خودت رو داشته باش!",
    "💫 تو توانایی رسیدن به هر چیزی رو داری!"
]

def get_motivational_messages():
    return _MOTIVATIONAL_MESSAGES


# تنظیمات دیتابیس
BOT_TOKEN = get_bot_token()
ADMIN_ID = get_admin_id()
MOTIVATIONAL_MESSAGES = get_motivational_messages()
DATABASE_URL = os.environ.get("DATABASE_URL", "konkour_bot.db")
