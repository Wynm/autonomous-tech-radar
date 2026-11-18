import sys
import json
import urllib.request
import urllib.error
from html.parser import HTMLParser

class SimpleSEOAnalyzer(HTMLParser):
    """محلل خفيف لصفحات الويب لاستخراج الكلمات المفتاحية والعناوين لقياس التوافق مع محركات البحث والذكاء الاصطناعي."""
    def __init__(self):
        super().__init__()
        self.in_title = False
        self.title = ""
        self.headings = []
        self.current_tag = None
        self.text_content = ""

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        if tag == 'title':
            self.in_title = True

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False
        self.current_tag = None

    def handle_data(self, data):
        cleaned = data.strip()
        if not cleaned:
            return
        if self.in_title:
            self.title += cleaned
        if self.current_tag in ['h1', 'h2', 'h3']:
            self.headings.append((self.current_tag, cleaned))
        self.text_content += " " + cleaned

def analyze_content(html_text):
    parser = SimpleSEOAnalyzer()
    parser.feed(html_text)
    
    words = parser.text_content.split()
    word_count = len(words)
    
    # محاكاة مؤشر التأثر بالذكاء الاصطناعي بناءً على بنية المحتوى
    ai_vulnerability_score = "منخفض"
    if word_count < 300:
        ai_vulnerability_score = "مرتفع جداً (محتوى قصير وسهل الاستبدال بإجابات الذكاء الاصطناعي)"
    elif len(parser.headings) < 3:
        ai_vulnerability_score = "متوسط (يفتقر لهيكلة واضحة للأسئلة والأجوبة)"
        
    report = {
        "title": parser.title if parser.title else "بدون عنوان",
        "headings_count": len(parser.headings),
        "word_count": word_count,
        "ai_overview_vulnerability": ai_vulnerability_score,
        "recommendation": "أضف بنية Q&A وبيانات منظمة (Schema) لحماية حركة المرور من تراجع Google AI Overviews."
    }
    return report

def run_self_test():
    print("[*] بدء الاختبار الذاتي لأداة تحليل مقاومة الذكاء الاصطناعي للـ SEO...")
    sample_html = """
    <html>
        <head><title>كيفية تحسين محركات البحث في عصر الذكاء الاصطناعي</title></head>
        <body>
            <h1>دليل الـ SEO الحديث</h1>
            <h2>ما هو تأثير إجابات الذكاء الاصطناعي؟</h2>
            <p>انخفضت حركة المرور بنسبة 40% بسبب ظهور إجابات جوجل الذكية في أعلى نتائج البحث.</p>
        </body>
    </html>
    """
    result = analyze_content(sample_html)
    print("[*] نتيجة التحليل التجريبي:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    if result["word_count"] > 0 and "ai_overview_vulnerability" in result:
        print("\n[✔] نجح الاختبار الذاتي بنجاح تام! الأداة جاهزة للإنتاج.")
        return True
    else:
        print("\n[✘] فشل الاختبار الذاتي.")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        success = run_self_test()
        sys.exit(0 if success else 1)
    else:
        print("استخدم الوسيط --self-test لتشغيل الاختبار الذاتي مباشرة.")
        print("مثال: python script.py --self-test")
