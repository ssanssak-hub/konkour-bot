# install_requirements.py
import subprocess
import sys
import os

def install_requirements():
    """نصب هوشمند requirements با مدیریت خطا"""
    
    print("🚀 شروع نصب کتابخانه‌های ربات کنکور...")
    
    requirements_files = [
        ('requirements.txt', 'اصلی'),
    ]
    
    for file, description in requirements_files:
        if os.path.exists(file):
            print(f"\n📦 نصب {description}...")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", "-r", file
                ])
                print(f"✅ {description} با موفقیت نصب شد")
            except subprocess.CalledProcessError as e:
                print(f"❌ خطا در نصب {description}: {e}")
                return False
        else:
            print(f"⚠️ فایل {file} یافت نشد")
    
    print("\n🎉 تمام کتابخانه‌ها با موفقیت نصب شدند!")
    return True

if __name__ == "__main__":
    install_requirements()
