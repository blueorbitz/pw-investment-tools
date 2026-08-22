#!/usr/bin/env python3
"""
SEC EDGAR Filings — Insider & Institutional Tracker

Queries SEC EDGAR for Form 4 (insider transactions), 13F (institutional holdings),
and 13D/13G (activist positions) for US-listed stocks.

Zero external dependencies — uses only Python stdlib (urllib, json, xml).

Usage:
    python3 sec_filings.py form4 <TICKER> [lookback_days]
    python3 sec_filings.py 13f <TICKER>
    python3 sec_filings.py activist <TICKER>
"""

import os
import sys
import json
import time
import xml.etree.ElementTree as ET
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timedelta

# --- Configuration ---

USER_AGENT = os.environ.get("SEC_EDGAR_USER_AGENT", "")
if not USER_AGENT:
    print("# SEC EDGAR Filings")
    print("")
    print("⚠️  `SEC_EDGAR_USER_AGENT` not set.")
    print("SEC requires a User-Agent with your name and email.")
    print("Set: `export SEC_EDGAR_USER_AGENT='YourName your@email.com'`")
    sys.exit(1)

EDGAR_BASE = "https://www.sec.gov"
EDGAR_COMPANY = "https://data.sec.gov/submissions"
EDGAR_FULL_TEXT = "https://efts.sec.gov/LATEST/search-index"

# Rate limiting: SEC allows 10 req/sec
_last_request_time = 0.0


def _rate_limit():
    """Enforce SEC's 10 requests/second limit."""
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < 0.1:
        time.sleep(0.1 - elapsed)
    _last_request_time = time.time()


def _get(url: str, params: dict = None) -> str:
    """Make a rate-limited GET request to SEC. Returns response body as string."""
    _rate_limit()
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url)
    req.add_header("User-Agent", USER_AGENT)
    req.add_header("Accept", "application/json, text/html, application/xml, */*")
    req.add_header("Accept-Encoding", "identity")
    resp = urllib.request.urlopen(req, timeout=30)
    return resp.read().decode("utf-8")


def _get_json(url: str, params: dict = None) -> dict:
    """Make a rate-limited GET request and parse JSON response."""
    body = _get(url, params)
    return json.loads(body)


# --- CIK Lookup ---

def get_cik(ticker: str) -> str:
    """Look up CIK number from ticker symbol."""
    url = "https://www.sec.gov/cgi-bin/browse-edgar"
    params = {
        "action": "getcompany",
        "company": "",
        "CIK": ticker,
        "type": "",
        "dateb": "",
        "owner": "include",
        "count": "1",
        "search_text": "",
        "output": "atom",
    }
    try:
        body = _get(url, params)
        root = ET.fromstring(body)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall("atom:entry", ns)
        if entries:
            cik_url = entries[0].find("atom:content/atom:cik-href", ns)
            if cik_url is not None:
                cik = cik_url.text.strip().split("/")[-1]
                return cik.lstrip("0") or "0"
    except Exception:
        pass

    return _get_cik_from_tickers(ticker)


def _get_cik_from_tickers(ticker: str) -> str:
    """Fallback: use SEC's company_tickers.json."""
    url = "https://www.sec.gov/files/company_tickers.json"
    data = _get_json(url)
    ticker_upper = ticker.upper()
    for entry in data.values():
        if entry.get("ticker", "").upper() == ticker_upper:
            return str(entry["cik_str"])
    print(f"Error: Could not find CIK for ticker '{ticker}'")
    sys.exit(1)


# --- Form 4 (Insider Transactions) ---

