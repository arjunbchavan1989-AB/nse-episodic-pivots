import json,sys,tempfile,unittest
from datetime import datetime,timedelta
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"pipeline"))
import run


def source():
    return {"last_trading_date":str(datetime.now(ZoneInfo("Asia/Kolkata")).date()-timedelta(days=1)),
            "filters":{"min_market_cap_cr":500,"min_avg_volume_shares":70000,"min_avg_rupee_vol_cr":3,
                       "min_avg_daily_range_pct":3,"avg_volume_window_days":20},
            "coverage_pct":100,"rows":[{"symbol":"TEST"}]}


class Guards(unittest.TestCase):
    def check(self,payload,message):
        with tempfile.TemporaryDirectory() as tmp:
            upstream=Path(tmp)/"upstream";upstream.mkdir()
            (upstream/"latest.json").write_text(json.dumps(payload))
            web=Path(tmp)/"web";(web/"data").mkdir(parents=True)
            good=web/"data/latest.json";good.write_text('{"last_good":true}')
            with patch.object(run,"WEB",web):
                with self.assertRaisesRegex(RuntimeError,message):run.scan(upstream)
            self.assertEqual(json.loads(good.read_text()),{"last_good":True})

    def test_low_upstream_coverage(self):
        d=source();d["coverage_pct"]=90;self.check(d,"coverage below 95%")

    def test_missing_charts(self):
        self.check(source(),"Chart coverage below 95%")

    def test_universe_filter_drift(self):
        d=source();d["filters"]["min_market_cap_cr"]=100;self.check(d,"filters changed")

    def test_future_session(self):
        d=source();d["last_trading_date"]=str(datetime.now(ZoneInfo("Asia/Kolkata")).date()+timedelta(days=2))
        self.check(d,"future")
