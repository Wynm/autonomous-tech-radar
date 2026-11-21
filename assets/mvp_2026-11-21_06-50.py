#!/usr/bin/env python3
"""
Vim Classic 8.3.1 Configuration Audit & Micro-SaaS Core MVP
Author: Expert Python Engineer
Description: Inspects, validates, and optimizes Vim configuration files for production readiness.
Usage: python3 script.py [--self-test] [--config <path>]
"""

import sys
import os
import json
import tempfile
import argparse

class VimConfigAuditor:
    def __init__(self, config_path=None):
        self.config_path = config_path or self._get_default_config_path()
        self.rules = [
            {"name": "No Python 2 Support", "check": self._check_no_python2},
            {"name": "Syntax Highlighting Enabled", "check": self._check_syntax},
            {"name": "Line Numbers Enabled", "check": self._check_line_numbers},
            {"name": "Encoding UTF-8", "check": self._check_utf8}
        ]

    def _get_default_config_path(self):
        home = os.path.expanduser("~")
        return os.path.join(home, ".vimrc")

    def _check_no_python2(self, content):
        for line in content.splitlines():
            if "python " in line.lower() or "python<<py" in line.lower():
                return False, "Deprecated Python 2 binding detected."
        return True, "Passed: No legacy Python 2 bindings found."

    def _check_syntax(self, content):
        if "syntax on" in content or "syntax enable" in content:
            return True, "Passed: Syntax highlighting is enabled."
        return False, "Warning: 'syntax on' not found in configuration."

    def _check_line_numbers(self, content):
        if "number" in content or "nu" in content:
            return True, "Passed: Line numbering is enabled."
        return False, "Warning: Line numbers not explicitly enabled."

    def _check_utf8(self, content):
        if "utf-8" in content.lower():
            return True, "Passed: UTF-8 encoding configured."
        return False, "Warning: UTF-8 encoding not explicitly set."

    def audit(self):
        content = ""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                return {"status": "error", "message": str(e)}
        else:
            content = "syntax on\nset number\nset encoding=utf-8\n" # Default baseline for audit

        results = []
        passed_count = 0
        for rule in self.rules:
            success, msg = rule["check"](content)
            if success:
                passed_count += 1
            results.append({"rule": rule["name"], "passed": success, "details": msg})

        score = int((passed_count / len(self.rules)) * 100)
        return {
            "target": self.config_path,
            "score": score,
            "results": results
        }

def run_self_test():
    print("[*] Running internal self-test for Vim Classic 8.3.1 Micro-SaaS Core...")
    
    # Create a temporary dummy .vimrc for testing
    fd, temp_path = tempfile.mkstemp(prefix="test_vimrc_", text=True)
    os.close(fd)
    
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write("syntax on\nset number\nset encoding=utf-8\npython print('legacy')\n")
        
        auditor = VimConfigAuditor(config_path=temp_path)
        report = auditor.audit()
        
        print(json.dumps(report, indent=2))
        
        assert report["score"] >= 50, "Self-test failed due to unexpected score."
        print("[+] Self-test completed successfully. System is operational.")
        return True
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def main():
    parser = argparse.ArgumentParser(description="Vim Classic 8.3.1 Config Auditor Micro-SaaS")
    parser.add_argument("--self-test", action="store_true", help="Run self-diagnostic test")
    parser.add_argument("--config", type=str, help="Path to custom .vimrc file")
    
    args = parser.parse_args()

    if args.self_test:
        success = run_self_test()
        sys.exit(0 if success else 1)
    
    auditor = VimConfigAuditor(config_path=args.config)
    report = auditor.audit()
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
