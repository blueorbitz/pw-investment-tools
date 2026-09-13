---
name: valuation-baseline
description: Sets the fair valuation multiple baseline for a stock from its own quote and the current rate environment, instead of a fixed multiple table. Consumed by the quality gate's dispatch B as the intrinsic-value anchor.
---

The buffett valuation reference carries a static multiple table (wide moat
20–25x, narrow 8–12x...). That table ignores the two things that move a fair
multiple most: the risk-free rate and the company's own growth. This skill
computes the baseline from the stock's quote instead, so the intrinsic-value
judgment in dispatch B starts from current numbers, not a fixed prior.

## Scope

Any equity with quote data (US and Bursa). Crypto is out of scope — tokenomics
use `crypto-valuation`.

## Input

From the ticker's scratch (already written by the shared data fetch):
- `quote.md` / quote_fetch output: price, forward PE, trailing PE, FCF yield, dividend yield
- `price_history.md` / fundamentals scratch: growth estimate (revenue or EPS trend)
- Risk-free rate: 10Y yield from the `us-macro` scratch (US) or the local
  10-year government bond yield (Bursa, via web search or `bursa-macro` scratch)
- Moat width: judged in dispatch B from `references/03-business-moat.md`

## Workflow

Run the script with the quote metrics:

```bash
python <ISK_ROOT>/analysis/valuation-baseline/scripts/baseline_calc.py \
  --price 495.63 --forward-pe 21.0 --trailing-pe 27.6 \
  --risk-free 4.2 --growth 10 --moat wide \
  --fcf-yield 0.45 --dividend-yield 0.73
```

The output gives:

- `fair_pe_range` - the multiple band justified by rates, growth, and moat
- `forward_eps` and `fair_value` - price-implied intrinsic value at the range midpoint
- `margin_of_safety_pct` and `verdict` - cheap (MOS >= 30%) | fair (10–30%) | expensive (< 10%)
- `notes` - bounded caps applied (growth capped at 10%/yr, PE clamped to 6–35x) and
  cross-check warnings (earnings-yield spread vs bonds below 2pp, FCF yield below the
  risk-free rate)

Growth estimates: use the forward growth the analysis in hand supports
(EPS revision trend, revenue CAGR). The script caps it at 10%/yr — above that
you are speculating, and the multiple ceiling handles the rest. If no growth
estimate exists, pass 0 and say so in the dispatch B output.

## Output

Dispatch B consumes this as the intrinsic-value anchor:

```markdown
## Valuation baseline

- Fair PE range: 17.9x – 23.8x (risk-free 4.2%, growth 10%, wide moat)
- Forward EPS: $23.60 -> fair value $494.60 at midpoint
- MOS at current price: +0.2% -> verdict: expensive
- Cross-check: earnings yield 3.6% vs risk-free 4.2% (spread -0.6pp — not compensated)
```

Copy the numbers verbatim into the `us-valuation.md` scratch — do not recompute
or round differently. When the margin-of-safety tiers from
`quality-gate/references/06-valuation-capital.md` are applied (20–50% discount
by uncertainty), combine: the baseline gives the fair value; reference 06 gives
how big a discount that fair value requires.

## Error handling

- Missing forward PE: the script still returns the fair PE range; dispatch B
  applies it to its own earnings estimate and states the method used.
- Missing risk-free rate: use 4.5% default and note the assumption in Gaps.
- Missing everything (no quote): report `status: unavailable`; dispatch B falls
  back to the static table in `references/06-valuation-capital.md` and says so.

## Dependencies

- `data/fundamentals/scripts/quote_fetch.py` - quote metrics (upstream, already written)
- `analysis/quality-gate` - consumer; dispatch B embeds this baseline in the US valuation factor
- `data/us-macro` / `data/bursa-macro` - risk-free rate source (when available)
