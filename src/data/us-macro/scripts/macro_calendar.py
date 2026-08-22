#!/usr/bin/env python3
"""Fetch upcoming economic calendar events."""

import sys
import requests
from datetime import datetime, timedelta

DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 7


def fetch_calendar_investing_com(days: int) -> list:
    """Fetch from TradingView economic calendar API."""
    start = datetime.now().strftime("%Y-%m-%d")
    end = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

    url = "https://economic-calendar.tradingview.com/events"
    params = {
        "from": f"{start}T00:00:00.000Z",
        "to": f"{end}T23:59:59.999Z",
        "countries": "US,MY,CN,JP,EU",
    }

    resp = requests.get(url, params=params, timeout=15, headers={
        "User-Agent": "Mozilla/5.0 (compatible; macro-research/1.0)",
        "Origin": "https://www.tradingview.com",
    })
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, dict):
        return data.get("result", [])
    return data if isinstance(data, list) else []


def format_impact(importance: int) -> str:
    """Convert numeric importance to label. TradingView uses: 1=High, 0=Medium, -1=Low."""
    if importance >= 1:
        return "🔴 High"
    elif importance == 0:
        return "🟡 Medium"
    else:
        return "⚪ Low"


def country_flag(code: str) -> str:
    """Map country code to a short label."""
    flags = {
        "US": "🇺🇸 US",
        "MY": "🇲🇾 MY",
        "CN": "🇨🇳 CN",
        "JP": "🇯🇵 JP",
        "EU": "🇪🇺 EU",
        "GB": "🇬🇧 UK",
    }
    return flags.get(code, code)


def main():
    print(f"# Economic Calendar — Next {DAYS} Days")
    print("")

    try:
        events = fetch_calendar_investing_com(DAYS)
    except Exception as e:
        print(f"⚠️  Failed to fetch calendar: {e}")
        print("")
        print("**Manual sources:**")
        print("- TradingView: https://www.tradingview.com/economic-calendar/")
        print("- Trading Economics: https://tradingeconomics.com/calendar")
        print("- Investing.com: https://www.investing.com/economic-calendar/")
        print("- BNM: https://www.bnm.gov.my/monetary-stability/opr-decisions")
        print("")
        fallback_table()
        return

    if not events:
        print("No events found for the requested period.")
        print("")
        fallback_table()
        return

    # Filter medium and high impact (TradingView: 1=High, 0=Medium, -1=Low)
    high_impact = [e for e in events if e.get("importance", -1) >= 1]
    medium_impact = [e for e in events if e.get("importance", -1) == 0]

    all_events = high_impact + medium_impact

    if not all_events:
        print("No medium/high impact events in period.")
        print("")
        fallback_table()
        return

    # Sort by date
    all_events.sort(key=lambda e: e.get("date", ""))

    print("| Date | Time | Country | Event | Impact | Forecast | Previous |")
    print("|------|------|---------|-------|--------|----------|----------|")

    for event in all_events[:30]:
        date_raw = event.get("date", "")
        date_str = date_raw[:10] if date_raw else "—"
        time_str = date_raw[11:16] if len(date_raw) > 11 else "—"
        country = country_flag(event.get("country", "—"))
        title = event.get("title", "—")
        importance = event.get("importance", 0)
        impact = format_impact(importance)
        forecast = event.get("forecast") or "—"
        previous = event.get("previous") or "—"

        print(f"| {date_str} | {time_str} | {country} | {title} | {impact} | {forecast} | {previous} |")

    print("")
    print(f"_Showing {len(all_events)} medium/high impact events. Source: TradingView Economic Calendar._")


def fallback_table():
    """Print static reference of key recurring events."""
    print("## Key Recurring Events Reference")
    print("")
    print("| Frequency | Event | Country | Typical Impact |")
    print("|-----------|-------|---------|---------------|")
    print("| Monthly | CPI | 🇺🇸 US | 🔴 High |")
    print("| Monthly (1st Fri) | Nonfarm Payrolls | 🇺🇸 US | 🔴 High |")
    print("| Monthly | ISM Manufacturing PMI | 🇺🇸 US | 🔴 High |")
    print("| Monthly | PCE Price Index | 🇺🇸 US | 🔴 High |")
    print("| 6-8 weeks | FOMC Rate Decision | 🇺🇸 US | 🔴 High |")
    print("| Monthly | NBS Manufacturing PMI | 🇨🇳 CN | 🟡 Medium |")
    print("| Monthly | Caixin PMI | 🇨🇳 CN | 🟡 Medium |")
    print("| 6x/year | OPR Decision | 🇲🇾 MY | 🔴 High |")
    print("| Monthly | CPI | 🇲🇾 MY | 🟡 Medium |")
    print("| Monthly | IPI | 🇲🇾 MY | 🟡 Medium |")
    print("| Monthly | Trade Balance | 🇲🇾 MY | 🟡 Medium |")
    print("| Quarterly | GDP | 🇺🇸🇲🇾🇨🇳 | 🔴 High |")


if __name__ == "__main__":
    main()
