# Bursa technical analysis

## Purpose

Takes the computed indicators from `data/price-history` and produces a technical assessment for Bursa Malaysia equities. Key differences from US technical analysis: weekly charts are preferred (more reliable given lower liquidity), volume confirmation is required for all signals, stages take longer to develop, and stops must be wider to accommodate low-liquidity whipsaws.

This skill interprets. It never fetches raw data itself.

## Input

Reads from scratch: `$ISK_NOTES/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/price-history.md`

## Output format

Write to scratch at: `$ISK_NOTES/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/bursa-technical.md`

```markdown
---
ticker: 1155
skill: bursa-technical
date: 2024-03-15
status: complete | partial | unavailable
---

## Technical verdict

**Trend: bullish | bearish | neutral**
**Volume confirmed: yes | no**

<one paragraph summarizing the technical picture with Bursa-specific context>

## Weekly chart preference

- Weekly trend: uptrend | downtrend | sideways
- Weekly stage: <Weinstein stage from weekly perspective>
- Weekly MA structure: <bullish stacking / bearish stacking / mixed>
- Daily vs weekly alignment: <confirming / diverging>
- Note: Weekly signals take priority for Bursa given low daily liquidity

## Stage identification

- Current stage: Stage 1 | 2 | 3 | 4 (or transition)
- Stage confidence: high | medium | low
- Stage development speed: <Bursa stages develop 1.5-2x slower than US due to lower volume>
- Reasoning: <what confirms this reading>

## Volume confirmation

- Average daily volume (50d): X,XXX,XXX shares
- Average daily value (50d): RM X.XM
- Liquidity classification: liquid (>RM5M/day) | moderate (RM1-5M) | illiquid (<RM1M)
- Volume confirming trend? yes | no
- Recent volume events: <any unusual spikes or dry-ups>

### Volume rules for Bursa

- Breakouts without volume are unreliable. Require at least 1.5x average volume for valid breakout.
- Low-liquidity stocks (<RM1M daily) can have false signals. Widen all stops by 50%.
- Institutional accumulation shows as gradual volume increase over weeks (not single-day spikes).

## Key levels

| Level | Price (RM) | Type | Reasoning |
|-------|-----------|------|-----------|
| Resistance 1 | X.XX | Near-term | <why> |
| Resistance 2 | X.XX | Major | <why> |
| Support 1 | X.XX | Near-term | <why> |
| Support 2 | X.XX | Major | <why> |

### Bursa-specific level notes

- Round sen levels (RM1.00, RM5.00, RM10.00) act as strong psychological S/R
- Institutional accumulation zones visible as price floors with steady volume
- IPO price often acts as long-term support for newer listings

## Moving average structure

- Price vs 50 SMA: above/below by X%
- Price vs 200 SMA: above/below by X%
- MA slope assessment: <rising/flat/falling>
- Weekly 20 MA: <most important MA for Bursa weekly traders>

## Entry and exit zones

### Suggested entry zone

- Aggressive: RM X.XX - RM X.XX (<reasoning, must have volume confirmation>)
- Conservative: RM X.XX - RM X.XX (<reasoning, breakout with volume required>)

### Stop loss zone

- Tight stop: RM X.XX (<wider than US equivalent, 8-12% from entry>)
- Wide stop: RM X.XX (<below major support, 15-20% for position trades>)

### Bursa stop loss notes

- Stops must be wider than US equivalents due to low liquidity whipsaws
- Minimum sensible stop for liquid stocks: 8% from entry
- Minimum sensible stop for illiquid stocks: 12-15% from entry
- Use weekly close below level, not intraday wick, for stop triggers
- Avoid stocks where the required stop exceeds your risk tolerance

## Relative strength vs KLCI

- RS vs ^KLSE (6mo): +/-X.X%
- RS trend: improving | deteriorating | flat
- Sector RS: <is the sector outperforming or underperforming KLCI?>

## Active signals

<from price-history, with Bursa-specific interpretation>

### Low-liquidity awareness

- If daily value <RM1M: flag as "thin stock, signals less reliable"
- If bid-ask spread is wide: flag as "execution risk, slippage expected"
- Adjust conviction downward for illiquid names regardless of other signals

## Data gaps

<what could not be assessed>
```

## Analysis framework

1. **Weekly chart preference.** Daily charts for Bursa stocks with <RM5M daily turnover produce too many false signals. The weekly chart smooths noise and reveals true trends. Use daily for timing entry/exit but weekly for direction.

2. **Volume confirmation is mandatory.** Every bullish signal (breakout, MA cross, stage transition) must be confirmed by above-average volume. Without volume, the move is suspect and likely to reverse. This is more critical for Bursa than US because institutional flow is more concentrated.

3. **Wider stop bands.** Bursa stocks gap and whipsaw more due to lower liquidity and wider spreads. A stop at -5% (normal for US) will get triggered by noise on Bursa. Use -8% minimum for liquid names, -12% for mid-cap, -15% for small-cap.

4. **Stage development speed.** Bursa stocks move slower through Weinstein stages. A Stage 1 base that takes 3 months in the US may take 6 months on Bursa. Patience is required. Premature entry into suspected Stage 2 transitions is a common trap.

5. **Institutional footprint.** When EPF, PNB, or large GLICs accumulate, it shows as sustained buying pressure over weeks (not single-day spikes). Look for gradual price floor formation with steady volume. When institutions distribute, they sell slowly to avoid moving price.

6. **Relative strength vs KLCI.** A stock outperforming the KLCI is attracting relative capital flow. A stock underperforming even as KLCI rises is likely seeing institutional exits.

## Error handling

- If price-history scratch is `unavailable`, write `status: unavailable`.
- If price-history is `partial` (insufficient for 200 MA), note limited analysis and focus on what's available.
- If volume data seems unreliable (common for very small caps), flag it and lower confidence.
- For stocks listed less than 1 year, long-term stage analysis is not possible. Focus on short-term momentum.

## Dependencies

- `data/price-history` - provides all price and indicator data (reads its scratch)
