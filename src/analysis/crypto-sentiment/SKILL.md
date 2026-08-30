---
name: crypto-sentiment
description: Assesses sentiment for a crypto token by evaluating social buzz, governance activity, developer engagement, and narrative momentum.
---

## Input

- Reads from any available crypto scratch files for context
- Primarily invokes `utility/web-search` for: social buzz, governance proposals, GitHub activity, CT (Crypto Twitter) consensus

## Output format

Write to scratch at: `$ISK_NOTES/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/crypto-sentiment.md`

```markdown
---
ticker: ETH
skill: crypto-sentiment
date: 2024-03-15
status: complete | partial | unavailable
---

## Sentiment verdict

**Overall: bullish | bearish | neutral**
**Confidence: high | medium | low**

## Social buzz

- Intensity: high | moderate | low | dead
- Tone: euphoric | optimistic | neutral | fearful | capitulation
- Trend (vs 30d ago): increasing | fading | stable
- Dominant discussion topics: <what people are talking about regarding this token>
- Notable influencer sentiment: <any significant calls from well-followed accounts>

## Narrative momentum

- Current narrative: <what story is driving interest, e.g., "ETH ETF approval speculation", "Solana DePIN adoption">
- Narrative strength: gaining traction | peaking | fading | none
- Narrative longevity estimate: <is this a multi-month theme or a flash-in-the-pan?>
- Competing narratives: <is capital rotating to competing tokens/narratives?>

## Developer activity

- GitHub commit frequency (30d): high | moderate | low | dead
- Notable development updates: <protocol upgrades, new features, partnerships>
- Developer sentiment signal: active development = team is building (bullish), declining commits = potential abandonment risk

## Governance

- Recent proposals: <any significant governance votes>
- Governance impact: <could proposals affect token value? e.g., fee switch, buyback, treasury spend>
- Community alignment: <is community united or fragmented on direction?>

## CT (Crypto Twitter) consensus

- CT consensus direction: bullish | bearish | mixed
- Contrarian indicator: <when CT is unanimously bullish, tops are near; when unanimously bearish, bottoms are near>
- Current positioning: <is CT already positioned, or is there dry powder?>

## Contrarian check

- Sentiment extreme detected: yes | no
- If yes: <extreme bullishness = crowded trade risk / extreme bearishness = potential bottom>
- Fear & Greed context: <current reading and what it implies>

## Data gaps

<what could not be assessed>
```

## Analysis framework

1. **Social buzz as attention proxy.** High social volume with positive tone = momentum. High social volume with negative tone = panic or controversy. Low social volume = no one cares (this can be bullish if fundamentals are strong, as it means no attention premium yet).

2. **Narrative momentum.** Crypto runs on narratives. A token attached to a gaining narrative (AI, RWA, DePIN) gets bid even without fundamental improvement. A token whose narrative peaked (previous cycle's star) faces headwinds. Identify where in the narrative cycle the token sits.

3. **Developer activity.** Active GitHub repos signal a team that's building. Declining activity, especially combined with insider token unlocks, signals potential abandonment. Not all tokens need active development (BTC doesn't), so weight this by token type.

4. **Governance as catalyst.** Major governance proposals (fee switches, buybacks, merge upgrades) can be material catalysts. A fee switch proposal for a high-revenue protocol can reprice the token overnight.

5. **CT consensus as contrarian indicator.** Crypto Twitter consensus is one of the best contrarian indicators. When everyone on CT is bullish and posting targets, the move is usually close to over. When CT is calling for much lower prices and sentiment is capitulatory, bottoms tend to form.

### Signal weighting

| Source | Weight | Rationale |
|--------|--------|-----------|
| Narrative momentum | 30% | Crypto is narrative-driven |
| CT consensus (contrarian) | 25% | Historically strong contrarian signal |
| Social buzz intensity | 20% | Attention proxy |
| Developer activity | 15% | Long-term health |
| Governance | 10% | Occasional catalyst |

## Error handling

- Sentiment data relies heavily on web search. If search returns nothing useful, report `status: partial` with available data.
- For smaller tokens, social data may be scarce. Note "low social coverage" and reduce confidence.
- Developer activity for closed-source projects or projects with private repos cannot be assessed. Note it.
- Never fabricate sentiment signals. If you cannot find signal, say "insufficient data to assess."
- CT consensus is directional guidance, not precise. One or two searches to gauge tone is sufficient.

## Dependencies

- `utility/web-search` - primary source for social, governance, and narrative data
