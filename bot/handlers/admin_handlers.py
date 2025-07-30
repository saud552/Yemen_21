"""
👑 معالجات إدارية متقدمة
تشمل إدارة المستخدمين، النظام، التقارير، والإحصائيات
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from pathlib import Path

from ..database import db_manager
from ..config import settings
from ..utils.security import auth_manager, permission_manager, SuperAdminFilter, AdminFilter
from ..utils.file_manager import file_manager
from ..utils.analytics import data_analyzer
from ..keyboards.admin_keyboards import AdminKeyboard

logger = logging.getLogger(__name__)

async def admin_panel_handler(callback: types.CallbackQuery, user):
    """معالج لوحة الإدارة الرئيسية"""
    
    try:
        if not permission_manager.has_permission(user, 'admin_access'):
            await callback.message.edit_text(
                "❌ **ليس لديك صلاحية للوصول لوحة الإدارة**",
                parse_mode="Markdown"
            )
            return
        
        # إحصائيات سريعة
        stats = await db_manager.get_general_statistics()
        
        admin_text = f"""
👑 **لوحة الإدارة المتقدمة**

📊 **إحصائيات سريعة:**
• المستخدمون النشطون: {stats.get('active_users', 0)}
• الجلسات اليوم: {stats.get('sessions_today', 0)}
• البيانات المُلتقطة: {stats.get('total_captures', 0)}
• معدل النجاح: {stats.get('success_rate', 0)}%

🔧 **اختر المهمة المطلوبة:**
"""
        
        await callback.message.edit_text(
            admin_text,
            reply_markup=AdminKeyboard.get_main_admin_menu(user),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"خطأ في لوحة الإدارة: {e}")
        await callback.message.edit_text(
            "❌ حدث خطأ في تحميل لوحة الإدارة",
            reply_markup=AdminKeyboard.get_back_button()
        )

async def user_management_handler(callback: types.CallbackQuery, user):
    """معالج إدارة المستخدمين"""
    
    try:
        if not permission_manager.has_permission(user, 'manage_users'):
            await callback.message.edit_text(
                "❌ **ليس لديك صلاحية إدارة المستخدمين**",
                parse_mode="Markdown"
            )
            return
        
        # إحصائيات المستخدمين
        user_stats = await db_manager.get_user_management_stats()
        
        management_text = f"""
👥 **إدارة المستخدمين**

📈 **الإحصائيات:**
• إجمالي المستخدمين: {user_stats.get('total_users', 0)}
• المستخدمون النشطون: {user_stats.get('active_users', 0)}
• المحظورون: {user_stats.get('banned_users', 0)}
• المدراء: {user_stats.get('admin_users', 0)}

