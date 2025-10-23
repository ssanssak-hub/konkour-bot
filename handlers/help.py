from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    help_text = (
        "📚 راهنمای کامل ربات کنکور ۱۴۰۵\n\n"
        
        "🎯 **دکمه 'چند روز تا کنکور؟'**\n"
        "• نمایش زمان باقی‌مانده تا کنکورهای مختلف\n"
        "• امکان بروزرسانی لحظه‌ای\n"
        "• نمایش هر دو تاریخ کنکور فرهنگیان\n"
        "• دریافت توصیه‌های مطالعاتی\n\n"
        
        "📅 **دکمه 'تقویم و رویدادها'**\n"
        "• تقویم شمسی کامل\n"
        "• نمایش مناسبت‌های ایران و جهان\n"
        "• مدیریت رویدادهای شخصی\n"
        "• قابلیت مشاهده ماه‌های قبل و بعد\n\n"
        
        "🔔 **دکمه 'مدیریت یادآوری‌ها'**\n"
        "• یادآوری کنکور: ارسال زمان باقی‌مانده\n"
        "• یادآوری متفرقه: پیام‌های دلخواه\n"
        "• یادآوری مطالعه: برنامه‌ریزی درسی\n"
        "• مدیریت کامل یادآوری‌ها\n\n"
        
        "📨 **دکمه 'ارسال پیام'**\n"
        "• ارسال پیام به ادمین اصلی\n"
        "• ارسال به همه ادمین‌ها\n"
        "• مدیریت پیام‌های ارسالی\n"
        "• قابلیت ویرایش و حذف\n\n"
        
        "✅ **دکمه 'اعلام حضور'**\n"
        "• ثبت حضور روزانه\n"
        "• مشاهده آمار حضور\n"
        "• نمایش لیست حاضرین\n"
        "• بروزرسانی لحظه‌ای\n\n"
        
        "📚 **دکمه 'اهداف و برنامه‌ریزی'**\n"
        "• ثبت اهداف روزانه/هفتگی/ماهانه\n"
        "• ثبت جلسات مطالعه\n"
        "• زمان‌سنج مطالعه\n"
        "• مدیریت کامل برنامه‌ها\n\n"
        
        "📊 **دکمه 'آمار و گزارش'**\n"
        "• آمار مطالعه شخصی\n"
        "• نمودارهای پیشرفت\n"
        "• مقایسه با برترین‌ها\n"
        "• گزارش‌های کامل\n\n"
        
        "🔧 **دکمه 'پنل مدیریت'**\n"
        "• مخصوص ادمین‌های ربات\n"
        "• مدیریت کاربران\n"
        "• ارسال پیام همگانی\n"
        "• آمار کلی سیستم\n\n"
        
        "💡 **نکات مهم:**\n"
        "• از دکمه‌های بازگشت برای Navigation استفاده کنید\n"
        "• داده‌ها در سرور امن ذخیره می‌شوند\n"
        "• برای گزارش مشکل به ادمین پیام بدهید\n"
        "• ربات به صورت ۲۴/۷ فعال است\n\n"
        
        "📞 **پشتیبانی:**\n"
        "برای ارتباط با پشتیبانی از دکمه 'ارسال پیام' استفاده کنید."
    )
    
    keyboard = [
        [InlineKeyboardButton("🎯 شروع کار با ربات", callback_data="getting_started")],
        [InlineKeyboardButton("❓ سوالات متداول", callback_data="faq")],
        [InlineKeyboardButton("📞 تماس با پشتیبانی", callback_data="send_message")],
        [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(help_text, reply_markup=reply_markup)

async def getting_started(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    guide_text = (
        "🎯 راهنمای شروع سریع\n\n"
        
        "۱. **اولین قدم: ثبت حضور** ✅\n"
        "   از منوی اصلی روی 'اعلام حضور' بزنید\n"
        "   این کار هر روز انگیزه‌تان را حفظ می‌کند\n\n"
        
        "۲. **تنظیم اهداف مطالعه** 🎯\n"
        "   به بخش 'اهداف و برنامه‌ریزی' بروید\n"
        "   یک هدف روزانه یا هفتگی تنظیم کنید\n"
        "   مثال: 'مطالعه ۳ ساعت ریاضی در روز'\n\n"
        
        "۳. **استفاده از زمان‌سنج** ⏱️\n"
        "   برای هر جلسه مطالعه زمان‌سنج تنظیم کنید\n"
        "   پیشرفت خود را实时 مشاهده کنید\n\n"
        
        "۴. **تنظیم یادآوری** 🔔\n"
        "   برای کنکور و مطالعه یادآوری بگذارید\n"
        "   ربات سر وقت به شما یادآوری می‌کند\n\n"
        
        "۵. **پیگیری پیشرفت** 📊\n"
        "   هر هفته به بخش 'آمار و گزارش' سر بزنید\n"
        "   نمودارهای پیشرفت را بررسی کنید\n\n"
        
        "۶. **مقایسه با دیگران** 🏆\n"
        "   ببینید چقدر از برترین‌ها فاصله دارید\n"
        "   این کار انگیزه شما را افزایش می‌دهد\n\n"
        
        "💪 **نکته انگیزشی:**\n"
        "هر روز حتی ۱ ساعت مطالعه بهتر از هیچ است!\n"
        "ثبات مهم‌تر از شدت مطالعه است."
    )
    
    keyboard = [
        [InlineKeyboardButton("📚 راهنمای کامل", callback_data="help")],
        [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(guide_text, reply_markup=reply_markup)

async def show_faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    faq_text = (
        "❓ سوالات متداول\n\n"
        
        "🔸 **چگونه یادآوری تنظیم کنم؟**\n"
        "به بخش 'مدیریت یادآوری‌ها' بروید و نوع یادآوری را انتخاب کنید\n\n"
        
        "🔸 **آیا می‌توانم برنامه مطالعه ام را ذخیره کنم؟**\n"
        "بله، در بخش 'اهداف و برنامه‌ریزی' می‌توانید برنامه‌ها را ذخیره کنید\n\n"
        
        "🔸 **چگونه با ادمین تماس بگیرم؟**\n"
        "از بخش 'ارسال پیام' استفاده کنید\n\n"
        
        "🔸 **آیا داده‌های من امن هستند؟**\n"
        "بله، تمام داده‌ها در سرورهای امن ذخیره می‌شوند\n\n"
        
        "🔸 **چگونه پیشرفتم را ببینم؟**\n"
        "به بخش 'آمار و گزارش' مراجعه کنید\n\n"
        
        "🔸 **آیا می‌توانم برنامه‌ها را ویرایش کنم؟**\n"
        "بله، در بخش مدیریت هر آیتم امکان ویرایش وجود دارد\n\n"
        
        "🔸 **ربات چه ساعاتی فعال است؟**\n"
        "ربات ۲۴ ساعته و ۷ روز هفته فعال است\n\n"
        
        "🔸 **چگونه باگ گزارش دهم؟**\n"
        "از طریق 'ارسال پیام' به ادمین گزارش دهید"
    )
    
    keyboard = [
        [InlineKeyboardButton("📞 تماس با پشتیبانی", callback_data="send_message")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="help")],
        [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(faq_text, reply_markup=reply_markup)

def setup_help_handlers(application):
    application.add_handler(CallbackQueryHandler(help_menu, pattern="^help$"))
    application.add_handler(CallbackQueryHandler(getting_started, pattern="^getting_started$"))
    application.add_handler(CallbackQueryHandler(show_faq, pattern="^faq$"))
