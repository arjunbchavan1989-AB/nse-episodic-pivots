import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"pipeline"))
from run import align_previous_session

class PreviousSessionTests(unittest.TestCase):
    def fixture(self,bad=0):
        rows=[{"symbol":str(i)} for i in range(100)]
        charts={str(i):{"bars":[{"t":"2026-10-15" if i<bad else "2026-10-16"},{"t":"2026-10-19"}]} for i in range(100)}
        return rows,charts
    def test_complete_history_kept(self):
        r,c=self.fixture();kept,charts,bad,coverage=align_previous_session(r,c,"2026-10-16",100)
        self.assertEqual((len(kept),len(charts),len(bad),coverage),(100,100,0,100))
    def test_one_bad_history_is_excluded_not_filled(self):
        r,c=self.fixture(1);kept,charts,bad,coverage=align_previous_session(r,c,"2026-10-16",100)
        self.assertEqual(coverage,99)
        self.assertNotIn("0",charts)
        self.assertEqual(bad[0]["symbol"],"0")
    def test_too_many_bad_histories_fail_closed(self):
        r,c=self.fixture(6)
        with self.assertRaisesRegex(RuntimeError,"below 95%"):align_previous_session(r,c,"2026-10-16",100)
    def test_no_majority_vote_can_override_verified_calendar(self):
        r,c=self.fixture(100)
        with self.assertRaisesRegex(RuntimeError,"below 95%"):align_previous_session(r,c,"2026-10-16",100)
    def test_missing_exchange_calendar_is_not_assumed(self):
        r,c=self.fixture()
        with self.assertRaisesRegex(RuntimeError,"not verified"):align_previous_session(r,c,None,100)
