#!/usr/bin/env python3
"""Quote-aware valuation baseline: sets the fair multiple range for a stock.

Replaces fixed multiple tables with a baseline computed from the stock's own
quote and the current rate environment. The buffett reference 06 table
(wide moat 20-25x etc.) is a static prior; this adjusts it for:

- Risk-free rate: fair multiple falls as rates rise (earnings yield must
  compete with bonds).
- Forward earnings growth: higher justified growth, higher multiple
  (sustainable growth capped at 10%/yr - anything above is speculation).
- Moat width: ranges shift up for wide moats, down for narrow ones.

Method:
    r        = risk_free + 5.0            (equity premium, percentage points)
    g        = clamp(growth, 0, 10)
    base PE  = 100 / (r - g), clamped to [6, 35]
    range    = base PE x moat multipliers:
                 wide   [0.90, 1.20]
                 average[0.75, 1.00]
                 narrow [0.60, 0.85]
    forward EPS = price / forward_pe (when forward PE given)
    fair value  = range midpoint x forward EPS
    MOS         = (fair value - price) / fair value
    verdict     = cheap (MOS >= 30) | fair (10 <= MOS < 30) | expensive (< 10)

Cross-checks reported: earnings yield vs risk-free spread, FCF yield vs
risk-free. A spread below 2 points means equities are not compensating for
equity risk at the current price.

Usage:
    python baseline_calc.py --price 495.63 --forward-pe 21.0 --trailing-pe 27.6 \
        --risk-free 4.2 --growth 10 --moat wide --fcf-yield 0.45 --dividend-yield 0.73
"""

import argparse
import json
import sys

EQUITY_PREMIUM = 5.0
GROWTH_CAP = 10.0
PE_FLOOR, PE_CEILING = 6.0, 35.0

MOAT_RANGE = {
    "wide": (0.90, 1.20),
    "average": (0.75, 1.00),
    "narrow": (0.60, 0.85),
}


def main():
    parser = argparse.ArgumentParser(description="Quote-aware valuation baseline")
    parser.add_argument("--price", type=float, required=True, help="Current price")
    parser.add_argument("--forward-pe", type=float, help="Forward PE from quote_fetch")
    parser.add_argument("--trailing-pe", type=float, help="Trailing PE from quote_fetch")
    parser.add_argument("--risk-free", type=float, default=4.5,
                        help="Risk-free rate in %% (10Y yield; from us-macro scratch). Default 4.5")
    parser.add_argument("--growth", type=float, default=0.0,
                        help="Forward earnings growth estimate in %%/yr. Default 0")
    parser.add_argument("--moat", default="average", choices=sorted(MOAT_RANGE),
                        help="Moat width judged in dispatch B (references/03)")
    parser.add_argument("--fcf-yield", type=float, help="FCF yield in %% from quote_fetch")
    parser.add_argument("--dividend-yield", type=float, help="Dividend yield in %% from quote_fetch")
    args = parser.parse_args()

    notes = []
    g = max(0.0, min(GROWTH_CAP, args.growth))
    if args.growth > GROWTH_CAP:
        notes.append(f"growth estimate {args.growth}% capped at {GROWTH_CAP}% (sustainable-rate assumption)")

    r = args.risk_free + EQUITY_PREMIUM
    spread_rg = r - g
    if spread_rg <= 0:
        notes.append("growth >= required return: model degenerate, using ceiling multiple")
        base_pe = PE_CEILING
    else:
        base_pe = 100.0 / spread_rg
    base_pe = max(PE_FLOOR, min(PE_CEILING, base_pe))

    lo_mult, hi_mult = MOAT_RANGE[args.moat]
    fair_pe_low = round(max(PE_FLOOR, min(PE_CEILING, base_pe * lo_mult)), 1)
    fair_pe_high = round(max(PE_FLOOR, min(PE_CEILING, base_pe * hi_mult)), 1)

    fair_value = None
    mos = None
    verdict = None
    forward_eps = None
    if args.forward_pe and args.price:
        forward_eps = args.price / args.forward_pe
        mid_pe = (fair_pe_low + fair_pe_high) / 2.0
        fair_value = round(mid_pe * forward_eps, 2)
        if fair_value > 0:
            mos = round((fair_value - args.price) / fair_value * 100, 1)
            if mos >= 30:
                verdict = "cheap"
            elif mos >= 10:
                verdict = "fair"
            else:
                verdict = "expensive"
    else:
        notes.append("forward PE missing: fair PE range returned without a price-implied verdict")

    earnings_yield = round(100.0 / args.trailing_pe, 2) if args.trailing_pe else None
    ey_spread = round(earnings_yield - args.risk_free, 2) if earnings_yield else None
    if ey_spread is not None and ey_spread < 2:
        notes.append(f"earnings yield spread vs risk-free is {ey_spread}pp (< 2pp): equity not compensating for risk at this price")
        # Sanity bound: a "cheap" verdict while earnings yield trails bonds is
        # not honest. Cap it at "fair" and let dispatch B judge further.
        if verdict == "cheap":
            verdict = "fair"
            notes.append("verdict capped at fair: earnings yield spread below 2pp")

    fcf_spread = round(args.fcf_yield - args.risk_free, 2) if args.fcf_yield is not None else None
    if fcf_spread is not None and fcf_spread < 0:
        notes.append(f"FCF yield {args.fcf_yield}% is below the risk-free rate {args.risk_free}%")

    print(json.dumps({
        "risk_free_pct": args.risk_free,
        "required_return_pct": round(r, 2),
        "growth_used_pct": g,
        "moat": args.moat,
        "fair_pe_range": [fair_pe_low, fair_pe_high],
        "forward_eps": round(forward_eps, 2) if forward_eps else None,
        "fair_value": fair_value,
        "margin_of_safety_pct": mos,
        "verdict": verdict,
        "earnings_yield_pct": earnings_yield,
        "fcf_yield_pct": args.fcf_yield,
        "dividend_yield_pct": args.dividend_yield,
        "notes": notes,
    }, indent=2))


if __name__ == "__main__":
    main()
