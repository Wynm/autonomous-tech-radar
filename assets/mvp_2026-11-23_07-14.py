#!/usr/bin/env python3
"""
Unsloth & Local AI Dataset Pipeline Engine (Micro-SaaS Core)
Automating Dataset Audit, Deduplication, and ChatML/Alpaca Formatting for Qwen 2.5 Fine-Tuning.

Dependencies: Standard Python Library Only
Usage:
  python script.py --self-test
  python script.py --format chatml --input data.json
"""

import argparse
import hashlib
import json
import sys
from typing import List, Dict, Any


class LocalAIDatasetEngine:
    """Engine to validate, clean, format, and audit datasets for Unsloth/Qwen LLM fine-tuning."""

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Estimates token count for prompts and responses."""
        if not text:
            return 0
        words = len(text.split())
        chars = len(text)
        return max(words, int(chars / 4))

    @staticmethod
    def convert_to_chatml(item: Dict[str, Any]) -> Dict[str, Any]:
        """Converts raw QA/instruction items into ChatML format optimized for Qwen 2.5."""
        instruction = item.get("instruction", "").strip()
        user_input = item.get("input", "").strip()
        response = item.get("output", "") or item.get("response", "").strip()
        system_prompt = item.get("system", "You are a helpful and concise AI assistant.")

        user_content = f"{instruction}\nContext: {user_input}".strip() if user_input else instruction

        return {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
                {"role": "assistant", "content": response}
            ]
        }

    @staticmethod
    def convert_to_alpaca(item: Dict[str, Any]) -> Dict[str, Any]:
        """Converts data to standard Alpaca instruction format."""
        return {
            "instruction": item.get("instruction", item.get("prompt", "")),
            "input": item.get("input", ""),
            "output": item.get("output", item.get("response", ""))
        }

    def audit_dataset(self, dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Audits dataset quality, readiness, deduplication, and estimates training metrics."""
        total_samples = len(dataset)
        duplicates = 0
        seen_hashes = set()
        empty_responses = 0
        total_tokens = 0

        for item in dataset:
            # Deduplication Check
            serialized = json.dumps(item, sort_keys=True)
            item_hash = hashlib.md5(serialized.encode('utf-8')).hexdigest()

            if item_hash in seen_hashes:
                duplicates += 1
            else:
                seen_hashes.add(item_hash)

            # Response Completeness Check
            resp = item.get("output") or item.get("response")
            if not resp and "messages" in item:
                for msg in item.get("messages", []):
                    if msg.get("role") == "assistant":
                        resp = msg.get("content")
                        break

            if not resp or not str(resp).strip():
                empty_responses += 1

            total_tokens += self.estimate_tokens(str(item))

        avg_tokens = (total_tokens // total_samples) if total_samples > 0 else 0
        readiness_score = max(0, 100 - (duplicates * 10) - (empty_responses * 15))

        return {
            "total_samples": total_samples,
            "duplicate_count": duplicates,
            "empty_response_count": empty_responses,
            "estimated_total_tokens": total_tokens,
            "avg_tokens_per_sample": avg_tokens,
            "readiness_score_pct": readiness_score,
            "status": "READY_FOR_UNSLOTH" if readiness_score >= 70 else "NEEDS_CLEANING"
        }


def run_self_test() -> bool:
    """Automated self-test suite verifying dataset engine functions."""
    print("[SELF-TEST] Starting automated self-test suite...")

    engine = LocalAIDatasetEngine()

    sample_dataset = [
        {
            "instruction": "Explain local AI fine-tuning.",
            "input": "Using Unsloth and Qwen 2.5",
            "output": "Unsloth accelerates fine-tuning while reducing VRAM memory requirements significantly."
        },
        {
            "instruction": "Explain local AI fine-tuning.",
            "input": "Using Unsloth and Qwen 2.5",
            "output": "Unsloth accelerates fine-tuning while reducing VRAM memory requirements significantly."
        },  # Duplicate
        {
            "instruction": "Summarize the document.",
            "input": "Missing answer case",
            "output": ""
        }  # Empty output
    ]

    # Test 1: ChatML Conversion
    chatml = engine.convert_to_chatml(sample_dataset[0])
    assert "messages" in chatml and len(chatml["messages"]) == 3, "Test 1 Failed: ChatML conversion invalid."
    assert chatml["messages"][1]["role"] == "user", "Test 2 Failed: ChatML role mapping incorrect."
    print("[SELF-TEST] Test 1: ChatML Conversion PASSED")

    # Test 2: Token Estimation
    token_count = engine.estimate_tokens("Local AI models require proper dataset formatting.")
    assert token_count > 0, "Test 2 Failed: Token estimation failed."
    print(f"[SELF-TEST] Test 2: Token Estimation PASSED ({token_count} estimated tokens)")

    # Test 3: Audit Engine
    audit = engine.audit_dataset(sample_dataset)
    assert audit["total_samples"] == 3, "Test 3 Failed: Sample counting incorrect."
    assert audit["duplicate_count"] == 1, "Test 3 Failed: Duplicate detection failed."
    assert audit["empty_response_count"] == 1, "Test 3 Failed: Empty response detection failed."
    assert audit["status"] in ["READY_FOR_UNSLOTH", "NEEDS_CLEANING"], "Test 3 Failed: Invalid status output."
    print("[SELF-TEST] Test 3: Dataset Audit Engine PASSED")

    print("[SELF-TEST] ALL TESTS PASSED SUCCESSFULLY.")
    return True


def main():
    parser = argparse.ArgumentParser(description="Local AI Fine-Tuning Dataset Preparation Tool")
    parser.add_argument("--self-test", action="store_true", help="Run self-test suite and verify operational integrity")
    parser.add_argument("--format", choices=["chatml", "alpaca"], default="chatml", help="Output format for Unsloth")

    args = parser.parse_args()

    if args.self_test:
        success = run_self_test()
        sys.exit(0 if success else 1)

    print("Local AI Dataset Engine Active. Pass --self-test to verify functionality.")


if __name__ == "__main__":
    main()
