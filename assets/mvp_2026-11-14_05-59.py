import sys
import json
import unittest

def analyze_market_signal(funding_amount: float, gpu_purchases: float, startup_valuation: float) -> dict:
    """
    تحليل مؤشرات السوق واستكشاف ما إذا كان التمويل يُستخدم لإنشاء نندرة مصطنعة
    (Round-Tripping / Circular Funding Analysis).
    """
    if funding_amount <= 0:
        return {"status": "Invalid Data", "risk_score": 0.0, "recommendation": "Reject"}
    
    # نسبة الأموال المعادة لشراء الأصول من الممول نفسه
    recycling_ratio = gpu_purchases / funding_amount
    inflation_factor = startup_valuation / funding_amount
    
    risk_score = min(10.0, (recycling_ratio * 5.0) + (inflation_factor * 0.5))
    
    if risk_score > 7.0:
        recommendation = "High Risk: Artificial Scarcity / Bubble Detected"
    elif risk_score > 4.0:
        recommendation = "Moderate Risk: Monitor Closely"
    else:
        recommendation = "Organic Growth / Low Risk"
        
    return {
        "status": "Success",
        "recycling_ratio": round(recycling_ratio, 2),
        "risk_score": round(risk_score, 2),
        "recommendation": recommendation
    }

class TestMarketAnalyzer(unittest.TestCase):
    def test_analysis_logic(self):
        # اختبار حالة تمويل مشبوه (ندرة مصطنعة)
        result = analyze_market_signal(funding_amount=100.0, gpu_purchases=90.0, startup_valuation=500.0)
        self.assertEqual(result["status"], "Success")
        self.assertGreater(result["risk_score"], 7.0)
        
    def test_organic_growth(self):
        # اختبار حالة نمو طبيعي
        result = analyze_market_signal(funding_amount=100.0, gpu_purchases=10.0, startup_valuation=150.0)
        self.assertLess(result["risk_score"], 5.0)

def run_self_test():
    print("[-] جاري تنفيذ الاختبار الذاتي (Self-Test) لأداة تحليل السوق...")
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestMarketAnalyzer)
    runner = unittest.TextTestRunner(stream=sys.stdout, verbosity=1)
    test_result = runner.run(suite)
    if test_result.wasSuccessful():
        print("[+] اجتاز الاختبار الذاتي بنجاح تام! الأداة جاهزة للتشغيل.")
        return True
    else:
        print("[-] فشل الاختبار الذاتي.")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        success = run_self_test()
        sys.exit(0 if success else 1)
    else:
        # مثال تشغيلي افتراضي عند التشغيل العادي
        sample_data = analyze_market_signal(1000.0, 850.0, 4000.0)
        print("Market Analysis Result:")
        print(json.dumps(sample_data, indent=2, ensure_ascii=False))
        sys.exit(0)
