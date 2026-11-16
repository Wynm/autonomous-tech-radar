#!/usr/bin/env python3
"""
Forex EA & Automated Trading Risk Audit Engine (Micro-SaaS Core)
Analyzes trading performance logs and repository metadata to detect scams, 
martingale traps, and calculate quantitative risk metrics.

Standard Library Only (Zero dependencies).
"""

import sys
import json
import math
import argparse

class EARiskAuditor:
    def analyze_trades(self, trades):
        """
        Analyzes a list of trade dictionaries.
        Each trade dict: {'id': int, 'profit': float, 'lot': float}
        """
        if not trades:
            return {"error": "No trade data provided"}

        total_trades = len(trades)
        wins = [t for t in trades if t.get('profit', 0) > 0]
        losses = [t for t in trades if t.get('profit', 0) < 0]

        win_rate = (len(wins) / total_trades) * 100 if total_trades > 0 else 0.0
        total_profit = sum(t.get('profit', 0) for t in wins)
        total_loss = abs(sum(t.get('profit', 0) for t in losses))

        profit_factor = round(total_profit / total_loss, 2) if total_loss > 0 else round(total_profit, 2)
        net_profit = sum(t.get('profit', 0) for t in trades)

        # Drawdown calculation
        equity = 0.0
        peak = 0.0
        max_dd = 0.0
        for t in trades:
            equity += t.get('profit', 0)
            if equity > peak:
                peak = equity
            dd = peak - equity
            if dd > max_dd:
                max_dd = dd

        max_dd_pct = round((max_dd / peak * 100), 2) if peak > 0 else (100.0 if net_profit < 0 else 0.0)

        # Sharpe Ratio estimation
        returns = [t.get('profit', 0) for t in trades]
        avg_return = sum(returns) / total_trades if total_trades > 0 else 0
        variance = sum((r - avg_return) ** 2 for r in returns) / total_trades if total_trades > 0 else 0
        std_dev = math.sqrt(variance) if variance > 0 else 0.0001
        sharpe_ratio = round((avg_return / std_dev) * math.sqrt(total_trades), 2)

        # Martingale Trap Detection
        is_martingale = False
        consecutive_losses = 0
        prev_loss_lot = 0.0
        martingale_events = 0

        for t in trades:
            profit = t.get('profit', 0)
            lot = t.get('lot', 1.0)
            if profit < 0:
                consecutive_losses += 1
                prev_loss_lot = lot
            elif profit > 0 and consecutive_losses > 0:
                if lot >= prev_loss_lot * 1.4:
                    martingale_events += 1
                consecutive_losses = 0

        if martingale_events >= 2 or (total_trades > 5 and win_rate > 90 and max_dd_pct > 35):
            is_martingale = True

        # Risk Scoring (0 to 100)
        risk_score = 20.0
        if max_dd_pct > 30:
            risk_score += 35
        if profit_factor < 1.2:
            risk_score += 20
        if is_martingale:
            risk_score += 40
        risk_score = min(100.0, risk_score)

        status = "HIGH_RISK" if risk_score >= 60 else ("MODERATE_RISK" if risk_score >= 35 else "SAFE")

        return {
            "summary": {
                "total_trades": total_trades,
                "win_rate_pct": round(win_rate, 2),
                "net_profit": round(net_profit, 2),
                "profit_factor": profit_factor,
                "max_drawdown_pct": max_dd_pct,
                "sharpe_ratio": sharpe_ratio
            },
            "risk_analysis": {
                "risk_score": risk_score,
                "risk_status": status,
                "martingale_detected": is_martingale,
                "warnings": self._generate_warnings(is_martingale, max_dd_pct, profit_factor)
            }
        }

    def inspect_repo_metadata(self, metadata):
        """
        Detects Clickbait shell repos and fake EAs (as seen in Discovery 1).
        """
        flags = []
        is_scam = False

        if metadata.get("executable_files_count", 0) == 0:
            flags.append("CRITICAL: Empty code structure (Clickbait Shell Repo - 0 executable files).")
            is_scam = True

        external_links = metadata.get("external_links", [])
        suspicious_tlds = [".xyz", ".top", ".download", ".club"]
        for link in external_links:
            if any(tld in link for tld in suspicious_tlds):
                flags.append(f"HIGH_RISK: Redirects to high-risk domain ({link}).")
                is_scam = True

        stars_per_hour = metadata.get("stars_per_hour", 0)
        if stars_per_hour > 5.0 and metadata.get("executable_files_count", 0) == 0:
            flags.append("WARNING: Artificial star manipulation on empty repo.")
            is_scam = True

        return {
            "is_scam_or_suspicious": is_scam,
            "security_flags": flags,
            "safety_rating": 1.0 if is_scam else 9.5
        }

    def _generate_warnings(self, is_martingale, max_dd, profit_factor):
        warnings = []
        if is_martingale:
            warnings.append("Martingale lot sizing detected: High risk of total account blow-up.")
        if max_dd > 30:
            warnings.append(f"Severe drawdown warning: {max_dd}% peak-to-trough decline.")
        if profit_factor < 1.2:
            warnings.append("Low profit factor: Marginally profitable after broker spreads.")
        return warnings

