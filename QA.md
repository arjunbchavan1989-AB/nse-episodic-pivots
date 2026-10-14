# NSE Episodic Pivot Lab verification

## Coverage inventory

- Strict gap >3%, RVOL >3× prior-20 mean, close position ≥65%, positive session/held open, neglect ≥60; threshold boundaries and zero-range bars.
- Neglect and RVOL exclude event-day volume/price from pre-event baselines.
- Insufficient history remains unknown; invalid prices fail.
- Dated catalyst windows exclude after-close and future stories; routine/negative/wrong-company items do not produce bullish catalysts; headline ratings cap at 2.
- Future sessions, universe filter changes, insufficient chart/upstream coverage preserve the last good published snapshot.
- Full universe and every ≥4% mover preserved; empty strict-EP days are legitimate.
- Browser: mover, EP, volume-led and full-universe tabs; search, catalyst and neglect filters; every sort; table/cards round trip; snapshot selector.
- Browser: copy all visible symbols and single symbol, CSV export, empty search/reset, rules and health dialogs.
- Browser: stock chart with 60/120/180 ranges, hover OHLCV, pass/fail gates, neglect breakdown, evidence links/publication times; Escape/close.
- Desktop ≥1440 and mobile 390, light/dark, horizontal table containment, no page/dialog overflow, missing snapshot/chart errors.
- Deployment: complete successful GitHub refresh, Pages built, current index/JSON reachable, live primary flow checked, separate preview deployed.
- Latest request: separate Valid Theme / Story EP view, verified exposure/primary evidence/corroboration, no loose theme labels; expiry, future dates, cancellation, headline-only and tape-failure exclusions.

## Local verification

35 regression tests passed across technical threshold boundaries, pre-event-only neglect, source windows, wrong-company/routine/speculative/repost exclusions, last-good publication guards, reviewed story exposure, expiry, cancellation persistence, and future-invalidation leakage.

Chromium checks at 1440×900 and 390×844 passed. The initial price scan includes 849/849 source stocks, all 70 ≥4% movers, three strict technical EP candidates, twelve volume-led candidates, and one reviewed Story EP. Catalyst counts can vary with changing RSS availability; they are not fabricated or forced to match the price moves.

Full mover clipboard exactly matched the complete sorted 70-symbol list. Strict EP clipboard contained GALLANTT, SEPC and SYNGENE. Story EP clipboard contained only GOODLUCK. Symbol search, no-result disabling, all sort modes, catalyst/neglect filtering, cards/table round trip, CSV download and snapshot switching were exercised.

Detail tests covered 60/120/180 bars, hover OHLCV, single-symbol copy, gates, neglect breakdown, reviewed primary filing and two corroborating sources, conditional merger caveats, rules/data-health dialogs, Escape and close. Missing snapshot/chart responses showed honest fallbacks. No JavaScript page errors were observed.

Desktop light/dark and mobile story/detail screens were visually inspected. Mobile page width equals viewport width; detail dialog content fits its container; wide tables scroll inside their wrapper. Story opening-gap gate is explicitly optional rather than shown as a failed validity condition.
