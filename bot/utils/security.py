"""
🛡️ نظام الأمان المتقدم لبوت Zphisher Telegram
يشمل المصادقة، إدارة الأذونات، والحماية من الهجمات
"""

import asyncio
import hashlib
import hmac
import time
import jwt
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from functools import wraps
from collections import defaultdict, deque

from aiogram import types
from aiogram.filters import BaseFilter

from ..config import settings
from ..database import db_manager, User, UserPermission

logger = logging.getLogger(__name__)

class AuthManager:
    """مدير المصادقة المتقدم مع دعم JWT والجلسات الآمنة"""
    
    def __init__(self):
        self.active_sessions: Dict[int, Dict[str, Any]] = {}
        self.failed_attempts: Dict[int, List[datetime]] = defaultdict(list)
        self.max_failed_attempts = 5
        self.lockout_duration = 3600  # ساعة واحدة
    
    async def authenticate_user(self, message: types.Message) -> Optional[User]:
        """مصادقة المستخدم وإنشاء جلسة"""
        user_id = message.from_user.id
        
        # فحص الحظر المؤقت
        if await self._is_locked_out(user_id):
            logger.warning(f"محاولة دخول من مستخدم محظور مؤقتاً: {user_id}")
            return None
        
        try:
            # الحصول على المستخدم من قاعدة البيانات
            user = await db_manager.get_user_by_id(user_id)
            
            if not user:
                # إنشاء مستخدم جديد إذا لم يكن موجوداً
                user = await self._create_new_user(message)
            
            # التحقق من حالة المستخدم
            if not await self._validate_user_status(user):
                await self._record_failed_attempt(user_id)
                return None
            
            # إنشاء جلسة آمنة
            await self._create_user_session(user)
            
            # تحديث آخر ظهور
            await db_manager.update_user_last_seen(user_id)
            
            # تسجيل نجاح العملية
            await db_manager.log_event(
                user_id=user_id,
                event_type="auth",
                event_action="login_success",
                event_description="تم تسجيل الدخول بنجاح",
                ip_address=self._get_user_ip(message),
                user_agent=self._get_user_agent(message)
            )
            
            return user
            
        except Exception as e:
            logger.error(f"خطأ في مصادقة المستخدم {user_id}: {e}")
            await self._record_failed_attempt(user_id)
            return None
    
    async def _create_new_user(self, message: types.Message) -> User:
        """إنشاء مستخدم جديد"""
        user_data = {
            'user_id': message.from_user.id,
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name,
            'language_code': message.from_user.language_code or 'en',
            'role': 'viewer',  # الدور الافتراضي
            'is_active': True,
            'is_banned': False
        }
        
        # التحقق من كون المستخدم مسؤول
        if settings.is_admin(message.from_user.id):
            user_data['role'] = 'admin'
        
        if settings.is_super_admin(message.from_user.id):
            user_data['role'] = 'super_admin'
        
        return await db_manager.create_user(user_data)
    
    async def _validate_user_status(self, user: User) -> bool:
        """التحقق من حالة المستخدم"""
        if user.is_banned:
            logger.info(f"محاولة دخول من مستخدم محظور: {user.user_id}")
            return False
        
        if not user.is_active:
            logger.info(f"محاولة دخول من مستخدم غير مفعل: {user.user_id}")
            return False
        
        return True
    
    async def _create_user_session(self, user: User) -> str:
        """إنشاء جلسة آمنة للمستخدم"""
        session_token = self._generate_session_token(user)
        
        session_data = {
            'user_id': user.user_id,
            'role': user.role,
            'created_at': datetime.utcnow(),
            'last_activity': datetime.utcnow(),
            'token': session_token
        }
        
        self.active_sessions[user.user_id] = session_data
        
        return session_token
    
    def _generate_session_token(self, user: User) -> str:
        """إنتاج رمز جلسة آمن"""
        payload = {
            'user_id': user.user_id,
            'role': user.role,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(seconds=settings.SESSION_LIFETIME)
        }
        
        return jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256')
    
    async def _record_failed_attempt(self, user_id: int) -> None:
        """تسجيل محاولة فاشلة"""
        now = datetime.utcnow()
        self.failed_attempts[user_id].append(now)
        
        # إزالة المحاولات القديمة
        cutoff = now - timedelta(seconds=self.lockout_duration)
        self.failed_attempts[user_id] = [
            attempt for attempt in self.failed_attempts[user_id] 
            if attempt > cutoff
        ]
        
        # تسجيل في قاعدة البيانات
        await db_manager.log_event(
            user_id=user_id,
            event_type="auth",
            event_action="login_failed",
            event_description="محاولة تسجيل دخول فاشلة",
            severity="warning"
        )
    
    async def _is_locked_out(self, user_id: int) -> bool:
        """التحقق من الحظر المؤقت"""
        if user_id not in self.failed_attempts:
            return False
        
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=self.lockout_duration)
        
        # إزالة المحاولات القديمة
        self.failed_attempts[user_id] = [
            attempt for attempt in self.failed_attempts[user_id] 
            if attempt > cutoff
        ]
        
        return len(self.failed_attempts[user_id]) >= self.max_failed_attempts
    
    def _get_user_ip(self, message: types.Message) -> Optional[str]:
        """الحصول على عنوان IP للمستخدم (محدود في Telegram)"""
        # Telegram لا يوفر عنوان IP مباشرة
        return None
    
    def _get_user_agent(self, message: types.Message) -> Optional[str]:
        """الحصول على User Agent للمستخدم"""
        # إنشاء user agent وهمي بناءً على معلومات Telegram
        if message.from_user:
            return f"Telegram Bot API - User {message.from_user.id}"
        return "Telegram Bot API"
    
    async def logout_user(self, user_id: int) -> None:
        """تسجيل خروج المستخدم"""
        if user_id in self.active_sessions:
            del self.active_sessions[user_id]
            
            await db_manager.log_event(
                user_id=user_id,
                event_type="auth",
                event_action="logout",
                event_description="تم تسجيل الخروج"
            )
    
    def is_session_valid(self, user_id: int) -> bool:
        """التحقق من صحة الجلسة"""
        if user_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[user_id]
        created_at = session['created_at']
        
        # التحقق من انتهاء صلاحية الجلسة
        if datetime.utcnow() - created_at > timedelta(seconds=settings.SESSION_LIFETIME):
            del self.active_sessions[user_id]
            return False
        
        return True
    
    async def refresh_session(self, user_id: int) -> None:
        """تحديث نشاط الجلسة"""
        if user_id in self.active_sessions:
            self.active_sessions[user_id]['last_activity'] = datetime.utcnow()

