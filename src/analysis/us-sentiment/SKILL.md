# US sentiment analysis

## Purpose

Takes the filing data from `data/us-filings` plus web search results and produces a sentiment assessment for US equities. Synthesizes insider behavior, institutional positioning, analyst revisions, options flow, and news tone into a net sentiment signal.

This skill interprets multiple data sources. It reads from scratch and invokes web search for analyst/news context.

## Input

Reads from scratch:
- `$ISK_NOTES/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/us-filings.md` (primary)
- May invoke `utility/web-search` for: analyst consensus, EPS revision data, recent news headlines

## Output format

Write to scratch at: `$ISK_NOTES/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/us-sentiment.md`

```markdown
---
ticker: MSFT
skill: us-sentiment
date: 2024-03-15
status: complete | partial | unavailable
---

## Sentiment verdict

**Overall: bullish | bearish | neutral**
**Confidence: high | medium | low**

## Insider signal

- Net activity: buying | selling | mixed | quiet
- Signal strength: strong | moderate | weak
- Key observation: <e.g., "CEO purchased $2M in open market, first buy in 3 years">
- Interpretation: <what this pattern typically implies>

## Institutional signal

- Net positioning: increasing | decreasing | stable
- Notable moves: <any significant new positions or exits by known funds>
- Signal strength: strong | moderate | weak

## Analyst revision direction

- Consensus rating: Buy | Hold | Sell (and count: X Buy, Y Hold, Z Sell)
- Recent revision trend: upgrades outpacing downgrades | downgrades outpacing | stable
- Price target trend: rising | falling | stable
- Notable calls: <any significant upgrades/downgrades from major firms>

## Options and positioning

- Unusual activity: <notable large trades or imbalances>
- Put/call context: <elevated puts = hedging/bearish, elevated calls = speculative/bullish>
- Interpretation: <what smart money positioning suggests>

## News tone

- Dominant narrative: <what the market is focused on for this stock>
- Tone: positive | negative | neutral | mixed
- Key headlines (last 30 days):
  - <headline 1 with source>
  - <headline 2 with source>
  - <headline 3 with source>

## Contrarian check

<if sentiment is extremely one-sided, flag potential contrarian opportunity. Extreme bullishness can signal crowded trade risk. Extreme bearishness near support can signal capitulation.>

## Data gaps

<what could not be assessed>
```

## Analysis framework

1. **Insider signal weight.** Insider buying is a stronger signal than insider selling. Officers sell for many reasons (diversification, taxes, estate planning) but rarely buy unless they believe in upside. Cluster buying (multiple insiders buying within weeks) is the strongest signal.

2. **Institutional signal.** 13F data is lagged by one quarter. Use it as directional context, not timing. Large fund initiating a new position is more notable than small trims to existing positions.

3. **Analyst revisions.** The direction of revisions matters more than the absolute target. Three upgrades in a month after a beat signals the street is catching up. Three downgrades after a miss signals deterioration not yet priced in.

4. **Options flow.** Large block trades (especially bought, not sold) from institutional players signal conviction. A surge in put buying ahead of earnings can signal hedging or informed bearishness. Context matters: is this hedging an existing long, or a directional bet?

5. **News tone.** Summarize the dominant narrative. Is the market focused on growth, regulatory risk, competitive threat, or a catalyst? The tone helps gauge whether expectations are high (vulnerable to disappointment) or low (setup for positive surprise).

6. **Contrarian check.** When all sentiment indicators align strongly in one direction, consider the contrarian read:
   - Everyone bullish + stock at highs = crowded trade risk
   - Everyone bearish + stock at lows = potential capitulation/bottom

## Error handling

- If `us-filings` scratch is `unavailable`, rely on web search alone for insider/institutional signals. Mark `status: partial`.
- If web search also fails, produce what you can from available data. At minimum, note "sentiment data unavailable" and mark `status: partial`.
- If only insider data is available (no analyst, no news), that's still worth reporting. Insider signal alone at partial confidence.
- Never invent sentiment data. If you cannot confirm analyst consensus, say "not available" rather than guessing.

## Dependencies

- `data/us-filings` - provides insider and institutional data (reads its scratch)
- `utility/web-search` - for analyst consensus, news headlines, EPS revision data
