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
