import urllib.request
import json
import sys
import time

class CodebergHealthMonitor:
    def __init__(self, target_url="https://codeberg.org"):
        self.target_url = target_url

    def check_health(self):
        """فحص حالة توفر منصة Codeberg أو أي خادم مستودعات بديل"""
        start_time = time.time()
        try:
            req = urllib.request.Request(
                self.target_url,
                headers={'User-Agent': 'Codeberg-SaaS-Monitor/1.0'}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                latency = round((time.time() - start_time) * 1000, 2)
                return {
                    "status": "UP",
                    "status_code": response.status,
                    "latency_ms": latency,
                    "url": self.target_url
                }
        except Exception as e:
            return {
                "status": "DOWN",
                "error": str(e),
                "url": self.target_url
            }

    def run_self_test(self):
        print("[-] Running Self-Test for Codeberg Monitor Micro-SaaS Core...")
        result = self.check_health()
        print(f"[-] Test Result: {json.dumps(result, indent=2)}")
        
        if result["status"] == "UP":
            print("[✓] Self-Test Passed Successfully: Infrastructure is reachable.")
            return True
        else:
            print("[X] Self-Test Warning: Target is currently unreachable.")
            return False

if __name__ == "__main__":
    monitor = CodebergHealthMonitor()
    
    if "--self-test" in sys.argv:
        success = monitor.run_self_test()
        sys.exit(0 if success else 1)
    else:
        print(json.dumps(monitor.check_health(), indent=2))
