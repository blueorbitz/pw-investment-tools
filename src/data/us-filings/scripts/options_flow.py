#!/usr/bin/env python3
"""
Options Flow — Unusual Activity Detector

Fetches options chain data from Yahoo Finance and identifies unusual activity
patterns that may indicate informed positioning ahead of catalysts.

Uses Yahoo's unofficial endpoints with cookie/crumb authentication.
Zero external dependencies — uses only Python stdlib (urllib, json, http.cookiejar).

Usage:
    python3 options_flow.py scan <TICKER> [expiry_date]
    python3 options_flow.py sentiment <TICKER>
    python3 options_flow.py multi <TICKER1,TICKER2,...>
"""

import sys
import json
import time
import http.cookiejar
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime

# --- Configuration ---

UNUSUAL_VOL_OI_THRESHOLD = 3.0
HIGH_PREMIUM_THRESHOLD = 500_000
PCR_BULLISH_THRESHOLD = 0.5
PCR_BEARISH_THRESHOLD = 1.5

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"


# --- HTTP Helpers ---

_opener = None
_crumb = None


def _init_session():
    """Initialize urllib opener with cookie jar and fetch crumb."""
    global _opener, _crumb

    if _opener and _crumb is not None:
        return

    cj = http.cookiejar.CookieJar()
    _opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    _opener.addheaders = [("User-Agent", USER_AGENT)]

    # Step 1: Hit fc.yahoo.com to get cookies
    try:
        _opener.open("https://fc.yahoo.com", timeout=10)
    except urllib.error.URLError:
        pass  # Expected to fail/redirect but sets cookies

    # Step 2: Get crumb
    try:
        req = urllib.request.Request("https://query2.finance.yahoo.com/v1/test/getcrumb")
        req.add_header("User-Agent", USER_AGENT)
        resp = _opener.open(req, timeout=10)
        _crumb = resp.read().decode("utf-8").strip()
    except Exception:
        _crumb = ""


def _yahoo_get(url: str, params: dict = None) -> dict:
    """Make authenticated GET request to Yahoo Finance."""
    _init_session()

    if params is None:
        params = {}
    if _crumb:
        params["crumb"] = _crumb

    if params:
        url = url + "?" + urllib.parse.urlencode(params)

    req = urllib.request.Request(url)
    req.add_header("User-Agent", USER_AGENT)
    resp = _opener.open(req, timeout=15)
    return json.loads(resp.read().decode("utf-8"))


def _simple_get(url: str, params: dict = None) -> dict:
    """Simple GET without session (for chart endpoint)."""
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url)
    req.add_header("User-Agent", USER_AGENT)
    resp = urllib.request.urlopen(req, timeout=10)
    return json.loads(resp.read().decode("utf-8"))


# --- Data Fetching ---

def fetch_options_data(ticker: str, expiry_epoch: int = None) -> dict:
    """Fetch options chain from Yahoo Finance v7 API with auth."""
    url = f"https://query2.finance.yahoo.com/v7/finance/options/{ticker}"
    params = {}
    if expiry_epoch:
        params["date"] = str(expiry_epoch)

    data = _yahoo_get(url, params)
    result = data.get("optionChain", {}).get("result", [])
    if not result:
        return {}
    return result[0]


def get_spot_price(ticker: str) -> float:
    """Get current stock price from chart endpoint (no auth needed)."""
    url = f"https://query2.finance.yahoo.com/v8/finance/chart/{ticker}"
    params = {"range": "1d", "interval": "1d"}
    try:
        data = _simple_get(url, params)
        result = data.get("chart", {}).get("result", [])
        if result:
            meta = result[0].get("meta", {})
            return meta.get("regularMarketPrice", 0)
    except Exception:
        pass
    return 0


# --- Analysis Functions ---

def analyze_unusual_activity(calls: list, puts: list, spot: float) -> list:
    """Find contracts with unusual volume relative to open interest."""
    unusual = []

    for contract_type, contracts in [("Call", calls), ("Put", puts)]:
        for c in contracts:
            vol = c.get("volume", 0) or 0
            oi = c.get("openInterest", 0) or 0
            strike = c.get("strike", 0)
            last_price = c.get("lastPrice", 0) or 0

            if oi == 0 or vol < 100:
                continue

            vol_oi = vol / oi
            premium_est = vol * last_price * 100

            if vol_oi >= UNUSUAL_VOL_OI_THRESHOLD:
                unusual.append({
                    "type": contract_type,
                    "strike": strike,
                    "volume": vol,
                    "oi": oi,
                    "vol_oi": vol_oi,
                    "last_price": last_price,
                    "premium_est": premium_est,
                    "iv": c.get("impliedVolatility", 0) or 0,
                })

    unusual.sort(key=lambda x: x["vol_oi"], reverse=True)
    return unusual[:20]


