#!/usr/bin/env python3
"""Shared Yahoo Finance fetcher with local file cache.

Cache location: $ISK_CACHE/<ticker>_<interval>_<period>.json
Cache default: ~/.cache when ISK_CACHE is unset.
Cache TTL: same local calendar day. A uniform daily TTL is used for all markets
(US, Bursa, crypto). This is intentional: the network targets daily-granularity
research, not intraday day-trading, so a single calendar-day rule is correct and
simple. Set ISK_CACHE_TTL_HOURS to override with a fixed-hours TTL instead
(useful for 24/7 crypto if you want fresher intraday data).

Usage:
    from yahoo_cache import fetch_yahoo_cached

    candles, meta = fetch_yahoo_cached("5180", period="1y", interval="1d")
"""

import os
import json
import urllib.request
from datetime import datetime, timedelta, timezone


MYT = timezone(timedelta(hours=8))

CACHE_DIR = os.path.expanduser(
    os.environ.get("ISK_CACHE", "~/.cache")
)


def _cache_key(ticker, interval, period):
    safe_ticker = ticker.replace("/", "_").replace(":", "_").replace(".", "_").upper()
    return f"{safe_ticker}_{interval}_{period}.json"


def _is_cache_valid(cache_path):
    """Uniform daily TTL for all markets.

    Valid if the cache file was written on the current local calendar day. If
    ISK_CACHE_TTL_HOURS is set, a fixed rolling-hours TTL is used instead of the
    calendar-day rule (e.g. set it to 4 for fresher 24/7 crypto data).

    No per-market close-time logic: the old Bursa-specific 17:30 MYT cutoff was
    applied to every market, which miscomputed freshness for US and had no meaning
    for 24/7 crypto. Daily granularity is sufficient for this network's use case.
    """
    if not os.path.exists(cache_path):
        return False

    mtime = os.path.getmtime(cache_path)
    cached_dt = datetime.fromtimestamp(mtime)
    now = datetime.now()

    ttl_hours = os.environ.get("ISK_CACHE_TTL_HOURS")
    if ttl_hours:
        try:
            return (now - cached_dt) < timedelta(hours=float(ttl_hours))
        except ValueError:
            pass  # fall through to calendar-day rule on a bad value

    # Default: valid only if written on the same local calendar day.
    return cached_dt.date() == now.date()


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
