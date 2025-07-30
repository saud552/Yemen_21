"""
🔗 نظام إدارة اتصالات قاعدة البيانات
يدعم العمليات غير المتزامنة والتجميع (pooling) المتقدم
"""

import asyncio
import logging
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import event
from contextlib import asynccontextmanager

from ..config import settings

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """مدير اتصال قاعدة البيانات المتقدم"""
    
    def __init__(self):
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker] = None
        self._is_initialized = False
    
    async def initialize(self) -> None:
        """تهيئة اتصال قاعدة البيانات"""
        if self._is_initialized:
            return
        
        try:
            # إعداد محرك قاعدة البيانات
            connect_args = {}
            if settings.DATABASE_URL.startswith("sqlite"):
                connect_args = {
                    "check_same_thread": False,
                    "timeout": 30
                }
            
            self._engine = create_async_engine(
                settings.DATABASE_URL,
                echo=settings.DATABASE_ECHO,
                pool_size=settings.DATABASE_POOL_SIZE,
                max_overflow=settings.DATABASE_MAX_OVERFLOW,
                connect_args=connect_args,
                poolclass=StaticPool if "sqlite" in settings.DATABASE_URL else None
            )
            
            # إعداد مصنع الجلسات
            self._session_factory = async_sessionmaker(
                bind=self._engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=True,
                autocommit=False
            )
            
            # تسجيل أحداث قاعدة البيانات للمراقبة
            @event.listens_for(self._engine.sync_engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                """تحسين إعدادات SQLite للأداء"""
                if "sqlite" in settings.DATABASE_URL:
                    cursor = dbapi_connection.cursor()
                    # تحسينات الأداء
                    cursor.execute("PRAGMA journal_mode=WAL")
                    cursor.execute("PRAGMA synchronous=NORMAL")
                    cursor.execute("PRAGMA cache_size=10000")
                    cursor.execute("PRAGMA temp_store=MEMORY")
                    cursor.execute("PRAGMA mmap_size=268435456")  # 256MB
                    cursor.close()
            
            self._is_initialized = True
            logger.info("✅ تم تهيئة اتصال قاعدة البيانات بنجاح")
            
        except Exception as e:
            logger.error(f"❌ خطأ في تهيئة قاعدة البيانات: {e}")
            raise
    
    async def close(self) -> None:
        """إغلاق اتصال قاعدة البيانات"""
        if self._engine:
            await self._engine.dispose()
            logger.info("🔒 تم إغلاق اتصال قاعدة البيانات")
    
    @property
    def engine(self) -> AsyncEngine:
        """الحصول على محرك قاعدة البيانات"""
        if not self._is_initialized or not self._engine:
            raise RuntimeError("قاعدة البيانات غير مهيأة - استدع initialize() أولاً")
        return self._engine
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """الحصول على جلسة قاعدة بيانات مع إدارة تلقائية للموارد"""
        if not self._session_factory:
            raise RuntimeError("مصنع الجلسات غير مهيأ")
        
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"خطأ في جلسة قاعدة البيانات: {e}")
                raise
            finally:
                await session.close()
    
    async def health_check(self) -> bool:
        """فحص صحة اتصال قاعدة البيانات"""
        try:
            async with self.get_session() as session:
                result = await session.execute("SELECT 1")
                return result.scalar() == 1
        except Exception as e:
            logger.error(f"فشل فحص صحة قاعدة البيانات: {e}")
            return False

# مثيل واحد من مدير قاعدة البيانات
_db_connection = DatabaseConnection()

async def get_database_engine() -> AsyncEngine:
    """الحصول على محرك قاعدة البيانات المُهيأ"""
    if not _db_connection._is_initialized:
        await _db_connection.initialize()
    return _db_connection.engine

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """الحصول على جلسة قاعدة بيانات"""
    if not _db_connection._is_initialized:
        await _db_connection.initialize()
    
    async with _db_connection.get_session() as session:
        yield session

async def close_database():
    """إغلاق اتصال قاعدة البيانات"""
    await _db_connection.close()

async def check_database_health() -> bool:
    """فحص صحة قاعدة البيانات"""
    if not _db_connection._is_initialized:
        await _db_connection.initialize()
    return await _db_connection.health_check()

class DatabaseHealthChecker:
    """فاحص صحة قاعدة البيانات الدوري"""
    
    def __init__(self, check_interval: int = 60):
        self.check_interval = check_interval
        self._running = False
        self._task: Optional[asyncio.Task] = None
    
    async def start(self):
        """بدء فحص الصحة الدوري"""
        if self._running:
            return
        
        self._running = True
        self._task = asyncio.create_task(self._health_check_loop())
        logger.info(f"🔍 بدء فحص صحة قاعدة البيانات كل {self.check_interval} ثانية")
    
    async def stop(self):
        """إيقاف فحص الصحة الدوري"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("⏹️ تم إيقاف فحص صحة قاعدة البيانات")
    
    async def _health_check_loop(self):
        """حلقة فحص الصحة الرئيسية"""
        while self._running:
            try:
                is_healthy = await check_database_health()
                if not is_healthy:
                    logger.warning("⚠️ قاعدة البيانات غير متاحة!")
                else:
                    logger.debug("✅ قاعدة البيانات تعمل بشكل طبيعي")
                
                await asyncio.sleep(self.check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"خطأ في فحص صحة قاعدة البيانات: {e}")
                await asyncio.sleep(self.check_interval)

# مثيل فاحص الصحة العام
health_checker = DatabaseHealthChecker()