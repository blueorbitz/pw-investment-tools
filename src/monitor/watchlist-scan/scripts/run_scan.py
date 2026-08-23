#!/usr/bin/env python3
"""Cron target for watchlist scan.

Validates the environment, ensures output directories exist, and prints
instructions for invoking the Kiro agent with the watchlist-scan skill.

Schedule examples:
    # Linux/Mac cron - weekly Sunday 10 AM
    0 10 * * 0 python3 /path/to/src/monitor/watchlist-scan/scripts/run_scan.py

    # Windows Task Scheduler
    python "C:\\path\\to\\src\\monitor\\watchlist-scan\\scripts\\run_scan.py"
"""

import os
import sys
from datetime import date
from pathlib import Path


def main():
    # Resolve notes directory (ISK_NOTES or default ~/notes)
    notes_dir = Path(os.environ.get("ISK_NOTES", Path.home() / "notes"))
    watchlist_file = notes_dir / "watchlist" / "watchlist.yaml"

    if not watchlist_file.exists():
        print(f"ERROR: Watchlist file not found at: {watchlist_file}", file=sys.stderr)
        print("Create it with tickers to track.", file=sys.stderr)
        print("See monitor/watchlist-scan/SKILL.md for schema.", file=sys.stderr)
        sys.exit(1)

    today = date.today()
    month_str = today.strftime("%Y-%m")
    date_str = today.strftime("%Y-%m-%d")
    output_dir = notes_dir / "watchlist" / "scans" / month_str
    output_file = output_dir / f"{date_str}-watchlist-scan.md"

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Watchlist Scan - {date_str}")
    print(f"Watchlist: {watchlist_file}")
    print(f"Output:    {output_file}")
    print()
    print("To run this scan, invoke the agent with:")
    print("  'Run watchlist scan using monitor/watchlist-scan skill'")
    print()

    # Print first 30 lines of watchlist as summary
    print("--- Watchlist Summary ---")
    with open(watchlist_file, "r") as f:
        for i, line in enumerate(f):
            if i >= 30:
                print("...")
                break
            print(line, end="")


if __name__ == "__main__":
    main()
