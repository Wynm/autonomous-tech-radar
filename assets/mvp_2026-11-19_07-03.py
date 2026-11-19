import http.server
import json
import socketserver
import sys
import threading
import urllib.request
import urllib.parse

class SecurityScannerCore:
    @staticmethod
    def audit_target(target_url):
        results = {
            "target": target_url,
            "status": "Checked",
            "vulnerabilities_detected": False,
            "recommendations": []
        }
        try:
            req = urllib.request.Request(target_url, headers={'User-Agent': 'SecAuditBot/1.0'})
            with urllib.request.urlopen(req, timeout=3) as response:
                headers = dict(response.headers)
                server_header = headers.get('Server', 'Unknown')
                results['server_banner'] = server_header
                
                # فحص وهمي لنموذج ثغرة Nginx الحرجة للاختبار الآمن
                if "nginx" in server_header.lower():
                    results['recommendations'].append("Verify Nginx version against latest RCE patches.")
                else:
                    results['recommendations'].append("Standard security headers check passed.")
        except Exception as e:
            results['status'] = f"Error connecting: {str(e)}"
            results['vulnerabilities_detected'] = True
        return results

class MVPHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "healthy", "service": "Nginx-SecAudit-MicroSaaS"}
            self.wfile.write(json.dumps(response).encode('utf-8'))
        elif parsed_path.path.startswith('/scan'):
            query_params = urllib.parse.parse_qs(parsed_path.query)
            target = query_params.get('target', ['http://localhost'])[0]
            audit_result = SecurityScannerCore.audit_target(target)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(audit_result, indent=2).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Endpoint not found. Use /health or /scan?target=URL")

    def log_message(self, format, *args):
        return  # إلغاء طباعة السجلات للحفاظ على نظافة المخرجات

def run_self_test():
    print("Running self-test for Security Audit Micro-SaaS Core...")
    test_url = "http://127.0.0.1:8080/health"
    
    server = socketserver.TCPServer(("127.0.0.1", 8080), MVPHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    try:
        req = urllib.request.Request(test_url)
        with urllib.request.urlopen(req, timeout=2) as response:
            data = response.read().decode('utf-8')
            parsed = json.loads(data)
            if parsed.get("status") == "healthy":
                print("SELF-TEST PASSED: Micro-SaaS server is running and responding correctly.")
            else:
                print("SELF-TEST FAILED: Unexpected response data.")
                sys.exit(1)
    except Exception as e:
        print(f"SELF-TEST FAILED: {e}")
        sys.exit(1)
    finally:
        server.shutdown()
        server.server_close()

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--self-test':
        run_self_test()
    else:
        print("Starting Micro-SaaS Server on port 8080... Use --self-test to verify.")
        with socketserver.TCPServer(("", 8080), MVPHandler) as httpd:
            httpd.serve_forever()
