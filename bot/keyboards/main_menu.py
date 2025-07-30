"""
🏠 لوحة المفاتيح الرئيسية لبوت Zphisher Telegram
تحتوي على جميع الوظائف الأساسية والمتقدمة
"""

from typing import List, Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from ..config import settings
from ..database import User

class MainMenuKeyboard:
    """مولد لوحات المفاتيح الرئيسية"""
    
    @staticmethod
    def get_main_menu(user: User) -> InlineKeyboardMarkup:
        """القائمة الرئيسية التفاعلية"""
        
        buttons = []
        
        # إحصائيات سريعة (صف أول)
        buttons.append([
            InlineKeyboardButton(
                text="📊 لوحة التحكم",
                callback_data="dashboard"
            ),
            InlineKeyboardButton(
                text="⚡ جلسة سريعة",
                callback_data="quick_session"
            )
        ])
        
        # إدارة الجلسات (صف ثاني)
        buttons.append([
            InlineKeyboardButton(
                text="🌐 جلسة جديدة",
                callback_data="new_session"
            ),
            InlineKeyboardButton(
                text="📱 جلساتي النشطة",
                callback_data="my_sessions"
            )
        ])
        
        # البيانات والتقارير (صف ثالث)
        buttons.append([
            InlineKeyboardButton(
                text="🎯 البيانات المُلتقطة",
                callback_data="captured_data"
            ),
            InlineKeyboardButton(
                text="📈 الإحصائيات",
                callback_data="statistics"
            )
        ])
        
        # أدوات إضافية (صف رابع)
        buttons.append([
            InlineKeyboardButton(
                text="🔧 الأدوات",
                callback_data="tools"
            ),
            InlineKeyboardButton(
                text="📚 المساعدة",
                callback_data="help"
            )
        ])
        
        # إعدادات الإدارة (للمسؤولين فقط)
        if user.is_admin():
            buttons.append([
                InlineKeyboardButton(
                    text="👑 إدارة النظام",
                    callback_data="admin_panel"
                ),
                InlineKeyboardButton(
                    text="👥 إدارة المستخدمين",
                    callback_data="user_management"
                )
            ])
        
        # معلومات وإعدادات (صف أخير)
        buttons.append([
            InlineKeyboardButton(
                text="⚙️ الإعدادات",
                callback_data="settings"
            ),
            InlineKeyboardButton(
                text="ℹ️ حول البوت",
                callback_data="about"
            )
        ])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_dashboard_menu() -> InlineKeyboardMarkup:
        """قائمة لوحة التحكم"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="📊 الإحصائيات العامة",
                    callback_data="stats_general"
                ),
                InlineKeyboardButton(
                    text="🎯 إحصائياتي",
                    callback_data="stats_personal"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔥 الجلسات النشطة",
                    callback_data="active_sessions_all"
                ),
                InlineKeyboardButton(
                    text="⏱️ النشاط الأخير",
                    callback_data="recent_activity"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🌍 خريطة الضحايا",
                    callback_data="victims_map"
                ),
                InlineKeyboardButton(
                    text="📱 تحليل الأجهزة",
                    callback_data="device_analysis"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔄 تحديث",
                    callback_data="dashboard_refresh"
                ),
                InlineKeyboardButton(
                    text="🏠 القائمة الرئيسية",
                    callback_data="main_menu"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_quick_session_menu() -> InlineKeyboardMarkup:
        """قائمة الجلسة السريعة"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="📘 Facebook",
                    callback_data="quick_facebook"
                ),
                InlineKeyboardButton(
                    text="📷 Instagram",
                    callback_data="quick_instagram"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📧 Google",
                    callback_data="quick_google"
                ),
                InlineKeyboardButton(
                    text="🐦 Twitter",
                    callback_data="quick_twitter"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💼 LinkedIn",
                    callback_data="quick_linkedin"
                ),
                InlineKeyboardButton(
                    text="🎮 Discord",
                    callback_data="quick_discord"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔧 جلسة مخصصة",
                    callback_data="new_session"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ رجوع",
                    callback_data="main_menu"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_tools_menu(user: User) -> InlineKeyboardMarkup:
        """قائمة الأدوات الإضافية"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="🔗 مولد الروابط",
                    callback_data="url_generator"
                ),
                InlineKeyboardButton(
                    text="🎭 أقنعة الروابط",
                    callback_data="url_masks"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📋 قوالب الرسائل",
                    callback_data="message_templates"
                ),
                InlineKeyboardButton(
                    text="🔍 فحص الروابط",
                    callback_data="url_checker"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 مولد التقارير",
                    callback_data="report_generator"
                ),
                InlineKeyboardButton(
                    text="💾 تصدير البيانات",
                    callback_data="data_export"
                )
            ]
        ]
        
        # أدوات المسؤولين
        if user.is_admin():
            buttons.append([
                InlineKeyboardButton(
                    text="🛠️ أدوات النظام",
                    callback_data="system_tools"
                ),
                InlineKeyboardButton(
                    text="🧹 تنظيف البيانات",
                    callback_data="cleanup_tools"
                )
            ])
        
        buttons.append([
            InlineKeyboardButton(
                text="◀️ رجوع",
                callback_data="main_menu"
            )
        ])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_help_menu() -> InlineKeyboardMarkup:
        """قائمة المساعدة والدعم"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="📖 دليل الاستخدام",
                    callback_data="user_guide"
                ),
                InlineKeyboardButton(
                    text="🎥 فيديوهات تعليمية",
                    callback_data="video_tutorials"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❓ الأسئلة الشائعة",
                    callback_data="faq"
                ),
                InlineKeyboardButton(
                    text="🔧 استكشاف الأخطاء",
                    callback_data="troubleshooting"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💬 الدعم الفني",
                    callback_data="technical_support"
                ),
                InlineKeyboardButton(
                    text="📢 التحديثات",
                    callback_data="updates_news"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ رجوع",
                    callback_data="main_menu"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_settings_menu(user: User) -> InlineKeyboardMarkup:
        """قائمة الإعدادات الشخصية"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="🌐 اللغة",
                    callback_data="settings_language"
                ),
                InlineKeyboardButton(
                    text="🔔 الإشعارات",
                    callback_data="settings_notifications"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎨 المظهر",
                    callback_data="settings_theme"
                ),
                InlineKeyboardButton(
                    text="⏰ المنطقة الزمنية",
                    callback_data="settings_timezone"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔐 الأمان",
                    callback_data="settings_security"
                ),
                InlineKeyboardButton(
                    text="📊 الخصوصية",
                    callback_data="settings_privacy"
                )
            ]
        ]
        
        # إعدادات متقدمة للمسؤولين
        if user.is_admin():
            buttons.append([
                InlineKeyboardButton(
                    text="⚙️ إعدادات النظام",
                    callback_data="settings_system"
                ),
                InlineKeyboardButton(
                    text="🔧 إعدادات متقدمة",
                    callback_data="settings_advanced"
                )
            ])
        
        buttons.append([
            InlineKeyboardButton(
                text="◀️ رجوع",
                callback_data="main_menu"
            )
        ])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_confirmation_keyboard(action: str, confirm_text: str = "✅ تأكيد", cancel_text: str = "❌ إلغاء") -> InlineKeyboardMarkup:
        """لوحة مفاتيح التأكيد"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text=confirm_text,
                    callback_data=f"confirm_{action}"
                ),
                InlineKeyboardButton(
                    text=cancel_text,
                    callback_data=f"cancel_{action}"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_pagination_keyboard(
        callback_prefix: str,
        current_page: int,
        total_pages: int,
        additional_buttons: List[List[InlineKeyboardButton]] = None
    ) -> InlineKeyboardMarkup:
        """لوحة مفاتيح التنقل بين الصفحات"""
        
        buttons = []
        
        # إضافة الأزرار الإضافية أولاً
        if additional_buttons:
            buttons.extend(additional_buttons)
        
        # أزرار التنقل
        nav_buttons = []
        
        # زر الصفحة السابقة
        if current_page > 1:
            nav_buttons.append(
                InlineKeyboardButton(
                    text="◀️ السابق",
                    callback_data=f"{callback_prefix}_page_{current_page - 1}"
                )
            )
        
        # معلومات الصفحة الحالية
        nav_buttons.append(
            InlineKeyboardButton(
                text=f"{current_page}/{total_pages}",
                callback_data="page_info"
            )
        )
        
        # زر الصفحة التالية
        if current_page < total_pages:
            nav_buttons.append(
                InlineKeyboardButton(
                    text="▶️ التالي",
                    callback_data=f"{callback_prefix}_page_{current_page + 1}"
                )
            )
        
        if nav_buttons:
            buttons.append(nav_buttons)
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_back_button(callback_data: str = "main_menu", text: str = "◀️ رجوع") -> InlineKeyboardMarkup:
        """زر الرجوع البسيط"""
        
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=text, callback_data=callback_data)]
        ])
    
    @staticmethod
    def get_loading_keyboard() -> InlineKeyboardMarkup:
        """لوحة مفاتيح التحميل"""
        
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⏳ جارٍ التحميل...", callback_data="loading")]
        ])
    
    @staticmethod
    def get_error_keyboard(retry_callback: str = None) -> InlineKeyboardMarkup:
        """لوحة مفاتيح الخطأ"""
        
        buttons = []
        
        if retry_callback:
            buttons.append([
                InlineKeyboardButton(
                    text="🔄 إعادة المحاولة",
                    callback_data=retry_callback
                )
            ])
        
        buttons.append([
            InlineKeyboardButton(
                text="🏠 القائمة الرئيسية",
                callback_data="main_menu"
            )
        ])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)

