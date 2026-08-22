#!/usr/bin/env python3
"""Aggregate key market sentiment and volatility indicators from FRED."""

import os
import sys
import requests

API_KEY = os.environ.get("FRED_API_KEY")
if not API_KEY:
    print("# Sentiment & Volatility Dashboard")
    print("")
    print("⚠️  `FRED_API_KEY` not set.")
    print("Get a free key at: https://fred.stlouisfed.org/docs/api/api_key.html")
    sys.exit(1)

BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

SERIES = [
    ("VIXCLS", "VIX (Equity Vol)", "Fear gauge — S&P 500 implied volatility"),
    ("BAMLH0A0HYM2", "HY OAS (Credit Spread)", "High yield option-adjusted spread"),
    ("BAMLC0A0CM", "IG OAS (Investment Grade)", "Investment grade corporate spread"),
]


def fetch_with_percentile(series_id: str, lookback: int = 252) -> dict:
    """Fetch latest value with 1Y percentile context."""
    params = {
        "series_id": series_id,
        "api_key": API_KEY,
        "file_type": "json",
        "sort_order": "desc",
        "limit": lookback,
    }
    resp = requests.get(BASE_URL, params=params, timeout=15)
    resp.raise_for_status()
    obs = [o for o in resp.json().get("observations", []) if o["value"] != "."]

    if not obs:
        return {"date": "—", "value": "N/A", "percentile": "—", "signal": "—"}

    values = [float(o["value"]) for o in obs]
    current = values[0]
    date = obs[0]["date"]

    # Percentile rank within lookback window
    rank = sum(1 for v in values if v <= current)
    percentile = (rank / len(values)) * 100

    # Signal interpretation
    if percentile >= 90:
        signal = "🔴 EXTREME HIGH"
    elif percentile >= 75:
        signal = "🟡 Elevated"
    elif percentile <= 10:
        signal = "🟢 EXTREME LOW"
    elif percentile <= 25:
        signal = "🟢 Depressed"
    else:
        signal = "⚪ Normal"

    return {
        "date": date,
        "value": f"{current:.2f}",
        "percentile": f"{percentile:.0f}%",
        "signal": signal,
    }


def main():
    print("# Sentiment & Volatility Dashboard")
    print("")
    print("| Indicator | Date | Current | 1Y Percentile | Signal |")
    print("|-----------|------|---------|---------------|--------|")

    for series_id, label, _ in SERIES:
        try:
            result = fetch_with_percentile(series_id)
            print(f"| {label} | {result['date']} | {result['value']} | {result['percentile']} | {result['signal']} |")
        except Exception as e:
            print(f"| {label} | — | Error | — | {e} |")

    print("")
    print("## Interpretation")
    print("")
    print("| Level | Meaning | Implication |")
    print("|-------|---------|-------------|")
    print("| EXTREME HIGH (≥90%) | Fear / stress elevated | Potential contrarian buy zone |")
    print("| EXTREME LOW (≤10%) | Complacency dominant | Risk-on excess, fragility building |")
    print("| Normal (25-75%) | No actionable extreme | Stay with regime positioning |")
    print("")
    print("**Note:** For additional sentiment data (not on FRED), check manually:")
    print("- AAII Sentiment: https://www.aaii.com/sentimentsurvey")
    print("- Put/Call Ratio: https://www.cboe.com/us/options/market_statistics/")
    print("- CNN Fear & Greed: https://edition.cnn.com/markets/fear-and-greed")
    print("")
    print("_Source: FRED (CBOE, ICE BofA indices)_")


if __name__ == "__main__":
    main()
