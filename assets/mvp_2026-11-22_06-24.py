#!/usr/bin/env python3
"""
Polymarket Arbitrage & Odds Analyzer MVP
Standard Library Only (No pip dependencies required)
"""

import argparse
import json
import math
import sys
import urllib.request
import urllib.error
from typing import Dict, List, Any


class PolymarketArbitrageEngine:
    """محرك فحص واكتشاف فرص الموازنة (Arbitrage) لأسواق التنبؤ الثنائية"""

    def __init__(self, fee_percentage: float = 0.0):
        self.fee_rate = fee_percentage / 100.0

    def calculate_binary_arbitrage(self, yes_ask: float, no_ask: float) -> Dict[str, Any]:
        """
        حساب عائد الموازنة للعقد الثنائي (YES + NO).
        توجد فرصة موازنة ربحية إذا كان (سعر YES + سعر NO + الرسوم) أقل من 1.0 دولار.
        """
        if yes_ask <= 0 or no_ask <= 0:
            return {"arbitrage_opportunity": False, "reason": "Invalid pricing"}

        total_cost = (yes_ask + no_ask) * (1.0 + self.fee_rate)
        payout = 1.0  # العائد المؤكد للطرف الفائز في عقد Polymarket
        profit = payout - total_cost
        roi_percentage = (profit / total_cost) * 100.0 if total_cost > 0 else 0.0

        # توزيع رأس المال الأمثل لمبلغ 100 دولار للتحوط الكامل
        budget = 100.0
        yes_allocation = (budget * (1.0 / yes_ask)) / ((1.0 / yes_ask) + (1.0 / no_ask))
        no_allocation = budget - yes_allocation

        return {
            "arbitrage_opportunity": profit > 0,
            "yes_ask": round(yes_ask, 4),
            "no_ask": round(no_ask, 4),
            "total_cost_per_share": round(total_cost, 4),
            "profit_per_share": round(profit, 4),
            "roi_percentage": round(roi_percentage, 2),
            "suggested_allocation_100_usd": {
                "buy_yes_usd": round(yes_allocation, 2),
                "buy_no_usd": round(no_allocation, 2)
            }
        }

    def scan_mock_or_live_markets(self, markets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """مسح مجموعة من الأسواق واستخراج الفرص الربحية"""
        opportunities = []
        for market in markets:
            title = market.get("title", market.get("question", "Unknown Market"))
            yes_price = market.get("yes_price", 0.0)
            no_price = market.get("no_price", 0.0)

            result = self.calculate_binary_arbitrage(yes_price, no_price)
            if result["arbitrage_opportunity"]:
                result["market_title"] = title
                opportunities.append(result)
        return opportunities


def run_self_test() -> bool:
    """تنفيذ اختبار ذاتي شامل للتأكد من صحة الحسابات دون تعديل النظام"""
    print("=== RUNNING SELF-TEST: Polymarket Arbitrage Engine ===")
    engine = PolymarketArbitrageEngine(fee_percentage=0.5)

    # الاختبار 1: حالة وجود فرصة موازنة مؤكدة (YES: $0.47, NO: $0.48, الرسوم: 0.5%)
    res1 = engine.calculate_binary_arbitrage(0.47, 0.48)
    assert res1["arbitrage_opportunity"] is True, "Test Case 1 Failed: Should detect arbitrage"
    assert res1["profit_per_share"] > 0, "Test Case 1 Failed: Profit should be > 0"
    print(f"[PASS] Test Case 1 (Arbitrage Detected): Profit ROI = {res1['roi_percentage']}%")

    # الاختبار 2: حالة عدم وجود فرصة موازنة (YES: $0.52, NO: $0.51)
    res2 = engine.calculate_binary_arbitrage(0.52, 0.51)
    assert res2["arbitrage_opportunity"] is False, "Test Case 2 Failed: Should NOT detect arbitrage"
    print("[PASS] Test Case 2 (No Arbitrage): Correctly identified normal market state")

    # الاختبار 3: مسح دفعة أسواق وتصنيف الفرص
    mock_markets = [
        {"title": "BTC > $100k in 15min", "yes_price": 0.45, "no_price": 0.49},  # مجموع 0.94 -> فرصة
        {"title": "ETH > $4k in 15min", "yes_price": 0.51, "no_price": 0.52},   # مجموع 1.03 -> ليس فرصة
    ]
    scan_results = engine.scan_mock_or_live_markets(mock_markets)
    assert len(scan_results) == 1, "Test Case 3 Failed: Should find exactly 1 opportunity"
    assert scan_results[0]["market_title"] == "BTC > $100k in 15min"
    print(f"[PASS] Test Case 3 (Batch Scanning): Successfully filtered {len(scan_results)} arbitrage opportunity")

    print("=== ALL SELF-TESTS PASSED SUCCESSFULLY ===")
    return True


def main():
    parser = argparse.ArgumentParser(description="Polymarket Arbitrage & Odds Analyzer MVP")
    parser.add_argument("--self-test", action="store_true", help="Run automated self-tests and exit")
    parser.add_argument("--yes", type=float, help="Ask price for YES outcome (e.g. 0.47)")
    parser.add_argument("--no", type=float, help="Ask price for NO outcome (e.g. 0.48)")
    parser.add_argument("--fee", type=float, default=0.0, help="Exchange fee percentage (default: 0.0)")

    args = parser.parse_args()

    if args.self_test:
        success = run_self_test()
        sys.exit(0 if success else 1)

    if args.yes is not None and args.no is not None:
        engine = PolymarketArbitrageEngine(fee_percentage=args.fee)
        analysis = engine.calculate_binary_arbitrage(args.yes, args.no)
        print(json.dumps(analysis, indent=2, ensure_ascii=False))
    else:
        print("No direct price inputs provided. Running sample calculation...")
        engine = PolymarketArbitrageEngine(fee_percentage=0.2)
        sample = engine.calculate_binary_arbitrage(0.46, 0.49)
        print(json.dumps(sample, indent=2, ensure_ascii=False))
        print("\nUsage example:")
        print("  python script.py --yes 0.47 --no 0.48 --fee 0.2")
        print("  python script.py --self-test")


if __name__ == "__main__":
    main()
