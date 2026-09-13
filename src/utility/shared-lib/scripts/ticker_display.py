#!/usr/bin/env python3
"""Shared ticker normalization and display helpers for the skills network.

Single source of truth for:
  * Yahoo Finance ticker normalization (`normalize_ticker_yf`)
  * Bursa Malaysia detection (`is_bursa_ticker`)
  * User-facing display labels (`display_ticker`, `display_ticker_token`)

The numeric Bursa codes otherwise render to the user as bare numbers
("1155", "1295"), which is hard to read. `display_ticker` turns those into
"1155.KL-MAYBANK" by combining the normalized exchange suffix with a short
company name.

Name lookup order for Bursa tickers:
  1. An explicit `name` argument (e.g. Yahoo's longName/shortName), when it
     looks like a short/common name rather than a long legal name.
  2. A curated table of well-known Bursa codes (BURSA_NAMES).
  3. Fallback: the normalized code with no name ("1155.KL").

Importable by data scripts; no network access.
"""

import re

# Known Bursa Malaysia numeric codes -> short display name. This is a curated
# convenience table so reports and scratch dirs are legible even when a live
# fetch returns no name. Add to it as you cover more names.
BURSA_NAMES = {
    "1023": "CIMB",
    "1155": "MAYBANK",
    "1295": "PBB",
    "5180": "HLBANK",
    "5211": "YTL",
    "4677": "GENM",
    "6947": "DIGI",
    "5398": "GAMUDA",
    "5347": "TENAGA",
    "5225": "IHH",
    "5296": "MRDIY",
    "5210": "GENTING",
    "2445": "KLK",
    "3182": "GASMSIA",
    "5249": "IRETEX",
    "1082": "HONGLEONG",
    "5819": "HLFG",
    "7084": "QL",
    "1961": "IOI",
}

# Yahoo modules where we prefer longName; if the returned name is longer than
# this many words it is treated as a legal name and we skip to the table.
_MAX_NAME_WORDS = 3


def normalize_ticker_yf(ticker):
    """Normalize a ticker for the Yahoo Finance API.

    - Numeric codes (e.g. "1155")  -> "1155.KL" (Bursa Malaysia)
    - Exchange-qualified (e.g. "1155:KLSE") -> "1155.KL"
    - Everything else (e.g. "MSFT", "BTC/USD") -> uppercased as-is
    """
    t = str(ticker).upper().strip()
    if t.isdigit():
        return f"{t}.KL"
    if ":" in t:
        base, exch = t.split(":", 1)
        base = base.strip()
        if exch.strip() in ("XKLS", "KLSE") and base.isdigit():
            return f"{base}.KL"
    return t


def is_bursa_ticker(ticker):
    """True when `ticker` denotes a Bursa Malaysia-listed stock."""
    raw = str(ticker).strip()
    if raw.isdigit():
        return True
    upper = raw.upper()
    if re.match(r"^\d+\.KL$", upper):
        return True
    if ":" in upper:
        _, exch = upper.split(":", 1)
        if exch.strip() in ("XKLS", "KLSE"):
            return True
    return False


def _short_name(name):
    """Return `name` only if it looks like a short/common name, else None.

    Yahoo often returns a long legal name ("Malayan Banking Berhad", "Public
    Bank Berhad"). Those are not suitable for a compact display label, so we
    fall back to the curated table instead.
    """
    if not name:
        return None
    name = str(name).strip()
    if not name:
        return None
    # A long multi-word name is a legal name; prefer the table.
    if len(name.split()) > _MAX_NAME_WORDS:
        return None
    # All-caps or title-case short names are fine.
    return name.upper()


def display_ticker(ticker, name=None):
    """User-facing display label for a ticker.

    Bursa:  "1155"        -> "1155.KL-MAYBANK"
            "1155.KL"     -> "1155.KL-MAYBANK"
            "1155:KLSE"   -> "1155.KL-MAYBANK"
    Others: "MSFT"        -> "MSFT"
            "BTC/USD"     -> "BTC-USD"   (slash -> dash, as report-writer does)

    `name` is an optional hint (e.g. from Yahoo meta). For Bursa tickers it is
    used only when it looks like a short name; otherwise the curated table or
    the bare code is used.
    """
    t = str(ticker).strip()
    if is_bursa_ticker(t):
        code = re.sub(r"[^0-9]", "", t) or t
        suffix = f"{code}.KL"
        short = _short_name(name) or BURSA_NAMES.get(code)
        if short:
            return f"{suffix}-{short}"
        return suffix
    # Non-Bursa: mirror report-writer's filename normalization (slash -> dash).
    return t.upper().replace("/", "-")


def display_ticker_token(ticker):
    """Filesystem token for report/scratch filenames (no name, normalized).

    Bursa:  "1155" -> "1155.KL"
    Others: "BTC/USD" -> "BTC-USD", "MSFT" -> "MSFT"
    """
    return display_ticker(ticker).split("-", 1)[0]