import sys
import os
import json
import urllib.request
import urllib.error

class SecurityAuditMVP:
    """
    أداة مبدئية مصغرة (MVP) لفحص أمان الشيفرات البرمجية واكتشاف ثغرات الذاكرة التقليدية
    أو الأنماط غير الآمنة (مثل استخدام الدوال الخطرة في C/C++ أو قصور التحقق في Rust/Python)،
    مع دعم كامل لاختبار الذات (--self-test).
    """
    def __init__(self):
        self.dangerous_patterns = [
            "strcpy", "strcat", "sprintf", "gets", 
            "unsafe {", "eval(", "exec("
        ]

    def scan_content(self, filename, content):
        issues = []
        lines = content.splitlines()
        for idx, line in enumerate(lines, 1):
            for pattern in self.dangerous_patterns:
                if pattern in line:
                    issues.append({
                        "line": idx,
                        "pattern": pattern,
                        "content": line.strip(),
                        "severity": "HIGH" if "unsafe" in pattern or "strcpy" in pattern else "MEDIUM"
                    })
        return issues

    def self_test(self):
        print("[*] بدء الاختبار الذاتي (Self-Test) لأداة الأمان...")
        test_code = """
        // اختبار لنمط غير آمن
        void vulnerable_func() {
            char buffer[10];
            strcpy(buffer, "This is too long");
        }
        unsafe {
            let x = raw_ptr;
        }
        """
        results = self.scan_content("test_sample.c", test_code)
        print(f"[*] تم العثور على {len(results)} مشكلة أمنية في عينة الاختبار.")
        
        assert len(results) >= 2, "فشل الاختبار الذاتي: لم يتم رصد الأنماط الخطرة المتوقعة!"
        print("[+] نجح الاختبار الذاتي بنجاح تام! الأداة جاهزة للعمل.")
        return True

if __name__ == "__main__":
    app = SecurityAuditMVP()
    
    # تنفيذ الاختبار الذاتي عند طلب المعامل --self-test
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        try:
            app.self_test()
            sys.exit(0)
        except Exception as e:
            print(f"[-] فشل الاختبار الذاتي: {e}")
            sys.exit(1)
            
    # الاستخدام الافتراضي في حال تمرير ملف للفحص
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
        if os.path.exists(target_file):
            with open(target_file, "r", encoding="utf-8", errors="ignore") as f:
                code_content = f.read()
            found_issues = app.scan_content(target_file, code_content)
            print(json.dumps(found_issues, indent=2, ensure_ascii=False))
        else:
            print(f"[-] الملف غير موجود: {target_file}")
    else:
        print("استخدام الأداة:")
        print("  python script.py --self-test       (لتنفيذ الاختبار الذاتي)")
        print("  python script.py <filename>        (لفحص ملف برمجي)")
