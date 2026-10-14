import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"pipeline"))
from engine import metrics


def fixture():
    bars=[{"t":f"day-{i}","o":100.,"h":101.,"l":99.,"c":100.,"v":100000} for i in range(100)]
    bars.append({"t":"2026-10-12","o":104.,"h":111.,"l":103.,"c":110.,"v":400000})
    p={"symbol":"TEST","close":110.}
    return bars,p


class PriceTests(unittest.TestCase):
    def test_strict_candidate(self):
        b,p=fixture();r=metrics(b,p)
        self.assertTrue(r["ep_candidate"]);self.assertEqual(r["rvol"],4)
        self.assertEqual(r["neglect_score"],90)

    def test_current_volume_not_in_baseline(self):
        b,p=fixture();b[-1]["v"]=10000000
        r=metrics(b,p);self.assertEqual(r["rvol"],100)
        self.assertEqual(r["prior_avg_vol20"],100000)

    def test_exact_three_percent_gap_fails(self):
        b,p=fixture();b[-1]["o"]=103.
        self.assertFalse(metrics(b,p)["gates"]["gap"])

    def test_exact_three_times_volume_fails(self):
        b,p=fixture();b[-1]["v"]=300000
        self.assertFalse(metrics(b,p)["ep_candidate"])

    def test_close_position_threshold(self):
        b,p=fixture();b[-1].update(o=104.,h=120.,l=100.,c=113.)
        self.assertTrue(metrics(b,p)["gates"]["close_position"])
        b[-1]["c"]=112.99
        self.assertFalse(metrics(b,p)["gates"]["close_position"])

    def test_zero_range_is_not_false_confirmation(self):
        b,p=fixture();b[-1].update(o=110.,h=110.,l=110.,c=110.)
        r=metrics(b,p);self.assertIsNone(r["close_position_pct"]);self.assertFalse(r["ep_candidate"])

    def test_faded_gap_excluded(self):
        b,p=fixture();b[-1].update(o=109.,c=108.)
        self.assertFalse(metrics(b,p)["gates"]["positive_session"])

    def test_volume_led_is_not_strict_gap(self):
        b,p=fixture();b[-1]["o"]=100.5;b[-1]["l"]=100.
        r=metrics(b,p);self.assertFalse(r["ep_candidate"]);self.assertTrue(r["volume_led"])

    def test_neglect_does_not_include_event_day(self):
        b,p=fixture();a=metrics(b,p);b[-1].update(v=90000000,c=109.)
        z=metrics(b,p)
        for k in ("neglect_score","neglect_reasons","return20_prior","return60_prior","volume_contraction"):
            self.assertEqual(a[k],z[k])

    def test_new_listing_neglect_unknown(self):
        b,p=fixture();r=metrics(b[-21:],p)
        self.assertIsNone(r["neglect_score"]);self.assertFalse(r["ep_candidate"])

    def test_invalid_price_rejected(self):
        b,p=fixture();b[-1]["l"]=-1
        with self.assertRaises(ValueError):metrics(b,p)
