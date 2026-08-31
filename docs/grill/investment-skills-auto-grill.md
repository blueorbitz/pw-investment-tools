# Grill Session: investment-skills network

Date: 2026-08-31
Method: Auto-grill — principle-based delegation

Scope: synergy of skills, thesis quality, the two interfaces (quick-look and
deep-research), verdict synthesis, and cron/scheduled output quality.

> **Read this first.** The rows that most need your attention are in the
> **Low Confidence** table and the **Top items needing human review** section.
> Those are the places where your stated principles are silent, in tension with
> each other, or where the current design directly contradicts a principle.

## Biggest tensions found

Three head-on contradictions between the current design and your principles, plus
two tensions among the principles themselves:

- **Static weights vs adaptiveness (#2).** `verdict-synthesis` hardcodes per-market
  factor weights and only "adapts" by zeroing-out missing inputs. That is
  degradation handling, not regime-awareness. This is the clearest
  design-vs-principle contradiction.
- **Cron stub vs autonomy (#4).** Originally the monitor scripts (`run_alerts.py` and
  peers) only validated the environment and printed "invoke the agent with...".
  Verified against the code. Your principle requires fully autonomous output that
  feeds an
  external system, so the scheduled layer does not actually schedule anything.
- **"Run everything" vs balanced depth (#5, #8).** `deep-research` fans out all
  data and analysis skills, but you want balanced depth and active length/noise
  control. The tension resolves at the report layer, not the fetch layer.

Internal principle tensions: running fewer skills (#5) means more missing factors
(#1) means capped conviction (#6), which structurally biases quick-look toward
Hold. Acceptable by design, but "speed" silently costs "decisiveness." And #7
(daily cache is fine) reveals the current per-market MYT close-time TTL is both
over-engineered and buggy for US/crypto.

## Principles

| # | Principle | Category |
|---|-----------|----------|
| 1 | Degrade-and-ship with caveats; failures must be named in the report (Gaps section + status headers). Do not hard-fail on missing data. | Data reliability |
| 2 | Favor adaptiveness / regime-awareness over static hardcoded weights, even at some cost to reproducibility. | Verdict logic |
| 3 | Keep prose conventions, loosely coupled, easy to edit. No heavy schema enforcement. | Coupling |
| 4 | Scheduling must be fully autonomous; it feeds external systems. A human-in-the-loop reminder is not acceptable. | Scheduling |
| 5 | quick-look prioritizes speed; deep-research is balanced depth (not exhaustive); guard against reports getting too long or noisy. | Interface boundary |
| 6 | Conservative by default; decisive (strong Buy/Sell) only on high conviction with clear evidence. | Verdict stance |
| 7 | Per-market close-time TTL is unnecessary; daily granularity is fine (not day-trading). | Cache correctness |
| 8 | Balance cost vs thoroughness; cut noise, avoid over-fetching. | Cost appetite |

## Decisions

### High Confidence (principles clearly decided)

| # | Question | Answer | Driving Principle |
|---|----------|--------|-------------------|
| Q1 | Cron scripts only print "invoke the agent with..." — isn't the monitor layer non-functional against #4? | Yes. As built it is a reminder stub. Close the loop: the cron target must invoke the agent headlessly and write the output file, or a scheduled `.kiro/hooks` must own the trigger. Printing a string is the wrong terminal state. | #4 |
| Q2 | Why isn't printing an instruction "good enough" as a first cut? | The consumer is external systems, not eyeballs. A print needs a human to act, which breaks the feed. #1 does not rescue it — #1 is about missing data inside a run, not whether the run happens. | #4 (#1 N/A) |
| Q3 | verdict-synthesis hardcodes weights — direct violation of #2? | Yes, the clearest contradiction. The only adaptation is redistributing weight for missing inputs (degradation, not regime-awareness). Introduce a regime signal that shifts weights. | #2 |
| Q4 | Should adaptiveness replace static weights entirely or layer on top? | Layer on top. Keep static per-market weights as the regime-neutral baseline (they encode real market-structure knowledge), then apply a bounded regime multiplier. Keeps the table human-editable. | #2, #3 |
| Q5 | quick-look caps conviction — is it ever the right tool for a decisive strong-Buy? | No, and that's correct. It skips macro/sentiment/on-chain so it can never clear the High-conviction bar. A decisive call requires deep-research. The cap is the honest expression of #6. | #6, #5 |
| Q6 | deep-research runs ALL skills — contradicts #5's "not exhaustive"? | Partial contradiction, resolved at the report layer. Fetch broadly for factor coverage, but report-writer must compress: lead with verdict, tight factor table, push raw scratch to appendix. "Run everything" is fine for inputs, not for output. | #5, #8 |
| Q7 | yahoo_cache.py uses a single Bursa MYT close time for all markets — why, and is it wrong? | Both unnecessary (#7) and wrong (miscomputes freshness for US, meaningless for 24/7 crypto). Drop close-time logic; use a uniform calendar-day TTL. | #7 |
| Q8 | What happens when an upstream skill crashes and writes no file? | Absence = `unavailable`. Downstream proceeds, records the factor missing, verdict redistributes weight and caps conviction, Gaps names it. The "no file = unavailable" mapping must be stated in prose. | #1, #3 |
| Q9 | Should the scratch bus add schema validation? | No. #3 is explicit: prose conventions, no heavy enforcement. A malformed file costs one missing factor (handled by #1), low blast radius. | #3, #1 |
| Q10 | Is the "Gaps and caveats" section standard or nice-to-have? | Mandatory. #1 requires failures be named; the Gaps section is the mechanism. A report without it violates #1. | #1 |
| Q11 | On mixed factors, what's the default verdict? | Hold or hedge. #6 is explicit: conservative by default, decisive only on high conviction. Mixed/contradictory factors cap conviction and steer to Hold. | #6 |

### Medium Confidence (principles align but don't directly address)

| # | Question | Answer | Driving Principle | Reasoning |
|---|----------|--------|-------------------|-----------|
| Q12 | `.kiro/hooks` scheduled hook vs headless agent in cron? | **Resolved differently:** no wrapper at all. The user's harness (Hermes) has a cron that triggers the skill directly, so the mechanism lives entirely in the harness config. No script, no vendor lock. The skill's own step 1 does the deterministic precondition checks. | #4 | #4 demands autonomy but is silent on mechanism; deferring it to the harness keeps the network vendor-neutral and avoids a redundant script. |
| Q13 | If the autonomous monitor fires while a source is down, emit nothing or a degraded alert? | Emit a degraded alert with the failure named — never silent. A silent skip looks identical to "nothing happened," dangerous for a feed. | #4, #1 | Both align; principles don't address the monitor's failure output specifically. |
| Q14 | On the 60s/skill timeout, redistribute-and-continue or retry? | Redistribute-and-continue, mark the factor unavailable. No retry by default; one cheap retry is defensible at most. | #1, #8 | Aligns toward continue; retry policy not spelled out. |
| Q15 | If deep-research gathers all factors but half are `partial`, is a High-conviction verdict trustworthy? | No. Conviction requires good data quality; half-partial degrades quality, cap to Medium. Running "everything" doesn't buy decisiveness if the everything is thin. | #6 | Aligns; "how much partial degrades quality" is left fuzzy. |
| Q16 | Adaptive weights hurt reproducibility — acceptable? | Yes, within bounds. #2 explicitly trades some reproducibility for adaptiveness. Mitigate by logging the regime signal + resulting weights into the verdict file, and bounding the multiplier. Explainable, not identical. | #2 | #2 accepts the tradeoff; "how much drift is OK" is unspecified. |
| Q17 | quick-look skips macro — in a macro-driven regime, isn't its verdict misleading? | Real risk. quick-look is blind to the driving factor. Mitigate with a standing caveat and (with adaptive weights) a "macro regime detected, re-run deep-research" hint. Capped conviction limits damage but it can still mislead on direction. | #5, #6, #2 | Principles point at a caveat + escalation but don't mandate it. |
| Q18 | Where do target/stop numbers come from, and how conservative? | Derived from named inputs (valuation range, support/resistance, volatility-based stops) with rationale shown. Honest weak-R/R disclosure (MAHSING is the model). Wider stops for Bursa/crypto. | #6 | Conservatism from #6; derivation method inferred from exemplar reports. |
| Q19 | Scraping + auth-gated + agent web-search inputs are non-deterministic — doesn't that undermine verdicts? | Tolerated, not fixed. Name the source and its reliability (#1); shakier inputs degrade data quality and cap conviction (#6). Never claim false precision. | #1, #6 | Both align; trust level in web-search numbers is judgmental. |
| Q20 | What protects a downstream skill from reading a half-written scratch file? | Nothing structural today, and #3 says don't add machinery. Convention: write the status header last, or write-then-rename, so a partial file reads as incomplete. | #3, #1 | #3 forbids heavy validation; #1 handles fallout. Batch ordering makes this rare. |
| Q21 | Does deep-research over-fetch for tickers quick-look already flagged as clear? | Potentially. Reuse same-day cached/scratch factors and only fetch the skipped layers (macro/sentiment/on-chain). Honors #8 and #5 without losing coverage. | #8, #5 | Aligns toward reuse; no principle mandates cross-orchestrator cache reuse. |

### Low Confidence (needs human review)

| # | Question | Answer (guess) | Reasoning | Tension |
|---|----------|----------------|-----------|---------|
| Q22 | Where is the "missing file = unavailable" convention enforced and owned? | State it in verdict-synthesis (the aggregator) as the authority, and echo in each downstream SKILL.md. | #3 allows prose conventions but is silent on where they live; today it is implicit and can drift. | #3 (convention fine) vs drift risk of an unstated rule. |
| Q23 | Should scheduled monitor runs use the same regime-adaptive weights as interactive runs? | Yes for consistency, but scheduled runs may want a stickier regime signal to avoid flip-flop alerts. | A verdict shouldn't depend on who triggered it, but an over-reactive regime signal could spam the feed. | #2 (adaptive) vs #4 (stable autonomous feed). |
| Q24 | Is a uniform daily TTL truly acceptable for 24/7 crypto? | Daily works for equities across closures; crypto may need one shorter-TTL exception. | Crypto's 24/7 nature pushes back on the uniform-daily simplification. | #7 says per-market TTL is unnecessary, but crypto reintroduces exactly that nuance. |
| Q25 | Is conservative gating so strict the tool is rarely actionable? | **RESOLVED — see below.** Root cause: old conviction rules measured only agreement + data completeness, so mild-everything and strong-everything both hit "3 aligned → High," making High common and meaningless while one blemish froze most tickers at Medium. Fix: gate conviction on signal *magnitude*, not just agreement. | #6 + implicit actionability need | Resolved by separating signal strength from conviction (see "Q25 resolution"). |
| Q26 | Where's the line between "balanced depth" and "dropped a factor the user needed"? | Keep every factor's signal + one-line rationale in the summary table; move raw evidence to appendix or omit. No factor leaves the decision, only the prose bulk. | The exact prose-cut point is a taste/UX judgment. | #5 (cut noise) vs #1 (name everything) vs #6 (honest/complete). |
| Q27 | Undocumented/auth endpoints can return garbage-but-parseable data — what's the containment? | Parse failures degrade to unavailable + named (#1). But silent shape-changes that return plausible-wrong data are uncovered — #3 says don't solve with schema. | This is an uncovered failure mode: wrong-but-parseable data flows into a verdict. | Direct #3 (no heavy validation) vs #1 (don't ship wrong data) conflict. |

## Q25 resolution: magnitude-gated conviction

Decision made and implemented in `src/analysis/verdict-synthesis/SKILL.md`.

**Problem.** The old conviction rules only measured *agreement* (>=3 factors aligned)
and *data completeness*. There was no notion of signal *strength*. So a mildly-cheap,
mildly-trending, mildly-positive ticker scored the same "3 aligned -> High" as a
deeply-undervalued, breaking-out, insider-bought one. High became common (and
therefore meaningless), while any single ugly factor froze most real tickers at
Medium. That is the "goes nowhere" feeling: the bar was both too easy to reach on
weak signals and too easy to block on one blemish.

**Fix - three changes.**

1. **Score each factor on strength, not just direction.** Internal scale -2..+2,
   surfaced in reports as words only: **strong bullish / mild bullish / neutral /
   mild bearish / strong bearish**. The internal numbers are never printed.

2. **Gate conviction on composite magnitude.** Compute a weighted composite score.
   - High (decisive): `|composite| >= 1.2`, >=3 factors aligned, no opposite extreme, good data quality.
   - Medium: `0.5 <= |composite| < 1.2`, or strong direction with one mild contradiction.
   - Low/Hold: `|composite| < 0.5`, or genuinely split factors.
   High is now self-scarce because reaching 1.2 genuinely is hard - so when it fires it *means* something.

3. **Single-factor override** so a genuine standout punches through. A lone
   **strong bullish/bearish** factor (valuation extreme, volume-confirmed breakout,
   whale accumulation/distribution, derivatives extreme) can escalate conviction one
   level even when others are neutral. **Sentiment can never escalate alone** (noisiest
   input). A contradicting *extreme* factor still blocks the override.

**Why this satisfies both #6 and actionability.** Most days still resolve
conservative because 1.2 is hard to reach - #6 stays intact. But a clear signal is
no longer diluted to Medium: high magnitude produces a decisive, credible call, and
scarcity is exactly what makes "strong Buy" trustworthy. The one-blemish-caps-Medium
trap is gone - only an *opposite-extreme* factor blocks High, not a mild disagreement.

**Two tunable knobs you own** (encode risk appetite):
- `HIGH_THRESHOLD` (default 1.2): lower -> more decisive calls, more false-strong risk; higher -> rarer, higher-quality strong calls. Given "conservative unless super sure," 1.2-1.4 is the sensible band.
- Override-eligible factors: currently valuation extremes + volume-confirmed technical (equities), on-chain + derivatives extremes (crypto); sentiment excluded.

## Design tree (resolved)

```
A. SYNERGY / DATA FLOW (scratch bus)
   - Prose conventions, NO schema enforcement                         [#3]
   - Missing/crashed upstream file == status: unavailable;
     downstream never blocks, redistribute + cap conviction           [#1]
   - Write status header LAST / write-then-rename (convention)        [#3]
   - OPEN: document "absence = unavailable", owned by verdict-synth   (Q22, low)

B. QUICK-LOOK (speed triage)
   - Caps conviction; can never strong-Buy/Sell, by design            [#5,#6]
   - Wrong tool in a macro-dominated regime; add standing caveat
     + hint to escalate to deep-research                              (Q17, medium)

C. DEEP-RESEARCH (balanced depth)
   - "Run everything" OK for FETCH, not for REPORT; compress          [#5,#8]
   - Timeout -> mark unavailable, redistribute, no retry by default   [#1,#8]
   - Consider reusing same-day cached factors                         (Q21, medium)
   - Half-partial inputs cannot yield High conviction                 [#6]

D. VERDICT-SYNTHESIS
   - DONE: static table = regime-NEUTRAL baseline + bounded regime
     multiplier (+/-10pp/factor), regime + weights logged in header   [#2,#3]
   - Conservative default: mixed -> Hold/hedge                        [#6]
   - Partial inputs -> redistribute + cap conviction                  [#1]
   - DONE: conviction gated on composite MAGNITUDE (strength labels
     -2..+2 internal, words in report) + single-factor override;
     HIGH_THRESHOLD default 1.2                                       (Q25 resolved)

E. THESIS QUALITY
   - Mandatory "Gaps and caveats" naming every missing source         [#1]
   - Targets/stops from named inputs + rationale; honest weak-R/R;
     wider stops for Bursa/crypto                                     [#6]
   - DONE: strong signals now punch through to decisive calls via
     magnitude gating; no longer stuck at Medium on one blemish       (Q25 resolved)

F. CRON / SCHEDULING
   - DONE: no wrapper scripts. Scheduler/agent harness (Hermes cron)
     triggers the monitor/* skill directly. Skill runs its own
     precondition checks as step 1. Fully autonomous, harness-agnostic. [#4]
   - Degraded runs emit a named-failure alert, never silent            [#4,#1]
   - OPEN: regime-signal stability for scheduled runs                  (Q23, low)

G. DATA RELIABILITY / CACHE
   - DONE: dropped per-market MYT close-time TTL; uniform calendar-day
     TTL + optional ISK_CACHE_TTL_HOURS override                       [#7]
   - Scraped/auth/undocumented sources degrade to unavailable +
     named on parse failure; NO heavy schema                           [#1,#3]
   - PARTLY DONE: shorter crypto TTL now possible via env override      (Q24)
   - OPEN: garbage-but-parseable data is uncovered (#3 vs #1)          (Q27, low)
```

## Top items needing human review

Design contradicts a principle (all four RESOLVED — implemented):

1. **[D / #2] RESOLVED — adaptive weights.** `verdict-synthesis` now treats the
   static per-market tables as a regime-neutral baseline and applies a bounded regime
   multiplier (±10pp per factor, renormalized), classified from macro-context +
   technical scratch. Regime signal and applied-vs-baseline weights are logged in the
   verdict YAML header. Sentiment is never raised by a regime shift. (Q3, Q4, Q16)
2. **[F / #4] RESOLVED — scheduler triggers the skill directly.** The wrapper scripts
   are gone entirely (`run_alerts.py`, `run_review.py`, `run_scan.py`, and the earlier
   `agent_runner.py` all removed). The user's scheduler / agent harness (Hermes cron)
   is configured to trigger the `monitor/*` skill directly; the harness runs the
   agentic work. Each skill does its own deterministic precondition checks (input file
   present, anything to check) as pipeline step 1, so nothing was lost by removing the
   scripts. This is fully autonomous, harness-agnostic, and preserves the
   "`.py` = deterministic fetch/compute only" rule — there was no deterministic work
   for these scripts to do. (Superseded both the Kiro-headless approach and the
   stdout-trigger approach.) (Q1, Q2, Q12)
3. **[G / #7] RESOLVED — cache TTL.** `yahoo_cache.py` dropped the Bursa-MYT
   close-time logic for a uniform local-calendar-day TTL across all markets, with an
   optional `ISK_CACHE_TTL_HOURS` override for fresher 24/7 crypto data. (Q7, Q24)
4. **[C / #5, #8] RESOLVED — fetch-broad / report-tight.** `deep-research` Step 5 now
   mandates compression (every factor keeps its signal; prose summarized; raw
   evidence stays in scratch; few-minute target length). Step 2 adds same-day scratch
   reuse for shared factors and a no-retry-on-timeout rule. (Q6, Q21)

Note on mirroring: `.kiro/skills/` holds regular-file copies (not symlinks) of the
`src/` scripts. All script edits above were mirrored and hash-verified; the `.kiro`
copies rely on `ISK_ROOT` being set.

Principles silent or in tension (need your call):

5. **[F / #3]** Where the "missing file = unavailable" convention is documented and
   owned. (Q22)
6. **[D/F / #2, #4]** Regime-signal temporal stability for scheduled vs interactive
   runs, to avoid alert spam. (Q23)
7. **[G / #7] PARTLY ADDRESSED.** Uniform daily TTL for 24/7 crypto — `yahoo_cache.py`
   now honors an optional `ISK_CACHE_TTL_HOURS` env override (e.g. set to 4 for
   crypto) on top of the default calendar-day rule. Remaining human input: decide
   whether to actually set a shorter crypto TTL in your environment. (Q24)
8. **[E / #6] RESOLVED.** Calibration: conservative gating vs actionability.
   Implemented magnitude-gated conviction (strength labels + composite score +
   single-factor override) in `verdict-synthesis`. Remaining human input: set the
   `HIGH_THRESHOLD` value (default 1.2) once you've seen a few live runs. (Q25)
9. **[C/E / #5, #1]** The exact line report-writer cuts between noise and needed
   factors. (Q26)
10. **[G / #3, #1]** Uncovered failure mode: garbage-but-parseable data from
    undocumented endpoints. How much lightweight range-checking is worth the
    coupling cost? (Q27)

Frontier status: exhausted across branches A-G. 27 questions total.
