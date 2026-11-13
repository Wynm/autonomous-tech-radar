import sys
import json
import urllib.request
import urllib.error

class IntentRouter:
    """
    موجّه نوايا ذكي (Intent Decider) يعتمد على مكتبات بايثون القياسية فقط.
    يصنف الاستعلامات لحظياً لتحديد أفضل مسار معالجة (بحث، استدلال، أو إجابة سريعة).
    """
    def __init__(self):
        self.rules = {
            "search": ["سعر", "أخبار", "حدث", "متى", "أين", "price", "news", "latest", "update"],
            "reasoning": ["لماذا", "كيف", "مقارنة", "تحليل", "why", "how", "compare", "analyze"],
            "direct": []
        }

    def route(self, query: str) -> dict:
        q_lower = query.lower()
        
        # فحص قواعد الاستدلال
        for kw in self.rules["reasoning"]:
            if kw in q_lower:
                return {
                    "intent": "complex_reasoning",
                    "recommended_model": "reasoning-model-pro",
                    "cost_level": "high",
                    "action": "route_to_deep_llm"
                }
                
        # فحص قواعد البحث اللحظي
        for kw in self.rules["search"]:
            if kw in q_lower:
                return {
                    "intent": "realtime_search",
                    "recommended_model": "search-augmented-llm",
                    "cost_level": "medium",
                    "action": "trigger_web_search_agent"
                }
                
        # الافتراضي: إجابة سريعة ورخيصة
        return {
            "intent": "direct_answer",
            "recommended_model": "fast-cheap-llm",
            "cost_level": "low",
            "action": "respond_directly"
        }

def run_self_test():
    print("[-] بدء الاختبار الذاتي لنظام Intent Router...")
    router = IntentRouter()
    
    test_cases = [
        ("ما هو سعر سهم تسلا اليوم؟", "realtime_search"),
        ("لماذا تفشل الشركات الناشئة في مراحلها المبكرة؟", "complex_reasoning"),
        ("مرحباً بك", "direct_answer")
    ]
    
    passed = 0
    for query, expected_intent in test_cases:
        result = router.route(query)
        print(f"  * الاستعلام: '{query}' -> التوجيه المكتشف: {result['intent']}")
        if result['intent'] == expected_intent:
            passed += 1
            
    print(f"[-] نتيجة الاختبار الذاتي: نجح {passed} من {len(test_cases)} اختبارات.")
    if passed == len(test_cases):
        print("[+] SUCCESS: جميع اختبارات التوجيه اجتازت بنجاح تامن!")
        return 0
    else:
        print("[-] FAILED: بعض الاختبارات فشلت.")
        return 1

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        sys.exit(run_self_test())
    else:
        # تشغيل تجريبي افتراضي
        router = IntentRouter()
        sample_query = "كيف يمكنني تحسين أداء خوادم بايثون؟"
        print(json.dumps(router.route(sample_query), ensure_ascii=False, indent=2))
