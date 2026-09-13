---
name: cache-cleanup
description: Prunes stale files from the ISK_CACHE directory. Removes cache entries older than a retention window (default 7 days) so the cache stays small without hurting the always-fresh data policy. Use when asked to clean up the cache, free disk space, or on a schedule.
---

# Cache cleanup

The Investment Skills Network cache lives at `ISK_CACHE` (from `.env`, default
`~/.cache`). Files are written into a date-addressed layout:

```
ISK_CACHE/
├── YYYY-MM/                       # per-month bucket
│   └── YYYY-MM-DD-<key>.json      # stamped with its fetch date
└── .bursawhale_token.json         # OAuth token (own TTL; left alone)
```

Because every cache file carries its birth date in its path, cleanup decides
age from the **path**, not the mtime — so moving or backing up the cache never
makes a file look freshly fetched.

## Retention

Default: **7 days**. Override either way:

- Env var: `ISK_CACHE_MAX_AGE_DAYS=14`
- CLI flag: `--max-age-days 14`

## Run

```bash
# Preview what would be removed (no deletion)
python <ISK_ROOT>/utility/cache-cleanup/scripts/cleanup_cache.py --dry-run

# Actually prune files older than the retention window
python <ISK_ROOT>/utility/cache-cleanup/scripts/cleanup_cache.py
```

Flags:

| Flag | Description |
|------|-------------|
| `--max-age-days N` | Retention window in days (default `ISK_CACHE_MAX_AGE_DAYS`, else 7) |
| `--dry-run` | Print what would be removed, delete nothing |
| `--include-token` | Also delete the bursawhale OAuth token when it ages out (it normally has its own TTL and is left untouched) |

## What is (and isn't) cleaned

- **Removed:** price/quote cache `.json` files whose embedded fetch date is older than the window, including any empty month buckets left behind.
- **Kept:** the `.bursawhale_token.json` OAuth token (unless `--include-token`), any file newer than the window, and any file that has no date in its path (so unrelated files in the cache dir are never touched).

## Schedule

Run on the same cadence as your other maintenance (e.g. a weekly cron/harness
job alongside the monitor skills). Example weekly entry:

```bash
python <ISK_ROOT>/utility/cache-cleanup/scripts/cleanup_cache.py
```

## Dependencies

None. Pure stdlib. Reads `ISK_CACHE` (and `ISK_ROOT` for resolution) the same
way the rest of the network does.
