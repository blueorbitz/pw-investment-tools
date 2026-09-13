#!/usr/bin/env python3
"""Prune stale files from the Investment Skills Network cache.

The cache layout is date-addressable by design:

    ISK_CACHE/
    ├── YYYY-MM/                  # per-month bucket
    │   └── YYYY-MM-DD-<key>.json  # file stamped with its fetch date
    └── .bursawhale_token.json     # auth token (kept unless --include-token)

Because every cache file carries its birth date in its path, age is determined
from the path, not the mtime — moving or copying the cache never makes a file
look freshly fetched.

Default retention: 7 days (override with ISK_CACHE_MAX_AGE_DAYS, or
--max-age-days). Pass --dry-run to preview deletions without removing anything.

The bursawhale OAuth token has its own TTL and is left alone unless
--include-token is passed.

Usage:
    python cleanup_cache.py [--max-age-days N] [--include-token] [--dry-run]
"""

import argparse
import os
import re
import sys
from datetime import datetime, timedelta, timezone

MYT = timezone(timedelta(hours=8))


def _resolve_cache_dir():
    """Resolve ISK_CACHE the same way the rest of the network does."""
    env = os.environ.get("ISK_CACHE")
    if env:
        return os.path.expanduser(env)
    # Fall back to the shared resolver so .env is honored.
    try:
        _ROOT = os.environ.get("ISK_ROOT")
        if not _ROOT or not os.path.isabs(_ROOT):
            _ROOT = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        sys.path.insert(0, os.path.join(_ROOT, "utility", "shared-lib", "scripts"))
        from yahoo_cache import _cache_dir  # noqa: E402
        return _cache_dir()
    except Exception:
        return os.path.expanduser("~/.cache")


# YYYY-MM-DD at the start of a filename, or a YYYY-MM directory component.
_RE_DATE_PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2}-")
_RE_MONTH_DIR = re.compile(r"^\d{4}-\d{2}$")


def _age_date_for(rel_parts):
    """Return a date for a cache entry based on its path, or None.

    Prefers the file's own YYYY-MM-DD- prefix, then its parent YYYY-MM
    directory (taken as the 1st of that month), so age tracks when the data
    was cached — independent of mtime.
    """
    if rel_parts:
        head = rel_parts[-1]
        m = _RE_DATE_PREFIX.match(head)
        if m:
            try:
                return datetime.strptime(m.group(0).rstrip("-"), "%Y-%m-%d").date()
            except ValueError:
                pass
    # Fall back to a YYYY-MM parent directory (age from the 1st of that month).
    for part in reversed(rel_parts[:-1]):
        if _RE_MONTH_DIR.match(part):
            try:
                return datetime.strptime(part + "-01", "%Y-%m-%d").date()
            except ValueError:
                pass
    return None


def _remove_empty_parents(root, path):
    """Walk up from `path`, removing empty directories that live under `root`."""
    current = path
    while current != root and os.path.isdir(current) and not os.listdir(current):
        try:
            os.rmdir(current)
        except OSError:
            break
        current = os.path.dirname(current)


def cleanup(cache_dir, max_age_days, include_token, dry_run):
    cutoff = (datetime.now(tz=MYT) - timedelta(days=max_age_days)).date()
    removed_files = 0
    removed_bytes = 0
    removed_dirs = 0
    token_path = os.path.join(cache_dir, ".bursawhale_token.json")

    for dirpath, dirnames, filenames in os.walk(cache_dir, topdown=False):
        for name in filenames:
            full = os.path.join(dirpath, name)
            if full == token_path and not include_token:
                continue
            rel_parts = os.path.relpath(full, cache_dir).split(os.sep)
            age = _age_date_for(rel_parts)
            if age is None or age >= cutoff:
                continue
            size = os.path.getsize(full)
            if not dry_run:
                try:
                    os.remove(full)
                except OSError:
                    continue
            removed_files += 1
            removed_bytes += size
            if dry_run:
                print(f"  [dry-run] would remove {os.path.relpath(full, cache_dir)}"
                      f" (cached {age.isoformat()})")
        if not dry_run:
            _remove_empty_parents(cache_dir, dirpath)

    return removed_files, removed_bytes


def main():
    parser = argparse.ArgumentParser(
        description="Remove Investment Skills Network cache files older than N days.")
    parser.add_argument(
        "--max-age-days", type=float, default=None,
        help="Retention window in days (default: ISK_CACHE_MAX_AGE_DAYS, else 7).")
    parser.add_argument(
        "--include-token", action="store_true",
        help="Also delete the bursawhale OAuth token when it ages out.")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print what would be removed without deleting anything.")
    args = parser.parse_args()

    cache_dir = _resolve_cache_dir()
    if not os.path.isdir(cache_dir):
        print(f"Cache directory does not exist: {cache_dir}")
        return 0

    max_age = args.max_age_days
    if max_age is None:
        env_age = os.environ.get("ISK_CACHE_MAX_AGE_DAYS")
        max_age = float(env_age) if env_age else 7.0

    if args.dry_run:
        print(f"[dry-run] cache: {cache_dir}  (keep files newer than {max_age} days)")
    else:
        print(f"Cleaning cache: {cache_dir}  (keeping files newer than {max_age} days)")

    removed_files, removed_bytes = cleanup(
        cache_dir, max_age, args.include_token, args.dry_run)

    # Count leftover empty dirs that walk didn't catch at the top level.
    print(f"{'Would remove' if args.dry_run else 'Removed'} "
          f"{removed_files} file(s), {removed_bytes} byte(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
