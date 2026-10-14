"""Independent EP scan of this repository's own validated EOD artifact."""
import argparse,csv,json,logging,shutil
from datetime import datetime,timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
from engine import metrics,CONFIG
from catalysts import collect
from themes import apply_themes

ROOT=Path(__file__).resolve().parents[1]
WEB=ROOT/"web"
LOG=logging.getLogger("ep")
PRICE_SOURCE="Independent acquisition: official NSE listing, Yahoo EOD prices and shares"


def scan(price_inputs,allow_historical=False):
    price_inputs=Path(price_inputs)
    source=json.loads((price_inputs/"latest.json").read_text())
    session=source["last_trading_date"]
    now=datetime.now(ZoneInfo("Asia/Kolkata"))
    completed=now.date() if now.hour>=19 else now.date()-timedelta(days=1)
    if datetime.fromisoformat(session).date()>completed:
        raise RuntimeError("Upstream refers to a future or not-yet-completed session")
    if not allow_historical and (datetime.now(ZoneInfo("Asia/Kolkata")).date()-datetime.fromisoformat(session).date()).days>4:
        raise RuntimeError("Upstream snapshot older than four calendar days; retaining last good output")
    filters=source["filters"]
    expected={"min_market_cap_cr":500,"min_avg_volume_shares":70000,"min_avg_rupee_vol_cr":3,
              "min_avg_daily_range_pct":3,"avg_volume_window_days":20}
    if any(filters.get(k)!=v for k,v in expected.items()):raise RuntimeError("Upstream universe filters changed")
    if len(source["rows"])==0 or len(source["rows"])!=len({r["symbol"] for r in source["rows"]}):
        raise RuntimeError("Empty or duplicate universe")
    if source.get("coverage_pct",0)<95:raise RuntimeError("Upstream coverage below 95%")
    names=dict(source.get("company_names",{}))
    with (ROOT/"pipeline/company_names.csv").open() as f:
        for r in csv.DictReader(f):names.setdefault(r["SYMBOL"].strip(),r["NAME OF COMPANY"].strip())
    rows=[];charts={};missing=[]
    for parent in source["rows"]:
        try:
            symbol=parent["symbol"];chart=json.loads((price_inputs/"charts"/f"{symbol}.json").read_text())
            bars=chart["bars"]
            if not bars or bars[-1]["t"]!=session:raise ValueError("Stale chart")
            row=metrics(bars,parent);rows.append(row);charts[symbol]=chart
        except (OSError,ValueError,KeyError,TypeError) as e:
            missing.append({"symbol":parent["symbol"],"error":str(e)})
    coverage=len(rows)/len(source["rows"])*100
    if coverage<95:raise RuntimeError(f"Chart coverage below 95% ({coverage:.1f}%), preserving last good output")
    # Every stock must share one date; every prior-day news window uses actual bars.
    previous_sessions={chart["bars"][-2]["t"] for chart in charts.values()}
    if len(previous_sessions)!=1:raise RuntimeError("Previous trading sessions do not match")
    previous_session=previous_sessions.pop()
    LOG.info("Price scan: %s stocks; %s movers; %s strict EP candidates",len(rows),sum(r["mover"] for r in rows),sum(r["ep_candidate"] for r in rows))
    diagnostics=collect(rows,names,session,previous_session,ROOT/"pipeline/news_archive.json")
    story_watchlist=apply_themes(rows,session,state_path=ROOT/"pipeline/story_state.json")
    rows.sort(key=lambda r:(r["change_pct"],r["rvol"]),reverse=True)
    good=sum(d["ok"] for d in diagnostics)
    payload={"title":"NSE Episodic Pivot Lab","generated_at":datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(),
             "refresh_batch":source.get("refresh_batch"),
             "last_trading_date":session,"previous_session":previous_session,"config":CONFIG,"filters":filters,
             "data_source":PRICE_SOURCE,"price_input_generated_at":source["generated_at"],
             "market_data":source.get("market_data",{}),
             "universe_count":len(source["rows"]),"scanned_count":len(rows),"coverage_pct":round(coverage,2),
             "missing":missing,"rows":rows,"story_watchlist":story_watchlist,"news_status":"Complete fetch" if good==len(diagnostics) else "Partial news availability",
             "news_diagnostics":diagnostics,"news_fetches_ok":good,"news_fetches_total":len(diagnostics),
             "counts":{"movers":sum(r["mover"] for r in rows),"ep":sum(r["ep_candidate"] for r in rows),
                       "technical":sum(r["technical_pass"] for r in rows),"volume_led":sum(r["volume_led"] for r in rows),
                       "rated":sum(r["catalyst"]["strength"] is not None for r in rows),
                       "primary":sum(r["catalyst"].get("status") in ("Exchange-reported event","Primary filing reviewed") for r in rows),
                       "story":sum(r["story_ep"] for r in rows),"story_valid":sum(r["story_valid"] for r in rows)},
             "method_note":"EOD price/volume neglect proxy. Analyst coverage and institutional neglect are not measured. Catalyst ratings are conservative, provisional evidence scores, not probabilities or proof of causation.",
             "price_basis":"Own Yahoo adjusted OHLCV; own raw EOD close displayed. Corporate actions and extreme volumes require checking."}
    # Valid empty EP sets are published; never fabricate qualifying signals.
    data=WEB/"data";data.mkdir(parents=True,exist_ok=True)
    staging=ROOT/".staging-data"
    if staging.exists():shutil.rmtree(staging)
    (staging/"charts").mkdir(parents=True)
    for symbol,chart in charts.items():(staging/"charts"/f"{symbol}.json").write_text(json.dumps(chart,separators=(",",":")))
    (staging/"latest.json").write_text(json.dumps(payload,ensure_ascii=False,separators=(",",":")))
    if (data/"charts").exists():shutil.rmtree(data/"charts")
    shutil.move(str(staging/"charts"),str(data/"charts"))
    (staging/"latest.json").replace(data/"latest.json")
    archives=data/"snapshots";archives.mkdir(exist_ok=True)
    (archives/f"{session}.json").write_text(json.dumps(payload,ensure_ascii=False,separators=(",",":")))
    files=sorted(archives.glob("*.json"),reverse=True)
    for p in files[30:]:p.unlink()
    (data/"history.json").write_text(json.dumps([p.stem for p in files[:30]]))
    shutil.rmtree(staging)
    LOG.info("Published snapshot %s: %s stocks, %s/%s news fetches",session,len(rows),good,len(diagnostics))
    return payload


if __name__=="__main__":
    logging.basicConfig(level=logging.INFO,format="%(asctime)s %(message)s")
    parser=argparse.ArgumentParser()
    parser.add_argument("--allow-historical",action="store_true")
    a=parser.parse_args()
    from prices import prepare
    scan(prepare(),a.allow_historical)
