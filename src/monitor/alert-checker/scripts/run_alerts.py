#!/usr/bin/env python3
"""Cron target for alert checking.

Validates the environment, checks whether any positions have alert_conditions,
and prints instructions for invoking the Kiro agent with the alert-checker skill.

Can run more frequently than portfolio review (e.g., every 4 hours for crypto).

Schedule examples:
    # Linux/Mac cron - daily at 8 AM
    0 8 * * * python3 /path/to/src/monitor/alert-checker/scripts/run_alerts.py

    # More frequent for crypto (every 4 hours)
    0 */4 * * * python3 /path/to/src/monitor/alert-checker/scripts/run_alerts.py

    # Windows Task Scheduler
    python "C:\\path\\to\\src\\monitor\\alert-checker\\scripts\\run_alerts.py"
"""

import os
import sys
from datetime import date, datetime
from pathlib import Path


def main():
    # Resolve notes directory (ISK_NOTES or default ~/notes)
    notes_dir = Path(os.environ.get("ISK_NOTES", Path.home() / "notes"))
    holdings_file = notes_dir / "portfolio" / "holdings.yaml"

    if not holdings_file.exists():
        print(f"ERROR: Holdings file not found at: {holdings_file}", file=sys.stderr)
        print("Create it with alert_conditions.", file=sys.stderr)
        print("See monitor/alert-checker/SKILL.md for schema.", file=sys.stderr)
        sys.exit(1)

    # Check if any positions have alert_conditions
    content = holdings_file.read_text()
    if "alert_conditions" not in content:
        print("No alert_conditions found in holdings.yaml. Nothing to check.")
        sys.exit(0)

    today = date.today()
    now = datetime.now().strftime("%H:%M")
    month_str = today.strftime("%Y-%m")
    date_str = today.strftime("%Y-%m-%d")
    output_dir = notes_dir / "portfolio" / "alerts" / month_str
    output_file = output_dir / f"{date_str}-alerts.md"

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Alert Checker - {date_str} {now}")
    print(f"Holdings: {holdings_file}")
    print(f"Output (if alerts fire): {output_file}")
    print()
    print("To run this check, invoke the agent with:")
    print("  'Run alert checker using monitor/alert-checker skill'")
    print()


if __name__ == "__main__":
    main()
