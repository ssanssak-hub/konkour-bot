# check_compatibility.py
import importlib
import sys

def check_requirements():
    """بررسی سازگاری کتابخانه‌های نصب‌شده"""
    
    requirements = {
        'python-telegram-bot': '20.7',
        'sqlalchemy': '2.0.23',
        'flask': '2.3.3',
        'pandas': '2.1.1',
    }
    
    print("🔍 بررسی سازگاری کتابخانه‌ها...")
    
    for package, expected_version in requirements.items():
        try:
            module = importlib.import_module(package)
            actual_version = getattr(module, '__version__', 'N/A')
            
            if actual_version == expected_version:
                print(f"✅ {package}: {actual_version}")
            else:
                print(f"⚠️  {package}: {actual_version} (انتظار: {expected_version})")
                
        except ImportError:
            print(f"❌ {package}: نصب نشده")
    
    print(f"🐍 نسخه پایتون: {sys.version}")

if __name__ == "__main__":
    check_requirements()
