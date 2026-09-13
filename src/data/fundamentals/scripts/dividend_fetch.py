#!/usr/bin/env python3
"""Data retrieval layer for dividend history.

Fetches historical dividend per share data from:
- Yahoo Finance chart API with dividend events (global stocks)
- KLSE Screener #dividends section (Bursa Malaysia stocks)

Consumed by the data/fundamentals skill; output lands in the fundamentals.md
scratch file for quick-look, deep-research, and the quality gate.
"""

import json
import os
import re
import sys
import urllib.request

# ISK_ROOT points at src/. A relative ISK_ROOT is ignored for import purposes
# (CWD-dependent); __file__-relative resolution is used instead.
_ROOT = os.environ.get("ISK_ROOT")
if not _ROOT or not os.path.isabs(_ROOT):
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(_ROOT, "utility", "shared-lib", "scripts"))

from yahoo_cache import isk_paths  # noqa: E402
from ticker_display import (  # noqa: E402
    is_bursa_ticker as is_klse_ticker,
    normalize_ticker_yf,
)

# Back-compat alias: is_klse_ticker is the historic name used below.
is_klse_ticker = is_klse_ticker

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


# =============================================================================
# YAHOO FINANCE — Dividend history
# =============================================================================


def fetch_yahoo_dividends(ticker):
    """Fetch dividend history from Yahoo Finance.

    Uses the chart API with events=div to get historical dividend payments,
    then aggregates to annual DPS.

    Returns list of {"date": "YYYY", "value": float} sorted oldest-first,
    or None on failure.
    """
    yf_ticker = normalize_ticker_yf(ticker)

    # Use chart API with dividend events — covers ~20 years
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{yf_ticker}"
        f"?period1=946684800&period2=9999999999&interval=1mo&events=div"
    )
    req = urllib.request.Request(url, headers={"User-Agent": UA})

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
    except Exception:
        return None

    chart = data.get("chart", {}).get("result", [])
    if not chart:
        return None

    events = chart[0].get("events", {}).get("dividends", {})
    if not events:
        return None

    # Parse dividend events — keyed by timestamp
    from datetime import datetime

    dividends_by_year = {}
    for ts_key, div_data in events.items():
        amount = div_data.get("amount", 0)
        timestamp = div_data.get("date", int(ts_key))
        if amount <= 0:
            continue

        year = datetime.utcfromtimestamp(timestamp).year
        if year not in dividends_by_year:
            dividends_by_year[year] = 0.0
        dividends_by_year[year] += amount

    if not dividends_by_year:
        return None

    # Convert to sorted list — only include complete years (exclude current partial)
    current_year = datetime.utcnow().year
    annual_dps = []
    for year in sorted(dividends_by_year.keys()):
        if year < current_year:  # Only complete years
            annual_dps.append({"date": str(year), "value": round(dividends_by_year[year], 4)})

    return annual_dps if annual_dps else None


# =============================================================================
# KLSE SCREENER — Bursa Malaysia dividend history
# =============================================================================


def fetch_klse_dividends(stock_code):
    """Fetch dividend history from KLSE Screener.

    Scrapes the #dividends section of klsescreener.com/v2/stocks/view/<code>:
    a plain table with Announced / Financial Year / Subject / EX Date /
    Payment Date / Amount columns. Amount is already in RM (0.3100 = 31 sen).

    Returns list of {"date": "YYYY", "value": float} sorted oldest-first,
    or None on failure.
    """
    url = f"https://www.klsescreener.com/v2/stocks/view/{stock_code}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
    except Exception:
        return None

    if "Page Not Found" in html or "404" in html[:500]:
        return None

    # The dividend history lives in the section with id="dividends"
    div_section = re.search(
        r'id="dividends".*?<table[^>]*>(.*?)</table>', html, re.DOTALL
    )
    if not div_section:
        return None

    table_html = div_section.group(1)
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", table_html, re.DOTALL)
    dividends_by_year = {}

    for row in rows:
        cells = re.findall(r"<td[^>]*>(.*?)</td>", row, re.DOTALL)
        if len(cells) < 6:
            continue

        texts = [re.sub(r"<[^>]+>", "", c).strip() for c in cells]
        announced, fy = texts[0], texts[1]
        # Amount is the "number" column (index 5); already in RM
        amount_match = re.match(r"^(\d+\.?\d*)$", texts[5])

        date_source = fy or announced
        year_match = re.search(r"(19\d\d|20\d\d)", date_source)
        if not year_match or not amount_match:
            continue

        year = int(year_match.group(1))
        amount = float(amount_match.group(1))
        if year > 0 and 0 < amount < 50:
            dividends_by_year[year] = dividends_by_year.get(year, 0.0) + amount

    if not dividends_by_year:
        return None

    # Sort and return — exclude potentially partial current year
    from datetime import datetime

    current_year = datetime.now().year

    annual_dps = []
    for year in sorted(dividends_by_year.keys()):
        if year < current_year:
            annual_dps.append({"date": str(year), "value": round(dividends_by_year[year], 4)})

    return annual_dps if annual_dps else None


# =============================================================================
# UNIFIED INTERFACE
# =============================================================================


def fetch_dividend_history(ticker):
    """Fetch annual dividend per share history for any ticker.

    Routes to the appropriate data source:
    - KLSE stocks (numeric codes) → KLSE Screener
    - Everything else → Yahoo Finance

    Returns:
        dict with key "dps_annual": list of {"date": str, "value": float}
        sorted oldest-first. Returns None if no data.
    """
    if is_klse_ticker(ticker):
        stock_code = str(ticker).strip().replace(".KL", "").replace(".kl", "")
        if ":" in stock_code:
            stock_code = stock_code.split(":")[0]
        result = fetch_klse_dividends(stock_code)
    else:
        result = fetch_yahoo_dividends(ticker)

    if result:
        return {"dps_annual": result}
    return None


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Fetch annual dividend history")
    parser.add_argument("ticker", help="Ticker, e.g. MSFT, 1155")
    args = parser.parse_args()

    try:
        data = fetch_dividend_history(args.ticker)
    except Exception as exc:
        data = None
        print(f"error: {type(exc).__name__}: {exc}", file=sys.stderr)

    if data:
        print(json.dumps({"ok": True, "ticker": args.ticker, **data, "paths": isk_paths()}, indent=2))
    else:
        print(json.dumps({
            "ok": False,
            "ticker": args.ticker,
            "status": "unavailable",
        }, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
