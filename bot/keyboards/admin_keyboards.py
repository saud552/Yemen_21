"""
⌨️ لوحات المفاتيح الإدارية المتقدمة
تشمل جميع واجهات الإدارة والتحكم
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Dict, List, Any, Optional

class AdminKeyboard:
    """مولد لوحات المفاتيح الإدارية"""
    
    @staticmethod
    def get_main_admin_menu(user) -> InlineKeyboardMarkup:
        """القائمة الرئيسية للإدارة"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="👥 إدارة المستخدمين",
                    callback_data="user_management"
                ),
                InlineKeyboardButton(
                    text="📊 التحليلات",
                    callback_data="analytics_dashboard"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⚙️ إدارة النظام",
                    callback_data="system_management"
                ),
                InlineKeyboardButton(
                    text="🛡️ مركز الأمان",
                    callback_data="security_center"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💾 تصدير البيانات",
                    callback_data="export_data"
                ),
                InlineKeyboardButton(
                    text="📢 إرسال جماعي",
                    callback_data="broadcast_message"
                )
            ]
        ]
        
        # إضافة إعدادات المدير الأعلى
        if user.role == "super_admin":
            buttons.append([
                InlineKeyboardButton(
                    text="🔧 إعدادات البوت",
                    callback_data="bot_settings"
                ),
                InlineKeyboardButton(
                    text="📋 سجل النظام",
                    callback_data="system_logs"
                )
            ])
        
        buttons.append([
            InlineKeyboardButton(
                text="◀️ القائمة الرئيسية",
                callback_data="main_menu"
            )
        ])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_user_management_menu() -> InlineKeyboardMarkup:
        """قائمة إدارة المستخدمين"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="📋 قائمة المستخدمين",
                    callback_data="list_users_1"
                ),
                InlineKeyboardButton(
                    text="🔍 البحث عن مستخدم",
                    callback_data="search_users"
                )
            ],
            [
                InlineKeyboardButton(
                    text="➕ إضافة مستخدم",
                    callback_data="add_user"
                ),
                InlineKeyboardButton(
                    text="📊 إحصائيات المستخدمين",
                    callback_data="user_statistics"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🚫 المحظورون",
                    callback_data="banned_users"
                ),
                InlineKeyboardButton(
                    text="👑 المدراء",
                    callback_data="admin_users"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ لوحة الإدارة",
                    callback_data="admin_panel"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_user_actions_menu(target_user, admin_role: str) -> InlineKeyboardMarkup:
        """قائمة إجراءات المستخدم"""
        
        buttons = []
        
        # إجراءات أساسية
        if target_user.is_active:
            buttons.append([
                InlineKeyboardButton(
                    text="🚫 حظر المستخدم",
                    callback_data=f"ban_user_{target_user.user_id}"
                )
            ])
        else:
            buttons.append([
                InlineKeyboardButton(
                    text="✅ إلغاء الحظر",
                    callback_data=f"unban_user_{target_user.user_id}"
                )
            ])
        
        # إدارة الأدوار (المدير الأعلى فقط)
        if admin_role == "super_admin" and target_user.role != "super_admin":
            role_buttons = []
            
            if target_user.role != "admin":
                role_buttons.append(
                    InlineKeyboardButton(
                        text="🔧 رفع لمدير",
                        callback_data=f"promote_admin_{target_user.user_id}"
                    )
                )
            else:
                role_buttons.append(
                    InlineKeyboardButton(
                        text="👤 تنزيل لمستخدم",
                        callback_data=f"demote_user_{target_user.user_id}"
                    )
                )
            
            if role_buttons:
                buttons.append(role_buttons)
        
        # إجراءات إضافية
        buttons.extend([
            [
                InlineKeyboardButton(
                    text="📊 إحصائيات المستخدم",
                    callback_data=f"user_stats_{target_user.user_id}"
                ),
                InlineKeyboardButton(
                    text="🗂️ جلسات المستخدم",
                    callback_data=f"user_sessions_{target_user.user_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💾 تصدير بيانات المستخدم",
                    callback_data=f"export_user_{target_user.user_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ قائمة المستخدمين",
                    callback_data="list_users_1"
                )
            ]
        ])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_system_management_menu() -> InlineKeyboardMarkup:
        """قائمة إدارة النظام"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="💾 نسخة احتياطية",
                    callback_data="create_backup"
                ),
                InlineKeyboardButton(
                    text="🔄 إعادة تشغيل البوت",
                    callback_data="restart_bot"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🗄️ حالة قاعدة البيانات",
                    callback_data="database_status"
                ),
                InlineKeyboardButton(
                    text="📊 معلومات الخادم",
                    callback_data="server_info"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🧹 تنظيف الملفات المؤقتة",
                    callback_data="cleanup_temp"
                ),
                InlineKeyboardButton(
                    text="📋 سجلات النظام",
                    callback_data="view_logs"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⚡ مراقبة الأداء",
                    callback_data="performance_monitor"
                ),
                InlineKeyboardButton(
                    text="🔧 إعدادات متقدمة",
                    callback_data="advanced_settings"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ لوحة الإدارة",
                    callback_data="admin_panel"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_export_menu() -> InlineKeyboardMarkup:
        """قائمة تصدير البيانات"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="📊 تصدير جميع البيانات",
                    callback_data="export_all"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👤 تصدير بيانات مستخدم",
                    callback_data="export_user_select"
                ),
                InlineKeyboardButton(
                    text="📅 تصدير فترة زمنية",
                    callback_data="export_date_range"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🌐 تصدير جلسة محددة",
                    callback_data="export_session_select"
                ),
                InlineKeyboardButton(
                    text="🎯 تصدير موقع محدد",
                    callback_data="export_site_select"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📄 صيغة التصدير",
                    callback_data="export_format"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ لوحة الإدارة",
                    callback_data="admin_panel"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_export_format_menu() -> InlineKeyboardMarkup:
        """قائمة اختيار صيغة التصدير"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="📊 Excel (.xlsx)",
                    callback_data="format_excel"
                ),
                InlineKeyboardButton(
                    text="📋 CSV (.csv)",
                    callback_data="format_csv"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔧 JSON (.json)",
                    callback_data="format_json"
                ),
                InlineKeyboardButton(
                    text="📄 Text (.txt)",
                    callback_data="format_txt"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📑 PDF Report",
                    callback_data="format_pdf"
                ),
                InlineKeyboardButton(
                    text="⚡ XML (.xml)",
                    callback_data="format_xml"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ تصدير البيانات",
                    callback_data="export_data"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_analytics_menu() -> InlineKeyboardMarkup:
        """قائمة التحليلات"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="📈 إحصائيات عامة",
                    callback_data="general_analytics"
                ),
                InlineKeyboardButton(
                    text="🌍 التوزيع الجغرافي",
                    callback_data="geo_analytics"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📱 تحليل الأجهزة",
                    callback_data="device_analytics"
                ),
                InlineKeyboardButton(
                    text="⏰ تحليل الأوقات",
                    callback_data="time_analytics"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎯 معدلات النجاح",
                    callback_data="success_analytics"
                ),
                InlineKeyboardButton(
                    text="👥 تحليل المستخدمين",
                    callback_data="user_analytics"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 تقرير شامل",
                    callback_data="comprehensive_report"
                ),
                InlineKeyboardButton(
                    text="📈 مقارنات زمنية",
                    callback_data="trend_analysis"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ لوحة الإدارة",
                    callback_data="admin_panel"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_security_menu() -> InlineKeyboardMarkup:
        """قائمة مركز الأمان"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="🔒 محاولات الدخول الفاشلة",
                    callback_data="failed_logins"
                ),
                InlineKeyboardButton(
                    text="🚨 التحذيرات الأمنية",
                    callback_data="security_alerts"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👥 الجلسات النشطة",
                    callback_data="active_sessions_security"
                ),
                InlineKeyboardButton(
                    text="🚫 قائمة المحظورين",
                    callback_data="blocked_ips"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔧 إعدادات الأمان",
                    callback_data="security_settings"
                ),
                InlineKeyboardButton(
                    text="📊 تقرير أمني",
                    callback_data="security_report"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🛡️ فحص أمني شامل",
                    callback_data="security_scan"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ لوحة الإدارة",
                    callback_data="admin_panel"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_broadcast_menu() -> InlineKeyboardMarkup:
        """قائمة الإرسال الجماعي"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="✏️ كتابة رسالة نصية",
                    callback_data="broadcast_text"
                ),
                InlineKeyboardButton(
                    text="🖼️ إرسال صورة",
                    callback_data="broadcast_photo"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📎 إرسال ملف",
                    callback_data="broadcast_document"
                ),
                InlineKeyboardButton(
                    text="🎵 إرسال صوت",
                    callback_data="broadcast_audio"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👥 اختيار المستلمين",
                    callback_data="select_recipients"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 إحصائيات الإرسال السابق",
                    callback_data="broadcast_stats"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ لوحة الإدارة",
                    callback_data="admin_panel"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_back_button(callback_data: str = "admin_panel") -> InlineKeyboardMarkup:
        """زر العودة"""
        
        return InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text="◀️ رجوع",
                callback_data=callback_data
            )
        ]])
    
    @staticmethod
    def get_confirmation_menu(action: str, target_id: str) -> InlineKeyboardMarkup:
        """قائمة التأكيد للإجراءات الحساسة"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="✅ تأكيد",
                    callback_data=f"confirm_{action}_{target_id}"
                ),
                InlineKeyboardButton(
                    text="❌ إلغاء",
                    callback_data="cancel_action"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)