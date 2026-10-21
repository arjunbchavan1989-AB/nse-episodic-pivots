"""Acquire this repository's own price artifact, independently of Kell and Stage."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from market_data import build
from benchmark import load as load_benchmark, excess

HERE=Path(__file__).resolve().parent
OUTPUT=HERE/"cache/price-inputs"


def safe(value):
    return round(float(value),4) if value is not None and np.isfinite(value) else None


def prepare():
    source,frames=build()
    benchmark=load_benchmark(source["last_trading_date"])
    source["previous_trading_date"]=str(benchmark.index[-2].date())
    chart_dir=OUTPUT/"charts";chart_dir.mkdir(parents=True,exist_ok=True)
    for row in source["rows"]:
        symbol=row["symbol"];raw=frames[symbol].rename(columns=str.lower);technical=raw.copy()
        if "adj close" in raw:
            ratio=raw["adj close"]/raw.close
            for column in ("open","high","low","close"):technical[column]*=ratio
        technical["e10"]=technical.close.ewm(span=10,adjust=False).mean()
        technical["e20"]=technical.close.ewm(span=20,adjust=False).mean()
        row["rs_excess_pct"]=safe(excess(technical,benchmark))
        bars=[{"t":str(dt.date()),"o":safe(r.open),"h":safe(r.high),"l":safe(r.low),
               "c":safe(r.close),"v":int(r.volume),"e10":safe(r.e10),"e20":safe(r.e20)}
              for dt,r in technical.tail(180).iterrows()]
        chart={"symbol":symbol,"date":source["last_trading_date"],"bars":bars,
               "price_basis":"Own Yahoo dividend-adjusted OHLCV; own raw EOD close displayed"}
        (chart_dir/f"{symbol}.json").write_text(json.dumps(chart,separators=(",",":"),allow_nan=False))
    values=np.array([r["rs_excess_pct"] for r in source["rows"] if r["rs_excess_pct"] is not None])
    for row in source["rows"]:
        row["rs_pct"]=int((values<row["rs_excess_pct"]).sum()/len(values)*100) if row["rs_excess_pct"] is not None and len(values) else None
    (OUTPUT/"latest.json").write_text(json.dumps(source,separators=(",",":"),allow_nan=False))
    return OUTPUT
