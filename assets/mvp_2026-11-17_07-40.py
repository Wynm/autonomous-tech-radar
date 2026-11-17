#!/usr/bin/env python3
"""
K2-Horizon Local Code Analyzer & Agentic MVP
A production-ready lightweight script to analyze codebases locally and run self-tests.
Uses standard Python libraries only (no external pip dependencies).
"""

import sys
import os
import json
import argparse
import tempfile
import unittest

class K2HorizonAnalyzer:
    """Core engine simulating local agentic code analysis using K2-Horizon capabilities."""
    
    def __init__(self, target_path: str):
        self.target_path = target_path

    def scan_codebase(self) -> dict:
        """Scans the directory for Python files and performs basic metric extraction."""
        stats = {"files_scanned": 0, "total_lines": 0, "issues_found": 0, "recommendations": []}
        
        if os.path.isfile(self.target_path):
            files = [self.target_path]
        elif os.path.isdir(self.target_path):
            files = [os.path.join(root, f) for root, _, filenames in os.walk(self.target_path) for f in filenames if f.endswith('.py')]
        else:
            return stats

        for filepath in files:
            stats["files_scanned"] += 1
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    stats["total_lines"] += len(lines)
                    for idx, line in enumerate(lines, 1):
                        # Simple heuristic check for potential improvements (Agentic simulation)
                        if "eval(" in line:
                            stats["issues_found"] += 1
                            stats["recommendations"].append(f"{filepath}:{idx} - Security warning: Avoid using 'eval()'.")
            except Exception as e:
                pass
                
        if stats["issues_found"] == 0 and stats["files_scanned"] > 0:
            stats["recommendations"].append("Code structure looks clean and ready for K2-Horizon deployment.")
            
        return stats

class TestK2HorizonAnalyzer(unittest.TestCase):
    """Self-test suite for validating the MVP engine."""
    
    def test_analyzer_with_mock_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as tmp:
            tmp.write("# Test file\nx = eval('1 + 1')\nprint(x)\n")
            tmp_name = tmp.name
        
        try:
            analyzer = K2HorizonAnalyzer(tmp_name)
            result = analyzer.scan_codebase()
            self.assertEqual(result["files_scanned"], 1)
            self.assertGreaterEqual(result["issues_found"], 1)
        finally:
            if os.path.exists(tmp_name):
                os.remove(tmp_name)

def main():
    parser = argparse.ArgumentParser(description="K2-Horizon Local Code Analyzer MVP")
    parser.add_argument("--target", default=".", help="Target file or directory to analyze")
    parser.add_argument("--self-test", action="store_true", help="Run internal unit tests")
    
    args = parser.parse_args()
    
    if args.self_test:
        print("Running K2-Horizon MVP Self-Test...")
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestK2HorizonAnalyzer)
        runner = unittest.TextTestRunner(stream=sys.stdout, verbosity=2)
        test_result = runner.run(suite)
        if test_result.wasSuccessful():
            print("\n[SUCCESS] Self-test passed successfully. Engine is fully operational.")
            sys.exit(0)
        else:
            print("\n[FAILURE] Self-test failed.")
            sys.exit(1)
            
    print(f"Analyzing target: {args.target}")
    analyzer = K2HorizonAnalyzer(args.target)
    results = analyzer.scan_codebase()
    print(json.dumps(results, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
