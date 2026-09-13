#!/usr/bin/env python3
"""Data retrieval layer for annual financial statements.

Fetches historical financial data from:
- Yahoo Finance quoteSummary API (non-KLSE global stocks; requires cookie+crumb,
  handled by yahoo_cache.yahoo_summary)
- KLSE Screener (Bursa Malaysia stocks; revenue and net income only)

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

from yahoo_cache import isk_paths, yahoo_summary  # noqa: E402


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
    - Everything else → as-is (e.g. 'MSFT', 'GOOG')
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
# YAHOO FINANCE — Global stocks (US, EU, etc.)
# =============================================================================

def fetch_yahoo_statements(ticker):
    """Fetch annual financials from Yahoo quoteSummary (cookie+crumb auth).

    The old timeseries endpoint stopped serving statement types crumb-free;
    quoteSummary is the working source. Returns up to 4 annual statements.

    Returns dict with keys: revenue, operating_income, fcf, net_income.
    Each value is a list of {"date": str, "value": float} sorted oldest-first.
    Returns None on failure.
    """
    yf_ticker = normalize_ticker_yf(ticker)

    def raw(node):
        return node.get("raw") if isinstance(node, dict) else None

    try:
        result = yahoo_summary(yf_ticker, "incomeStatementHistory,cashflowStatementHistory")
    except Exception:
        return None

    parsed = {"revenue": [], "operating_income": [], "fcf": [], "net_income": []}

    ish = result.get("incomeStatementHistory", {}).get("incomeStatementHistory", [])
    for s in ish:
        date = (s.get("endDate") or {}).get("fmt")
        if not date:
            continue
        for key, field in (("revenue", "totalRevenue"),
                           ("operating_income", "operatingIncome"),
                           ("net_income", "netIncome")):
            value = raw(s.get(field))
            if value is not None:
                parsed[key].append({"date": date, "value": value})

    cfh = result.get("cashflowStatementHistory", {}).get("cashflowStatements", [])
    for s in cfh:
        date = (s.get("endDate") or {}).get("fmt")
        ocf = raw(s.get("totalCashFromOperatingActivities"))
        capex = raw(s.get("capitalExpenditures"))
        if date and ocf is not None and capex is not None:
            # Yahoo reports capex as a negative number
            fcf = ocf + capex if capex < 0 else ocf - capex
            parsed["fcf"].append({"date": date, "value": fcf})

    for key in parsed:
        parsed[key].sort(key=lambda x: x["date"])

    return parsed if any(parsed[k] for k in parsed) else None


# =============================================================================
# KLSE SCREENER — Bursa Malaysia stocks
# =============================================================================

def _parse_klse_amount(amount_str):
    """Parse KLSE Screener amount string like '14.9b' or '132.3m' to float.

    Handles: b (billion), m (million), k (thousand).
    Returns None if unparseable.
    """
    if not amount_str or not isinstance(amount_str, str):
        return None
    s = amount_str.strip().lower().replace(",", "")
    multiplier = 1
    if s.endswith("b"):
        multiplier = 1e9
        s = s[:-1]
    elif s.endswith("m"):
        multiplier = 1e6
        s = s[:-1]
    elif s.endswith("k"):
        multiplier = 1e3
        s = s[:-1]
    try:
        return float(s) * multiplier
    except (ValueError, TypeError):
        return None


def fetch_klse_screener(stock_code):
    """Fetch quarterly reports from KLSE Screener and aggregate to annual.

    Scrapes klsescreener.com/v2/stocks/view/<code> for the financial_reports
    table, parses quarterly revenue and profit/loss, then groups by fiscal year.

    Only returns complete fiscal years (4 quarters summed).

    Returns dict in same format as fetch_yahoo_timeseries, or None on failure.
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

    # Find the financial_reports table
    table_match = re.search(
        r"<table class='financial_reports[^']*'>(.*?)</table>", html, re.DOTALL
    )
    if not table_match:
        return None

    # Parse each quarterly row
    quarters = []
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_match.group(1), re.DOTALL)

    for row in rows:
        cells = re.findall(r"<td[^>]*>(.*?)</td>", row, re.DOTALL)
        if len(cells) < 10:
            continue

        def text(cell):
            return re.sub(r'<[^>]+>', '', cell).strip()

        revenue = _parse_klse_amount(text(cells[3]))
        profit_loss = _parse_klse_amount(text(cells[4]))
        quarter_date = text(cells[6])
        financial_year = text(cells[7])

        if revenue is not None and quarter_date:
            quarters.append({
                "date": quarter_date,
                "fy": financial_year,
                "revenue": revenue,
                "profit_loss": profit_loss,
            })

    if not quarters:
        return None

    # Aggregate into fiscal years (only complete ones with 4 quarters)
    fy_data = {}
    for q in quarters:
        fy = q["fy"]
        if fy not in fy_data:
            fy_data[fy] = {"revenue": 0, "net_income": 0, "q_count": 0}
        fy_data[fy]["revenue"] += q["revenue"] or 0
        fy_data[fy]["net_income"] += q["profit_loss"] or 0
        fy_data[fy]["q_count"] += 1

    parsed = {"revenue": [], "operating_income": [], "fcf": [], "net_income": []}
    for fy in sorted(fy_data.keys()):
        if fy_data[fy]["q_count"] == 4:
            parsed["revenue"].append({"date": fy, "value": fy_data[fy]["revenue"]})
            parsed["net_income"].append({"date": fy, "value": fy_data[fy]["net_income"]})

    return parsed if parsed["revenue"] else None


# =============================================================================
# UNIFIED INTERFACE
# =============================================================================

def fetch_annual_financials(ticker):
    """Fetch annual financial data for any ticker.

    Routes to the appropriate data source:
    - KLSE stocks (numeric codes) → KLSE Screener
    - Everything else → Yahoo Finance timeseries API

    Returns:
        dict with keys: revenue, operating_income, fcf, net_income
        Each is a list of {"date": str, "value": float} sorted oldest-first.
        Returns None if no data available from any source.
    """
    if is_klse_ticker(ticker):
        stock_code = str(ticker).strip().replace(".KL", "").replace(".kl", "")
        if ":" in stock_code:
            stock_code = stock_code.split(":")[0]
        return fetch_klse_screener(stock_code)
    else:
        return fetch_yahoo_statements(ticker)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Fetch annual financial statements")
    parser.add_argument("ticker", help="Ticker, e.g. MSFT, 1155, BTC-USD")
    args = parser.parse_args()

    try:
        data = fetch_annual_financials(args.ticker)
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
