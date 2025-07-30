"""
👑 لوحة مفاتيح التحكم الإداري للمسؤولين
تحتوي على جميع وظائف إدارة النظام والمستخدمين
"""

from typing import List, Dict, Any, Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class AdminControlsKeyboard:
    """مولد لوحات مفاتيح التحكم الإداري"""
    
    @staticmethod
    def get_admin_panel() -> InlineKeyboardMarkup:
        """لوحة التحكم الإدارية الرئيسية"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="👥 إدارة المستخدمين",
                    callback_data="admin_users"
                ),
                InlineKeyboardButton(
                    text="🌐 إدارة الجلسات",
                    callback_data="admin_sessions"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 إحصائيات النظام",
                    callback_data="admin_system_stats"
                ),
                InlineKeyboardButton(
                    text="📈 تقارير مفصلة",
                    callback_data="admin_reports"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🛠️ صيانة النظام",
                    callback_data="admin_maintenance"
                ),
                InlineKeyboardButton(
                    text="🔧 إعدادات النظام",
                    callback_data="admin_system_config"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📝 سجلات النظام",
                    callback_data="admin_logs"
                ),
                InlineKeyboardButton(
                    text="🔔 إدارة الإشعارات",
                    callback_data="admin_notifications"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💾 النسخ الاحتياطي",
                    callback_data="admin_backup"
                ),
                InlineKeyboardButton(
                    text="🔒 الأمان والمراقبة",
                    callback_data="admin_security"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ القائمة الرئيسية",
                    callback_data="main_menu"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_user_management() -> InlineKeyboardMarkup:
        """قائمة إدارة المستخدمين"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="👁️ عرض جميع المستخدمين",
                    callback_data="admin_view_users"
                ),
                InlineKeyboardButton(
                    text="🔍 البحث عن مستخدم",
                    callback_data="admin_search_user"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👨‍💼 المسؤولون",
                    callback_data="admin_view_admins"
                ),
                InlineKeyboardButton(
                    text="🚫 المستخدمون المحظورون",
                    callback_data="admin_view_banned"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 إحصائيات المستخدمين",
                    callback_data="admin_user_stats"
                ),
                InlineKeyboardButton(
                    text="⚡ المستخدمون النشطون",
                    callback_data="admin_active_users"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🆕 مستخدمون جدد",
                    callback_data="admin_new_users"
                ),
                InlineKeyboardButton(
                    text="🎯 تحليل النشاط",
                    callback_data="admin_user_activity"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔐 إدارة الأذونات",
                    callback_data="admin_permissions"
                ),
                InlineKeyboardButton(
                    text="📢 إرسال إعلان",
                    callback_data="admin_broadcast"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ لوحة التحكم",
                    callback_data="admin_panel"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_user_details(user_id: int) -> InlineKeyboardMarkup:
        """تفاصيل مستخدم محدد"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="📊 إحصائيات المستخدم",
                    callback_data=f"admin_user_stats_{user_id}"
                ),
                InlineKeyboardButton(
                    text="🌐 جلسات المستخدم",
                    callback_data=f"admin_user_sessions_{user_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔐 إدارة الأذونات",
                    callback_data=f"admin_user_permissions_{user_id}"
                ),
                InlineKeyboardButton(
                    text="👨‍💼 تغيير الدور",
                    callback_data=f"admin_user_role_{user_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🚫 حظر المستخدم",
                    callback_data=f"admin_ban_user_{user_id}"
                ),
                InlineKeyboardButton(
                    text="✅ إلغاء الحظر",
                    callback_data=f"admin_unban_user_{user_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⏸️ إيقاف مؤقت",
                    callback_data=f"admin_suspend_user_{user_id}"
                ),
                InlineKeyboardButton(
                    text="🗑️ حذف البيانات",
                    callback_data=f"admin_delete_user_data_{user_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📝 سجل المستخدم",
                    callback_data=f"admin_user_logs_{user_id}"
                ),
                InlineKeyboardButton(
                    text="💬 إرسال رسالة",
                    callback_data=f"admin_message_user_{user_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ إدارة المستخدمين",
                    callback_data="admin_users"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_role_selection(user_id: int) -> InlineKeyboardMarkup:
        """اختيار دور المستخدم"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="👑 Super Admin",
                    callback_data=f"admin_set_role_{user_id}_super_admin"
                ),
                InlineKeyboardButton(
                    text="👨‍💼 Admin",
                    callback_data=f"admin_set_role_{user_id}_admin"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👨‍💻 Operator",
                    callback_data=f"admin_set_role_{user_id}_operator"
                ),
                InlineKeyboardButton(
                    text="👁️ Viewer",
                    callback_data=f"admin_set_role_{user_id}_viewer"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🚫 Banned",
                    callback_data=f"admin_set_role_{user_id}_banned"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ رجوع للمستخدم",
                    callback_data=f"admin_user_details_{user_id}"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_session_management() -> InlineKeyboardMarkup:
        """إدارة الجلسات للمسؤولين"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="🔥 جميع الجلسات النشطة",
                    callback_data="admin_all_active_sessions"
                ),
                InlineKeyboardButton(
                    text="📊 إحصائيات الجلسات",
                    callback_data="admin_session_stats"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⚠️ جلسات مشكوك فيها",
                    callback_data="admin_suspicious_sessions"
                ),
                InlineKeyboardButton(
                    text="❌ جلسات فاشلة",
                    callback_data="admin_failed_sessions"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🌍 توزيع جغرافي",
                    callback_data="admin_session_geo"
                ),
                InlineKeyboardButton(
                    text="📈 تحليل الأداء",
                    callback_data="admin_session_performance"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🛑 إيقاف جميع الجلسات",
                    callback_data="admin_stop_all_sessions"
                ),
                InlineKeyboardButton(
                    text="🧹 تنظيف الجلسات القديمة",
                    callback_data="admin_cleanup_sessions"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ لوحة التحكم",
                    callback_data="admin_panel"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_system_stats() -> InlineKeyboardMarkup:
        """إحصائيات النظام"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="📊 إحصائيات عامة",
                    callback_data="admin_general_stats"
                ),
                InlineKeyboardButton(
                    text="📈 إحصائيات الأداء",
                    callback_data="admin_performance_stats"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👥 إحصائيات المستخدمين",
                    callback_data="admin_detailed_user_stats"
                ),
                InlineKeyboardButton(
                    text="🎯 إحصائيات البيانات",
                    callback_data="admin_data_stats"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🌍 التوزيع الجغرافي",
                    callback_data="admin_geo_stats"
                ),
                InlineKeyboardButton(
                    text="📱 إحصائيات الأجهزة",
                    callback_data="admin_device_stats"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⚡ الاستخدام الحالي",
                    callback_data="admin_current_usage"
                ),
                InlineKeyboardButton(
                    text="📉 اتجاهات الاستخدام",
                    callback_data="admin_usage_trends"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💾 تصدير الإحصائيات",
                    callback_data="admin_export_stats"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ لوحة التحكم",
                    callback_data="admin_panel"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_maintenance_menu() -> InlineKeyboardMarkup:
        """قائمة صيانة النظام"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="🧹 تنظيف قاعدة البيانات",
                    callback_data="admin_cleanup_database"
                ),
                InlineKeyboardButton(
                    text="🗂️ تحسين الفهارس",
                    callback_data="admin_optimize_indexes"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 فحص سلامة البيانات",
                    callback_data="admin_check_data_integrity"
                ),
                InlineKeyboardButton(
                    text="🔄 إعادة بناء الإحصائيات",
                    callback_data="admin_rebuild_stats"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💾 إنشاء نسخة احتياطية",
                    callback_data="admin_create_backup"
                ),
                InlineKeyboardButton(
                    text="📥 استعادة نسخة احتياطية",
                    callback_data="admin_restore_backup"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔄 إعادة تشغيل النظام",
                    callback_data="admin_restart_system"
                ),
                InlineKeyboardButton(
                    text="⚠️ وضع الصيانة",
                    callback_data="admin_maintenance_mode"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📈 مراقبة الموارد",
                    callback_data="admin_resource_monitor"
                ),
                InlineKeyboardButton(
                    text="🔍 فحص الأخطاء",
                    callback_data="admin_error_check"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ لوحة التحكم",
                    callback_data="admin_panel"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_security_menu() -> InlineKeyboardMarkup:
        """قائمة الأمان والمراقبة"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="🛡️ سجل الأمان",
                    callback_data="admin_security_log"
                ),
                InlineKeyboardButton(
                    text="⚠️ التهديدات المكتشفة",
                    callback_data="admin_threats"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🚫 عناوين IP المحظورة",
                    callback_data="admin_blocked_ips"
                ),
                InlineKeyboardButton(
                    text="🔍 مراقبة الأنشطة المشبوهة",
                    callback_data="admin_suspicious_activity"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔐 إدارة الجلسات الآمنة",
                    callback_data="admin_secure_sessions"
                ),
                InlineKeyboardButton(
                    text="🔑 إدارة مفاتيح التشفير",
                    callback_data="admin_encryption_keys"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 تقرير الأمان",
                    callback_data="admin_security_report"
                ),
                InlineKeyboardButton(
                    text="⚙️ إعدادات الأمان",
                    callback_data="admin_security_settings"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔄 فحص أمني شامل",
                    callback_data="admin_security_scan"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ لوحة التحكم",
                    callback_data="admin_panel"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_logs_menu() -> InlineKeyboardMarkup:
        """قائمة إدارة السجلات"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="📝 سجل النظام العام",
                    callback_data="admin_system_logs"
                ),
                InlineKeyboardButton(
                    text="🛡️ سجل الأمان",
                    callback_data="admin_security_logs"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👥 سجل المستخدمين",
                    callback_data="admin_user_logs"
                ),
                InlineKeyboardButton(
                    text="🌐 سجل الجلسات",
                    callback_data="admin_session_logs"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ سجل الأخطاء",
                    callback_data="admin_error_logs"
                ),
                InlineKeyboardButton(
                    text="⚠️ سجل التحذيرات",
                    callback_data="admin_warning_logs"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔍 بحث في السجلات",
                    callback_data="admin_search_logs"
                ),
                InlineKeyboardButton(
                    text="📊 تحليل السجلات",
                    callback_data="admin_analyze_logs"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💾 تصدير السجلات",
                    callback_data="admin_export_logs"
                ),
                InlineKeyboardButton(
                    text="🧹 تنظيف السجلات القديمة",
                    callback_data="admin_cleanup_logs"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ لوحة التحكم",
                    callback_data="admin_panel"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_confirmation_keyboard(action: str, item_id: Optional[str] = None) -> InlineKeyboardMarkup:
        """لوحة تأكيد للإجراءات الحساسة"""
        
        confirm_callback = f"admin_confirm_{action}"
        cancel_callback = "admin_panel"
        
        if item_id:
            confirm_callback += f"_{item_id}"
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="⚠️ تأكيد التنفيذ",
                    callback_data=confirm_callback
                ),
                InlineKeyboardButton(
                    text="❌ إلغاء",
                    callback_data=cancel_callback
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_broadcast_options() -> InlineKeyboardMarkup:
        """خيارات الإعلانات"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="📢 إعلان لجميع المستخدمين",
                    callback_data="admin_broadcast_all"
                ),
                InlineKeyboardButton(
                    text="👨‍💼 إعلان للمسؤولين فقط",
                    callback_data="admin_broadcast_admins"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⚡ إعلان للمستخدمين النشطين",
                    callback_data="admin_broadcast_active"
                ),
                InlineKeyboardButton(
                    text="🆕 إعلان للمستخدمين الجدد",
                    callback_data="admin_broadcast_new"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎯 إعلان مخصص",
                    callback_data="admin_broadcast_custom"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ إدارة المستخدمين",
                    callback_data="admin_users"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)