#!/usr/bin/env python3
"""
Ternary Local Code Agent & Micro-SaaS Engine
--------------------------------------------
A standard-library-only light engine inspired by Ternary Bonsai logic (-1, 0, +1 weight states).
Provides static code analysis, security auditing, and agentic code scoring for local SaaS endpoints.

Supports `--self-test` for immediate standalone verification.
"""

import sys
import json
import argparse
import ast
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

class TernaryCodeAnalyzer:
    """Core analysis engine utilizing ternary evaluation logic for fast, low-memory local code scoring."""

    def __init__(self):
        # Ternary weight mapping: -1 (Defect/Risk), 0 (Neutral), +1 (Best Practice)
        self.weights = {
            "has_docstring": 1,
            "has_type_hints": 1,
            "unsafe_eval_exec": -1,
            "bare_except": -1,
            "long_function": -1,
        }

    def analyze(self, source_code: str) -> dict:
        score = 0
        findings = []

        try:
            tree = ast.parse(source_code)
        except SyntaxError as err:
            return {
                "status": "error",
                "message": f"Syntax Error: {err}",
                "ternary_state": -1,
                "score": -10,
                "findings": ["Failed to parse Python syntax."]
            }

        func_count = 0
        documented_funcs = 0
        annotated_funcs = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_count += 1

                # Check Docstring (+1)
                if ast.get_docstring(node):
                    documented_funcs += 1

                # Check Type Annotations (+1)
                if node.returns or any(arg.annotation for arg in node.args.args):
                    annotated_funcs += 1

                # Check Function Length (-1 if > 30 lines)
                if len(node.body) > 30:
                    score += self.weights["long_function"]
                    findings.append(f"Quality Warning: Function '{node.name}' is too long (>30 statements).")

            # Check Unsafe Calls (-1)
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ("eval", "exec"):
                    score += self.weights["unsafe_eval_exec"]
                    findings.append(f"Security Alert: Unsafe dynamic call '{node.func.id}' detected.")

            # Check Bare Except (-1)
            elif isinstance(node, ast.ExceptHandler) and node.type is None:
                score += self.weights["bare_except"]
                findings.append("Quality Warning: Bare 'except:' block detected.")

        if func_count > 0:
            if documented_funcs == func_count:
                score += self.weights["has_docstring"]
                findings.append("Optimization: 100% Docstring coverage (+1).")
            if annotated_funcs == func_count:
                score += self.weights["has_type_hints"]
                findings.append("Optimization: 100% Type Annotation coverage (+1).")

        # Classify into Ternary Logic States (-1: High Risk/Low Quality, 0: Neutral/Needs Work, +1: Production Ready)
        if score > 0:
            ternary_state = 1
            quality = "PRODUCTION_READY"
        elif score == 0:
            ternary_state = 0
            quality = "NEEDS_IMPROVEMENT"
        else:
            ternary_state = -1
            quality = "HIGH_RISK_REJECT"

        return {
            "status": "success",
            "quality_rating": quality,
            "ternary_state": ternary_state,
            "total_score": score,
            "metrics": {
                "total_functions": func_count,
                "documented_functions": documented_funcs,
                "annotated_functions": annotated_funcs
            },
            "findings": findings
        }


class AgentRequestHandler(BaseHTTPRequestHandler):
    """Micro-SaaS HTTP Endpoint to process code analysis requests."""

    analyzer = TernaryCodeAnalyzer()

    def do_POST(self):
        if self.path == "/analyze":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            try:
                payload = json.loads(post_data)
                code = payload.get("code", "")
                result = self.analyzer.analyze(code)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result, indent=2).encode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Silence default HTTP server logging for clean output
        pass


def run_self_test() -> bool:
    """Executes non-destructive self-test suite and prints results."""
    print("=== STARTING TERNARY ENGINE SELF-TEST ===")
    analyzer = TernaryCodeAnalyzer()

    # Test Case 1: High Quality Code (+1)
    clean_code = '''
def add_numbers(a: int, b: int) -> int:
    """Adds two integers."""
    return a + b
'''
    res1 = analyzer.analyze(clean_code)
    test1_pass = res1["ternary_state"] == 1

    # Test Case 2: Vulnerable / Poor Code (-1)
    vulnerable_code = '''
def execute_input(user_input):
    try:
        eval(user_input)
    except:
        pass
'''
    res2 = analyzer.analyze(vulnerable_code)
    test2_pass = res2["ternary_state"] == -1

    print(f"Test 1 (Clean Code Evaluation): {'PASSED' if test1_pass else 'FAILED'}")
    print(f"  -> State: {res1['ternary_state']} | Rating: {res1['quality_rating']}")
    
    print(f"Test 2 (Vulnerable Code Evaluation): {'PASSED' if test2_pass else 'FAILED'}")
    print(f"  -> State: {res2['ternary_state']} | Findings: {len(res2['findings'])} security/quality alerts")

    all_passed = test1_pass and test2_pass
    print("-----------------------------------------")
    print(f"OVERALL SELF-TEST RESULT: {'SUCCESS' if all_passed else 'FAILURE'}")
    print("=========================================")
    return all_passed


def main():
    parser = argparse.ArgumentParser(description="Ternary Local Code Agent & Micro-SaaS Engine")
    parser.add_argument("--self-test", action="store_true", help="Run automated self-test and exit")
    parser.add_argument("--port", type=int, default=8080, help="Port to run the HTTP Micro-SaaS API server")
    args = parser.parse_args()

    if args.self_test:
        success = run_self_test()
        sys.exit(0 if success else 1)

    server_address = ('', args.port)
    httpd = HTTPServer(server_address, AgentRequestHandler)
    print(f"Ternary Code Agent Micro-SaaS Server running on port {args.port}...")
    print(f"Endpoint: POST http://localhost:{args.port}/analyze")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server gracefully.")

if __name__ == "__main__":
    main()
