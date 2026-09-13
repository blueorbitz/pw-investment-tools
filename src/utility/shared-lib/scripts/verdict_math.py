#!/usr/bin/env python3
"""Verdict math: factor strength labels in, composite + conviction + weights out.

The LLM labels each factor (see utility/shared-lib/verdict_rubric.md); this
script does all scoring arithmetic: baseline weights, bounded regime
multipliers, missing-input redistribution, composite score, and conviction.

Usage:
    python verdict_math.py --market US \
        --label valuation=2 --label technical=2 --label macro=0 --label sentiment=1

    python verdict_math.py --market Crypto \
        --label technical=1 --label onchain=2 --label macro=0 --label valuation=-1 \
        --regime-risk risk-off --volatility high-vol --driver macro-driven \
        --data-quality complete --volume-confirmed --cap Medium
"""

import argparse
import json
import sys

BASELINE_WEIGHTS = {
    "US": {"valuation": 30, "technical": 30, "macro": 20, "sentiment": 20},
    "Bursa": {"valuation": 35, "technical": 25, "macro": 25, "sentiment": 15},
    "Crypto": {"technical": 25, "onchain": 25, "macro": 25, "valuation": 15, "sentiment": 10},
}

# Crypto treats on-chain as its own factor; equities fold derivatives into technical.
OVERRIDE_ELIGIBLE = {
    "US": {"valuation", "technical"},
    "Bursa": {"valuation", "technical"},
    "Crypto": {"onchain", "technical"},
}

HIGH_THRESHOLD = 1.2
MEDIUM_THRESHOLD = 0.5
REGIME_BOUND_PP = 10
FACTOR_LABELS = {-2: "strong bearish", -1: "mild bearish", 0: "neutral",
                 1: "mild bullish", 2: "strong bullish"}
CONVICTION_ORDER = ["Low", "Medium", "High"]


def apply_regime(baseline, market, risk, volatility, driver):
    """Bounded regime multipliers: shift, clamp to +/-10pp, sentiment never
    raised, renormalize to 100%. Returns (weights, notes)."""
    weights = dict(baseline)
    shifts = {}
    if driver == "macro-driven":
        shifts["macro"] = shifts.get("macro", 0) + 10
    if driver == "stock-driven":
        anchored = "onchain" if market == "Crypto" else "valuation"
        shifts[anchored] = shifts.get(anchored, 0) + 10
    if volatility == "high-vol":
        shifts["technical"] = shifts.get("technical", 0) + 10
        shifts["sentiment"] = shifts.get("sentiment", 0) - 10
    if risk == "risk-off":
        shifts["macro"] = shifts.get("macro", 0) + 5
    if risk == "risk-on":
        shifts["technical"] = shifts.get("technical", 0) + 5

    for factor, shift in shifts.items():
        if factor not in weights:
            continue
        target = weights[factor] + shift
        # Bound: never more than +/-10pp from baseline.
        target = max(baseline[factor] - REGIME_BOUND_PP,
                     min(baseline[factor] + REGIME_BOUND_PP, target))
        # Sentiment is never raised by a regime shift.
        if factor == "sentiment":
            target = min(target, baseline[factor])
        weights[factor] = target

    notes = []
    total = sum(weights.values())
    if total != 100:
        # Renormalize, but never push past the bound or raise sentiment.
        factor_scale = total / 100.0
        for factor in weights:
            if shifts.get(factor) or factor == "sentiment":
                continue  # already shifted or protected: don't scale further
            weights[factor] = weights[factor] / factor_scale
        # One clamp pass in case renormalization pushed a shifted factor out of bounds.
        for factor in weights:
            if factor == "sentiment":
                weights[factor] = min(weights[factor], baseline[factor])
            weights[factor] = max(baseline[factor] - REGIME_BOUND_PP,
                                  min(baseline[factor] + REGIME_BOUND_PP, weights[factor]))
        notes.append("weights renormalized to 100% after regime shifts")

    _resolve_rounding(weights)
    return weights, notes


def _resolve_rounding(weights):
    """Round to one decimal; put any rounding residue on the largest weight."""
    for factor in weights:
        weights[factor] = round(weights[factor], 1)
    residual = round(100 - sum(weights.values()), 1)
    if residual:
        largest = max(weights, key=weights.get)
        weights[largest] = round(weights[largest] + residual, 1)


def apply_missing_inputs(weights, labels, missing):
    """Drop missing factors, redistribute their weight proportionally."""
    notes = []
    for factor in missing:
        if factor in weights:
            weights.pop(factor)
            labels.pop(factor, None)
            remaining = sum(weights.values())
            if remaining > 0:
                for f in weights:
                    weights[f] = weights[f] / remaining * 100
            notes.append(f"{factor} missing: weight redistributed proportionally")
    _resolve_rounding(weights)
    return notes


def compute_composite(labels, weights):
    composite = sum(labels.get(f, 0) * w for f, w in weights.items()) / 100.0
    return round(composite, 2)


