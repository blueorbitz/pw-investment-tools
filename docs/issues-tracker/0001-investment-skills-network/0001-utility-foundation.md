# 0001: Utility foundation (report-writer + web-search)

**What to build:** Two utility skills that every other skill depends on. `utility/report-writer/SKILL.md` handles path selection, template application, writing final reports to `~/notes/YYYY-MM/`, and writing incremental scratch notes to `.scratch/`. `utility/web-search/SKILL.md` wraps the agent's web search capability with instructions for when and how to search, output formatting, and token-conscious result trimming. Both skills should include `## Dependencies`, `## Error Handling`, and `## Output Format` sections.

**Blocked by:** None (can start immediately).

**Status:** done

- [x] `utility/report-writer/SKILL.md` exists with sections: Purpose, Input, Output Format (report template with Verdict/Thesis/Fundamentals/Technical Setup/Sentiment & News/Macro Context/Risks/Position Sizing), Output Paths, Error Handling, Dependencies
- [x] Report-writer documents the verdict block format: Action, Conviction, Target Price, Timeframe, Stop Loss, one-line thesis
- [x] Report-writer documents scratch note path convention: `~/notes/YYYY-MM/.scratch/YYYY-MM-DD-<TICKER>/<skill-name>.md`
- [x] `utility/web-search/SKILL.md` exists with sections: Purpose, When to Use, Input, Output Format, Error Handling, Dependencies
- [x] Web-search skill instructs the agent to prefer structured APIs and use web search only as fallback or for follow-up questions
