#!/usr/bin/env python3
"""Quality-gate scripted checks: threshold screening from buffett reference 05.

Takes the numeric metrics gathered from fundamentals scratch (annual statements
via financials_fetch.py, quote via quote_fetch.py) and returns a per-check
pass/warn/fail verdict plus an overall tier: quality-pass, speculative, or
reject. The quick-screen judgment questions live in the skill's SKILL.md; this
script covers only the mechanical thresholds.

Thresholds (from references/05-financial-metrics.md):
- ROE: pass >= 15%, warn >= 10%, fail < 10% (leverage-inflated ROE is a trap)
- Net margin: pass >= 10%, warn >= 5%, fail < 5%
- Debt/EBITDA: pass <= 2x, warn <= 3x, fail > 3x
- Cash conversion (OCF/net income): pass >= 90%, warn >= 70%, fail < 70%
- Dividend stability (years grown/stable): pass >= 10, warn >= 3, fail < 3
- EPS trend: pass "up", warn "flat", fail "down"

Usage:
    python gate_checks.py --roe 18 --net-margin 15 --debt-to-ebitda 1.5 \
        --cash-conversion 95 --dividend-years 12 --eps-trend up

Omit a metric when data is unavailable: it is reported as "unknown" and does
not fail the gate, but the tier degrades toward speculative if too much is
unknown.
"""

import argparse
import json
import sys

CHECKS = [
    ("roe", "ROE >= 15%", "warn if >= 10, fail < 10", "pct"),
    ("net_margin", "Net margin >= 10%", "warn if >= 5, fail < 5", "pct"),
    ("debt_to_ebitda", "Debt/EBITDA <= 2x", "warn if <= 3, fail > 3", "x"),
    ("cash_conversion", "Cash conversion >= 90%", "warn if >= 70, fail < 70", "pct"),
    ("dividend_years", "Dividend grown/stable >= 10y", "warn if >= 3, fail < 3", "y"),
    ("eps_trend", "EPS trend up", "warn if flat, fail if down", "categorical"),
]


def check_roe(v):
    if v >= 15: return "pass"
    if v >= 10: return "warn"
    return "fail"


def check_net_margin(v):
    if v >= 10: return "pass"
    if v >= 5: return "warn"
    return "fail"


def check_debt(v):
    if v <= 2: return "pass"
    if v <= 3: return "warn"
    return "fail"


def check_cash_conversion(v):
    if v >= 90: return "pass"
    if v >= 70: return "warn"
    return "fail"


def check_dividend_years(v):
    if v >= 10: return "pass"
    if v >= 3: return "warn"
    return "fail"


def check_eps_trend(v):
    v = str(v).lower()
    if v == "up": return "pass"
    if v == "flat": return "warn"
    if v == "down": return "fail"
    return "unknown"


CHECK_FNS = {
    "roe": check_roe,
    "net_margin": check_net_margin,
    "debt_to_ebitda": check_debt,
    "cash_conversion": check_cash_conversion,
    "dividend_years": check_dividend_years,
    "eps_trend": check_eps_trend,
}


def main():
    parser = argparse.ArgumentParser(description="Quality-gate scripted threshold checks")
    parser.add_argument("--roe", type=float, help="ROE percent (10y avg preferred)")
    parser.add_argument("--net-margin", type=float, help="Net margin percent")
    parser.add_argument("--debt-to-ebitda", type=float, help="Debt to EBITDA ratio")
    parser.add_argument("--cash-conversion", type=float, help="OCF / net income, percent")
    parser.add_argument("--dividend-years", type=float, help="Years of grown/stable dividend")
    parser.add_argument("--eps-trend", choices=["up", "flat", "down"], help="EPS trend direction")
    args = parser.parse_args()

    values = {
        "roe": args.roe,
        "net_margin": args.net_margin,
        "debt_to_ebitda": args.debt_to_ebitda,
        "cash_conversion": args.cash_conversion,
        "dividend_years": args.dividend_years,
        "eps_trend": args.eps_trend,
    }

    results = []
    counts = {"pass": 0, "warn": 0, "fail": 0, "unknown": 0}
    for key, rule, _, _ in CHECKS:
        value = values[key]
        if value is None:
            status = "unknown"
            shown = None
        else:
            status = CHECK_FNS[key](value)
            shown = value
        counts[status] += 1
        results.append({"check": key, "value": shown, "rule": rule, "status": status})

    # Tier: rejects need hard failures; unknowns degrade toward speculative.
    if counts["fail"] >= 2:
        tier = "reject"
    elif counts["fail"] == 1:
        tier = "speculative"
    elif counts["unknown"] >= 3:
        tier = "speculative"
    elif counts["warn"] >= 2:
        tier = "speculative"
    else:
        tier = "quality-pass"

    print(json.dumps({
        "tier": tier,
        "counts": counts,
        "checks": results,
    }, indent=2))


if __name__ == "__main__":
    main()