def calculate_pcr(calls: list, puts: list) -> dict:
    """Calculate put/call ratio."""
    total_call_vol = sum(c.get("volume", 0) or 0 for c in calls)
    total_put_vol = sum(p.get("volume", 0) or 0 for p in puts)
    total_call_oi = sum(c.get("openInterest", 0) or 0 for c in calls)
    total_put_oi = sum(p.get("openInterest", 0) or 0 for p in puts)

    pcr_vol = total_put_vol / total_call_vol if total_call_vol > 0 else 0
    pcr_oi = total_put_oi / total_call_oi if total_call_oi > 0 else 0

    return {
        "call_volume": total_call_vol,
        "put_volume": total_put_vol,
        "call_oi": total_call_oi,
        "put_oi": total_put_oi,
        "pcr_volume": pcr_vol,
        "pcr_oi": pcr_oi,
    }


def estimate_implied_move(calls: list, puts: list, spot: float) -> float:
    """Estimate implied move from ATM straddle."""
    if not spot or not calls or not puts:
        return 0

    atm_call = min(calls, key=lambda c: abs(c.get("strike", 0) - spot), default=None)
    atm_put = min(puts, key=lambda p: abs(p.get("strike", 0) - spot), default=None)

    if not atm_call or not atm_put:
        return 0

    straddle = (atm_call.get("lastPrice", 0) or 0) + (atm_put.get("lastPrice", 0) or 0)
    return (straddle / spot) * 100 if spot > 0 else 0


def find_max_pain(calls: list, puts: list) -> float:
    """Calculate max pain strike."""
    strikes = set()
    for c in calls:
        strikes.add(c.get("strike", 0))
    for p in puts:
        strikes.add(p.get("strike", 0))

    if not strikes:
        return 0

    min_pain = float("inf")
    max_pain_strike = 0

    for strike in sorted(strikes):
        total_pain = 0
        for c in calls:
            c_strike = c.get("strike", 0)
            c_oi = c.get("openInterest", 0) or 0
            if strike > c_strike:
                total_pain += (strike - c_strike) * c_oi * 100
        for p in puts:
            p_strike = p.get("strike", 0)
            p_oi = p.get("openInterest", 0) or 0
            if strike < p_strike:
                total_pain += (p_strike - strike) * p_oi * 100

        if total_pain < min_pain:
            min_pain = total_pain
            max_pain_strike = strike

    return max_pain_strike


# --- Commands ---

