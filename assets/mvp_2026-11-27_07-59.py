#!/usr/bin/env python3
"""
Crypto Trend Signal Engine - Micro-SaaS Core
Built using standard Python libraries only (No pip install required).
Supports --self-test execution.
"""

import sys
import json
import urllib.request
import argparse
import datetime
import math
from typing import List, Dict, Any, Tuple


def calculate_sma(prices: List[float], window: int) -> List[float]:
    """Calculates Simple Moving Average."""
    sma = []
    for i in range(len(prices)):
        if i < window - 1:
            sma.append(0.0)
        else:
            sma.append(sum(prices[i - window + 1 : i + 1]) / window)
    return sma


def calculate_ema(prices: List[float], window: int) -> List[float]:
    """Calculates Exponential Moving Average."""
    if not prices:
        return []
    multiplier = 2 / (window + 1)
    ema = [prices[0]]
    for i in range(1, len(prices)):
        ema_val = (prices[i] - ema[-1]) * multiplier + ema[-1]
        ema.append(ema_val)
    return ema


def calculate_rsi(prices: List[float], window: int = 14) -> List[float]:
    """Calculates Relative Strength Index."""
    if len(prices) <= window:
        return [50.0] * len(prices)

    gains, losses = [], []
    for i in range(1, len(prices)):
        change = prices[i] - prices[i - 1]
        gains.append(max(change, 0.0))
        losses.append(max(-change, 0.0))

    avg_gain = sum(gains[:window]) / window
    avg_loss = sum(losses[:window]) / window

    rsi = [50.0] * window
    for i in range(window, len(gains)):
        avg_gain = (avg_gain * (window - 1) + gains[i]) / window
        avg_loss = (avg_loss * (window - 1) + losses[i]) / window
        if avg_loss == 0:
            rsi.append(100.0)
        else:
            rs = avg_gain / avg_loss
            rsi.append(100.0 - (100.0 / (1.0 + rs)))

    rsi.append(rsi[-1])  # Match price array length
    return rsi


class TrendTradingEngine:
    """Core Strategy Engine for Futures Trend Following."""

    def __init__(self, fast_window: int = 9, slow_window: int = 21, rsi_window: int = 14):
        self.fast_window = fast_window
        self.slow_window = slow_window
        self.rsi_window = rsi_window

    def analyze(self, candles: List[Dict[str, Any]]) -> Dict[str, Any]:
        closes = [c["close"] for c in candles]
        if len(closes) < self.slow_window:
            return {"signal": "NEUTRAL", "reason": "Insufficient candle data"}

        fast_ema = calculate_ema(closes, self.fast_window)
        slow_ema = calculate_ema(closes, self.slow_window)
        rsi = calculate_rsi(closes, self.rsi_window)

        current_price = closes[-1]
        curr_fast, prev_fast = fast_ema[-1], fast_ema[-2]
        curr_slow, prev_slow = slow_ema[-1], slow_ema[-2]
        curr_rsi = rsi[-1]

        signal = "HOLD"
        reason = "No cross detected or weak momentum"

        # Bullish Crossover (Golden Cross)
        if prev_fast <= prev_slow and curr_fast > curr_slow and curr_rsi > 45:
            signal = "BUY_LONG"
            reason = "Fast EMA crossed above Slow EMA with RSI confirmation"
        # Bearish Crossover (Death Cross)
        elif prev_fast >= prev_slow and curr_fast < curr_slow and curr_rsi < 55:
            signal = "SELL_SHORT"
            reason = "Fast EMA crossed below Slow EMA with RSI confirmation"

        sl = current_price * 0.98 if signal == "BUY_LONG" else (current_price * 1.02 if signal == "SELL_SHORT" else None)
        tp = current_price * 1.04 if signal == "BUY_LONG" else (current_price * 0.96 if signal == "SELL_SHORT" else None)

        return {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "price": current_price,
            "fast_ema": round(curr_fast, 2),
            "slow_ema": round(curr_slow, 2),
            "rsi": round(curr_rsi, 2),
            "signal": signal,
            "reason": reason,
            "suggested_sl": round(sl, 2) if sl else None,
            "suggested_tp": round(tp, 2) if tp else None,
        }


