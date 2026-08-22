#!/usr/bin/env python3
"""Compare relative strength of tickers against a benchmark."""

import sys
import os
import json
from datetime import datetime

SKILLS_ROOT = os.environ.get("SKILLS_ROOT", os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(SKILLS_ROOT, "utility", "shared-lib", "scripts"))
from yahoo_cache import fetch_yahoo_cached


def fetch_closes(ticker, period):
    """Fetch close prices using shared cache."""
    candles, meta = fetch_yahoo_cached(ticker, period)
    closes = [c["close"] for c in candles]
    name = meta.get("shortName") or meta.get("longName") or ticker
    return closes, name


def rs_trend(stock_closes, bench_closes, lookback=20):
    """Determine if RS ratio is improving, deteriorating, or flat."""
    if len(stock_closes) < lookback + 20 or len(bench_closes) < lookback + 20:
        return "insufficient_data"

    # Use matching lengths
    n = min(len(stock_closes), len(bench_closes))
    stock_closes = stock_closes[-n:]
    bench_closes = bench_closes[-n:]

    # RS ratio at two points
    recent_rs = stock_closes[-1] / bench_closes[-1]
    prior_rs = stock_closes[-(lookback + 1)] / bench_closes[-(lookback + 1)]

    change = (recent_rs - prior_rs) / prior_rs * 100
    if change > 2:
        return "improving"
    elif change < -2:
        return "deteriorating"
    return "flat"


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"ok": False, "error": "Usage: ta_sector_rs.py <tickers_csv> [benchmark] [period]"}))
        sys.exit(1)

    tickers = [t.strip() for t in sys.argv[1].split(",") if t.strip()]
    benchmark = sys.argv[2] if len(sys.argv) > 2 else "^KLSE"
    period = sys.argv[3] if len(sys.argv) > 3 else "6mo"

    # Fetch benchmark
    try:
        bench_closes, bench_name = fetch_closes(benchmark, period)
    except Exception as e:
        print(json.dumps({"ok": False, "error": f"Failed to fetch benchmark {benchmark}: {e}"}))
        sys.exit(1)

    if len(bench_closes) < 20:
        print(json.dumps({"ok": False, "error": "Insufficient benchmark data"}))
        sys.exit(1)

    bench_perf = round((bench_closes[-1] - bench_closes[0]) / bench_closes[0] * 100, 2)

    results = []
    for ticker in tickers:
        try:
            closes, name = fetch_closes(ticker, period)
        except Exception as e:
            results.append({"ticker": ticker, "ok": False, "error": str(e)})
            continue

        if len(closes) < 20:
            results.append({"ticker": ticker, "ok": False, "error": "insufficient_data"})
            continue

        perf = round((closes[-1] - closes[0]) / closes[0] * 100, 2)
        rs_ratio = round(perf - bench_perf, 2)  # Excess return
        trend = rs_trend(closes, bench_closes)

        results.append({
            "ticker": ticker,
            "ok": True,
            "name": name,
            "performance_pct": perf,
            "rs_vs_benchmark": rs_ratio,
            "rs_trend": trend
        })

    # Sort by RS (strongest first)
    results.sort(key=lambda x: x.get("rs_vs_benchmark", -999), reverse=True)

    output = {
        "ok": True,
        "benchmark": benchmark,
        "benchmark_name": bench_name,
        "benchmark_performance_pct": bench_perf,
        "period": period,
        "rankings": results
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
