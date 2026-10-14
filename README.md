# NSE Episodic Pivot Lab

A separate daily Indian-equity dashboard for biggest movers, gap/volume EP candidates, pre-event neglect and catalyst evidence. It is a research tool, not Stockbee's proprietary screener, a verified optimal strategy, or personalized financial advice.

## Dashboard and universe

The public deployment is [NSE Episodic Pivot Lab](https://arjunbchavan1989-ab.github.io/nse-episodic-pivots/). [GitHub Actions](https://github.com/arjunbchavan1989-AB/nse-episodic-pivots/actions) performs daily refreshes; the attached Perplexity preview is a captured snapshot.

The source universe is the user's [NSE Price Cycle dashboard](https://arjunbchavan1989-ab.github.io/nse-kell-price-cycle/), itself based on the existing stage-analysis universe. It retains strict market cap >₹500 crore, average shares volume20 >70,000, average close×volume20 >₹3 crore, and average range20 >3%. The inherited range implementation is mean(True Range / previous close ×100), including gaps, not gap-excluding ADR.

The pipeline consumes the user's already-validated adjusted OHLCV chart artifacts from the public `nse-kell-price-cycle` repository. It does not introduce another stock-price provider or resume the paused NSE-only equity migration. Latest displayed close and market cap are inherited raw figures; opening gap/candle metrics use the upstream adjusted artifact. RS is inherited against Nifty MidSmallcap 400. Corporate actions and extreme volume should be independently checked.

## Scan rules

- **Opening gap:** (open / previous close −1) ×100 >3%. This is the selected Indian-market adaptation, not a backtested optimum.
- **RVOL:** today's shares volume / average of the preceding 20 sessions >3×. Today's volume is excluded from its own baseline. “300% of average” means 3×, not a 300% increase (4×).
- **Closing strength:** (close − low) / (high − low) ×100 ≥65%, the upper 35% of the daily range. Require a positive close-to-close return and close ≥ open. Zero-range bars cannot confirm close position.
- **Neglect:** score ≥60/100 and prior 20-session return ≤10%. This is a price/volume proxy, not a finding of low analyst, media or institutional interest.

Neglect uses only pre-event bars:

| Component | Points |
|---|---|
| Prior 20-session return ≤5%; otherwise ≤10% | 30; otherwise 20 |
| Prior 60-session return ≤10%; otherwise ≤20% | 25; otherwise 15 |
| Prior 20-session average volume / preceding 40-session average ≤0.7; otherwise ≤1.0 | 25; otherwise 15 |
| No prior ≥10% up-day on >3× its own prior-20 volume during the preceding 60 sessions | 20 |

Insufficient history yields unknown neglect and does not pass a strict EP. A distressed downtrend can score highly, so deep drawdowns are flagged.

The views distinguish all ≥4% biggest movers, strict technical+neglect EP candidates, volume-led pivots without a >3% opening gap, and the full scanned universe. A price setup alone never proves an economic catalyst. Candle/EMA10/20 charts, source timelines, pass/fail gates, neglect breakdowns, TradingView symbol copying, CSV export, filtering, light/dark modes and up to 30 saved daily snapshots are provided.

## Catalyst evidence and ratings

Stockbee's original [EP context](https://stockbee.blogspot.com/2010/02/what-are-episodic-pivots-and-how-to.html) and [process flow](https://stockbee.blogspot.com/2014/07/my-process-flow-for-episodic-pivots-ep.html) emphasize investigating genuinely surprising, game-changing information plus neglect. The numerical defaults here are an independent adaptation.

The collector fetches [NSE announcements RSS](https://nsearchives.nseindia.com/content/RSS/Online_announcements.xml), [BSE announcements RSS](https://www.bseindia.com/data/xml/announcements.xml), and dated company-specific Google News RSS results for every ≥4% mover and every technical EP candidate. Headlines and feed excerpts are matched to company names/symbols. Routine compliance, meeting intimations, price/volume enquiries and negative headlines do not establish a bullish economic catalyst.

Evidence must fall after the preceding trading session's 15:30 IST and at or before the event session's 15:30 IST. Later news is excluded. Post-open coverage is labelled “During session” and cannot itself establish why the stock gapped at the open. Search-returned items outside the actual timestamps are discarded, even if the search engine ignores its date query.

Ratings are provisional evidence-strength assessments, not measured probabilities, valuation models, or proof that the event caused the move:

- **1/5:** low-significance corporate-action context, shown on individual evidence where relevant.
- **2/5:** a company-matched, event-specific positive media headline. Headline-only ratings are capped here.
- **3/5:** specific positive language in an exchange feed excerpt, or primary evidence published during the session.
- **4/5:** a specific positive primary exchange disclosure before the open, still provisional on business materiality and recurrence.
- **5/5:** reserved for an independently reviewed exceptional, materially significant recurring change; the automatic engine never awards it.

Summary ratings select economic event candidates; routine or corporate-action-only context does not establish an economic EP and can remain unverified. The engine does not invent earnings surprises, order-to-sales materiality, demand persistence, news silence, fund ownership, or a causal explanation when sources do not establish them. No qualifying event found means “Unverified,” not “there was no catalyst.”

A readable source link and publication time accompany each collected item. Google News headline links are aggregator links; paywalls or redirects may apply. Original article bodies and earnings documents are not automatically read, so media headline candidates need manual verification. The news archive stores excerpts, not full commercial articles.

## Daily GitHub deployment

Schedule: Monday–Friday at **20:30 IST (15:00 UTC)**, after the upstream Kell scan's 20:00 IST refresh. GitHub cron runs can be delayed. Public repositories need no paid API key for these feeds. All pipeline code uses Python's standard library.

Workflow steps: regression tests; sparse checkout of the upstream validated data; price/neglect computation; dated news collection; commit the validated JSON and news archive; deploy `web/` to `gh-pages`. Configure repository Settings → Pages to `gh-pages`, `/ (root)`.

Upstream filter drift, duplicate/empty universes, future/incomplete dates, snapshots older than four calendar days, or <95% same-session chart coverage fail without committing/deploying partial output. A valid zero-candidate EP day is published honestly. News outages do not fabricate evidence: price results publish with “Partial news availability,” explicit diagnostics and conservative/unverified ratings.

Run workflow manually with `refresh_data=true` to refresh everything, or `false` for a UI-only redeploy of the existing validated snapshot. Saved snapshot metrics/news are point-in-time; historical charts use current adjusted bars filtered to that date, not a separate historical-data archive. This is not a survivorship-free backtest.

## Local commands

```bash
python -m unittest discover -s tests -v
python pipeline/run.py --upstream-dir ../kell-dashboard/web/data
```

Serve `web/` with a static HTTP server. Company aliases live in `pipeline/company_names.csv` and may need updating for renamed/newly listed companies. Thresholds are in `pipeline/engine.py`; event matching and rating rules are in `pipeline/catalysts.py`.
