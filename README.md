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

## Valid Theme / Story EP

This is a separate narrative EP bucket, not the automatic attachment of a fashionable sector label. Require verified company exposure and either reviewed primary evidence with dated corroborating reporting, or a company-matched positive primary theme disclosure plus at least two reputable media publishers addressing the same theme. Headline-only stories remain candidates, not valid story EPs.

Price confirmation requires a ≥4% up-day, RVOL >3×, close position ≥65%, close ≥open and neglect passed. An opening gap is optional in this separate category; strict gap EP rules remain unchanged. Reviewed stories expire after 30 days; cancellation/withdrawal flags suppress validation and are persisted in `pipeline/story_state.json` until later evidence revalidates the narrative. Future invalidation timestamps cannot leak into older snapshots. A story can remain evidence-qualified while failing today's tape conditions; that is not a new Story EP.

The initial reviewed example is GOODLUCK's defence/green-energy restructuring, supported by its [12 October primary filing](https://nsearchives.nseindia.com/corporate/GOODLUCK_12102026125629_BM_outcome_12102026.pdf), [CNBC TV18 reporting](https://www.cnbctv18.com/market/goodluck-india-shares-jump-19-pc-from-days-low-heres-what-triggered-the-rally-20009881.htm), and [The Economic Times](https://economictimes.com/markets/stocks/news/goodluck-india-shares-surge-17-as-merger-expands-defence-arm-to-join-firm-along-with-green-energy-unit/articleshow/134888841.cms). The board gave in-principle approval to enlarge the proposed restructuring scope; amalgamation is not completed and financial terms remain unresolved. The filing establishes the named subsidiary exposure, not guaranteed profit accretion.

The conservative “available by” timestamp on the initial primary source uses the corroborating CNBC publication time, not an invented exact exchange broadcast timestamp. All evidence was available before that session's close, although the review was performed retrospectively on 14 October. It is not a backtest.

Automatic themes cover defence/aerospace, AI/data-centres, semiconductors/electronics, renewables, railways/infrastructure, sugar/ethanol and pharma/regulatory opportunity. These are matching taxonomies, not claims that each theme is presently valid. `pipeline/story_reviews.json` holds reviewed evidence and expiry windows; `pipeline/themes.py` validates it daily. New automatic feed-qualified themes and reviewed full-document stories are labelled separately. No ongoing manual human research or future curated reviews are promised by the scheduled script.

“Valid” means the evidence/exposure test passes, not that an event caused the move, is economically material, or will produce a profitable trade. The detail view shows thesis, conditional risks, source quality and links. Media novelty and financial materiality still require investigation.

## Daily GitHub deployment

Schedule: Monday–Friday at **19:30 IST (14:00 UTC)**. GitHub cron runs can be delayed; this is the job's start time, not a guarantee the published refresh finishes at exactly 19:30.

Because the existing Kell dashboard publishes later, this workflow installs and runs that same approved upstream pipeline locally in its own runner before computing EP results. Its cached histories and validations are reused; the underlying equity/index data sources are unchanged. The existing stage and Kell repositories and their schedules are not modified. Price/benchmark providers can publish late; an unsuccessful upstream or EP scan retains the last good public snapshot rather than pretending to have fresh data.

The EP/news/theme code uses Python's standard library; local upstream regeneration installs the existing Kell pipeline's documented Python dependencies. No new paid data key is required.

Workflow steps: EP regression tests; sparse checkout of the existing upstream data, pipeline and tests; upstream regression tests and local EOD regeneration; price/neglect computation; dated news collection; commit the validated JSON and news archive; deploy `web/` to `gh-pages`. Configure repository Settings → Pages to `gh-pages`, `/ (root)`.

Upstream filter drift, duplicate/empty universes, future/incomplete dates, snapshots older than four calendar days, or <95% same-session chart coverage fail without committing/deploying partial output. A valid zero-candidate EP day is published honestly. News outages do not fabricate evidence: price results publish with “Partial news availability,” explicit diagnostics and conservative/unverified ratings.

Run workflow manually with `refresh_data=true` to refresh everything, or `false` for a UI-only redeploy of the existing validated snapshot. Saved snapshot metrics/news are point-in-time; historical charts use current adjusted bars filtered to that date, not a separate historical-data archive. This is not a survivorship-free backtest.

## Local commands

```bash
python -m unittest discover -s tests -v
python pipeline/run.py --upstream-dir ../kell-dashboard/web/data
```

Serve `web/` with a static HTTP server. Company aliases live in `pipeline/company_names.csv` and may need updating for renamed/newly listed companies. Thresholds are in `pipeline/engine.py`; event matching and rating rules are in `pipeline/catalysts.py`.