class QuickActionKeyboard:
    """لوحات المفاتيح للإجراءات السريعة"""
    
    @staticmethod
    def get_session_actions(session_id: str, status: str) -> InlineKeyboardMarkup:
        """أزرار إدارة الجلسة"""
        
        buttons = []
        
        if status == "active":
            buttons.append([
                InlineKeyboardButton(
                    text="📊 عرض الإحصائيات",
                    callback_data=f"session_stats_{session_id}"
                ),
                InlineKeyboardButton(
                    text="🎯 البيانات المُلتقطة",
                    callback_data=f"session_data_{session_id}"
                )
            ])
            
            buttons.append([
                InlineKeyboardButton(
                    text="🔗 الحصول على الروابط",
                    callback_data=f"session_links_{session_id}"
                ),
                InlineKeyboardButton(
                    text="⚙️ إعدادات الجلسة",
                    callback_data=f"session_settings_{session_id}"
                )
            ])
            
            buttons.append([
                InlineKeyboardButton(
                    text="⏸️ إيقاف مؤقت",
                    callback_data=f"session_pause_{session_id}"
                ),
                InlineKeyboardButton(
                    text="🛑 إيقاف نهائي",
                    callback_data=f"session_stop_{session_id}"
                )
            ])
            
        elif status in ["stopped", "error"]:
            buttons.append([
                InlineKeyboardButton(
                    text="🔄 إعادة التشغيل",
                    callback_data=f"session_restart_{session_id}"
                ),
                InlineKeyboardButton(
                    text="📊 عرض التقرير",
                    callback_data=f"session_report_{session_id}"
                )
            ])
            
            buttons.append([
                InlineKeyboardButton(
                    text="🗑️ حذف الجلسة",
                    callback_data=f"session_delete_{session_id}"
                )
            ])
        
        buttons.append([
            InlineKeyboardButton(
                text="◀️ رجوع للجلسات",
                callback_data="my_sessions"
            )
        ])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_data_actions(data_id: str) -> InlineKeyboardMarkup:
        """أزرار إدارة البيانات المُلتقطة"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="👁️ عرض التفاصيل",
                    callback_data=f"data_view_{data_id}"
                ),
                InlineKeyboardButton(
                    text="📋 نسخ البيانات",
                    callback_data=f"data_copy_{data_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅ تحقق صحيح",
                    callback_data=f"data_verify_{data_id}"
                ),
                InlineKeyboardButton(
                    text="❌ بيانات خاطئة",
                    callback_data=f"data_invalid_{data_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏷️ إضافة علامة",
                    callback_data=f"data_tag_{data_id}"
                ),
                InlineKeyboardButton(
                    text="📝 إضافة ملاحظة",
                    callback_data=f"data_note_{data_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🗑️ حذف",
                    callback_data=f"data_delete_{data_id}"
                ),
                InlineKeyboardButton(
                    text="◀️ رجوع",
                    callback_data="captured_data"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)

class StatusKeyboard:
    """لوحات المفاتيح لعرض الحالة"""
    
    @staticmethod
    def get_status_indicator(status: str, with_text: bool = True) -> str:
        """مؤشرات الحالة"""
        
        status_indicators = {
            "active": "🟢" + (" نشط" if with_text else ""),
            "inactive": "🔴" + (" متوقف" if with_text else ""),
            "starting": "🟡" + (" جارٍ البدء" if with_text else ""),
            "stopping": "🟠" + (" جارٍ الإيقاف" if with_text else ""),
            "error": "❌" + (" خطأ" if with_text else ""),
            "preparing": "⚪" + (" يتم التحضير" if with_text else ""),
            "paused": "⏸️" + (" موقوف مؤقتاً" if with_text else "")
        }
        
        return status_indicators.get(status, "⚫" + (" غير معروف" if with_text else ""))
    
    @staticmethod
    def get_tunnel_indicator(tunnel_type: str) -> str:
        """مؤشرات نوع النفق"""
        
        tunnel_indicators = {
            "localhost": "🏠 محلي",
            "cloudflared": "☁️ Cloudflared", 
            "localxpose": "🌐 LocalXpose"
        }
        
        return tunnel_indicators.get(tunnel_type, "❓ غير معروف")
    
    @staticmethod
    def get_site_indicator(site_type: str) -> str:
        """مؤشرات نوع الموقع"""
        
        site_indicators = {
            "facebook": "📘",
            "instagram": "📷",
            "google": "📧",
            "twitter": "🐦",
            "linkedin": "💼",
            "discord": "🎮",
            "github": "🐙",
            "netflix": "🎬",
            "paypal": "💳",
            "steam": "🎮"
        }
        
        return site_indicators.get(site_type, "🌐")