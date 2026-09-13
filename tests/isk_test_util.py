"""Shared helpers for the investment-skills regression test suite.

Everything here lives in the repository and runs the resolver the same way the
orchestrators do, so the assertions exercise the real path-resolution contract
(`.env` in the workspace root is the source of truth).
"""

import json
import os
import re
import subprocess
import sys
from datetime import date

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "src")
PATH_RESOLVER = os.path.join(
    SRC, "utility", "shared-lib", "scripts", "isk_paths.py"
)
# Shared ticker-display helper (single source of truth for report/scratch
# filenames). Imported lazily so the util module stays import-light.
_DISPLAY_TICKER_CACHE = {}


def _display_ticker(ticker):
    """Bursa -> '1155.KL-MAYBANK'; others -> normalized symbol.

    Cached per-ticker. Only imported on first use so tests that don't need it
    avoid the import."""
    if ticker not in _DISPLAY_TICKER_CACHE:
        _SHARED = os.path.join(SRC, "utility", "shared-lib", "scripts")
        if _SHARED not in sys.path:
            sys.path.insert(0, _SHARED)
        from ticker_display import display_ticker as _dt  # noqa: E402
        _DISPLAY_TICKER_CACHE[ticker] = _dt(ticker)
    return _DISPLAY_TICKER_CACHE[ticker]

MARKETS = ("US", "Bursa", "Crypto")
REPORT_TYPES = ("quick-look", "deep-research")


def run_python(argv, cwd=None):
    return subprocess.run(
        [sys.executable] + [str(a) for a in argv],
        cwd=cwd or REPO,
        capture_output=True,
        text=True,
    )


def resolve_isk_paths():
    """Run the canonical path resolver and return its JSON dict.

    Throws if the resolution fails. This is the same resolver every
    orchestrator invokes first, so matching its output means matching `.env`.
    """
    proc = run_python([PATH_RESOLVER])
    if proc.returncode != 0:
        raise RuntimeError(
            f"isk_paths.py failed ({proc.returncode}): {proc.stderr}"
        )
    return json.loads(proc.stdout)


def sk(path):
    """Absolute path to a skill directory (or its file)."""
    return os.path.join(SRC, *path.split("/"))


def skill_md_exists(*rel):
    return os.path.isfile(os.path.join(SRC, *rel, "SKILL.md"))


def ticker_token(ticker):
    """The display-ticker token used in report/scratch filenames.

    Mirrors the report-writer convention: Bursa tickers become
    '1155.KL-MAYBANK', others the normalized symbol ('MSFT', 'BTC-USD')."""
    return _display_ticker(ticker)


def month_dir(isk_notes, day=None):
    return os.path.join(isk_notes, (day or date.today()).strftime("%Y-%m"))


def scratch_dir_for(isk_notes, ticker, day=None):
    """$ISK_NOTES/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>"""
    return os.path.join(
        month_dir(isk_notes, day),
        ".scratch",
        (day or date.today()).strftime("%Y-%m-%d") + "-" + ticker_token(ticker),
    )


def find_new_report(isk_notes, ticker, report_type, created_after=0.0):
    """Locate the report file for a ticker+type created after `created_after`.

    Returns the newest matching file path or None. Matches by normalized
    ticker token and `-<report_type>.md` suffix so the exact filename shape
    (slash handling, .KL stripping) never makes the assertion brittle.
    """
    mdir = month_dir(isk_notes)
    if not os.path.isdir(mdir):
        return None
    token = ticker_token(ticker)
    candidate = None
    latest = created_after
    for name in os.listdir(mdir):
        if not name.endswith(f"-{report_type}.md"):
            continue
        if token not in name:
            continue
        path = os.path.join(mdir, name)
        mtime = os.path.getmtime(path)
        if mtime <= latest:
            continue
        if candidate is None or mtime > latest:
            candidate = path
            latest = mtime
    return candidate