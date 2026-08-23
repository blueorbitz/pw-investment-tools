#!/usr/bin/env python3
"""Cron target for portfolio review.

Validates the environment, ensures output directories exist, and prints
instructions for invoking the Kiro agent with the portfolio-review skill.

Schedule examples:
    # Linux/Mac cron - weekly Sunday 9 AM
    0 9 * * 0 python3 /path/to/src/monitor/portfolio-review/scripts/run_review.py

    # Windows Task Scheduler
    python "C:\\path\\to\\src\\monitor\\portfolio-review\\scripts\\run_review.py"
"""

import os
import sys
from datetime import date
from pathlib import Path


def main():
    # Resolve notes directory (ISK_NOTES or default ~/notes)
    notes_dir = Path(os.environ.get("ISK_NOTES", Path.home() / "notes"))
    holdings_file = notes_dir / "portfolio" / "holdings.yaml"

    if not holdings_file.exists():
        print(f"ERROR: Holdings file not found at: {holdings_file}", file=sys.stderr)
        print("Create it with your portfolio positions.", file=sys.stderr)
        print("See monitor/portfolio-review/SKILL.md for schema.", file=sys.stderr)
        sys.exit(1)

    today = date.today()
    month_str = today.strftime("%Y-%m")
    date_str = today.strftime("%Y-%m-%d")
    output_dir = notes_dir / "portfolio" / "reviews" / month_str
    output_file = output_dir / f"{date_str}-portfolio-review.md"

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Portfolio Review - {date_str}")
    print(f"Holdings: {holdings_file}")
    print(f"Output:   {output_file}")
    print()
    print("To run this review, invoke the agent with:")
    print("  'Run portfolio review using monitor/portfolio-review skill'")
    print()

    # Print first 30 lines of holdings as summary
    print("--- Holdings Summary ---")
    with open(holdings_file, "r") as f:
        for i, line in enumerate(f):
            if i >= 30:
                print("...")
                break
            print(line, end="")


if __name__ == "__main__":
    main()