def run_self_test():
    print("=== RUNNING SELF-TEST FOR EA RISK AUDITOR ===")
    auditor = EARiskAuditor()

    # Test 1: Fake/Clickbait EA Repo Detection
    fake_repo_meta = {
        "executable_files_count": 0,
        "external_links": ["https://go-release.xyz/download"],
        "stars_per_hour": 7.23
    }
    repo_result = auditor.inspect_repo_metadata(fake_repo_meta)
    assert repo_result["is_scam_or_suspicious"] == True, "Failed to identify scam repo!"
    print("[PASS] Test 1: Scam Repository / Shell Detection")

    # Test 2: Martingale Strategy Detection
    martingale_trades = [
        {"id": 1, "profit": -10.0, "lot": 0.1},
        {"id": 2, "profit": -20.0, "lot": 0.2},
        {"id": 3, "profit": 30.0, "lot": 0.4},  # Doubling lot size after losses
        {"id": 4, "profit": -10.0, "lot": 0.1},
        {"id": 5, "profit": 30.0, "lot": 0.3}
    ]
    trade_result = auditor.analyze_trades(martingale_trades)
    assert trade_result["risk_analysis"]["martingale_detected"] == True, "Failed to identify Martingale pattern!"
    assert trade_result["risk_analysis"]["risk_status"] == "HIGH_RISK", "Incorrect risk status!"
    print("[PASS] Test 2: Martingale Strategy Trap Detection")

    # Test 3: Healthy Trading Strategy
    healthy_trades = [
        {"id": 1, "profit": 15.0, "lot": 0.1},
        {"id": 2, "profit": -5.0, "lot": 0.1},
        {"id": 3, "profit": 20.0, "lot": 0.1},
        {"id": 4, "profit": 12.0, "lot": 0.1},
        {"id": 5, "profit": -4.0, "lot": 0.1}
    ]
    healthy_result = auditor.analyze_trades(healthy_trades)
    assert healthy_result["risk_analysis"]["risk_status"] == "SAFE", "False positive risk flag!"
    print("[PASS] Test 3: Healthy Strategy Quantitative Verification")

    print("\nALL SELF-TESTS PASSED SUCCESSFULLY! (Status: 100% Operational)")
    return 0

def main():
    parser = argparse.ArgumentParser(description="Forex EA & Trading Bot Risk Audit Engine")
    parser.add_argument("--self-test", action="store_true", help="Run automated self-tests and exit")
    args = parser.parse_args()

    if args.self_test:
        sys.exit(run_self_test())
    else:
        print("EA Risk Audit Engine CLI")
        print("Usage: python script.py --self-test")

if __name__ == "__main__":
    main()
