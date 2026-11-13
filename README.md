# 📡 Autonomous Tech Radar

رادار تقني ذاتي التشغيل يرصد الفرص الجديدة في الذكاء الاصطناعي، Micro-SaaS، والأدوات المفتوحة المصدر، ثم يحللها ويولّد MVP جاهز للتشغيل.

## المصادر المدعومة (v7)

| المصدر | الوصف |
|--------|--------|
| GitHub Search | مستودعات جديدة حسب المجالات الثلاثة |
| GitHub Trending | المستودعات الرائجة يومياً |
| Hacker News | القصص التقنية الرائجة |
| Product Hunt | إطلاقات المنتجات التجارية |
| Hugging Face | أوراق الأبحاث اليومية |
| Reddit | r/SaaS, LocalLLaMA, Entrepreneur, SideProject, startups |
| **Lobsters** | مجتمع تقني عالي الجودة (جديد) |
| **Dev.to** | مقالات المطورين الرائجة (جديد) |

## الميزات

- **مختبر حي سحابي**: يسحب كل مستودع GitHub ويفحص البنية النحوية + عينات الكود + ملفات التهيئة
- **تتبع القفزات المفاجئة** (Breakout Tracker)
- **توليد وتشغيل MVP** تلقائياً مع إصلاح الأخطاء
- **تقرير أسبوعي استراتيجي**
- **إرسال تلقائي عبر تيليجرام** (نص + ملف MVP)

## التشغيل على GitHub Actions

1. أضف الأسرار (Secrets) في إعدادات المستودع:
   - `GEMINI_API_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
2. تأكد من وجود `radar_engine.py` في الجذر و`.github/workflows/autopilot.yml`.
3. فعّل GitHub Actions.

الجدول الافتراضي:
- كل 6 ساعات → الوضع العادي
- الجمعة 18:00 UTC → التقرير الأسبوعي
- يمكن التشغيل يدوياً واختيار الوضع (normal / full / weekly)

## التشغيل المحلي (اختياري)

```bash
export GEMINI_API_KEY="..."
export TELEGRAM_BOT_TOKEN="..."
export TELEGRAM_CHAT_ID="..."
# لتفعيل المختبر الحي محلياً (احذر):
# export ENABLE_SANDBOX=true
python radar_engine.py normal
```

## الترخيص

MIT — استخدم بحرية وعدّل كما تشاء.