class PermissionManager:
    """مدير الأذونات المتقدم مع دعم الأذونات المعقدة"""
    
    def __init__(self):
        self.permission_cache: Dict[int, Dict[str, bool]] = {}
        self.cache_ttl = 300  # 5 دقائق
    
    async def check_permission(
        self, 
        user_id: int, 
        permission: str, 
        resource: Optional[str] = None
    ) -> bool:
        """فحص إذن محدد للمستخدم"""
        
        # فحص التخزين المؤقت
        cache_key = f"{user_id}:{permission}:{resource or 'global'}"
        if await self._get_from_cache(cache_key):
            return True
        
        try:
            # الحصول على المستخدم
            user = await db_manager.get_user_by_id(user_id)
            if not user or not user.can_view_data():
                return False
            
            # فحص الأذونات الأساسية حسب الدور
            if await self._check_role_permission(user.role, permission):
                await self._set_cache(cache_key, True)
                return True
            
            # فحص الأذونات المخصصة
            custom_permission = await self._check_custom_permission(
                user_id, permission, resource
            )
            
            if custom_permission:
                await self._set_cache(cache_key, True)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"خطأ في فحص الأذونات للمستخدم {user_id}: {e}")
            return False
    
    async def _check_role_permission(self, role: str, permission: str) -> bool:
        """فحص أذونات الدور الأساسية"""
        role_permissions = {
            'super_admin': [
                'admin.*', 'session.*', 'user.*', 'system.*', 'view.*'
            ],
            'admin': [
                'session.*', 'user.view', 'user.manage', 'view.*', 'system.view'
            ],
            'operator': [
                'session.create', 'session.manage', 'session.view', 'view.*'
            ],
            'viewer': [
                'session.view', 'view.own_data'
            ]
        }
        
        if role not in role_permissions:
            return False
        
        permissions = role_permissions[role]
        
        for perm in permissions:
            if perm.endswith('.*'):
                # إذن عام للفئة
                if permission.startswith(perm[:-2]):
                    return True
            elif perm == permission:
                # إذن محدد
                return True
        
        return False
    
    async def _check_custom_permission(
        self, 
        user_id: int, 
        permission: str, 
        resource: Optional[str]
    ) -> bool:
        """فحص الأذونات المخصصة"""
        try:
            from sqlalchemy import select, and_
            from ..database import get_session
            
            async with get_session() as session:
                stmt = select(UserPermission).where(
                    and_(
                        UserPermission.user_id == user_id,
                        UserPermission.permission == permission,
                        UserPermission.granted == True
                    )
                )
                
                if resource:
                    stmt = stmt.where(UserPermission.resource == resource)
                
                result = await session.execute(stmt)
                user_permission = result.scalar_one_or_none()
                
                if user_permission and user_permission.is_valid():
                    return True
                
                return False
                
        except Exception as e:
            logger.error(f"خطأ في فحص الأذونات المخصصة: {e}")
            return False
    
    async def grant_permission(
        self, 
        user_id: int, 
        permission: str, 
        granted_by: int,
        resource: Optional[str] = None,
        expires_at: Optional[datetime] = None
    ) -> bool:
        """منح إذن للمستخدم"""
        try:
            from ..database import get_session
            
            async with get_session() as session:
                # فحص وجود الإذن مسبقاً
                existing = await session.scalar(
                    select(UserPermission).where(
                        and_(
                            UserPermission.user_id == user_id,
                            UserPermission.permission == permission,
                            UserPermission.resource == resource
                        )
                    )
                )
                
                if existing:
                    # تحديث الإذن الموجود
                    existing.granted = True
                    existing.granted_by = granted_by
                    existing.granted_at = datetime.utcnow()
                    existing.expires_at = expires_at
                else:
                    # إنشاء إذن جديد
                    new_permission = UserPermission(
                        user_id=user_id,
                        permission=permission,
                        resource=resource,
                        granted=True,
                        granted_by=granted_by,
                        expires_at=expires_at
                    )
                    session.add(new_permission)
                
                await session.commit()
                
                # تسجيل العملية
                await db_manager.log_event(
                    user_id=granted_by,
                    event_type="permission",
                    event_action="granted",
                    event_description=f"تم منح إذن {permission} للمستخدم {user_id}",
                    metadata={
                        "target_user": user_id,
                        "permission": permission,
                        "resource": resource
                    }
                )
                
                # إزالة من التخزين المؤقت
                await self._invalidate_user_cache(user_id)
                
                return True
                
        except Exception as e:
            logger.error(f"خطأ في منح الإذن: {e}")
            return False
    
    async def revoke_permission(
        self, 
        user_id: int, 
        permission: str, 
        revoked_by: int,
        resource: Optional[str] = None
    ) -> bool:
        """سحب إذن من المستخدم"""
        try:
            from sqlalchemy import update, and_
            from ..database import get_session
            
            async with get_session() as session:
                stmt = (
                    update(UserPermission)
                    .where(
                        and_(
                            UserPermission.user_id == user_id,
                            UserPermission.permission == permission,
                            UserPermission.resource == resource
                        )
                    )
                    .values(granted=False, updated_at=datetime.utcnow())
                )
                
                result = await session.execute(stmt)
                await session.commit()
                
                if result.rowcount > 0:
                    # تسجيل العملية
                    await db_manager.log_event(
                        user_id=revoked_by,
                        event_type="permission",
                        event_action="revoked",
                        event_description=f"تم سحب إذن {permission} من المستخدم {user_id}",
                        metadata={
                            "target_user": user_id,
                            "permission": permission,
                            "resource": resource
                        }
                    )
                    
                    # إزالة من التخزين المؤقت
                    await self._invalidate_user_cache(user_id)
                    
                    return True
                
                return False
                
        except Exception as e:
            logger.error(f"خطأ في سحب الإذن: {e}")
            return False
    
    async def _get_from_cache(self, cache_key: str) -> bool:
        """الحصول على قيمة من التخزين المؤقت"""
        if hasattr(self, '_cache_timestamps'):
            if cache_key in self._cache_timestamps:
                timestamp = self._cache_timestamps[cache_key]
                if time.time() - timestamp < self.cache_ttl:
                    return cache_key in self.permission_cache
                else:
                    # إزالة البيانات المنتهية الصلاحية
                    if cache_key in self.permission_cache:
                        del self.permission_cache[cache_key]
                    del self._cache_timestamps[cache_key]
        return False
    
    async def _set_cache(self, cache_key: str, value: bool) -> None:
        """حفظ قيمة في التخزين المؤقت"""
        if not hasattr(self, '_cache_timestamps'):
            self._cache_timestamps = {}
        
        self.permission_cache[cache_key] = value
        self._cache_timestamps[cache_key] = time.time()
    
    async def _invalidate_user_cache(self, user_id: int) -> None:
        """إزالة تخزين المستخدم المؤقت"""
        keys_to_remove = [
            key for key in self.permission_cache.keys() 
            if key.startswith(f"{user_id}:")
        ]
        
        for key in keys_to_remove:
            if key in self.permission_cache:
                del self.permission_cache[key]
            if hasattr(self, '_cache_timestamps') and key in self._cache_timestamps:
                del self._cache_timestamps[key]

