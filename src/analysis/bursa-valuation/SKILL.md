# Bursa valuation analysis

## Purpose

Takes the structured financial data from `data/fundamentals` (Bursa route) and market context from `data/bursa-fundamentals` to produce a valuation assessment for Bursa Malaysia equities. Dividend yield is weighted higher than for US equities. The Malaysian market has a strong income-investor culture, so sustainable dividend payers command a premium.

This skill interprets. It never fetches raw data itself.

## Input

Reads from scratch:
- `~/notes/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/fundamentals.md` (required)
- `~/notes/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/bursa-fundamentals.md` (optional, for peer context)

## Output format

Write to scratch at: `~/notes/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/bursa-valuation.md`

```markdown
---
ticker: 1155
skill: bursa-valuation
date: 2024-03-15
status: complete | partial | unavailable
---

## Valuation verdict

**Assessment: cheap | fair | expensive**

<one paragraph reasoning, referencing specific numbers and Bursa market context>

## Dividend assessment

- Current dividend yield: X.X%
- DPS trend (5Y): growing | stable | declining | erratic
- Payout ratio (estimated): XX%
- Dividend sustainability: high | medium | low
- Yield vs sector median: above | in-line | below
- Yield vs FD rate: attractive spread (>2%) | marginal (1-2%) | unattractive (<1%)
- DRP (Dividend Reinvestment Plan): active? discount?

### Dividend quality scoring

- Consecutive years of payment: X years
- Consecutive years of growth: X years
- Coverage ratio (earnings/dividend): X.Xx
- Assessment: <reliable income stock / growth-and-income / speculative yield>

## Multiples analysis

- PE (trailing): XX.X vs sector median XX.X
- PB ratio: X.X vs sector median X.X
- Interpretation: <premium/discount to sector and why>

## Quality scoring

- ROE: XX% (trend: stable | improving | deteriorating)
- ROE consistency (5Y): <stable above 10% is quality / volatile is lower quality>
- Revenue growth (3Y CAGR): X%
- Net margin: XX% (trend)
- Cash vs debt: net cash RM X.XB | net debt RM X.XB
- Gearing ratio: XX% (<30% healthy, 30-60% moderate, >60% elevated)

## Peer comparison

| Stock | PE | PB | DY% | ROE% | Market Cap |
|-------|----|----|-----|------|-----------|
| <target> | XX | X.X | X.X | XX | RM X.XB |
| Peer 1 | XX | X.X | X.X | XX | RM X.XB |
| Peer 2 | XX | X.X | X.X | XX | RM X.XB |

- Relative to peers: <premium / discount / in-line>
- Premium/discount justified? <reasoning>

## Moat assessment (MY context)

- Market position: <#1, #2 in sector? oligopoly? regulated?>
- Competitive advantages: <brand, licenses, network effects, scale, GLCs>
- Bursa-specific moats: <government-linked companies have policy tailwinds, banking licenses are scarce, plantation land is finite>

## Key risks to valuation

- <specific risk>
- <specific risk>

## Data gaps

<what could not be assessed>
```

## Analysis framework

1. **Dividend-focused framework.** For Bursa, dividend yield is the primary valuation anchor for blue chips. A stock yielding 5%+ with stable DPS and reasonable payout ratio is considered attractive. Compare yield against FD (fixed deposit) rate as the opportunity cost benchmark.

2. **Peer comparison within sector.** The KLCI is sector-concentrated (financials, plantations, utilities). Compare within sector, not cross-sector. A plantation stock at PE 15 may be expensive while a tech stock at PE 15 is cheap.

3. **Quality scoring for Malaysian context.** ROE consistency matters more than absolute level. A stable 12% ROE is better than volatile swings between 5% and 20%. Low gearing is prized because Malaysian companies sometimes have limited access to cheap refinancing.

4. **Moat in Malaysian context.** Government-linked companies (GLCs) have policy moats. Banking licenses are scarce (only 8 domestic banks). Plantation land cannot be replicated. Utility concessions provide visible earnings. Identify which moat type applies.

5. **PB ratio relevance.** PB is more relevant for Bursa (asset-heavy sectors: banks, plantations, property) than for US tech. A bank below PB 1.0 with stable ROE above cost of equity is classically cheap.

## Error handling

- If fundamentals scratch is `unavailable`, write `status: unavailable`.
- If fundamentals is `partial` (common for KLSE Screener), do what you can. PE and DY are the minimum for a useful assessment.
- If bursa-fundamentals (market overview) is missing, skip peer comparison or use general knowledge of sector multiples.
- Never invent financial data. If metrics are missing, say so.

## Dependencies

- `data/fundamentals` - provides individual stock financials (reads its scratch)
- `data/bursa-fundamentals` - provides market overview and peer context (optional)
