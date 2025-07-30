"""
☁️ نظام التخزين السحابي المتقدم
يدعم عدة منصات تخزين سحابية مع إمكانيات متقدمة
"""

import asyncio
import logging
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import aiofiles
from io import BytesIO

from ..config import settings

logger = logging.getLogger(__name__)

class CloudStorageManager:
    """مدير التخزين السحابي المتقدم"""
    
    def __init__(self):
        self.storage_providers = {
            'local': LocalStorage(),
            's3': S3Storage(),
            'gdrive': GoogleDriveStorage(),
            'dropbox': DropboxStorage()
        }
        self.current_provider = settings.CLOUD_STORAGE_TYPE
    
    async def upload_file(self, file_path: Path, remote_path: str = None, provider: str = None) -> Dict[str, Any]:
        """رفع ملف للتخزين السحابي"""
        
        provider = provider or self.current_provider
        storage = self.storage_providers.get(provider)
        
        if not storage:
            return {'success': False, 'error': f'مزود التخزين غير مدعوم: {provider}'}
        
        try:
            result = await storage.upload(file_path, remote_path)
            
            # تسجيل عملية الرفع
            await self._log_operation('upload', file_path, remote_path, provider, result)
            
            return result
            
        except Exception as e:
            logger.error(f"خطأ في رفع الملف {file_path}: {e}")
            return {'success': False, 'error': str(e)}
    
    async def download_file(self, remote_path: str, local_path: Path = None, provider: str = None) -> Dict[str, Any]:
        """تحميل ملف من التخزين السحابي"""
        
        provider = provider or self.current_provider
        storage = self.storage_providers.get(provider)
        
        if not storage:
            return {'success': False, 'error': f'مزود التخزين غير مدعوم: {provider}'}
        
        try:
            result = await storage.download(remote_path, local_path)
            
            # تسجيل عملية التحميل
            await self._log_operation('download', local_path, remote_path, provider, result)
            
            return result
            
        except Exception as e:
            logger.error(f"خطأ في تحميل الملف {remote_path}: {e}")
            return {'success': False, 'error': str(e)}
    
    async def list_files(self, remote_directory: str = "", provider: str = None) -> Dict[str, Any]:
        """عرض قائمة الملفات في المجلد"""
        
        provider = provider or self.current_provider
        storage = self.storage_providers.get(provider)
        
        if not storage:
            return {'success': False, 'error': f'مزود التخزين غير مدعوم: {provider}'}
        
        try:
            return await storage.list_files(remote_directory)
            
        except Exception as e:
            logger.error(f"خطأ في عرض الملفات: {e}")
            return {'success': False, 'error': str(e)}
    
    async def delete_file(self, remote_path: str, provider: str = None) -> Dict[str, Any]:
        """حذف ملف من التخزين السحابي"""
        
        provider = provider or self.current_provider
        storage = self.storage_providers.get(provider)
        
        if not storage:
            return {'success': False, 'error': f'مزود التخزين غير مدعوم: {provider}'}
        
        try:
            result = await storage.delete(remote_path)
            
            # تسجيل عملية الحذف
            await self._log_operation('delete', None, remote_path, provider, result)
            
            return result
            
        except Exception as e:
            logger.error(f"خطأ في حذف الملف {remote_path}: {e}")
            return {'success': False, 'error': str(e)}
    
    async def sync_directory(self, local_dir: Path, remote_dir: str, provider: str = None) -> Dict[str, Any]:
        """مزامنة مجلد محلي مع التخزين السحابي"""
        
        provider = provider or self.current_provider
        storage = self.storage_providers.get(provider)
        
        if not storage:
            return {'success': False, 'error': f'مزود التخزين غير مدعوم: {provider}'}
        
        try:
            uploaded_files = []
            failed_files = []
            
            for file_path in local_dir.rglob('*'):
                if file_path.is_file():
                    relative_path = file_path.relative_to(local_dir)
                    remote_file_path = f"{remote_dir}/{relative_path}".replace('\\', '/')
                    
                    result = await storage.upload(file_path, remote_file_path)
                    
                    if result.get('success'):
                        uploaded_files.append(str(relative_path))
                    else:
                        failed_files.append({
                            'file': str(relative_path),
                            'error': result.get('error', 'Unknown error')
                        })
            
            return {
                'success': True,
                'uploaded_files': uploaded_files,
                'failed_files': failed_files,
                'total_uploaded': len(uploaded_files),
                'total_failed': len(failed_files)
            }
            
        except Exception as e:
            logger.error(f"خطأ في مزامنة المجلد: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_storage_info(self, provider: str = None) -> Dict[str, Any]:
        """الحصول على معلومات التخزين"""
        
        provider = provider or self.current_provider
        storage = self.storage_providers.get(provider)
        
        if not storage:
            return {'success': False, 'error': f'مزود التخزين غير مدعوم: {provider}'}
        
        try:
            return await storage.get_storage_info()
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على معلومات التخزين: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _log_operation(self, operation: str, local_path: Path, remote_path: str, provider: str, result: Dict[str, Any]):
        """تسجيل عمليات التخزين السحابي"""
        
        try:
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'operation': operation,
                'provider': provider,
                'local_path': str(local_path) if local_path else None,
                'remote_path': remote_path,
                'success': result.get('success', False),
                'error': result.get('error'),
                'file_size': result.get('file_size'),
                'duration': result.get('duration')
            }
            
            # حفظ في ملف سجل
            log_file = Path(settings.TEMP_DIR) / 'cloud_storage.log'
            
            async with aiofiles.open(log_file, 'a', encoding='utf-8') as f:
                await f.write(json.dumps(log_entry) + '\n')
                
        except Exception as e:
            logger.warning(f"فشل في تسجيل عملية التخزين السحابي: {e}")

