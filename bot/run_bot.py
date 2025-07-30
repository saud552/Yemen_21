#!/usr/bin/env python3
"""
🚀 ملف تشغيل بوت Zphisher Telegram المتقدم
يتعامل مع تشغيل البوت وإدارة دورة الحياة
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path

# إضافة مسار المشروع
sys.path.append(str(Path(__file__).parent))

from main import main, logger

def signal_handler(signum, frame):
    """معالج إشارات النظام للإغلاق الآمن"""
    logger.info(f"تم استلام إشارة {signum}، جاري إيقاف البوت...")
    sys.exit(0)

def setup_signal_handlers():
    """إعداد معالجات إشارات النظام"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    try:
        # إعداد معالجات الإشارات
        setup_signal_handlers()
        
        # تشغيل البوت
        asyncio.run(main())
        
    except KeyboardInterrupt:
        logger.info("تم إيقاف البوت بواسطة المستخدم")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"خطأ فادح في تشغيل البوت: {e}")
        sys.exit(1)