class RateLimiter:
    """نظام الحد من المعدل المتقدم"""
    
    def __init__(self):
        self.user_requests: Dict[int, deque] = defaultdict(lambda: deque())
        self.blocked_users: Dict[int, datetime] = {}
    
    async def is_rate_limited(self, user_id: int) -> bool:
        """فحص الحد من المعدل للمستخدم"""
        now = datetime.utcnow()
        
        # فحص الحظر المؤقت
        if user_id in self.blocked_users:
            if now < self.blocked_users[user_id]:
                return True
            else:
                del self.blocked_users[user_id]
        
        # تنظيف الطلبات القديمة
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)
        
        user_queue = self.user_requests[user_id]
        
        # إزالة الطلبات القديمة
        while user_queue and user_queue[0] < hour_ago:
            user_queue.popleft()
        
        # عد الطلبات في الدقيقة الأخيرة
        minute_requests = sum(1 for req_time in user_queue if req_time >= minute_ago)
        
        # فحص الحدود
        if minute_requests >= settings.RATE_LIMIT_PER_MINUTE:
            # حظر مؤقت لمدة 5 دقائق
            self.blocked_users[user_id] = now + timedelta(minutes=5)
            
            await db_manager.log_event(
                user_id=user_id,
                event_type="security",
                event_action="rate_limit_exceeded",
                event_description="تم تجاوز حد المعدل المسموح",
                severity="warning"
            )
            
            return True
        
        if len(user_queue) >= settings.RATE_LIMIT_PER_HOUR:
            return True
        
        # تسجيل الطلب الحالي
        user_queue.append(now)
        
        return False
    
    async def add_request(self, user_id: int) -> None:
        """إضافة طلب جديد للمستخدم"""
        now = datetime.utcnow()
        self.user_requests[user_id].append(now)