class BaseStorage:
    """الفئة الأساسية لمزودي التخزين"""
    
    async def upload(self, local_path: Path, remote_path: str) -> Dict[str, Any]:
        """رفع ملف"""
        raise NotImplementedError
    
    async def download(self, remote_path: str, local_path: Path = None) -> Dict[str, Any]:
        """تحميل ملف"""
        raise NotImplementedError
    
    async def delete(self, remote_path: str) -> Dict[str, Any]:
        """حذف ملف"""
        raise NotImplementedError
    
    async def list_files(self, remote_directory: str = "") -> Dict[str, Any]:
        """عرض قائمة الملفات"""
        raise NotImplementedError
    
    async def get_storage_info(self) -> Dict[str, Any]:
        """معلومات التخزين"""
        raise NotImplementedError

class LocalStorage(BaseStorage):
    """التخزين المحلي"""
    
    def __init__(self):
        self.base_path = Path(settings.UPLOAD_DIR)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    async def upload(self, local_path: Path, remote_path: str) -> Dict[str, Any]:
        """نسخ ملف محلياً"""
        
        try:
            start_time = datetime.utcnow()
            
            target_path = self.base_path / remote_path
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # نسخ الملف
            import shutil
            shutil.copy2(local_path, target_path)
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            file_size = target_path.stat().st_size
            
            return {
                'success': True,
                'remote_path': str(target_path),
                'file_size': file_size,
                'duration': duration
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def download(self, remote_path: str, local_path: Path = None) -> Dict[str, Any]:
        """نسخ ملف من التخزين المحلي"""
        
        try:
            source_path = self.base_path / remote_path
            
            if not source_path.exists():
                return {'success': False, 'error': 'الملف غير موجود'}
            
            if local_path is None:
                local_path = Path(settings.TEMP_DIR) / remote_path
            
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            import shutil
            shutil.copy2(source_path, local_path)
            
            return {
                'success': True,
                'local_path': str(local_path),
                'file_size': local_path.stat().st_size
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def delete(self, remote_path: str) -> Dict[str, Any]:
        """حذف ملف من التخزين المحلي"""
        
        try:
            target_path = self.base_path / remote_path
            
            if target_path.exists():
                target_path.unlink()
                return {'success': True}
            else:
                return {'success': False, 'error': 'الملف غير موجود'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def list_files(self, remote_directory: str = "") -> Dict[str, Any]:
        """عرض قائمة الملفات المحلية"""
        
        try:
            target_dir = self.base_path / remote_directory
            
            if not target_dir.exists():
                return {'success': True, 'files': []}
            
            files = []
            for item in target_dir.iterdir():
                if item.is_file():
                    files.append({
                        'name': item.name,
                        'path': str(item.relative_to(self.base_path)),
                        'size': item.stat().st_size,
                        'modified': datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                    })
            
            return {'success': True, 'files': files}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def get_storage_info(self) -> Dict[str, Any]:
        """معلومات التخزين المحلي"""
        
        try:
            import shutil
            
            total, used, free = shutil.disk_usage(self.base_path)
            
            return {
                'success': True,
                'provider': 'Local Storage',
                'total_space': total,
                'used_space': used,
                'free_space': free,
                'base_path': str(self.base_path)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

class S3Storage(BaseStorage):
    """تخزين Amazon S3"""
    
    def __init__(self):
        self.bucket_name = settings.AWS_BUCKET_NAME
        self.region = settings.AWS_REGION
        self._client = None
    
    async def _get_client(self):
        """الحصول على عميل S3"""
        
        if self._client is None:
            try:
                import aioboto3
                
                session = aioboto3.Session()
                self._client = session.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=self.region
                )
                
            except ImportError:
                raise Exception("مكتبة aioboto3 غير مثبتة")
            except Exception as e:
                raise Exception(f"خطأ في إعداد عميل S3: {e}")
        
        return self._client
    
    async def upload(self, local_path: Path, remote_path: str) -> Dict[str, Any]:
        """رفع ملف لـ S3"""
        
        try:
            start_time = datetime.utcnow()
            
            client = await self._get_client()
            
            async with client as s3:
                await s3.upload_file(
                    str(local_path),
                    self.bucket_name,
                    remote_path
                )
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            file_size = local_path.stat().st_size
            
            return {
                'success': True,
                'remote_path': f"s3://{self.bucket_name}/{remote_path}",
                'file_size': file_size,
                'duration': duration
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def download(self, remote_path: str, local_path: Path = None) -> Dict[str, Any]:
        """تحميل ملف من S3"""
        
        try:
            if local_path is None:
                local_path = Path(settings.TEMP_DIR) / Path(remote_path).name
            
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            client = await self._get_client()
            
            async with client as s3:
                await s3.download_file(
                    self.bucket_name,
                    remote_path,
                    str(local_path)
                )
            
            return {
                'success': True,
                'local_path': str(local_path),
                'file_size': local_path.stat().st_size
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def delete(self, remote_path: str) -> Dict[str, Any]:
        """حذف ملف من S3"""
        
        try:
            client = await self._get_client()
            
            async with client as s3:
                await s3.delete_object(
                    Bucket=self.bucket_name,
                    Key=remote_path
                )
            
            return {'success': True}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def list_files(self, remote_directory: str = "") -> Dict[str, Any]:
        """عرض قائمة الملفات في S3"""
        
        try:
            client = await self._get_client()
            
            async with client as s3:
                response = await s3.list_objects_v2(
                    Bucket=self.bucket_name,
                    Prefix=remote_directory
                )
            
            files = []
            for obj in response.get('Contents', []):
                files.append({
                    'name': Path(obj['Key']).name,
                    'path': obj['Key'],
                    'size': obj['Size'],
                    'modified': obj['LastModified'].isoformat()
                })
            
            return {'success': True, 'files': files}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def get_storage_info(self) -> Dict[str, Any]:
        """معلومات تخزين S3"""
        
        try:
            return {
                'success': True,
                'provider': 'Amazon S3',
                'bucket': self.bucket_name,
                'region': self.region,
                'note': 'S3 has virtually unlimited storage'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

class GoogleDriveStorage(BaseStorage):
    """تخزين Google Drive"""
    
    def __init__(self):
        self.credentials_file = settings.GOOGLE_DRIVE_CREDENTIALS_FILE
        self._service = None
    
    async def _get_service(self):
        """الحصول على خدمة Google Drive"""
        
        if self._service is None:
            try:
                from googleapiclient.discovery import build
                from google.oauth2.service_account import Credentials
                
                creds = Credentials.from_service_account_file(
                    self.credentials_file,
                    scopes=['https://www.googleapis.com/auth/drive']
                )
                
                self._service = build('drive', 'v3', credentials=creds)
                
            except ImportError:
                raise Exception("مكتبة Google API غير مثبتة")
            except Exception as e:
                raise Exception(f"خطأ في إعداد Google Drive: {e}")
        
        return self._service
    
    async def upload(self, local_path: Path, remote_path: str) -> Dict[str, Any]:
        """رفع ملف لـ Google Drive"""
        
        try:
            start_time = datetime.utcnow()
            
            service = await self._get_service()
            
            from googleapiclient.http import MediaFileUpload
            
            media = MediaFileUpload(str(local_path))
            
            file_metadata = {
                'name': Path(remote_path).name
            }
            
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            file_size = local_path.stat().st_size
            
            return {
                'success': True,
                'remote_path': f"gdrive://{file.get('id')}",
                'file_id': file.get('id'),
                'file_size': file_size,
                'duration': duration
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def download(self, remote_path: str, local_path: Path = None) -> Dict[str, Any]:
        """تحميل ملف من Google Drive"""
        
        try:
            # تنفيذ مبسط للتحميل من Google Drive
            return {'success': False, 'error': 'التحميل من Google Drive قيد التطوير'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def delete(self, remote_path: str) -> Dict[str, Any]:
        """حذف ملف من Google Drive"""
        
        try:
            # تنفيذ مبسط للحذف من Google Drive
            return {'success': False, 'error': 'الحذف من Google Drive قيد التطوير'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def list_files(self, remote_directory: str = "") -> Dict[str, Any]:
        """عرض قائمة الملفات في Google Drive"""
        
        try:
            # تنفيذ مبسط لعرض الملفات من Google Drive
            return {'success': True, 'files': []}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def get_storage_info(self) -> Dict[str, Any]:
        """معلومات تخزين Google Drive"""
        
        try:
            return {
                'success': True,
                'provider': 'Google Drive',
                'note': 'Google Drive integration is in development'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

class DropboxStorage(BaseStorage):
    """تخزين Dropbox"""
    
    def __init__(self):
        self.access_token = settings.DROPBOX_ACCESS_TOKEN
        self._client = None
    
    async def _get_client(self):
        """الحصول على عميل Dropbox"""
        
        if self._client is None:
            try:
                import dropbox
                
                self._client = dropbox.Dropbox(self.access_token)
                
            except ImportError:
                raise Exception("مكتبة Dropbox غير مثبتة")
            except Exception as e:
                raise Exception(f"خطأ في إعداد عميل Dropbox: {e}")
        
        return self._client
    
    async def upload(self, local_path: Path, remote_path: str) -> Dict[str, Any]:
        """رفع ملف لـ Dropbox"""
        
        try:
            start_time = datetime.utcnow()
            
            client = await self._get_client()
            
            with open(local_path, 'rb') as f:
                client.files_upload(
                    f.read(),
                    f"/{remote_path}",
                    mode=dropbox.files.WriteMode.overwrite
                )
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            file_size = local_path.stat().st_size
            
            return {
                'success': True,
                'remote_path': f"dropbox:/{remote_path}",
                'file_size': file_size,
                'duration': duration
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def download(self, remote_path: str, local_path: Path = None) -> Dict[str, Any]:
        """تحميل ملف من Dropbox"""
        
        try:
            # تنفيذ مبسط للتحميل من Dropbox
            return {'success': False, 'error': 'التحميل من Dropbox قيد التطوير'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def delete(self, remote_path: str) -> Dict[str, Any]:
        """حذف ملف من Dropbox"""
        
        try:
            # تنفيذ مبسط للحذف من Dropbox
            return {'success': False, 'error': 'الحذف من Dropbox قيد التطوير'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def list_files(self, remote_directory: str = "") -> Dict[str, Any]:
        """عرض قائمة الملفات في Dropbox"""
        
        try:
            # تنفيذ مبسط لعرض الملفات من Dropbox
            return {'success': True, 'files': []}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def get_storage_info(self) -> Dict[str, Any]:
        """معلومات تخزين Dropbox"""
        
        try:
            return {
                'success': True,
                'provider': 'Dropbox',
                'note': 'Dropbox integration is in development'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

# مثيل عام
cloud_storage = CloudStorageManager()