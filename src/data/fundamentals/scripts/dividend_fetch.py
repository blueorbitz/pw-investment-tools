#!/usr/bin/env python3
"""Data retrieval layer for dividend model.

Fetches historical dividend per share data from:
- Yahoo Finance timeseries API (global stocks)
- KLSE Screener (Bursa Malaysia stocks)

Returns standardized annual DPS data consumed by dividend_model.py.
"""

import json
import re
import urllib.request


UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


# =============================================================================
# TICKER UTILITIES
# =============================================================================


def normalize_ticker_yf(ticker):
    """Normalize ticker for Yahoo Finance API.

    - Numeric codes (e.g. '1155') → '1155.KL' (Bursa Malaysia)
    - Exchange-qualified (e.g. '1155:KLSE') → '1155.KL'
    - Everything else → as-is (e.g. 'JNJ', 'KO')
    """
    t = str(ticker).upper().strip()
    if t.isdigit():
        return f"{t}.KL"
    if ":" in t:
        base, exch = t.split(":")
        if exch in ("XKLS", "KLSE"):
            return f"{base}.KL"
    return t


def is_klse_ticker(ticker):
    """Check if a ticker represents a KLSE-listed stock."""
    raw = str(ticker).strip()
    if raw.isdigit():
        return True
    upper = raw.upper()
    if upper.endswith(".KL") and upper.split(".")[0].isdigit():
        return True
    if ":" in upper:
        _, exch = upper.split(":", 1)
        if exch in ("XKLS", "KLSE"):
            return True
    return False


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

    Scrapes the dividend tab of klsescreener.com/v2/stocks/view/<code>
    for historical DPS data.

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

    # Look for dividend table — KLSE Screener has a dividends section
    # Pattern: rows with ex-date, amount, type columns
    # Try the dividend_reports table first
    div_table = re.search(
        r"<table[^>]*class=['\"]?dividend[^'\"]*['\"]?[^>]*>(.*?)</table>",
        html, re.DOTALL | re.IGNORECASE
    )

    if not div_table:
        # Alternative: look for "Dividend" section by header
        div_section = re.search(
            r"(?:Dividend|DPS).*?<table[^>]*>(.*?)</table>",
            html, re.DOTALL | re.IGNORECASE
        )
        if div_section:
            div_table = div_section

    if not div_table:
        # Fallback: try to find dividend data in any table with "Ex-Date" header
        tables = re.findall(r"<table[^>]*>(.*?)</table>", html, re.DOTALL)
        for table in tables:
            if re.search(r"Ex[\s-]*Date", table, re.IGNORECASE):
                div_table = type('obj', (object,), {'group': lambda self, x=None: table})()
                break

    if not div_table:
        return None

    table_html = div_table.group(1) if hasattr(div_table, 'group') else div_table.group(0)

    # Parse rows — look for date and amount patterns
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", table_html, re.DOTALL)
    dividends_by_year = {}

    for row in rows:
        cells = re.findall(r"<td[^>]*>(.*?)</td>", row, re.DOTALL)
        if len(cells) < 2:
            continue

        # Clean cell text
        texts = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]

        # Find a date cell (YYYY-MM-DD or DD/MM/YYYY or DD-Mon-YYYY)
        year = None
        amount = None

        for text in texts:
            # Try to extract year from date
            year_match = re.search(r'(20[0-2]\d|19\d\d)', text)
            if year_match and not year:
                year = int(year_match.group(1))

            # Try to extract amount (e.g., "0.15", "15.0 sen", "3.5%")
            amt_match = re.search(r'(\d+\.?\d*)\s*(?:sen|cents?)?', text, re.IGNORECASE)
            if amt_match and not amount:
                val = float(amt_match.group(1))
                # KLSE often reports in sen (1/100 of RM)
                if "sen" in text.lower() or val > 5:  # Likely in sen if > 5
                    val = val / 100.0
                if 0 < val < 50:  # Reasonable DPS range
                    amount = val

        if year and amount:
            if year not in dividends_by_year:
                dividends_by_year[year] = 0.0
            dividends_by_year[year] += amount

    if not dividends_by_year:
        return None

    # Sort and return — exclude potentially partial current year
    from datetime import datetime
    current_year = datetime.utcnow().year

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
