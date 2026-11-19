import sys
import json
import urllib.request
import urllib.error

class POE2PriceAnalyzer:
    """أداة تحليل أسعار الأصول والسلع (نموذج محاكاة سوق Path of Exile 2)"""
    def __init__(self, market_data=None):
        # بيانات افتراضية للسوق تحاكي الأسعار الحية
        self.market_data = market_data or {
            "Divine Orb": {"price_chaos": 185, "trend": "+5%"},
            "Exalted Orb": {"price_chaos": 22, "trend": "-2%"},
            "Chaos Orb": {"price_chaos": 1, "trend": "0%"},
            "Mirror of Kalandra": {"price_chaos": 38000, "trend": "+12%"}
        }

    def analyze_item(self, item_name):
        """تحليل سعر العنصر ومقارنته بمتوسط السوق"""
        item = self.market_data.get(item_name)
        if not item:
            return {"error": "Item not found in market database."}
        
        # محاكاة تقييم الصفقة
        recommendation = "HOLD"
        if "+" in item["trend"]:
            recommendation = "BUY / INVEST"
        elif "-" in item["trend"]:
            recommendation = "SELL QUICK"
            
        return {
            "item": item_name,
            "current_price_chaos": item["price_chaos"],
            "market_trend": item["trend"],
            "recommendation": recommendation
        }

    def run_self_test(self):
        """تنفيذ اختبار ذاتي حقيقي وطباعة النتيجة بوضوح"""
        print("[*] Running POE2PriceAnalyzer Self-Test...")
        test_item = "Divine Orb"
        result = self.analyze_item(test_item)
        
        print(f"[*] Testing item lookup for: {test_item}")
        print(f"[*] Analysis Result: {json.dumps(result, indent=2)}")
        
        assert "current_price_chaos" in result, "Self-test failed: Missing price data"
        assert result["recommendation"] == "BUY / INVEST", "Self-test failed: Unexpected recommendation"
        print("[+] Self-Test Passed Successfully!")
        return True

if __name__ == "__main__":
    analyzer = POE2PriceAnalyzer()
    
    # التحقق من معامل الاختبار الذاتي
    if "--self-test" in sys.argv:
        success = analyzer.run_self_test()
        sys.exit(0 if success else 1)
    else:
        # تشغيل افتراضي في حال عدم وجود المعامل
        print("POE2 Price Checker MVP is running. Use --self-test to execute diagnostics.")
        sample = analyzer.analyze_item("Mirror of Kalandra")
        print(json.dumps(sample, indent=2))
