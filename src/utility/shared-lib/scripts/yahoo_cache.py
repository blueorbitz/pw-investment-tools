#!/usr/bin/env python3
"""Shared Yahoo Finance fetcher with local file cache.

Cache location: $ISK_CACHE/<ticker>_<interval>_<period>.json
Cache default: ~/.cache when ISK_CACHE is unset.
Cache TTL: same calendar trading day (invalidates after market close or next day).

Usage:
    from yahoo_cache import fetch_yahoo_cached

    candles, meta = fetch_yahoo_cached("5180", period="1y", interval="1d")
"""

import os
import json
import urllib.request
from datetime import datetime, timezone, timedelta


CACHE_DIR = os.path.expanduser(
    os.environ.get("ISK_CACHE", "~/.cache")
)
# MYT = UTC+8, Bursa closes at 17:00 MYT. Use 17:30 as safe cutoff.
MYT = timezone(timedelta(hours=8))


def _cache_key(ticker, interval, period):
    safe_ticker = ticker.replace("/", "_").replace(":", "_").replace(".", "_").upper()
    return f"{safe_ticker}_{interval}_{period}.json"


def _is_cache_valid(cache_path):
    """Cache is valid if written today (MYT) and market hasn't closed since."""
    if not os.path.exists(cache_path):
        return False

    mtime = os.path.getmtime(cache_path)
    cached_dt = datetime.fromtimestamp(mtime, tz=MYT)
    now = datetime.now(tz=MYT)

    # Same calendar day in MYT
    if cached_dt.date() != now.date():
        return False

    # If cached before market close (17:30) and now is after, invalidate
    market_close = now.replace(hour=17, minute=30, second=0, microsecond=0)
    if cached_dt < market_close and now >= market_close:
        return False

    return True


def _normalize_ticker(ticker):
    """Normalize ticker for Yahoo Finance API."""
    yf_ticker = ticker.upper()
    if yf_ticker.isdigit():
        yf_ticker = f"{yf_ticker}.KL"
    elif ":" in yf_ticker:
        base, exch = yf_ticker.split(":")
        if exch in ("XKLS", "KLSE"):
            yf_ticker = f"{base}.KL"
    elif "/" in yf_ticker:
        base, quote = yf_ticker.split("/")
        yf_ticker = f"{base}-{quote}"
    return yf_ticker


def fetch_yahoo_cached(ticker, period="1y", interval="1d"):
    """Fetch OHLCV data with local cache. Returns (candles, meta).

    candles: list of {"date", "open", "high", "low", "close", "volume"}
    meta: dict from Yahoo Finance chart meta
    """
    os.makedirs(CACHE_DIR, exist_ok=True)

    key = _cache_key(ticker, interval, period)
    cache_path = os.path.join(CACHE_DIR, key)

    # Check cache
    if _is_cache_valid(cache_path):
        with open(cache_path, "r") as f:
            cached = json.load(f)
        return cached["candles"], cached["meta"]

    # Fetch from Yahoo
    yf_ticker = _normalize_ticker(ticker)
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yf_ticker}?interval={interval}&range={period}"
    req = urllib.request.Request(url, headers={"User-Agent": ua})

    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())

    result = data["chart"]["result"][0]
    meta = result["meta"]
    timestamps = result["timestamp"]
    quote = result["indicators"]["quote"][0]

    candles = []
    for i in range(len(timestamps)):
        o = quote["open"][i]
        h = quote["high"][i]
        l = quote["low"][i]
        c = quote["close"][i]
        v = quote["volume"][i]
        if o is None or c is None:
            continue
        candles.append({
            "date": datetime.utcfromtimestamp(timestamps[i]).strftime("%Y-%m-%d"),
            "open": round(o, 4),
            "high": round(h, 4),
            "low": round(l, 4),
            "close": round(c, 4),
            "volume": v or 0
        })

    # Write cache
    cache_data = {"candles": candles, "meta": meta, "fetched_at": datetime.now(tz=MYT).isoformat()}
    with open(cache_path, "w") as f:
        json.dump(cache_data, f)

    return candles, meta
