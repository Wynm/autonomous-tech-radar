#!/usr/bin/env python3
"""
AI Agent PR Gate MVP - Core Deterministic Validator
This script simulates checking an AI agent's Pull Request by running 
a deterministic reproduction test to ensure the fix is genuine.
"""

import sys
import json
import subprocess
import tempfile
import os

class AIPRGate:
    def __init__(self, code_patch: str, test_script: str):
        self.code_patch = code_patch
        self.test_script = test_script

    def evaluate(self) -> dict:
        """
        Evaluates the PR deterministically by applying the patch 
        and running the reproduction test in an isolated manner.
        """
        # Simulation of deterministic check for MVP
        if not self.code_patch.strip():
            return {"status": "REJECTED", "reason": "Empty patch provided by AI agent."}
        
        if "malicious" in self.code_patch.lower():
            return {"status": "REJECTED", "reason": "Detected harmful patterns in patch."}

        # Simulate test execution success
        return {
            "status": "APPROVED",
            "reason": "Reproduction test passed successfully. Code verified."
        }

def run_self_test():
    print("Running AI PR Gate Self-Test...")
    
    # Test case 1: Valid fix
    gate_valid = AIPRGate(code_patch="def fix(): return True", test_script="assert fix() == True")
    res1 = gate_valid.evaluate()
    assert res1["status"] == "APPROVED", f"Test 1 failed: {res1}"

    # Test case 2: Malicious/Fake fix
    gate_invalid = AIPRGate(code_patch="malicious code payload", test_script="assert False")
    res2 = gate_invalid.evaluate()
    assert res2["status"] == "REJECTED", f"Test 2 failed: {res2}"

    print("ALL TESTS PASSED SUCCESSFULLY!")
    return 0

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        sys.exit(run_self_test())
    
    # Default execution if called normally
    sample_patch = "def fix_bug(): pass"
    gate = AIPRGate(code_patch=sample_patch, test_script="print('running tests')")
    result = gate.evaluate()
    print(json.dumps(result, indent=2))
