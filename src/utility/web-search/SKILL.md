---
name: web-search
description: Wraps the agent's web search capability with guidelines for when to search, how to formulate queries, and how to format results. Keeps searches token-conscious by trimming and summarizing.
---

## When to use

Web search is a fallback, not a primary data source. Use it when:

1. A structured API returned incomplete or stale data and you need to fill a gap.
2. An analysis skill raises a follow-up question that numbers alone cannot answer (e.g., "Why did revenue drop 30% in Q3?" or "What's the narrative around this token?").
3. You need recent news, analyst commentary, or event context that no API covers.
4. The target market has no reliable free API (common for Bursa Malaysia macro data).

Do not use web search when:

- A data skill's script or API can answer the question with structured data.
- You're looking for price, volume, or indicator data (use `data/price-history` instead).
- You're looking for financial statements (use `data/fundamentals` instead).

## Input

The calling skill provides:

- `query` - a specific, focused search query (not a broad topic)
- `context` - why this search is needed (helps the agent judge relevance of results)
- `max_results` - how many results to inspect (default: 3, max: 5)

## Output format

Write results to scratch as a focused summary, not raw search dumps:

```markdown
---
ticker: <TICKER>
skill: web-search
date: YYYY-MM-DD
status: complete | partial | unavailable
query: "<the search query>"
---

## Key findings

- <finding 1 with source attribution>
- <finding 2 with source attribution>
- <finding 3 with source attribution>

## Sources

1. [<title>](<url>) - <one-line summary of what was useful>
2. ...
```

### Formatting rules

- Summarize, do not paste. Each finding should be one to two sentences.
- Attribute every claim to its source.
- If search returns nothing relevant, write `status: unavailable` and note the query tried.
- Cap total output to roughly 500 words. The analysis skill needs signal, not volume.

## Error handling

- If web search returns no results: write `status: unavailable` with the query attempted.
- If results are low-confidence or clearly outdated: note the limitation in the output and mark `status: partial`.
- Never invent information. If search cannot confirm something, say so.

## Dependencies

None. This is a leaf utility skill. It uses the agent's built-in web search tool.
