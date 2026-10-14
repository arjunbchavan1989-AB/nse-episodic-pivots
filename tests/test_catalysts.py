import sys,unittest
from datetime import datetime
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"pipeline"))
from catalysts import describe,IST,stamp

START=datetime(2026,10,9,15,30,tzinfo=IST)
END=datetime(2026,10,12,15,30,tzinfo=IST)
OPEN=END.replace(hour=9,minute=15)


def news(title="Acme Steel wins a contract",official=False,when="2026-10-12T08:00:00+05:30",summary=""):
    return {"title":title,"official":official,"published_at":when,"summary":summary,
            "url":"https://nsearchives.nseindia.com/corporate/ACME_notice.pdf" if official else "https://example.com/article",
            "publisher":"NSE" if official else "Example"}


class CatalystTests(unittest.TestCase):
    def test_headline_cap(self):
        r=describe(news(),"Acme Steel Limited","ACME",START,END,OPEN)
        self.assertEqual(r["strength"],2);self.assertTrue(r["candidate"])

    def test_preopen_primary_strength(self):
        r=describe(news("Acme Steel Limited",True,summary="Company has received a contract"),"Acme Steel Limited","ACME",START,END,OPEN)
        self.assertEqual(r["strength"],4)

    def test_future_news_excluded(self):
        self.assertIsNone(describe(news(when="2026-10-13T08:00:00+05:30"),"Acme Steel Limited","ACME",START,END,OPEN))

    def test_afterclose_excluded(self):
        self.assertIsNone(describe(news(when="2026-10-12T16:00:00+05:30"),"Acme Steel Limited","ACME",START,END,OPEN))

    def test_intraday_primary_is_capped(self):
        r=describe(news("Acme Steel Limited",True,when="2026-10-12T12:00:00+05:30",summary="Company received a contract"),"Acme Steel Limited","ACME",START,END,OPEN)
        self.assertEqual(r["strength"],3);self.assertEqual(r["timing"],"During session")

    def test_negative_not_bullish(self):
        r=describe(news("Acme Steel contract cancelled"),"Acme Steel Limited","ACME",START,END,OPEN)
        self.assertFalse(r["candidate"]);self.assertEqual(r["strength"],0)

    def test_routine_intimation_not_earnings_catalyst(self):
        r=describe(news("Acme Steel Limited",True,summary="Board Meeting Intimation for financial results"),"Acme Steel Limited","ACME",START,END,OPEN)
        self.assertFalse(r["candidate"]);self.assertEqual(r["strength"],0)

    def test_wrong_company_not_attached(self):
        self.assertIsNone(describe(news("Another Steel wins a contract"),"Acme Steel Limited","ACME",START,END,OPEN))

    def test_date_formats(self):
        self.assertEqual(stamp("12-Oct-2026 08:00:00").hour,8)
        self.assertIsNone(stamp("undated"))

    def test_speculative_order_not_completed_catalyst(self):
        r=describe(news("Acme Steel could win a government contract"),"Acme Steel Limited","ACME",START,END,OPEN)
        self.assertFalse(r["candidate"])

    def test_agm_approval_is_routine(self):
        r=describe(news("Acme Steel AGM resolutions get approval"),"Acme Steel Limited","ACME",START,END,OPEN)
        self.assertFalse(r["candidate"])

    def test_social_repost_not_fresh_event(self):
        item=news("Acme Steel wins a contract - LinkedIn");item["publisher"]="LinkedIn"
        r=describe(item,"Acme Steel Limited","ACME",START,END,OPEN)
        self.assertFalse(r["candidate"])