🔧 **المهام المتاحة:**
"""
        
        await callback.message.edit_text(
            management_text,
            reply_markup=AdminKeyboard.get_user_management_menu(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"خطأ في إدارة المستخدمين: {e}")
        await callback.message.edit_text(
            "❌ حدث خطأ في تحميل إدارة المستخدمين",
            reply_markup=AdminKeyboard.get_back_button("admin_panel")
        )

async def list_users_handler(callback: types.CallbackQuery, user, page: int = 1):
    """معالج عرض قائمة المستخدمين"""
    
    try:
        users_per_page = 10
        offset = (page - 1) * users_per_page
        
        # الحصول على المستخدمين
        users_list = await db_manager.get_users_paginated(
            limit=users_per_page,
            offset=offset
        )
        
        total_users = await db_manager.get_total_users_count()
        total_pages = (total_users + users_per_page - 1) // users_per_page
        
        if not users_list:
            await callback.message.edit_text(
                "📭 **لا يوجد مستخدمون**",
                reply_markup=AdminKeyboard.get_back_button("user_management"),
                parse_mode="Markdown"
            )
            return
        
        # إنشاء قائمة المستخدمين
        users_text = f"👥 **قائمة المستخدمين** (صفحة {page}/{total_pages})\n\n"
        
        buttons = []
        for i, user_item in enumerate(users_list, 1 + offset):
            status_icon = "✅" if user_item.is_active else "❌"
            role_icon = "👑" if user_item.role == "super_admin" else "🔧" if user_item.role == "admin" else "👤"
            
            users_text += f"{i}. {role_icon} {user_item.first_name} {status_icon}\n"
            users_text += f"   ID: `{user_item.user_id}` | دور: {user_item.role}\n"
            users_text += f"   آخر نشاط: {user_item.last_seen.strftime('%Y-%m-%d %H:%M')}\n\n"
            
            buttons.append([
                InlineKeyboardButton(
                    text=f"{role_icon} {user_item.first_name}",
                    callback_data=f"manage_user_{user_item.user_id}"
                )
            ])
        
        # أزرار التنقل
        nav_buttons = []
        if page > 1:
            nav_buttons.append(
                InlineKeyboardButton(
                    text="⬅️ السابق",
                    callback_data=f"list_users_{page-1}"
                )
            )
        if page < total_pages:
            nav_buttons.append(
                InlineKeyboardButton(
                    text="➡️ التالي",
                    callback_data=f"list_users_{page+1}"
                )
            )
        
        if nav_buttons:
            buttons.append(nav_buttons)
        
        # أزرار إضافية
        buttons.extend([
            [
                InlineKeyboardButton(
                    text="➕ إضافة مستخدم",
                    callback_data="add_user"
                ),
                InlineKeyboardButton(
                    text="🔍 البحث",
                    callback_data="search_users"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔄 تحديث",
                    callback_data=f"list_users_{page}"
                ),
                InlineKeyboardButton(
                    text="◀️ رجوع",
                    callback_data="user_management"
                )
            ]
        ])
        
        await callback.message.edit_text(
            users_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"خطأ في عرض قائمة المستخدمين: {e}")
        await callback.message.edit_text(
            "❌ حدث خطأ في تحميل قائمة المستخدمين",
            reply_markup=AdminKeyboard.get_back_button("user_management")
        )

async def manage_user_handler(callback: types.CallbackQuery, user, target_user_id: int):
    """معالج إدارة مستخدم محدد"""
    
    try:
        # الحصول على بيانات المستخدم المحدد
        target_user = await db_manager.get_user_by_id(target_user_id)
        
        if not target_user:
            await callback.message.edit_text(
                "❌ **المستخدم غير موجود**",
                reply_markup=AdminKeyboard.get_back_button("list_users_1"),
                parse_mode="Markdown"
            )
            return
        
        # التحقق من الصلاحيات
        if target_user.role == "super_admin" and user.role != "super_admin":
            await callback.message.edit_text(
                "❌ **لا يمكنك إدارة المدير الأعلى**",
                reply_markup=AdminKeyboard.get_back_button("list_users_1"),
                parse_mode="Markdown"
            )
            return
        
        # إحصائيات المستخدم
        user_sessions = await db_manager.get_user_sessions_count(target_user_id)
        user_captures = await db_manager.get_user_captures_count(target_user_id)
        
        status_text = "✅ نشط" if target_user.is_active else "❌ محظور"
        role_icon = "👑" if target_user.role == "super_admin" else "🔧" if target_user.role == "admin" else "👤"
        
        user_text = f"""
👤 **إدارة المستخدم**

{role_icon} **المعلومات الأساسية:**
• الاسم: {target_user.first_name} {target_user.last_name or ''}
• المعرف: `{target_user.user_id}`
• اسم المستخدم: @{target_user.username or 'غير محدد'}

📊 **الإحصائيات:**
• الدور: {target_user.role}
• الحالة: {status_text}
• الجلسات: {user_sessions}
• البيانات المُلتقطة: {user_captures}
• تاريخ التسجيل: {target_user.created_at.strftime('%Y-%m-%d')}
• آخر نشاط: {target_user.last_seen.strftime('%Y-%m-%d %H:%M')}

🔧 **إجراءات الإدارة:**
"""
        
        await callback.message.edit_text(
            user_text,
            reply_markup=AdminKeyboard.get_user_actions_menu(target_user, user.role),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"خطأ في إدارة المستخدم: {e}")
        await callback.message.edit_text(
            "❌ حدث خطأ في تحميل بيانات المستخدم",
            reply_markup=AdminKeyboard.get_back_button("list_users_1")
        )

async def system_management_handler(callback: types.CallbackQuery, user):
    """معالج إدارة النظام"""
    
    try:
        if not permission_manager.has_permission(user, 'system_admin'):
            await callback.message.edit_text(
                "❌ **ليس لديك صلاحية إدارة النظام**",
                parse_mode="Markdown"
            )
            return
        
        # معلومات النظام
        import psutil
        import platform
        
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        system_info = f"""
⚙️ **إدارة النظام**

