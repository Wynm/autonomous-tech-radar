import argparse
import json
import sys
import urllib.request
import urllib.error

class DataBrokerDeleterMVP:
    def __init__(self, target_email: str):
        self.target_email = target_email
        # قائمة تجريبية لوسطاء بيانات وهمية لأغراض الاختبار الذاتي
        self.brokers = [
            {"name": "MockBrokerA", "opt_out_url": "https://httpbin.org/post"},
            {"name": "MockBrokerB", "opt_out_url": "https://httpbin.org/post"}
        ]

    def send_removal_request(self, broker):
        payload = json.dumps({"email": self.target_email, "action": "opt_out"}).encode('utf-8')
        req = urllib.request.Request(
            broker["opt_out_url"],
            data=payload,
            headers={'Content-Type': 'application/json', 'User-Agent': 'DataPrivacyBot/1.0'}
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                return response.status == 200
        except Exception:
            return False

    def run_audit(self):
        results = []
        for broker in self.brokers:
            success = self.send_removal_request(broker)
            results.append({"broker": broker["name"], "status": "Submitted" if success else "Failed"})
        return results

    def self_test(self):
        print("[*] Running Self-Test for DataBrokerDeleterMVP...")
        test_results = self.run_audit()
        print(f"[*] Test Results: {json.dumps(test_results, indent=2)}")
        if len(test_results) > 0:
            print("[+] Self-Test PASSED successfully.")
            return True
        else:
            print("[-] Self-Test FAILED.")
            return False

def main():
    parser = argparse.ArgumentParser(description="Data Broker Deletion Requests Automation MVP")
    parser.add_argument("--email", type=str, default="user@example.com", help="Target email for deletion")
    parser.add_argument("--self-test", action="store_true", help="Run internal self-test")
    
    args = parser.parse_args()
    
    bot = DataBrokerDeleterMVP(target_email=args.email)
    
    if args.self_test:
        success = bot.self_test()
        sys.exit(0 if success else 1)
    else:
        print(f"[*] Starting removal requests for: {args.email}")
        results = bot.run_audit()
        print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
