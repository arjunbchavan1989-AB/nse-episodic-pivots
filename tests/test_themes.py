import copy,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"pipeline"))
from themes import apply_themes


def row():
    return {"symbol":"GOODLUCK","mover":True,"neglect_pass":True,
            "gates":{"rvol":True,"close_position":True,"positive_session":True},
            "catalyst":{"sources":[],"strength":None}}


class StoryTests(unittest.TestCase):
    def test_reviewed_story_ep(self):
        r=row();apply_themes([r],"2026-10-12")
        self.assertTrue(r["story_ep"]);self.assertEqual(r["catalyst"]["strength"],3)
        self.assertTrue(r["catalyst"]["status"]=="Primary filing reviewed")

    def test_future_review_not_used(self):
        r=row();apply_themes([r],"2026-10-09");self.assertFalse(r["story_valid"])

    def test_expired_story_not_used(self):
        r=row();apply_themes([r],"2026-11-20");self.assertFalse(r["story_ep"])

    def test_no_tape_confirmation_no_story_ep(self):
        r=row();r["gates"]["rvol"]=False;apply_themes([r],"2026-10-12")
        self.assertTrue(r["story_valid"]);self.assertFalse(r["story_ep"])

    def test_cancellation_suppresses_story(self):
        r=row();r["catalyst"]["sources"]=[{"title":"Goodluck restructuring withdrawn","official":True,"summary":"","candidate":False,"publisher":"NSE","published_at":"2026-10-12T15:00:00+05:30"}]
        apply_themes([r],"2026-10-12");self.assertFalse(r["story_valid"])

    def test_sector_headline_alone_not_valid(self):
        r=row();r["symbol"]="TEST";r["catalyst"]["sources"]=[{"title":"TEST wins a defence order","official":False,"summary":"","candidate":True,"publisher":"CNBC TV18","published_at":"2026-10-12T15:00:00+05:30"}]
        apply_themes([r],"2026-10-12");self.assertFalse(r["story_valid"]);self.assertEqual(r["stories"][0]["status"],"Narrative candidate, unverified")
