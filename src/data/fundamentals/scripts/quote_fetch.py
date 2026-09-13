#!/usr/bin/env python3
"""Yahoo quote fetcher: point-in-time valuation metrics from quoteSummary.

Returns trailing/forward PE, PEG, market cap, trailing FCF and FCF yield,
shares outstanding, 52-week range, price-to-book, and dividend yield —
everything the agent previously web-browsed from Yahoo Finance pages.

The endpoint requires cookie + crumb auth; the bootstrap flow is handled here
on a single cookie-jar opener so cookie and crumb ride the same request.

Cache policy follows yahoo_cache (principle 2): quotes are fetched LIVE every
run (price policy); the cache is a fallback served only when the live fetch
fails, marked "stale": true in the meta.

Usage:
    python quote_fetch.py MSFT
    python quote_fetch.py 1155
    python quote_fetch.py BTC-USD
"""

import json
import os
import sys

# ISK_ROOT points at src/. A relative ISK_ROOT is ignored for import purposes
# (CWD-dependent); __file__-relative resolution is used instead.
_ROOT = os.environ.get("ISK_ROOT")
if not _ROOT or not os.path.isabs(_ROOT):
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(_ROOT, "utility", "shared-lib", "scripts"))

from yahoo_cache import (  # noqa: E402
    _cache_path,
    _normalize_ticker,
    _serve_cached,
    isk_paths,
    store_cache,
    yahoo_summary,
)
from ticker_display import display_ticker  # noqa: E402

QUOTE_MODULES = "price,summaryDetail,defaultKeyStatistics,financialData"


def _raw(node):
    if isinstance(node, dict):
        return node.get("raw")
    return node


def _yield_pct(node):
    """quoteSummary reports dividendYield as a fraction (0.0073 = 0.73%)."""
    value = _raw(node)
    if value is not None and value < 1:
        return round(value * 100, 3)
    return value


def _parse_quote(result):
    r = result
    price = r.get("price", {})
    sd = r.get("summaryDetail", {})
    dks = r.get("defaultKeyStatistics", {})
    fd = r.get("financialData", {})

    market_cap = _raw(price.get("marketCap"))
    fcf = _raw(fd.get("freeCashflow"))
    fcf_yield = round(fcf / market_cap * 100, 2) if (fcf and market_cap) else None

    symbol = _raw(price.get("symbol")) or price.get("symbol")
    display_name = price.get("shortName") or price.get("longName")
    payload = {
        "symbol": symbol,
        "name": price.get("longName") or price.get("shortName"),
        "display_ticker": display_ticker(symbol or ticker, name=display_name),
        "currency": _raw(price.get("currency")),
        "price": _raw(price.get("regularMarketPrice")),
        "trailing_pe": _raw(sd.get("trailingPE")),
        "forward_pe": _raw(sd.get("forwardPE")),
        "peg_ratio": _raw(dks.get("trailingPegRatio")),
        "market_cap": market_cap,
        "shares_outstanding": _raw(dks.get("sharesOutstanding")),
        "fcf_trailing": fcf,
        "fcf_yield_pct": fcf_yield,
        "price_to_book": _raw(dks.get("priceToBook")),
        "dividend_yield_pct": _yield_pct(sd.get("dividendYield")),
        "fifty_two_week": {
            "low": _raw(sd.get("fiftyTwoWeekLow")),
            "high": _raw(sd.get("fiftyTwoWeekHigh")),
        },
    }
    if payload["price"] is None:
        raise ValueError("no price in quoteSummary response")
    return payload, {"kind": "quote", "symbol": payload["symbol"]}


def _live_quote(yf_ticker):
    """Live quote fetch via the shared authenticated quoteSummary helper."""
    result = yahoo_summary(yf_ticker, QUOTE_MODULES)
    return _parse_quote(result)


def fetch_quote(ticker):
    """Fetch quote metrics with the price policy: live every run, the cache is
    a fallback served only when the live fetch fails (marked stale)."""
    cache_path = _cache_path("quote", ticker)
    try:
        payload, meta = _live_quote(_normalize_ticker(ticker))
        store_cache(cache_path, {"payload": payload, "meta": meta})
        return payload, meta
    except Exception:
        served = _serve_cached(cache_path, stale=True)
        if served:
            return served
        raise


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Fetch Yahoo quote metrics")
    parser.add_argument("ticker", help="Ticker, e.g. MSFT, 1155, BTC-USD")
    args = parser.parse_args()

    try:
        payload, meta = fetch_quote(args.ticker)
        print(json.dumps({"ok": True, **meta, **payload, "paths": isk_paths()}, indent=2))
    except Exception as exc:
        print(json.dumps({
            "ok": False,
            "ticker": args.ticker,
            "error": f"{type(exc).__name__}: {exc}",
            "status": "unavailable",
        }, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
