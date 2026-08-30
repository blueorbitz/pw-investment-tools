---
name: bursa-sentiment
description: Assesses sentiment for Bursa Malaysia equities by evaluating filings, insider transaction patterns, news from The Edge and i3investor, and institutional flow signals.
---

## Input

Reads from scratch:
- `$ISK_NOTES/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/bursa-announcements.md` (primary)

May invoke `utility/web-search` for: The Edge Markets articles, i3investor discussions, analyst reports.

## Output format

Write to scratch at: `$ISK_NOTES/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/bursa-sentiment.md`

```markdown
---
ticker: 1155
skill: bursa-sentiment
date: 2024-03-15
status: complete | partial | unavailable
---

## Sentiment verdict

**Overall: bullish | bearish | neutral**
**Confidence: high | medium | low**

## Insider signal

- Net activity (30d): buying | selling | mixed | quiet
- Signal strength: strong | moderate | weak
- Key observation: <e.g., "Major shareholder increased stake by 2M shares at RM9.50">
- Institutional vs personal: <EPF/PNB buying is different from director selling for personal reasons>
- Interpretation: <what this pattern implies for this stock>

### Insider interpretation for Bursa

- Director/CEO buying in open market is a strong signal (same as US)
- EPF/Persaraan increasing stake is mild positive (routine rebalancing vs conviction buy)
- Major shareholder buying during privatization speculation is different from organic conviction
- Disposed for "estate planning" or "personal financial" is noise, ignore

## Institutional flow signal

- Foreign flow direction: net buying | net selling | neutral
- Domestic institution direction: accumulating | distributing | neutral
- Signal: <foreign buying of a specific stock = strong positive / selling = headwind>
- Context: <is this stock-specific or part of broad market flow?>

## News tone

- Primary sources checked: The Edge, i3investor, Bursa announcements
- Dominant narrative: <what the market is focused on for this stock>
- Tone: positive | negative | neutral | mixed
- Key items:
  - <news item 1 with source>
  - <news item 2 with source>
  - <news item 3 with source>

### The Edge / i3investor context

- Recent coverage frequency: frequent | occasional | rare
- Coverage tone: promotional | analytical | critical
- Retail investor sentiment (i3investor): bullish | bearish | divided
- Note: i3investor is retail-heavy. Extreme retail bullishness can be a contrarian warning.

## Corporate action signals

- Recent quarterly results: beat | miss | in-line (if within 90 days)
- Dividend announcement: <any recent declaration, special dividend, or cut>
- Share buyback activity: active | dormant
- Corporate action pending: <any M&A, privatization, rights issue in play>

## Contrarian check

- Is sentiment extreme? <If retail is extremely bullish on i3investor and insiders are selling, flag>
- Privatization speculation: <if market is pricing in a privatization that may not materialize, flag risk>
- "Hot stock" warning: <if coverage frequency spiked recently, retail may be late>

## Data gaps

<what could not be assessed>
```

## Analysis framework

1. **Insider transaction patterns.** The most reliable signal for Bursa. Malaysia has strong disclosure requirements for substantial shareholders. Focus on:
   - Open market purchases by directors (strong buy signal)
   - Major shareholder increasing above mandatory offer threshold
   - Cluster selling by multiple insiders (distribution warning)
   - Distinguish EPF rebalancing (routine) from conviction positions (meaningful)

2. **Institutional vs retail.** Foreign institutional flow is the strongest price driver for KLCI components. When foreigners buy a stock, it tends to outperform. Domestic institutions (EPF, PNB) provide a floor but don't drive momentum. Retail flow (visible on i3investor) is usually late and a contrarian indicator.

3. **News from The Edge Markets.** Malaysia's primary financial newspaper. Coverage frequency itself is a signal: stocks getting frequent Edge coverage are in play. Tone matters: investigative pieces on governance are red flags.

4. **i3investor as contrarian.** The i3investor forum is primarily retail investors. When a stock's i3 thread is extremely active and bullish, the easy money has been made. When a thread is dead and sentiment is bearish, it may be bottoming. Use as contrarian, not confirming, signal.

5. **Corporate actions as catalysts.** Bursa corporate actions (privatization offers, special dividends, M&A) can be material catalysts. A stock with privatization rumors trades differently. Factor this into sentiment but note the binary risk.

## Error handling

- If bursa-announcements scratch is `unavailable`, rely on web search for insider data and news. Mark `status: partial`.
- If web search also returns nothing, produce minimal output noting data limitations. Mark `status: partial`.
- For less-covered small caps, sentiment data will be sparse. Note "limited coverage" and lower confidence.
- Never fabricate insider activity. If data is not available, say "insider data not available for this period."

## Dependencies

- `data/bursa-announcements` - provides insider transactions and corporate actions (reads its scratch)
- `utility/web-search` - for The Edge, i3investor news, analyst reports