# مرشحات الأمان المخصصة
class AdminFilter(BaseFilter):
    """مرشح للمسؤولين فقط"""
    
    async def __call__(self, message: types.Message) -> bool:
        return settings.is_admin(message.from_user.id)

class SuperAdminFilter(BaseFilter):
    """مرشح للمسؤول الرئيسي فقط"""
    
    async def __call__(self, message: types.Message) -> bool:
        return settings.is_super_admin(message.from_user.id)

class PermissionFilter(BaseFilter):
    """مرشح للأذونات المخصصة"""
    
    def __init__(self, permission: str, resource: Optional[str] = None):
        self.permission = permission
        self.resource = resource
    
    async def __call__(self, message: types.Message) -> bool:
        permission_manager = PermissionManager()
        return await permission_manager.check_permission(
            message.from_user.id, 
            self.permission, 
            self.resource
        )

# الديكوريتر للأمان
def require_auth(func: Callable) -> Callable:
    """ديكوريتر لطلب المصادقة"""
    @wraps(func)
    async def wrapper(message: types.Message, *args, **kwargs):
        auth_manager = AuthManager()
        user = await auth_manager.authenticate_user(message)
        
        if not user:
            await message.answer(
                "❌ غير مسموح لك بالوصول إلى هذه الوظيفة.",
                reply_markup=types.ReplyKeyboardRemove()
            )
            return
        
        # تحديث نشاط الجلسة
        await auth_manager.refresh_session(user.user_id)
        
        return await func(message, user, *args, **kwargs)
    
    return wrapper

def require_permission(permission: str, resource: Optional[str] = None):
    """ديكوريتر لطلب إذن محدد"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(message: types.Message, *args, **kwargs):
            permission_manager = PermissionManager()
            
            if not await permission_manager.check_permission(
                message.from_user.id, permission, resource
            ):
                await message.answer(
                    f"❌ لا تملك الإذن المطلوب: {permission}",
                    reply_markup=types.ReplyKeyboardRemove()
                )
                return
            
            return await func(message, *args, **kwargs)
        
        return wrapper
    return decorator

def rate_limit(func: Callable) -> Callable:
    """ديكوريتر للحد من المعدل"""
    @wraps(func)
    async def wrapper(message: types.Message, *args, **kwargs):
        rate_limiter = RateLimiter()
        
        if await rate_limiter.is_rate_limited(message.from_user.id):
            await message.answer(
                "⏳ تم تجاوز الحد المسموح من الطلبات. يرجى الانتظار قليلاً.",
                reply_markup=types.ReplyKeyboardRemove()
            )
            return
        
        await rate_limiter.add_request(message.from_user.id)
        return await func(message, *args, **kwargs)
    
    return wrapper

# مثيلات عامة
auth_manager = AuthManager()
permission_manager = PermissionManager()
rate_limiter = RateLimiter()