def cmd_scan(ticker: str, target_expiry: str = None):
    """Scan for unusual options activity."""
    print(f"# Options Flow — {ticker} — {datetime.now().strftime('%Y-%m-%d')}")
    print("")

    spot = get_spot_price(ticker)

    try:
        data = fetch_options_data(ticker)
    except Exception as e:
        print(f"Error fetching options data: {e}")
        sys.exit(1)

    if not data:
        print(f"No options data found for {ticker}")
        return

    if not spot:
        quote = data.get("quote", {})
        spot = quote.get("regularMarketPrice", 0)

    expiry_dates = data.get("expirationDates", [])
    print(f"**Spot Price:** ${spot:.2f} | **Expirations Available:** {len(expiry_dates)}")
    print("")

    if target_expiry:
        target_ts = int(datetime.strptime(target_expiry, "%Y-%m-%d").timestamp())
        closest = min(expiry_dates, key=lambda x: abs(x - target_ts)) if expiry_dates else None
        if closest:
            closest_date = datetime.fromtimestamp(closest).strftime("%Y-%m-%d")
            if closest_date != target_expiry:
                print(f"_Exact expiry {target_expiry} not available. Using closest: {closest_date}_")
                print("")
            expiries_to_scan = [closest]
        else:
            expiries_to_scan = []
    else:
        expiries_to_scan = expiry_dates[:3]

    all_unusual = []
    pcr = None
    implied_move = 0
    max_pain = 0

    for i, expiry_epoch in enumerate(expiries_to_scan):
        if i == 0:
            options = data.get("options", [{}])
            chain = options[0] if options else {}
        else:
            try:
                chain_data = fetch_options_data(ticker, expiry_epoch)
                options = chain_data.get("options", [{}])
                chain = options[0] if options else {}
                time.sleep(0.2)
            except Exception:
                continue

        calls = chain.get("calls", [])
        puts = chain.get("puts", [])
        expiry_str = datetime.fromtimestamp(expiry_epoch).strftime("%Y-%m-%d")

        unusual = analyze_unusual_activity(calls, puts, spot)
        for u in unusual:
            u["expiry"] = expiry_str
        all_unusual.extend(unusual)

        if i == 0:
            pcr = calculate_pcr(calls, puts)
            implied_move = estimate_implied_move(calls, puts, spot)
            max_pain = find_max_pain(calls, puts)

    if all_unusual:
        print("## Unusual Activity Detected")
        print("")
        print("| Expiry | Type | Strike | Volume | OI | Vol/OI | Premium Est | Signal |")
        print("|--------|------|--------|--------|-----|--------|-------------|--------|")

        for u in all_unusual[:10]:
            signal = "BULLISH" if u["type"] == "Call" else "BEARISH"
            if u["premium_est"] > HIGH_PREMIUM_THRESHOLD:
                signal = f"**{signal}**"
            premium_str = f"${u['premium_est']:,.0f}" if u["premium_est"] else "—"
            print(f"| {u['expiry']} | {u['type']} | ${u['strike']:.0f} | {u['volume']:,} | {u['oi']:,} | {u['vol_oi']:.1f}x | {premium_str} | {signal} |")

        high_premium = [u for u in all_unusual if u["premium_est"] > HIGH_PREMIUM_THRESHOLD]
        if high_premium:
            print("")
            print(f"💰 **{len(high_premium)} high-premium bet(s)** detected (>${HIGH_PREMIUM_THRESHOLD/1000:.0f}K)")
    else:
        print("No unusual options activity detected for near-term expirations.")

    print("")
    print("## Sentiment")
    print("")
    if pcr:
        print(f"- **Put/Call Ratio (Volume):** {pcr['pcr_volume']:.2f}")
        print(f"- **Put/Call Ratio (OI):** {pcr['pcr_oi']:.2f}")
        print(f"- **Total Call Volume:** {pcr['call_volume']:,}")
        print(f"- **Total Put Volume:** {pcr['put_volume']:,}")

    if implied_move:
        print(f"- **Implied Move (next expiry):** ±{implied_move:.1f}%")
    if max_pain:
        print(f"- **Max Pain:** ${max_pain:.0f}")
        if spot > 0:
            mp_diff = ((max_pain - spot) / spot) * 100
            print(f"- **Spot vs Max Pain:** {mp_diff:+.1f}%")

    print("")
    print("## Interpretation")
    print("")
    if pcr:
        if pcr["pcr_volume"] < PCR_BULLISH_THRESHOLD:
            print("- PCR below 0.5 → **Extreme bullish positioning** (contrarian: may be near a top)")
        elif pcr["pcr_volume"] > PCR_BEARISH_THRESHOLD:
            print("- PCR above 1.5 → **Extreme bearish positioning** (contrarian: may be near a bottom)")
        else:
            print(f"- PCR at {pcr['pcr_volume']:.2f} → Within normal range")

    if all_unusual:
        call_unusual = sum(1 for u in all_unusual if u["type"] == "Call")
        put_unusual = sum(1 for u in all_unusual if u["type"] == "Put")
        if call_unusual > put_unusual * 2:
            print("- Unusual activity heavily skewed to calls → **Bullish bias**")
        elif put_unusual > call_unusual * 2:
            print("- Unusual activity heavily skewed to puts → **Bearish bias or hedging**")


