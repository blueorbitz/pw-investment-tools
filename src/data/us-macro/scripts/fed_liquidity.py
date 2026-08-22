#!/usr/bin/env python3
"""Fetch latest Fed balance sheet and liquidity plumbing data from FRED."""

import os
import sys
import requests

API_KEY = os.environ.get("FRED_API_KEY")
if not API_KEY:
    print("# Fed Liquidity Dashboard")
    print("")
    print("⚠️  `FRED_API_KEY` not set.")
    print("Get a free key at: https://fred.stlouisfed.org/docs/api/api_key.html")
    sys.exit(1)

BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

SERIES = [
    ("WALCL", "Fed Total Assets"),
    ("RRPONTSYD", "Reverse Repo (ON RRP)"),
    ("WTREGEN", "Treasury General Account"),
    ("WRESBAL", "Reserve Balances"),
]


def fetch_latest(series_id: str, limit: int = 2) -> dict:
    """Fetch latest observations for a FRED series."""
    params = {
        "series_id": series_id,
        "api_key": API_KEY,
        "file_type": "json",
        "sort_order": "desc",
        "limit": limit,
    }
    resp = requests.get(BASE_URL, params=params, timeout=15)
    resp.raise_for_status()
    obs = [o for o in resp.json().get("observations", []) if o["value"] != "."]
    return obs


def main():
    print("# Fed Liquidity Dashboard")
    print("")
    print("| Indicator | Date | Value ($B) | WoW Δ ($B) | WoW % |")
    print("|-----------|------|-----------|-----------|-------|")

    for series_id, label in SERIES:
        try:
            obs = fetch_latest(series_id)
            if len(obs) >= 2:
                curr = float(obs[0]["value"])
                prev = float(obs[1]["value"])
                date = obs[0]["date"]
                chg = curr - prev
                pct = (chg / prev) * 100
                # FRED reports in millions for these series
                curr_b = curr / 1000
                chg_b = chg / 1000
                print(f"| {label} | {date} | {curr_b:,.1f} | {chg_b:+,.1f} | {pct:+.2f}% |")
            elif len(obs) == 1:
                curr = float(obs[0]["value"])
                date = obs[0]["date"]
                curr_b = curr / 1000
                print(f"| {label} | {date} | {curr_b:,.1f} | — | — |")
            else:
                print(f"| {label} | — | N/A | — | — |")
        except Exception as e:
            print(f"| {label} | — | Error: {e} | — | — |")

    print("")

    # Net liquidity estimate
    try:
        assets_obs = fetch_latest("WALCL", 1)
        rrp_obs = fetch_latest("RRPONTSYD", 1)
        tga_obs = fetch_latest("WTREGEN", 1)

        if assets_obs and rrp_obs and tga_obs:
            assets = float(assets_obs[0]["value"])
            rrp = float(rrp_obs[0]["value"])
            tga = float(tga_obs[0]["value"])
            # Net liquidity = Fed Assets - RRP - TGA
            net_liq = (assets - rrp - tga) / 1000
            print(f"**Net Liquidity Estimate:** ${net_liq:,.1f}B (Assets - RRP - TGA)")
            print("")
    except Exception:
        pass

    print("_Source: FRED (Federal Reserve Economic Data)_")


if __name__ == "__main__":
    main()
