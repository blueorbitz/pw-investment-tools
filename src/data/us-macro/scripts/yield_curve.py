#!/usr/bin/env python3
"""Fetch US Treasury yield curve data and compute spread signals."""

import os
import sys
import requests

API_KEY = os.environ.get("FRED_API_KEY")
if not API_KEY:
    print("# US Treasury Yield Curve")
    print("")
    print("⚠️  `FRED_API_KEY` not set.")
    print("Get a free key at: https://fred.stlouisfed.org/docs/api/api_key.html")
    sys.exit(1)

BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

# Treasury yield series in maturity order
TENORS = [
    ("DGS1MO", "1M"),
    ("DGS3MO", "3M"),
    ("DGS6MO", "6M"),
    ("DGS1", "1Y"),
    ("DGS2", "2Y"),
    ("DGS3", "3Y"),
    ("DGS5", "5Y"),
    ("DGS7", "7Y"),
    ("DGS10", "10Y"),
    ("DGS20", "20Y"),
    ("DGS30", "30Y"),
]


def fetch_latest(series_id: str) -> tuple:
    """Return (date, value) for the latest observation."""
    params = {
        "series_id": series_id,
        "api_key": API_KEY,
        "file_type": "json",
        "sort_order": "desc",
        "limit": 5,
    }
    resp = requests.get(BASE_URL, params=params, timeout=15)
    resp.raise_for_status()
    obs = [o for o in resp.json().get("observations", []) if o["value"] != "."]
    if obs:
        return obs[0]["date"], float(obs[0]["value"])
    return None, None


def spread_signal(val: float) -> str:
    """Interpret a spread value."""
    if val < -0.5:
        return "🔴 Deeply Inverted"
    elif val < 0:
        return "🔴 Inverted"
    elif val < 0.2:
        return "🟡 Flat"
    elif val > 1.5:
        return "🟢 Very Steep"
    elif val > 0.8:
        return "🟢 Steep"
    else:
        return "⚪ Normal"


def main():
    print("# US Treasury Yield Curve")
    print("")

    # Fetch all tenors
    values = {}
    print("| Tenor | Yield (%) | Date |")
    print("|-------|-----------|------|")

    for series_id, label in TENORS:
        try:
            date, val = fetch_latest(series_id)
            if val is not None:
                values[label] = val
                print(f"| {label} | {val:.2f} | {date} |")
            else:
                print(f"| {label} | N/A | — |")
        except Exception as e:
            print(f"| {label} | Error | {e} |")

    print("")
    print("## Key Spreads")
    print("")
    print("| Spread | Value (bps) | Signal |")
    print("|--------|-------------|--------|")

    spreads = [
        ("10Y-2Y", "10Y", "2Y"),
        ("10Y-3M", "10Y", "3M"),
        ("30Y-10Y", "30Y", "10Y"),
        ("2Y-1Y", "2Y", "1Y"),
        ("5Y-2Y", "5Y", "2Y"),
    ]

    for name, long, short in spreads:
        if long in values and short in values:
            diff = values[long] - values[short]
            bps = diff * 100
            signal = spread_signal(diff)
            print(f"| {name} | {bps:+.0f} | {signal} |")
        else:
            print(f"| {name} | N/A | — |")

    # Overall assessment
    print("")
    ten_two = values.get("10Y", 0) - values.get("2Y", 0) if "10Y" in values and "2Y" in values else None
    ten_three = values.get("10Y", 0) - values.get("3M", 0) if "10Y" in values and "3M" in values else None

    if ten_two is not None and ten_three is not None:
        if ten_two < 0 and ten_three < 0:
            print("**Curve Assessment:** Deeply inverted — recession signal active.")
        elif ten_two < 0 or ten_three < 0:
            print("**Curve Assessment:** Partially inverted — watch for un-inversion (often precedes recession onset).")
        elif ten_two > 1.0:
            print("**Curve Assessment:** Steep — reflation / growth recovery posture.")
        else:
            print("**Curve Assessment:** Normal — no immediate recession signal from curve.")

    print("")
    print("_Source: FRED (US Treasury Constant Maturity Rates)_")


if __name__ == "__main__":
    main()