💻 **معلومات النظام:**
• النظام: {platform.system()} {platform.release()}
• المعالج: {cpu_percent}%
• الذاكرة: {memory.percent}% ({memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB)
• القرص: {disk.percent}% ({disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB)

🗄️ **قاعدة البيانات:**
• حالة الاتصال: {'✅ متصل' if await db_manager.health_check() else '❌ غير متصل'}
• عدد الجلسات النشطة: {len(await db_manager.get_active_sessions())}

🔧 **مهام النظام:**
"""
        
        await callback.message.edit_text(
            system_info,
            reply_markup=AdminKeyboard.get_system_management_menu(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"خطأ في إدارة النظام: {e}")
        await callback.message.edit_text(
            "❌ حدث خطأ في تحميل إدارة النظام",
            reply_markup=AdminKeyboard.get_back_button("admin_panel")
        )

async def export_data_handler(callback: types.CallbackQuery, user):
    """معالج تصدير البيانات"""
    
    try:
        if not permission_manager.has_permission(user, 'export_data'):
            await callback.message.edit_text(
                "❌ **ليس لديك صلاحية تصدير البيانات**",
                parse_mode="Markdown"
            )
            return
        
        export_text = """
💾 **تصدير البيانات**

📋 **الخيارات المتاحة:**
• تصدير جميع البيانات
• تصدير بيانات مستخدم محدد  
• تصدير بيانات فترة زمنية
• إنشاء نسخة احتياطية شاملة

📄 **صيغ التصدير:**
• Excel (.xlsx)
• CSV (.csv)
• JSON (.json)
• PDF تقرير

🔒 **ملاحظة:** جميع كلمات المرور ستكون مخفية في التصدير العادي
"""
        
        await callback.message.edit_text(
            export_text,
            reply_markup=AdminKeyboard.get_export_menu(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"خطأ في تصدير البيانات: {e}")
        await callback.message.edit_text(
            "❌ حدث خطأ في تحميل تصدير البيانات",
            reply_markup=AdminKeyboard.get_back_button("admin_panel")
        )

async def create_backup_handler(callback: types.CallbackQuery, user):
    """معالج إنشاء نسخة احتياطية"""
    
    try:
        # إظهار رسالة التحميل
        await callback.message.edit_text(
            "⏳ **جارٍ إنشاء النسخة الاحتياطية...**\n\nهذا قد يستغرق عدة دقائق",
            reply_markup=None
        )
        
        # إنشاء النسخة الاحتياطية
        backup_path = await file_manager.create_backup(include_files=True)
        
        if backup_path and backup_path.exists():
            # إرسال الملف
            file_info = await file_manager.get_file_info(backup_path)
            
            success_text = f"""
✅ **تم إنشاء النسخة الاحتياطية بنجاح**

📄 **معلومات الملف:**
• الاسم: {file_info['name']}
• الحجم: {file_info['size_mb']} MB
• تاريخ الإنشاء: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📎 **سيتم إرسال الملف الآن...**
"""
            
            await callback.message.edit_text(success_text, parse_mode="Markdown")
            
            # إرسال الملف
            await callback.message.answer_document(
                InputFile(backup_path),
                caption=f"🗄️ نسخة احتياطية - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            
            # حذف الملف المؤقت بعد الإرسال
            backup_path.unlink()
            
        else:
            await callback.message.edit_text(
                "❌ **فشل في إنشاء النسخة الاحتياطية**\n\nحاول مرة أخرى لاحقاً",
                reply_markup=AdminKeyboard.get_back_button("system_management"),
                parse_mode="Markdown"
            )
            
    except Exception as e:
        logger.error(f"خطأ في إنشاء النسخة الاحتياطية: {e}")
        await callback.message.edit_text(
            f"❌ **خطأ في إنشاء النسخة الاحتياطية**\n\n`{str(e)}`",
            reply_markup=AdminKeyboard.get_back_button("system_management"),
            parse_mode="Markdown"
        )

async def analytics_dashboard_handler(callback: types.CallbackQuery, user):
    """معالج لوحة التحليلات"""
    
    try:
        if not permission_manager.has_permission(user, 'view_analytics'):
            await callback.message.edit_text(
                "❌ **ليس لديك صلاحية عرض التحليلات**",
                parse_mode="Markdown"
            )
            return
        
        # الحصول على التحليلات
        analytics = await data_analyzer.get_comprehensive_analytics()
        
        dashboard_text = f"""
📊 **لوحة التحليلات المتقدمة**

📈 **الإحصائيات العامة:**
• إجمالي الجلسات: {analytics.get('total_sessions', 0)}
• معدل النجاح: {analytics.get('success_rate', 0):.1f}%
• أكثر المواقع استخداماً: {analytics.get('top_site', 'غير محدد')}
• متوسط الزوار/جلسة: {analytics.get('avg_visitors', 0):.1f}

🌍 **التوزيع الجغرافي:**
• أكثر الدول: {', '.join(analytics.get('top_countries', [])[:3])}

📱 **الأجهزة:**
• الجوال: {analytics.get('mobile_percentage', 0):.1f}%
• سطح المكتب: {analytics.get('desktop_percentage', 0):.1f}%

⏰ **أوقات الذروة:** {analytics.get('peak_hours', 'غير محدد')}
"""
        
        await callback.message.edit_text(
            dashboard_text,
            reply_markup=AdminKeyboard.get_analytics_menu(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"خطأ في لوحة التحليلات: {e}")
        await callback.message.edit_text(
            "❌ حدث خطأ في تحميل التحليلات",
            reply_markup=AdminKeyboard.get_back_button("admin_panel")
        )

async def security_center_handler(callback: types.CallbackQuery, user):
    """معالج مركز الأمان"""
    
    try:
        if not permission_manager.has_permission(user, 'security_admin'):
            await callback.message.edit_text(
                "❌ **ليس لديك صلاحية الوصول لمركز الأمان**",
                parse_mode="Markdown"
            )
            return
        
        # إحصائيات الأمان
        security_stats = await auth_manager.get_security_statistics()
        
        security_text = f"""
🛡️ **مركز الأمان**

🔒 **حالة النظام:**
• محاولات تسجيل الدخول الفاشلة: {security_stats.get('failed_logins', 0)}
• الجلسات النشطة: {security_stats.get('active_sessions', 0)}
• المستخدمون المحظورون: {security_stats.get('banned_users', 0)}

⚠️ **التحذيرات الأخيرة:**
{chr(10).join(security_stats.get('recent_alerts', ['لا توجد تحذيرات']))}

🔧 **أدوات الأمان:**
"""
        
        await callback.message.edit_text(
            security_text,
            reply_markup=AdminKeyboard.get_security_menu(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"خطأ في مركز الأمان: {e}")
        await callback.message.edit_text(
            "❌ حدث خطأ في تحميل مركز الأمان",
            reply_markup=AdminKeyboard.get_back_button("admin_panel")
        )

# معالجات أخرى متقدمة...

async def broadcast_message_handler(callback: types.CallbackQuery, user):
    """معالج إرسال رسالة جماعية"""
    
    if not permission_manager.has_permission(user, 'broadcast'):
        await callback.message.edit_text(
            "❌ **ليس لديك صلاحية الإرسال الجماعي**",
            parse_mode="Markdown"
        )
        return
    
    broadcast_text = """
📢 **الإرسال الجماعي**

✏️ **اكتب الرسالة التي تريد إرسالها لجميع المستخدمين**

📝 يمكنك استخدام:
• **النص العادي** أو *المائل* أو `الكود`
• الرموز التعبيرية 😊
• الروابط

⚠️ **تحذير:** سيتم إرسال الرسالة لجميع المستخدمين النشطين
"""
    
    await callback.message.edit_text(
        broadcast_text,
        reply_markup=AdminKeyboard.get_broadcast_menu(),
        parse_mode="Markdown"
    )

# التصدير
__all__ = [
    'admin_panel_handler',
    'user_management_handler', 
    'list_users_handler',
    'manage_user_handler',
    'system_management_handler',
    'export_data_handler',
    'create_backup_handler',
    'analytics_dashboard_handler',
    'security_center_handler',
    'broadcast_message_handler'
]