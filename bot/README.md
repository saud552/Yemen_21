# 🤖 Zphisher Pro Telegram Bot

بوت تيليجرام متقدم لإدارة أداة Zphisher بواجهة تفاعلية احترافية ومتكاملة.

## ✨ الميزات الرئيسية

### 🎯 وظائف متقدمة
- **35+ موقع مدعوم** مع أشكال متعددة لكل موقع
- **3 أنواع أنفاق**: Localhost، Cloudflared، LocalXpose
- **مراقبة فورية** للبيانات المُلتقطة
- **إحصائيات وتقارير** مفصلة
- **واجهة تفاعلية** سهلة الاستخدام

### 🛡️ أمان متقدم
- **نظام مصادقة** متعدد المستويات
- **إدارة أذونات** ديناميكية
- **تشفير البيانات** الحساسة
- **حماية من معدل الطلبات** (Rate Limiting)
- **جلسات آمنة** مع JWT

### 📊 إدارة البيانات
- **قاعدة بيانات محسنة** مع SQLAlchemy
- **تحليل جغرافي** لعناوين IP
- **تحليل الأجهزة** والمتصفحات
- **تصدير البيانات** بصيغ متعددة

## 🚀 التثبيت السريع

### المتطلبات الأساسية
- Python 3.9+
- Zphisher (مثبت في مجلد أعلى من البوت)
- رمز بوت تيليجرام من [@BotFather](https://t.me/BotFather)

### خطوات التثبيت

1. **استنساخ المستودع**
```bash
cd /path/to/zphisher
git clone https://github.com/your-repo/zphisher-telegram-bot.git bot
cd bot
```

2. **تثبيت المتطلبات**
```bash
pip install -r requirements.txt
```

3. **إعداد متغيرات البيئة**
```bash
cp .env.example .env
# قم بتعديل .env وإضافة رمز البوت ومعرف المسؤول
```

4. **تشغيل البوت**
```bash
python main.py
```

## ⚙️ الإعداد المفصل

### 1. إعداد ملف البيئة (.env)

```env
# معلومات البوت الأساسية
BOT_TOKEN=your_bot_token_from_botfather
SUPER_ADMIN_ID=your_telegram_user_id
ADMIN_USER_IDS=123456789,987654321

# إعدادات قاعدة البيانات
DATABASE_URL=sqlite+aiosqlite:///./data/bot.db

# إعدادات الأمان
SECRET_KEY=your_secret_key_here
JWT_SECRET=your_jwt_secret_here
ENCRYPTION_KEY=your_encryption_key_here

# مسارات Zphisher
ZPHISHER_PATH=../zphisher.sh
ZPHISHER_SITES_PATH=../.sites/
ZPHISHER_SERVER_PATH=../.server/

# إعدادات الأنفاق
CLOUDFLARED_PATH=../.server/cloudflared
LOCALXPOSE_PATH=../.server/loclx
LOCALXPOSE_TOKEN=your_localxpose_token
```

### 2. الحصول على معرف المستخدم

لمعرفة معرف المستخدم الخاص بك:
1. ابدأ محادثة مع [@userinfobot](https://t.me/userinfobot)
2. ضع المعرف في متغير `SUPER_ADMIN_ID`

### 3. إعداد المجلدات

تأكد من وجود المجلدات التالية:
```
project/
├── zphisher.sh
├── .sites/
├── .server/
│   ├── cloudflared
│   └── loclx
└── bot/
    ├── main.py
    ├── config.py
    └── ...
```

## 🎛️ استخدام البوت

### الأوامر الأساسية
- `/start` - بدء البوت والقائمة الرئيسية
- `/help` - دليل المساعدة
- `/status` - حالة النظام والجلسات
- `/sessions` - الجلسات النشطة
- `/stats` - الإحصائيات الشخصية

### إنشاء جلسة جديدة

1. **اضغط على "🌐 جلسة جديدة"**
2. **اختر فئة الموقع** (وسائل التواصل، خدمات مهنية، إلخ)
3. **حدد الموقع المحدد** من القائمة
4. **اختر نوع النفق**:
   - 🏠 **محلي**: للاختبار المحلي
   - ☁️ **Cloudflared**: نفق مجاني عبر الإنترنت
   - 🌐 **LocalXpose**: نفق بمدة 15 دقيقة مجانية
5. **انتظر إعداد الجلسة** وابدأ الحملة

### إدارة الجلسات

من "📱 جلساتي النشطة" يمكنك:
- **عرض الإحصائيات** المباشرة
- **الحصول على الروابط** (محلي، عام، مختصر، مقنع)
- **مراقبة البيانات** المُلتقطة
- **إيقاف أو إعادة تشغيل** الجلسات

### مراقبة البيانات

استخدم "🎯 البيانات المُلتقطة" لمشاهدة:
- **بيانات الاعتماد** المُلتقطة (مشفرة)
- **معلومات الزوار** (IP، الموقع، الجهاز)
- **إحصائيات مفصلة** حسب البلد والجهاز
- **تحليل زمني** للنشاط

## 🔧 الأدوات المتقدمة

### مولد الروابط المقنعة
- **أقنعة جاهزة**: فحص الأمان، جوائز، استطلاعات
- **أقنعة مخصصة**: إنشاء روابط مقنعة خاصة بك
- **اختصار الروابط**: تقصير الروابط تلقائياً

### قوالب الرسائل
- **رسائل احترافية** لكل موقع
- **نصوص مقنعة** بلغات متعددة
- **قوالب قابلة للتخصيص**

### تصدير البيانات
- **Excel**: ملفات XLSX مفصلة
- **CSV**: للتحليل الإحصائي
- **JSON**: للمطورين
- **PDF**: تقارير احترافية

## 👥 إدارة المستخدمين (للمسؤولين)

### الأدوار المتاحة
- **👑 Super Admin**: جميع الصلاحيات
- **👨‍💼 Admin**: إدارة المستخدمين والجلسات
- **👨‍💻 Operator**: إنشاء وإدارة الجلسات
- **👁️ Viewer**: مشاهدة البيانات فقط
- **🚫 Banned**: محظور

### إدارة الأذونات
```python
# منح إذن لمستخدم
await permission_manager.grant_permission(
    user_id=123456789,
    permission="session.create",
    granted_by=admin_id
)

# سحب إذن من مستخدم
await permission_manager.revoke_permission(
    user_id=123456789,
    permission="session.create",
    revoked_by=admin_id
)
```

## 📊 النظام الأمني

### التشفير
- **بيانات الاعتماد**: مشفرة بـ Fernet
- **الجلسات**: محمية بـ JWT
- **كلمات المرور**: مُشفرة بـ bcrypt

### الحماية من التهديدات
- **Rate Limiting**: حد أقصى 30 طلب/دقيقة
- **جلسات آمنة**: انتهاء صلاحية تلقائي
- **تسجيل شامل**: جميع الأنشطة مُسجلة
- **IP Tracking**: مراقبة المصادر المشبوهة

## 🐛 استكشاف الأخطاء

### مشاكل شائعة

**1. البوت لا يستجيب**
```bash
# تحقق من السجلات
tail -f logs/bot.log

# تحقق من صحة رمز البوت
python -c "from config import settings; print(settings.BOT_TOKEN[:10])"
```

**2. فشل في إنشاء الجلسات**
```bash
# تحقق من وجود ملفات Zphisher
ls -la ../.sites/
ls -la ../.server/

# تحقق من صلاحيات PHP
which php
php --version
```

**3. مشاكل قاعدة البيانات**
```bash
# إعادة تهيئة قاعدة البيانات
rm data/bot.db
python -c "from database import create_tables; import asyncio; asyncio.run(create_tables())"
```

**4. مشاكل الأنفاق**
```bash
# للCloudflared
../server/cloudflared version

# للLocalXpose
../server/loclx version
```

### السجلات والمراقبة

السجلات محفوظة في:
- `logs/bot.log` - سجل البوت العام
- `logs/database.log` - سجل قاعدة البيانات
- `logs/security.log` - سجل الأمان

## 🔄 التحديث والصيانة

### تحديث البوت
```bash
git pull origin main
pip install -r requirements.txt --upgrade
python main.py
```

### النسخ الاحتياطي
```bash
# نسخ احتياطي لقاعدة البيانات
cp data/bot.db backups/bot_$(date +%Y%m%d_%H%M%S).db

# نسخ احتياطي للإعدادات
cp .env backups/env_$(date +%Y%m%d_%H%M%S).backup
```

### تنظيف البيانات القديمة
```python
# تنظيف البيانات الأقدم من 30 يوم
from database import db_manager
import asyncio

async def cleanup():
    result = await db_manager.cleanup_old_data(days=30)
    print(f"تم حذف: {result}")

asyncio.run(cleanup())
```

## 🚨 الأمان والقانون

### ⚠️ تنويه مهم
- هذه الأداة مخصصة **للأغراض التعليمية** فقط
- استخدمها بمسؤولية وفقاً **للقوانين المحلية**
- المطور **غير مسؤول** عن سوء الاستخدام

### أفضل الممارسات الأمنية
1. **غيّر كلمات المرور** الافتراضية
2. **استخدم مفاتيح تشفير قوية** (32+ حرف)
3. **قيّد الوصول** للمستخدمين الموثوقين فقط
4. **راقب السجلات** بانتظام
5. **احتفظ بنسخ احتياطية** دورية

## 🤝 المساهمة والدعم

### المساهمة في التطوير
1. Fork المستودع
2. إنشاء فرع جديد للميزة
3. إجراء التغييرات
4. إرسال Pull Request

### الحصول على الدعم
- **GitHub Issues**: للبلاغات والمشاكل التقنية
- **Telegram**: [@your_support_username](https://t.me/your_support_username)
- **Email**: support@yourproject.com

### التبرع والدعم
إذا كان هذا المشروع مفيداً لك، يمكنك دعمنا:
- **Bitcoin**: `bc1q...`
- **PayPal**: `https://paypal.me/yourproject`

## 📄 الرخصة

هذا المشروع مرخص تحت [MIT License](LICENSE).

---

**تطوير بواسطة**: فريق Zphisher Pro  
**الإصدار**: 1.0.0  
**تاريخ التحديث**: 2024-12-28

---

💡 **نصيحة**: للاستفادة القصوى من البوت، اقرأ جميع أقسام الدليل وجرب الميزات المختلفة في بيئة آمنة أولاً.