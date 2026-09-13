#!/usr/bin/env python3
"""Shared Yahoo Finance fetcher with local file cache.

Environment resolution: env vars take precedence; a `.env` file in the
workspace root is loaded as a fallback for unset vars (same convention as
utility/report-writer). Relative paths in `.env` (e.g. ISK_CACHE=./.cache)
resolve against the workspace root, not the current directory.

Cache policy (principle 2: always-fresh data, cache only as fallback):

- Prices and quotes (policy="price"): fetched LIVE on every run. The cache is
  a FALLBACK only — it is served when the live fetch fails, regardless of age,
  with "stale": true recorded in the meta. Set ISK_PRICE_TTL_MINUTES to serve
  the cache within that window instead (opt-in cost control; e.g. 15).
- Statements (policy="statement"): cached for the local calendar day. Quarterly
  statements cannot change intraday, so refetching buys nothing. A same-day
  cache is served without refetch; an older cache triggers a live fetch.

Set ISK_CACHE_TTL_HOURS to override the statement policy with a fixed-hours
TTL (useful for 24/7 crypto statement-like feeds if you want fresher data).

Usage:
    from yahoo_cache import fetch_yahoo_cached

    candles, meta = fetch_yahoo_cached("5180", period="1y", interval="1d")
"""

import os
import json
import http.cookiejar
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone


MYT = timezone(timedelta(hours=8))

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


def _find_workspace_root():
    """Walk up from this file to the directory containing src/ or .env."""
    here = os.path.dirname(os.path.abspath(__file__))
    for _ in range(5):
        if os.path.isfile(os.path.join(here, ".env")) or os.path.isdir(os.path.join(here, "src")):
            return here
        parent = os.path.dirname(here)
        if parent == here:
            return None
        here = parent
    return None


_ENV_PATH_VARS = ("ISK_NOTES", "ISK_CACHE", "ISK_ROOT")