def cmd_sentiment(ticker: str):
    """Quick sentiment summary."""
    print(f"# Options Sentiment — {ticker} — {datetime.now().strftime('%Y-%m-%d')}")
    print("")

    spot = get_spot_price(ticker)

    try:
        data = fetch_options_data(ticker)
    except Exception as e:
        print(f"Error fetching options data: {e}")
        sys.exit(1)

    if not data:
        print(f"No options data found for {ticker}")
        return

    if not spot:
        quote = data.get("quote", {})
        spot = quote.get("regularMarketPrice", 0)

    options = data.get("options", [{}])
    chain = options[0] if options else {}
    calls = chain.get("calls", [])
    puts = chain.get("puts", [])
    expiry_dates = data.get("expirationDates", [])
    expiry_str = datetime.fromtimestamp(expiry_dates[0]).strftime("%Y-%m-%d") if expiry_dates else "—"

    pcr = calculate_pcr(calls, puts)
    implied_move = estimate_implied_move(calls, puts, spot)
    max_pain = find_max_pain(calls, puts)

    print(f"**Spot:** ${spot:.2f} | **Expiry:** {expiry_str}")
    print("")
    print("| Metric | Value | Reading |")
    print("|--------|-------|---------|")

    if pcr["pcr_volume"] < PCR_BULLISH_THRESHOLD:
        pcr_reading = "Extreme Bullish (contrarian bearish)"
    elif pcr["pcr_volume"] < 0.7:
        pcr_reading = "Bullish"
    elif pcr["pcr_volume"] < 1.0:
        pcr_reading = "Neutral"
    elif pcr["pcr_volume"] < PCR_BEARISH_THRESHOLD:
        pcr_reading = "Bearish"
    else:
        pcr_reading = "Extreme Bearish (contrarian bullish)"

    print(f"| Put/Call Ratio (Vol) | {pcr['pcr_volume']:.2f} | {pcr_reading} |")
    print(f"| Put/Call Ratio (OI) | {pcr['pcr_oi']:.2f} | — |")
    print(f"| Call Volume | {pcr['call_volume']:,} | — |")
    print(f"| Put Volume | {pcr['put_volume']:,} | — |")
    if implied_move:
        print(f"| Implied Move | ±{implied_move:.1f}% | — |")
    if max_pain:
        print(f"| Max Pain | ${max_pain:.0f} | — |")

    print("")
    if pcr["pcr_volume"] < 0.7:
        print("**Net Assessment:** Bullish positioning dominant.")
    elif pcr["pcr_volume"] > 1.2:
        print("**Net Assessment:** Bearish positioning dominant.")
    else:
        print("**Net Assessment:** Balanced positioning. No strong directional signal.")


def cmd_multi(tickers_str: str):
    """Scan multiple tickers."""
    tickers = [t.strip().upper() for t in tickers_str.split(",")]

    print(f"# Options Flow Multi-Scan — {datetime.now().strftime('%Y-%m-%d')}")
    print("")
    print(f"**Tickers:** {', '.join(tickers)}")
    print("")
    print("| Ticker | Spot | Top Signal | Strike | Vol/OI | Premium Est | Direction |")
    print("|--------|------|-----------|--------|--------|-------------|-----------|")

    for ticker in tickers:
        try:
            spot = get_spot_price(ticker)
            data = fetch_options_data(ticker)

            if not data:
                print(f"| {ticker} | — | No data | — | — | — | — |")
                continue

            if not spot:
                quote = data.get("quote", {})
                spot = quote.get("regularMarketPrice", 0)

            options = data.get("options", [{}])
            chain = options[0] if options else {}
            calls = chain.get("calls", [])
            puts = chain.get("puts", [])

            unusual = analyze_unusual_activity(calls, puts, spot)

            if unusual:
                top = unusual[0]
                direction = "BULLISH" if top["type"] == "Call" else "BEARISH"
                premium_str = f"${top['premium_est']:,.0f}"
                print(f"| {ticker} | ${spot:.2f} | {top['type']} | ${top['strike']:.0f} | {top['vol_oi']:.1f}x | {premium_str} | {direction} |")
            else:
                pcr = calculate_pcr(calls, puts)
                print(f"| {ticker} | ${spot:.2f} | No unusual | — | — | PCR: {pcr['pcr_volume']:.2f} | — |")

            time.sleep(0.3)
        except Exception as e:
            print(f"| {ticker} | — | Error | — | — | {str(e)[:25]} | — |")

    print("")
    print("_Threshold: Volume/OI ≥ 3.0x, min 100 contracts_")


# --- Main ---

def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python3 options_flow.py scan <TICKER> [expiry_date]")
        print("  python3 options_flow.py sentiment <TICKER>")
        print("  python3 options_flow.py multi <TICKER1,TICKER2,...>")
        sys.exit(1)

    command = sys.argv[1].lower()
    target = sys.argv[2]

    if command == "scan":
        expiry = sys.argv[3] if len(sys.argv) > 3 else None
        cmd_scan(target.upper(), expiry)
    elif command == "sentiment":
        cmd_sentiment(target.upper())
    elif command == "multi":
        cmd_multi(target)
    else:
        print(f"Unknown command: {command}")
        print("Available: scan, sentiment, multi")
        sys.exit(1)


if __name__ == "__main__":
    main()
