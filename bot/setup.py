#!/usr/bin/env python3
"""
⚙️ ملف إعداد وتثبيت بوت Zphisher Telegram
يقوم بإعداد البيئة وتثبيت المتطلبات
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """فحص إصدار Python"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 أو أحدث مطلوب!")
        print(f"الإصدار الحالي: {sys.version}")
        sys.exit(1)
    else:
        print(f"✅ Python {sys.version.split()[0]} - مناسب")

def install_requirements():
    """تثبيت المتطلبات"""
    requirements_file = Path("requirements.txt")
    
    if not requirements_file.exists():
        print("❌ ملف requirements.txt غير موجود!")
        sys.exit(1)
    
    print("📦 جاري تثبيت المتطلبات...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ تم تثبيت جميع المتطلبات بنجاح")
    except subprocess.CalledProcessError:
        print("❌ فشل في تثبيت المتطلبات!")
        sys.exit(1)

def create_directories():
    """إنشاء المجلدات المطلوبة"""
    directories = [
        "logs",
        "data",
        "uploads", 
        "temp",
        "backups",
        "ssl"
    ]
    
    print("📁 جاري إنشاء المجلدات...")
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ تم إنشاء مجلد: {directory}")

def setup_env_file():
    """إعداد ملف البيئة"""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if not env_example.exists():
        print("❌ ملف .env.example غير موجود!")
        return
    
    if not env_file.exists():
        print("📝 جاري إنشاء ملف .env...")
        shutil.copy(env_example, env_file)
        print("✅ تم إنشاء ملف .env من .env.example")
        print("⚠️  يرجى تعديل ملف .env وإضافة البيانات المطلوبة!")
    else:
        print("ℹ️  ملف .env موجود بالفعل")

def check_dependencies():
    """فحص التبعيات الخارجية"""
    print("🔍 جاري فحص التبعيات الخارجية...")
    
    # قائمة الأدوات المطلوبة (اختيارية)
    tools = {
        "cloudflared": "Cloudflare Tunnel",
        "loclx": "LocalXpose",
        "ngrok": "Ngrok"
    }
    
    for tool, description in tools.items():
        if shutil.which(tool):
            print(f"✅ {description} ({tool}) - موجود")
        else:
            print(f"⚠️  {description} ({tool}) - غير موجود (اختياري)")

def main():
    """الدالة الرئيسية للإعداد"""
    print("🤖 مرحباً بك في إعداد بوت Zphisher Telegram المتقدم")
    print("=" * 50)
    
    # فحص إصدار Python
    check_python_version()
    
    # إنشاء المجلدات
    create_directories()
    
    # إعداد ملف البيئة
    setup_env_file()
    
    # تثبيت المتطلبات
    install_requirements()
    
    # فحص التبعيات
    check_dependencies()
    
    print("\n" + "=" * 50)
    print("🎉 تم إعداد البوت بنجاح!")
    print("\n📋 الخطوات التالية:")
    print("1. تعديل ملف .env وإضافة رمز البوت")
    print("2. تعديل مسار Zphisher في ملف .env")
    print("3. تشغيل البوت: python run_bot.py")
    print("\n🔗 للمساعدة: اقرأ ملف README.md")

if __name__ == "__main__":
    main()