def load_workspace_env():
    """Resolve the ISK_* path variables against the workspace root.

    Precedence for ISK_NOTES / ISK_CACHE / ISK_ROOT: the `.env` file in the
    workspace root is the source of truth (it overrides an inherited env var —
    scheduler/harness sessions often carry stale copies). For every other key
    (API keys etc.) the real environment wins and `.env` is the fallback.

    Relative paths — from either source — resolve against the workspace root,
    never the current directory. Returns the workspace root (or None).
    """
    root = _find_workspace_root()
    if not root:
        return None
    env_file = {}
    env_path = os.path.join(root, ".env")
    if os.path.isfile(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except OSError:
            lines = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and value:
                env_file[key] = value
            # Non-path keys: real env wins, .env is the fallback
            if key and key not in _ENV_PATH_VARS and key not in os.environ and value:
                os.environ[key] = value
    # ISK_* path vars: .env overrides the environment; relative -> workspace root
    for var in _ENV_PATH_VARS:
        value = env_file.get(var) or os.environ.get(var)
        if not value:
            continue
        if not os.path.isabs(value):
            value = os.path.normpath(os.path.join(root, value))
        os.environ[var] = value
    # Defaults when neither source defines a path
    src_dir = os.path.join(root, "src")
    if os.path.isdir(src_dir):
        os.environ.setdefault("ISK_ROOT", src_dir)
    os.environ.setdefault("ISK_NOTES", os.path.join(os.path.expanduser("~"), "notes"))
    os.environ.setdefault("ISK_CACHE", os.path.join(os.path.expanduser("~"), ".cache"))
    return root


def isk_paths():
    """Resolved workspace paths, for agents and script output."""
    return {
        "isk_root": os.environ.get("ISK_ROOT"),
        "isk_notes": os.environ.get("ISK_NOTES"),
        "isk_cache": _cache_dir(),
    }


load_workspace_env()


def _cache_dir():
    """Cache directory: ISK_CACHE (env or .env), defaulting to ~/.cache.
    Resolved lazily so runtime env changes are honored."""
    return os.path.expanduser(os.environ.get("ISK_CACHE", "~/.cache"))


def http_json(url, timeout=15):
    """GET a URL and parse the JSON body. Raises on HTTP/network errors."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


_opener = None
_crumb = None


def get_yahoo_session():
    """Cookie-jar opener + API crumb for endpoints that require auth
    (quoteSummary). Cookie and crumb ride the same opener."""
    global _opener, _crumb
    if _opener is None:
        cj = http.cookiejar.CookieJar()
        _opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    if _crumb is None:
        try:
            req = urllib.request.Request("https://fc.yahoo.com", headers={"User-Agent": UA})
            _opener.open(req, timeout=10).read()
        except Exception:
            pass  # fc.yahoo.com normally 404s; it only needs to set the cookie
        req = urllib.request.Request(
            "https://query1.finance.yahoo.com/v1/test/getcrumb", headers={"User-Agent": UA}
        )
        crumb = _opener.open(req, timeout=10).read().decode().strip()
        if not crumb:
            raise RuntimeError("empty crumb from Yahoo")
        _crumb = crumb
    return _opener, _crumb


def yahoo_summary(ticker, modules):
    """Authenticated quoteSummary fetch. Returns the result dict.

    The timeseries endpoint stopped serving statement types crumb-free;
    quoteSummary with cookie+crumb is the working source for statements
    and point-in-time metrics."""
    opener, crumb = get_yahoo_session()
    url = (
        "https://query2.finance.yahoo.com/v10/finance/quoteSummary/{ticker}"
        "?modules={modules}&crumb={crumb}"
    ).format(ticker=urllib.parse.quote(ticker), modules=modules, crumb=urllib.parse.quote(crumb))
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    data = json.loads(opener.open(req, timeout=15).read().decode())
    result = data["quoteSummary"]["result"]
    if not result:
        raise ValueError("empty quoteSummary result")
    return result[0]


def _cache_key(kind, ticker, interval="NA", period="NA"):
    safe_ticker = ticker.replace("/", "_").replace(":", "_").replace(".", "_").upper()
    return f"{safe_ticker}_{kind}_{interval}_{period}.json"


def _date_prefix():
    """Today's date prefix for the cache layout: YYYY-MM/YYYY-MM-DD-.

    Keeping cache files grouped under a per-month directory, stamped with the
    fetch date, makes the cache self-describing and trivial to prune by age
    (see utility/cache-cleanup): every file's birth date is in its path.
    """
    now = datetime.now(tz=MYT)
    month = now.strftime("%Y-%m")
    day = now.strftime("%Y-%m-%d")
    return month, f"{day}-"


def _cache_path(kind, ticker, interval="NA", period="NA"):
    month, day_prefix = _date_prefix()
    return os.path.join(
        _cache_dir(), month, f"{day_prefix}{_cache_key(kind, ticker, interval, period)}",
    )


def load_cache(cache_path):
    """Load a cache file, or None if missing/corrupt."""
    try:
        with open(cache_path, "r") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def store_cache(cache_path, payload):
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    payload = dict(payload)
    payload["fetched_at"] = datetime.now(tz=MYT).isoformat()
    with open(cache_path, "w") as f:
        json.dump(payload, f)


def _cache_age_hours(cache_path):
    mtime = os.path.getmtime(cache_path)
    return (datetime.now() - datetime.fromtimestamp(mtime)) / timedelta(hours=1)


def _same_local_day(cache_path):
    return datetime.fromtimestamp(os.path.getmtime(cache_path)).date() == datetime.now().date()


def _serve_cached(cache_path, payload_key="payload", stale=False):
    cached = load_cache(cache_path)
    if cached is None:
        return None
    # Legacy cache files (pre per-endpoint-TTL) stored candles at top level.
    payload = cached.get(payload_key, cached.get("candles"))
    if payload is None:
        return None
    meta = dict(cached.get("meta", {}))
    if stale:
        meta["stale"] = True
        meta["stale_reason"] = "live fetch failed; cache served as fallback"
    return payload, meta


def fetch_cached(url, ticker, kind, policy, parse_fn, interval="NA", period="NA"):
    """Generic cached fetch implementing the per-endpoint policy.

    parse_fn(data) -> (payload, meta) from the live JSON. Raises inside on a
    malformed response so the fallback cache is used.
    """
    cache_path = _cache_path(kind, ticker, interval, period)

    # Statement policy: a same-day cache is served without refetch.
    if policy == "statement":
        if os.path.exists(cache_path):
            ttl_hours = os.environ.get("ISK_CACHE_TTL_HOURS")
            try:
                fresh = (
                    (_cache_age_hours(cache_path) < float(ttl_hours))
                    if ttl_hours
                    else _same_local_day(cache_path)
                )
            except ValueError:
                fresh = _same_local_day(cache_path)
            if fresh:
                served = _serve_cached(cache_path)
                if served:
                    return served

    # Live fetch. On failure, the cache is the fallback (any age, marked stale).
    try:
        data = http_json(url)
        payload, meta = parse_fn(data)
        store_cache(cache_path, {"payload": payload, "meta": meta})
        return payload, meta
    except Exception:
        if os.path.exists(cache_path):
            served = _serve_cached(cache_path, stale=True)
            if served:
                return served
        raise


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


def _parse_chart(data):
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

    return candles, meta


def fetch_yahoo_cached(ticker, period="1y", interval="1d", policy="price"):
    """Fetch OHLCV data with the per-endpoint cache policy. Returns (candles, meta).

    candles: list of {"date", "open", "high", "low", "close", "volume"}
    meta: dict from Yahoo Finance chart meta; "stale": true when served from
    the fallback cache after a failed live fetch.

    policy="price" (default): live fetch every run, cache is fallback-only.
    policy="statement": same-day cache served without refetch.
    """
    yf_ticker = _normalize_ticker(ticker)
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yf_ticker}?interval={interval}&range={period}"

    # Optional opt-in: serve the price cache within ISK_PRICE_TTL_MINUTES.
    if policy == "price":
        ttl_min = os.environ.get("ISK_PRICE_TTL_MINUTES")
        cache_path = _cache_path("price", ticker, interval, period)
        if ttl_min and os.path.exists(cache_path):
            try:
                age_min = _cache_age_hours(cache_path) * 60
                if age_min < float(ttl_min):
                    served = _serve_cached(cache_path)
                    if served:
                        return served
            except (ValueError, OSError):
                pass  # bad TTL value or unreadable mtime: fall through to live fetch

    return fetch_cached(url, ticker, kind="price", policy=policy, parse_fn=_parse_chart,
                        interval=interval, period=period)