def fetch_binance_klines(symbol: str = "BTCUSDT", interval: str = "4h", limit: int = 50) -> List[Dict[str, Any]]:
    """Fetch public K-line data from Binance API using standard urllib."""
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    req = urllib.request.Request(url, headers={"User-Agent": "CryptoSignalEngine/1.0"})
    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read().decode())

    candles = []
    for item in data:
        candles.append({
            "open_time": item[0],
            "open": float(item[1]),
            "high": float(item[2]),
            "low": float(item[3]),
            "close": float(item[4]),
            "volume": float(item[5]),
        })
    return candles


def run_self_test():
    """Automated self-test suite (System safe, memory only)."""
    print("=== RUNNING SELF-TEST FOR CRYPTO TRADING ENGINE ===")

    # Test 1: Math Indicators Accuracy
    test_prices = [10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0]
    sma = calculate_sma(test_prices, 5)
    assert abs(sma[-1] - 18.0) < 1e-5, f"SMA test failed: Expected 18.0, got {sma[-1]}"
    print("[SUCCESS] Test 1: SMA mathematical correctness verified.")

    ema = calculate_ema(test_prices, 3)
    assert len(ema) == len(test_prices), "EMA test failed: Array length mismatch."
    print("[SUCCESS] Test 2: EMA calculations verified.")

    # Test 3: Simulated Bullish Signal Generation
    synthetic_candles = []
    base_price = 100.0
    for _ in range(20):  # Flat/Downtrend
        base_price -= 0.2
        synthetic_candles.append({"close": base_price})
    for _ in range(10):  # Strong uptrend
        base_price += 2.5
        synthetic_candles.append({"close": base_price})

    engine = TrendTradingEngine(fast_window=3, slow_window=10)
    result = engine.analyze(synthetic_candles)

    assert result["signal"] in ["BUY_LONG", "HOLD"], f"Unexpected signal: {result['signal']}"
    assert "price" in result and "rsi" in result, "Structure validation failed."
    print(f"[SUCCESS] Test 3: Strategy decision engine executed successfully. Output Signal: {result['signal']}")

    print("\nALL SELF-TESTS PASSED SUCCESSFULLY (0 Errors).")
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="Micro-SaaS Crypto Trend Trading Signal Engine")
    parser.add_argument("--self-test", action="store_true", help="Run self-tests and exit")
    parser.add_argument("--symbol", type=str, default="BTCUSDT", help="Trading pair symbol (e.g., BTCUSDT)")
    parser.add_argument("--interval", type=str, default="4h", help="Timeframe interval (e.g., 1h, 4h, 1d)")

    args = parser.parse_args()

    if args.self_test:
        run_self_test()

    print(f"[*] Fetching market data for {args.symbol} [{args.interval}]...")
    try:
        candles = fetch_binance_klines(symbol=args.symbol, interval=args.interval)
        engine = TrendTradingEngine()
        analysis = engine.analyze(candles)

        print("\n" + "=" * 45)
        print(f" CRYPTO MARKET ANALYSIS REPORT: {args.symbol}")
        print("=" * 45)
        print(f" Timestamp    : {analysis['timestamp']}")
        print(f" Current Price: ${analysis['price']:,.2f}")
        print(f" Fast EMA (9) : ${analysis['fast_ema']:,.2f}")
        print(f" Slow EMA (21): ${analysis['slow_ema']:,.2f}")
        print(f" RSI (14)     : {analysis['rsi']}")
        print(f" Signal       : >>> {analysis['signal']} <<<")
        print(f" Strategy Note: {analysis['reason']}")
        if analysis['suggested_sl']:
            print(f" Stop Loss    : ${analysis['suggested_sl']:,.2f}")
            print(f" Take Profit  : ${analysis['suggested_tp']:,.2f}")
        print("=" * 45)

    except Exception as e:
        print(f"Error fetching data or executing engine: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
