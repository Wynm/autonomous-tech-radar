import sys
import json
import argparse
import uuid
import hashlib
from datetime import datetime

class AICanaryEngine:
    """
    نواة أداة أمنية لحماية سلاسل إمداد الذكاء الاصطناعي عبر زراعة ومراقبة الوسوم التمويهية (Canary Tokens)
    في قواعد البيانات المتجهة (Vector DBs) وبيئات RAG لتكشيف تسريب البيانات الحساسة.
    """
    def __init__(self):
        self.registry = {}

    def generate_token(self, label: str, token_type: str = "api_key") -> dict:
        """توليد وسم تمويهي فريد وتسجيله في النظام"""
        token_id = str(uuid.uuid4())[:8]
        
        if token_type == "api_key":
            token_val = f"sk-live-canary-{token_id}-{hashlib.md5(token_id.encode()).hexdigest()[:6]}"
        elif token_type == "email":
            token_val = f"canary.{token_id}@audit-ai-security.internal"
        else:
            token_val = f"CANARY_SECRET_{token_id.upper()}"

        record = {
            "token": token_val,
            "label": label,
            "token_type": token_type,
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        self.registry[token_val] = record
        return record

    def inject_canary_into_context(self, context_text: str, token_val: str) -> str:
        """دمج الوسم التمويهي في سياق النص المعالج لبيئات RAG"""
        metadata_block = f"\n<!-- SYSTEM_SECURITY_CANARY: {token_val} -->\n"
        return context_text + metadata_block

    def scan_output_for_leaks(self, text_payload: str) -> list:
        """فحص النص المخرج من نموذج الذكاء الاصطناعي للكشف عن تسريب أي وسم تمويهي"""
        detected_leaks = []
        for token_val, meta in self.registry.items():
            if token_val in text_payload:
                detected_leaks.append({
                    "alert": "DATA_LEAK_DETECTED",
                    "severity": "CRITICAL",
                    "token_found": token_val,
                    "metadata": meta,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                })
        return detected_leaks

def run_self_test():
    """اختبار ذاتي شامل للتحقق من كفاءة الأداة بدون التعديل على النظام"""
    print("=== STARTING AI CANARY ENGINE SELF-TEST ===")
    engine = AICanaryEngine()

    # 1. اختبار توليد الوسوم
    tok_record = engine.generate_token("RAG_Confidential_DB", "api_key")
    token_val = tok_record["token"]
    assert token_val.startswith("sk-live-canary-"), "Test Failed: Invalid API key generation format"
    print("[PASS] 1. Canary Token Generation Success.")

    # 2. اختبار الحقن والدمج
    original_text = "This document contains enterprise financial forecasts for Q4."
    injected_text = engine.inject_canary_into_context(original_text, token_val)
    assert token_val in injected_text, "Test Failed: Injection failed to append canary token"
    print("[PASS] 2. Canary Injection into RAG Context Success.")

    # 3. اختبار كشف التسريب (حالة إيجابية)
    simulated_llm_response = f"Based on internal documents, the key is {token_val}."
    leaks = engine.scan_output_for_leaks(simulated_llm_response)
    assert len(leaks) == 1, "Test Failed: Leak detection failed to capture compromised token"
    assert leaks[0]["metadata"]["label"] == "RAG_Confidential_DB", "Test Failed: Metadata mismatch"
    print("[PASS] 3. Data Leak Detection Engine Success.")

    # 4. اختبار حالة النص السليم (عدم وجود بلاغ كاذب)
    clean_response = "Here is the public summary of company operations."
    clean_leaks = engine.scan_output_for_leaks(clean_response)
    assert len(clean_leaks) == 0, "Test Failed: False positive leak detected"
    print("[PASS] 4. False-Positive Validation Success.")

    print("\n[RESULT] ALL SELF-TESTS PASSED SUCCESSFULLY! (100% Operational Readiness)\n")
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="AI Supply Chain Canary Token & Leak Detector MVP")
    parser.add_argument("--self-test", action="store_true", help="Execute standalone unit & integration self-tests")
    parser.add_argument("--generate", type=str, help="Generate a canary token with a specific label")
    parser.add_argument("--type", type=str, default="api_key", choices=["api_key", "email", "secret"], help="Canary token type")
    parser.add_argument("--scan", type=str, help="Scan string payload for active canary token leaks")

    args = parser.parse_args()

    if args.self_test:
        run_self_test()

    engine = AICanaryEngine()

    if args.generate:
        result = engine.generate_token(args.generate, args.type)
        print(json.dumps(result, indent=2))
    elif args.scan:
        # تسجيل وسم تجريبي لمعاينة الفحص المباشر عبر CLI
        engine.generate_token("CLI_Sample_Canary", "api_key")
        scan_results = engine.scan_output_for_leaks(args.scan)
        output = {
            "scanned_payload_length": len(args.scan),
            "total_leaks_found": len(scan_results),
            "details": scan_results
        }
        print(json.dumps(output, indent=2))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
