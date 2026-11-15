#!/usr/bin/env python3
"""
Prediction Market Arbitrage & Orderbook Analyzer Engine
Core engine to detect mispriced binary prediction market tokens (Arbitrage).
Uses standard library only. Supports --self-test flag.
"""

import sys
import json
import math
import argparse
from typing import Dict, List, Any


class PredictionMarketArbitrage:
    def __init__(self, platform_fee: float = 0.02):
        """
        Initialize the Arbitrage Engine.
        :param platform_fee: Fee ratio per transaction (e.g., 0.02 = 2%)
        """
        self.platform_fee = platform_fee

    def analyze_binary_spread(self, yes_ask: float, no_ask: float) -> Dict[str, Any]:
        """
        Analyzes YES and NO ask prices for risk-free arbitrage.
        If sum(YES_ask, NO_ask) + fees < 1.00, arbitrage exists.
        """
        if yes_ask <= 0 or no_ask <= 0:
            return {"error": "Prices must be positive numbers"}

        total_cost_raw = yes_ask + no_ask
        total_fee = total_cost_raw * self.platform_fee
        total_cost_effective = total_cost_raw + total_fee
        payout = 1.00  # Binary markets settle at $1.00 for winning side

        profit_margin = payout - total_cost_effective
        roi_percentage = (profit_margin / total_cost_effective) * 100 if total_cost_effective > 0 else 0

        is_arbitrage = profit_margin > 0

        return {
            "yes_ask": round(yes_ask, 4),
            "no_ask": round(no_ask, 4),
            "total_raw_cost": round(total_cost_raw, 4),
            "total_effective_cost": round(total_cost_effective, 4),
            "guaranteed_payout": payout,
            "profit_per_share": round(profit_margin, 4),
            "roi_percentage": round(roi_percentage, 2),
            "is_arbitrage": is_arbitrage
        }

    def batch_scan_orderbook(self, markets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Scans multiple markets for potential arbitrage opportunities.
        """
        opportunities = []
        for market in markets:
            analysis = self.analyze_binary_spread(market.get("yes_ask", 0), market.get("no_ask", 0))
            if analysis.get("is_arbitrage", False):
                analysis["market_id"] = market.get("id")
                analysis["market_title"] = market.get("title")
                opportunities.append(analysis)
        return opportunities


def run_self_test() -> bool:
    """Executes a self-contained test suite without touching system files."""
    print("[+] Initiating Self-Test Suite...")
    engine = PredictionMarketArbitrage(platform_fee=0.01) # 1% Fee

    # Test 1: Valid Arbitrage Case (YES: 0.45, NO: 0.50 => Total: 0.95 + 1% fee = 0.9595 < 1.00)
    res1 = engine.analyze_binary_spread(0.45, 0.50)
    assert res1["is_arbitrage"] is True, "Test 1 Failed: Should detect arbitrage"
    assert res1["roi_percentage"] > 0, "Test 1 Failed: ROI should be positive"
    print("  [PASS] Test 1: Positive Arbitrage Detection")

    # Test 2: No Arbitrage Case (YES: 0.52, NO: 0.50 => Total: 1.02 > 1.00)
    res2 = engine.analyze_binary_spread(0.52, 0.50)
    assert res2["is_arbitrage"] is False, "Test 2 Failed: Should NOT detect arbitrage"
    print("  [PASS] Test 2: Negative Arbitrage Detection")

    # Test 3: Batch Market Scanner
    mock_markets = [
        {"id": "MKT-1", "title": "Will Fed cut rates in Q3?", "yes_ask": 0.40, "no_ask": 0.55}, # Arb! (0.95)
        {"id": "MKT-2", "title": "Will BTC hit 100k?", "yes_ask": 0.65, "no_ask": 0.40}         # No Arb (1.05)
    ]
    opps = engine.batch_scan_orderbook(mock_markets)
    assert len(opps) == 1, f"Test 3 Failed: Expected 1 opportunity, found {len(opps)}"
    assert opps[0]["market_id"] == "MKT-1", "Test 3 Failed: Wrong market identified"
    print("  [PASS] Test 3: Batch Market Scanner")

    print("\n[SUCCESS] ALL SELF-TESTS PASSED PERFECTLY!")
    return True


def main():
    parser = argparse.ArgumentParser(description="Prediction Market Arbitrage Detection Engine")
    parser.add_argument("--self-test", action="store_true", help="Run automated self-tests")
    parser.add_argument("--yes", type=float, help="Ask price for YES option")
    parser.add_argument("--no", type=float, help="Ask price for NO option")
    args = parser.parse_args()

    if args.self_test:
        success = run_self_test()
        sys.exit(0 if success else 1)

    if args.yes is not None and args.no is not None:
        engine = PredictionMarketArbitrage()
        result = engine.analyze_binary_spread(args.yes, args.no)
        print(json.dumps(result, indent=2))
    else:
        print("--- Prediction Market Arbitrage Engine ---")
        print("Usage:")
        print("  Execute Self-Test: python3 script.py --self-test")
        print("  Analyze Pair:      python3 script.py --yes 0.45 --no 0.50")


if __name__ == "__main__":
    main()