def compute_conviction(composite, labels, weights, market, data_quality,
                       volume_confirmed, notes):
    direction = 1 if composite > 0 else (-1 if composite < 0 else 0)
    aligned = sum(1 for f, s in labels.items()
                  if s != 0 and (s > 0) == (direction > 0) and direction != 0)
    opposite_extreme = any(
        (s == -2 and direction > 0) or (s == 2 and direction < 0) for s in labels.values()
    )
    magnitude = abs(composite)

    if (magnitude >= HIGH_THRESHOLD and aligned >= 3 and not opposite_extreme
            and data_quality == "complete"):
        conviction = "High"
    elif magnitude >= MEDIUM_THRESHOLD:
        conviction = "Medium"
    else:
        conviction = "Low"

    if conviction == "Low" and aligned >= 2 and direction != 0 and magnitude >= MEDIUM_THRESHOLD:
        conviction = "Medium"  # split-but-moderate resolves to Medium, not Low

    # Single-factor override: one dominant eligible factor escalates one level.
    if conviction in ("Low", "Medium") and not opposite_extreme and data_quality == "complete":
        for factor, score in labels.items():
            if factor not in OVERRIDE_ELIGIBLE[market] or abs(score) != 2:
                continue
            if factor == "technical" and not volume_confirmed:
                continue
            if direction != 0 and (score > 0) != (direction > 0):
                continue
            idx = CONVICTION_ORDER.index(conviction)
            conviction = CONVICTION_ORDER[min(idx + 1, len(CONVICTION_ORDER) - 1)]
            notes.append(f"single-factor override on {factor} escalated conviction")
            break

    return conviction, aligned, opposite_extreme


def main():
    parser = argparse.ArgumentParser(description="Verdict scoring math")
    parser.add_argument("--market", required=True, choices=sorted(BASELINE_WEIGHTS))
    parser.add_argument("--label", action="append", default=[],
                        help="factor=score, e.g. valuation=2 (repeatable)")
    parser.add_argument("--missing", nargs="*", default=[],
                        help="factors with no data (weights redistributed)")
    parser.add_argument("--regime-risk", default="neutral",
                        choices=["risk-on", "neutral", "risk-off"])
    parser.add_argument("--volatility", default="normal", choices=["high-vol", "normal"])
    parser.add_argument("--driver", default="unknown",
                        choices=["macro-driven", "stock-driven", "unknown"],
                        help="unknown means no regime classified: baseline weights")
    parser.add_argument("--data-quality", default="complete", choices=["complete", "partial"])
    parser.add_argument("--volume-confirmed", action="store_true",
                        help="technical signals are volume-confirmed (enables override)")
    parser.add_argument("--cap", default="High", choices=["Low", "Medium", "High"],
                        help="conviction ceiling, e.g. Medium on a gate-FAIL speculative track")
    args = parser.parse_args()

    baseline = dict(BASELINE_WEIGHTS[args.market])
    labels = {}
    for item in args.label:
        try:
            factor, score = item.split("=")
            score = int(score)
        except ValueError:
            parser.error(f"--label expects factor=score, got {item!r}")
        if factor not in baseline:
            parser.error(f"unknown factor {factor!r} for market {args.market}")
        if score not in FACTOR_LABELS:
            parser.error(f"score must be an integer -2..+2, got {score!r}")
        labels[factor] = score

    weights, notes = apply_regime(baseline, args.market, args.regime_risk,
                                  args.volatility, args.driver)
    weights_before_missing = dict(weights)
    notes += apply_missing_inputs(weights, labels, args.missing)

    for factor in weights:
        labels.setdefault(factor, 0)

    composite = compute_composite(labels, weights)
    conviction, aligned, opposite_extreme = compute_conviction(
        composite, labels, weights, args.market, args.data_quality,
        args.volume_confirmed, notes)

    if conviction != args.cap and CONVICTION_ORDER.index(conviction) > CONVICTION_ORDER.index(args.cap):
        conviction = args.cap
        notes.append(f"conviction capped at {args.cap}")

    action = "Hold" if abs(composite) < MEDIUM_THRESHOLD else ("Buy" if composite > 0 else "Sell")

    print(json.dumps({
        "market": args.market,
        "labels": {f: FACTOR_LABELS[s] for f, s in sorted(labels.items())},
        "weights_baseline": baseline,
        "weights_applied": weights,
        "weights_after_regime": weights_before_missing,
        "regime": {"risk": args.regime_risk, "volatility": args.volatility, "driver": args.driver},
        "composite_score": composite,
        "composite_label": FACTOR_LABELS[max(-2, min(2, round(composite)))],
        "aligned_factors": aligned,
        "opposite_extreme": opposite_extreme,
        "action": action,
        "conviction": conviction,
        "conviction_cap": args.cap,
        "data_quality": args.data_quality,
        "notes": notes,
    }, indent=2))


if __name__ == "__main__":
    main()