def fetch_form4(ticker: str, lookback_days: int = 30):
    """Fetch and parse recent Form 4 filings for a ticker."""
    cik = get_cik(ticker)
    cik_padded = cik.zfill(10)

    print(f"# Form 4 Insider Transactions — {ticker.upper()}")
    print("")
    print(f"**CIK:** {cik} | **Lookback:** {lookback_days} days | **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("")

    # Fetch filings list
    url = f"{EDGAR_COMPANY}/CIK{cik_padded}.json"
    data = _get_json(url)

    recent_filings = data.get("filings", {}).get("recent", {})
    forms = recent_filings.get("form", [])
    dates = recent_filings.get("filingDate", [])
    accessions = recent_filings.get("accessionNumber", [])
    primary_docs = recent_filings.get("primaryDocument", [])

    cutoff = (datetime.now() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")

    # Filter Form 4 filings within lookback
    form4_filings = []
    for i, form_type in enumerate(forms):
        if form_type in ("4", "4/A") and dates[i] >= cutoff:
            form4_filings.append({
                "date": dates[i],
                "accession": accessions[i],
                "doc": primary_docs[i],
            })

    if not form4_filings:
        print(f"No Form 4 filings found in the last {lookback_days} days.")
        return

    print(f"**Found:** {len(form4_filings)} Form 4 filing(s)")
    print("")

    # Parse each Form 4 XML
    transactions = []
    for filing in form4_filings[:20]:
        try:
            accession_clean = filing["accession"].replace("-", "")
            doc_name = filing["doc"]
            if "/" in doc_name:
                doc_name = doc_name.split("/")[-1]

            doc_url = f"{EDGAR_BASE}/Archives/edgar/data/{cik}/{accession_clean}/{doc_name}"
            body = _get(doc_url)
            txns = _parse_form4_xml(body, filing["date"])
            transactions.extend(txns)
        except Exception:
            continue

    if not transactions:
        print("Form 4 filings found but could not parse transaction details.")
        print("Filings may be in HTML format. Check EDGAR directly:")
        print(f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=4&dateb=&owner=include&count=20")
        return

    # Output transactions table
    print("## Transactions")
    print("")
    print("| Date | Insider | Title | Type | Shares | Price | Value | Direction |")
    print("|------|---------|-------|------|--------|-------|-------|-----------|")

    net_buys = 0
    net_sells = 0
    buyers = set()

    for txn in sorted(transactions, key=lambda x: x["date"], reverse=True):
        direction = "BUY" if txn["acquired"] else "SELL"
        value = abs(txn["shares"] * txn["price"]) if txn["price"] else 0
        value_str = f"${value:,.0f}" if value else "—"
        price_str = f"${txn['price']:.2f}" if txn["price"] else "—"

        print(f"| {txn['date']} | {txn['insider'][:25]} | {txn['title'][:15]} | {txn['code']} | {txn['shares']:,.0f} | {price_str} | {value_str} | {direction} |")

        if txn["acquired"]:
            net_buys += txn["shares"] * (txn["price"] or 0)
            buyers.add(txn["insider"])
        else:
            net_sells += txn["shares"] * (txn["price"] or 0)

    # Summary
    print("")
    print("## Summary")
    print("")
    print(f"- **Net Insider Buying:** ${net_buys:,.0f}")
    print(f"- **Net Insider Selling:** ${net_sells:,.0f}")
    print(f"- **Net Flow:** ${net_buys - net_sells:+,.0f}")
    print(f"- **Unique Buyers:** {len(buyers)}")

    if len(buyers) >= 3:
        print("")
        print(f"⚡ **CLUSTER BUY DETECTED** — {len(buyers)} unique insiders buying within {lookback_days} days")
        print("This is a high-confidence bullish signal.")
    elif len(buyers) >= 2:
        print("")
        print(f"📊 **Multiple insiders buying** — {len(buyers)} unique buyers (not yet a cluster)")

    if net_buys > net_sells:
        print("")
        print("**Signal: BULLISH** — Net insider buying exceeds selling")
    elif net_sells > net_buys * 2:
        print("")
        print("**Signal: BEARISH** — Significant net insider selling")


def _parse_form4_xml(xml_text: str, filing_date: str) -> list:
    """Parse Form 4 XML and extract transactions."""
    transactions = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []

    owner_elem = root.find(".//reportingOwner")
    if owner_elem is None:
        return []

    owner_name_elem = owner_elem.find(".//rptOwnerName")
    owner_title_elem = owner_elem.find(".//officerTitle")
    is_director_elem = owner_elem.find(".//isDirector")
    is_officer_elem = owner_elem.find(".//isOfficer")

    owner_name = owner_name_elem.text.strip() if owner_name_elem is not None and owner_name_elem.text else "Unknown"
    owner_title = ""
    if owner_title_elem is not None and owner_title_elem.text:
        owner_title = owner_title_elem.text.strip()
    elif is_director_elem is not None and is_director_elem.text == "1":
        owner_title = "Director"
    elif is_officer_elem is not None and is_officer_elem.text == "1":
        owner_title = "Officer"

    for txn_elem in root.findall(".//nonDerivativeTransaction"):
        try:
            date_elem = txn_elem.find(".//transactionDate/value")
            code_elem = txn_elem.find(".//transactionCoding/transactionCode")
            shares_elem = txn_elem.find(".//transactionAmounts/transactionShares/value")
            price_elem = txn_elem.find(".//transactionAmounts/transactionPricePerShare/value")
            acq_disp_elem = txn_elem.find(".//transactionAmounts/transactionAcquiredDisposedCode/value")

            txn_date = date_elem.text if date_elem is not None else filing_date
            txn_code = code_elem.text if code_elem is not None else "?"
            shares = float(shares_elem.text) if shares_elem is not None and shares_elem.text else 0
            price = float(price_elem.text) if price_elem is not None and price_elem.text else 0
            acquired = (acq_disp_elem.text == "A") if acq_disp_elem is not None else False

            if txn_code in ("P", "S", "A", "M"):
                transactions.append({
                    "date": txn_date,
                    "insider": owner_name,
                    "title": owner_title,
                    "code": txn_code,
                    "shares": shares,
                    "price": price,
                    "acquired": acquired,
                })
        except (ValueError, AttributeError):
            continue

    return transactions


# --- 13F (Institutional Holdings) ---

def fetch_13f(ticker: str):
    """Search for 13F filings referencing the ticker."""
    print(f"# 13F Institutional Holdings — {ticker.upper()}")
    print("")
    print(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("")

    url = EDGAR_FULL_TEXT
    params = {
        "q": f'"{ticker.upper()}"',
        "dateRange": "custom",
        "startdt": (datetime.now() - timedelta(days=120)).strftime("%Y-%m-%d"),
        "enddt": datetime.now().strftime("%Y-%m-%d"),
        "forms": "13F-HR",
    }

    try:
        data = _get_json(url, params)
    except urllib.error.HTTPError as e:
        if e.code == 403:
            search_url = f"https://efts.sec.gov/LATEST/search-index?q=%22{ticker.upper()}%22&forms=13F-HR"
            print("SEC EDGAR full-text search is currently unavailable (403 Forbidden).")
            print("")
            print("**Manual alternatives:**")
            print(f"- EDGAR search: https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company=&CIK={ticker}&type=13F-HR&dateb=&owner=include&count=40")
            print(f"- WhaleWisdom: https://whalewisdom.com/stock/{ticker.lower()}")
            print(f"- Dataroma: https://www.dataroma.com/m/stock.php?sym={ticker.upper()}")
            return
        raise

    hits = data.get("hits", {}).get("hits", [])
    total = data.get("hits", {}).get("total", {}).get("value", 0)

    if not hits:
        print(f"No recent 13F-HR filings found referencing {ticker.upper()} in the last 120 days.")
        print("")
        print("**Alternative:** Check WhaleWisdom or Dataroma for aggregated 13F data.")
        return

    print(f"**Found:** {total} recent 13F filing(s) referencing {ticker.upper()}")
    print("")
    print("## Recent 13F Filers Holding This Stock")
    print("")
    print("| Filing Date | Filer | Accession | Link |")
    print("|-------------|-------|-----------|------|")

    seen_filers = set()
    for hit in hits[:15]:
        source = hit.get("_source", {})
        filer = source.get("display_names", ["Unknown"])[0] if source.get("display_names") else "Unknown"
        filing_date = source.get("file_date", "—")
        accession = source.get("accession_no", "")

        if filer in seen_filers:
            continue
        seen_filers.add(filer)

        link = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company={urllib.parse.quote_plus(filer)}&CIK=&type=13F-HR&dateb=&owner=include&count=5"
        print(f"| {filing_date} | {filer[:40]} | {accession} | [EDGAR]({link}) |")

    print("")
    print("## How to Use")
    print("")
    print("- Compare quarter-over-quarter position changes for conviction signals")
    print("- New positions by top funds = institutional validation")
    print("- Position exits = potential concern (check if rotation or thesis break)")
    print("- Significant sizing changes (>50% increase) = high conviction")
    print("")
    print("_Note: 13F filings are reported with a 45-day delay from quarter end._")


# --- 13D/13G (Activist Positions) ---

def fetch_activist(ticker: str):
    """Search for 13D and 13G filings for activist positions."""
    print(f"# 13D/13G Activist Positions — {ticker.upper()}")
    print("")
    print(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("")

    results = []
    for form_type in ("SC 13D", "SC 13G", "SC 13D/A", "SC 13G/A"):
        url = EDGAR_FULL_TEXT
        params = {
            "q": f'"{ticker.upper()}"',
            "dateRange": "custom",
            "startdt": (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
            "enddt": datetime.now().strftime("%Y-%m-%d"),
            "forms": form_type,
        }
        try:
            data = _get_json(url, params)
            hits = data.get("hits", {}).get("hits", [])
            results.extend(hits)
        except urllib.error.HTTPError as e:
            if e.code == 403:
                print("SEC EDGAR full-text search is currently unavailable (403 Forbidden).")
                print("")
                print("**Manual alternatives:**")
                print(f"- EDGAR search: https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company=&CIK={ticker}&type=SC+13D&dateb=&owner=include&count=40")
                print(f"- OpenInsider: https://openinsider.com/screener?s={ticker.upper()}")
                return
            continue
        except Exception:
            continue

    if not results:
        print(f"No 13D/13G filings found for {ticker.upper()} in the last 12 months.")
        print("")
        print("This means no activist investors have disclosed >5% stakes recently.")
        return

    print(f"**Found:** {len(results)} activist-related filing(s)")
    print("")
    print("## Activist Filings")
    print("")
    print("| Date | Form | Filer | Link |")
    print("|------|------|-------|------|")

    seen = set()
    for hit in sorted(results, key=lambda x: x.get("_source", {}).get("file_date", ""), reverse=True)[:15]:
        source = hit.get("_source", {})
        filer = source.get("display_names", ["Unknown"])[0] if source.get("display_names") else "Unknown"
        filing_date = source.get("file_date", "—")
        form = source.get("form_type", "—")
        accession = source.get("accession_no", "")

        key = f"{filer}-{form}-{filing_date}"
        if key in seen:
            continue
        seen.add(key)

        link = f"https://www.sec.gov/Archives/edgar/data/{source.get('entity_id', '')}/{accession.replace('-', '')}"
        print(f"| {filing_date} | {form} | {filer[:40]} | [View]({link}) |")

    print("")
    print("## Interpretation")
    print("")
    print("- **SC 13D** = Activist intent (plans to influence management/strategy)")
    print("- **SC 13G** = Passive >5% stake (no activist intent declared)")
    print("- **SC 13D/A** = Amended filing (position increase, new demands, or settlement)")
    print("- Multiple 13D filings = Escalating activist campaign")
    print("")
    print("**Action:** Read the filing for stated intentions (board seats, strategic review, buybacks, spin-offs)")


# --- Main ---

def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python3 sec_filings.py form4 <TICKER> [lookback_days]")
        print("  python3 sec_filings.py 13f <TICKER>")
        print("  python3 sec_filings.py activist <TICKER>")
        sys.exit(1)

    command = sys.argv[1].lower()
    ticker = sys.argv[2].upper()

    if command == "form4":
        lookback = int(sys.argv[3]) if len(sys.argv) > 3 else 30
        fetch_form4(ticker, lookback)
    elif command == "13f":
        fetch_13f(ticker)
    elif command == "activist":
        fetch_activist(ticker)
    else:
        print(f"Unknown command: {command}")
        print("Available: form4, 13f, activist")
        sys.exit(1)


if __name__ == "__main__":
    main()
