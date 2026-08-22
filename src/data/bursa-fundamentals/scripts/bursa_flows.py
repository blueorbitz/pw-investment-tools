#!/usr/bin/env python3
"""Fetch Bursa Malaysia market overview and foreign flow guidance.

Foreign fund flow data (daily net foreign buy/sell) is only available via
JavaScript-rendered pages on Bursa Malaysia / KLSE Screener / i3investor.
This script provides what's programmatically accessible (market snapshot)
and directs the agent to use web browsing for flow details.
"""

import sys
import requests
import json


def fetch_bursa_top_movers() -> dict:
    """Fetch top Bursa Malaysia stocks by market cap from TradingView."""
    url = "https://scanner.tradingview.com/malaysia/scan"
    payload = {
        "columns": [
            "name", "description", "close", "change", "volume",
            "market_cap_basic", "sector",
        ],
        "filter": [{"left": "exchange", "operation": "equal", "right": "MYX"}],
        "options": {"lang": "en"},
        "range": [0, 20],
        "sort": {"sortBy": "market_cap_basic", "sortOrder": "desc"},
        "symbols": {},
        "markets": ["malaysia"],
    }
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/json",
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json()


def main():
    print("# Bursa Malaysia — Market Overview & Fund Flow")
    print("")

    # Top 20 by market cap
    try:
        data = fetch_bursa_top_movers()
        items = data.get("data", [])

        if items:
            print("## Top 20 Stocks by Market Cap")
            print("")
            print("| # | Ticker | Name | Close | Chg % | Volume | Sector |")
            print("|---|--------|------|-------|-------|--------|--------|")

            gainers = 0
            losers = 0
            total_vol = 0

            for i, item in enumerate(items, 1):
                d = item.get("d", [])
                ticker = item.get("s", "").replace("MYX:", "")
                name = d[0] if d else "—"
                desc = d[1] if len(d) > 1 else ""
                close = d[2] if len(d) > 2 else 0
                change = d[3] if len(d) > 3 else 0
                volume = d[4] if len(d) > 4 else 0
                mcap = d[5] if len(d) > 5 else 0
                sector = d[6] if len(d) > 6 else "—"

                if change > 0:
                    gainers += 1
                elif change < 0:
                    losers += 1
                total_vol += volume if volume else 0

                chg_str = f"{change:+.2f}%" if change else "0.00%"
                vol_str = f"{volume/1e6:.1f}M" if volume and volume > 0 else "—"
                close_str = f"{close:.2f}" if close else "—"

                print(f"| {i} | {ticker} | {desc[:20]} | {close_str} | {chg_str} | {vol_str} | {sector or '—'} |")

            print("")
            print(f"**Breadth (Top 20):** {gainers} gainers, {losers} losers, {20 - gainers - losers} unchanged")
            print(f"**Total Volume (Top 20):** {total_vol/1e6:.0f}M shares")
            print("")

    except Exception as e:
        print(f"⚠️  Could not fetch market data: {e}")
        print("")

    # Foreign flow section — requires web browsing
    print("## Foreign Fund Flow Data")
    print("")
    print("Daily foreign net flow data requires browser access (JavaScript-rendered pages).")
    print("Use web browsing to check these sources:")
    print("")
    print("1. **KLSE Screener** — https://www.klsescreener.com/v2/markets")
    print("   Look for: Daily Foreign Net, Institutional Net, Retail Net")
    print("")
    print("2. **Bursa Malaysia** — https://www.bursamalaysia.com/market_information/market_statistic")
    print("   Look for: Trading Participation by category")
    print("")
    print("3. **i3investor** — https://klse.i3investor.com/web/market/foreignflow")
    print("   Look for: Foreign flow table with daily net")
    print("")
    print("**What to extract:**")
    print("- Today's net foreign flow (RM millions)")
    print("- 5-day cumulative foreign net")
    print("- Whether foreign is net buyer or seller")
    print("- Any notable divergence from local institutional flow")
    print("")
    print("_Source: TradingView (market data), manual sources (fund flow)_")


if __name__ == "__main__":
    main()
