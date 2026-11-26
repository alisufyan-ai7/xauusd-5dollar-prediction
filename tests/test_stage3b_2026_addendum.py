"""No-provider D-120 synthetic science and chronology tests."""
import importlib.util
from pathlib import Path
import unittest

source=Path(__file__).resolve().parents[1]/"scripts"/"stage3b_2026_addendum.py"
spec=importlib.util.spec_from_file_location("stage3b_2026_addendum",source)
g=importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

class TestGovernance(unittest.TestCase):
    def test_owner_execution_approval_absent(self):
        with self.assertRaises(PermissionError):
            g.market_request("XAUUSD_BID","2026-06-01T00:00:00Z","2026-10-09T00:00:00Z")
        with self.assertRaises(ValueError):
            g.market_request("XAUUSD_BID","2026-06-01T00:00:00Z","2026-12-01T00:00:00Z",owner_final_approval=True)
        with self.assertRaises(ValueError):
            g.market_request("BTCUSD_BID","2026-06-01T00:00:00Z","2026-10-09T00:00:00Z",owner_final_approval=True)

    def test_hard_fence_and_approved_window_only(self):
        g.fail_on_new_source_window("2026-06-01T00:00:00Z","2026-10-09T00:00:00Z")
        with self.assertRaises(ValueError):
            g.fail_on_new_source_window("2026-05-01T00:00:00Z","2026-10-09T00:00:00Z")

    def test_retroactive_calendar_evidence_is_missing(self):
        base={"family":"NFP","release_at_utc":"2026-10-02T12:30:00Z","source_url":"https://www.bls.gov/schedule/2026/","published_at_utc":"2026-11-01T00:00:00Z","pre_release_schedule_evidence":True}
        self.assertIsNone(g.causal_calendar_entry(base,"2026-10-02T12:29:00Z"))
        self.assertIsNone(g.causal_calendar_entry({**base,"published_at_utc":None},"2026-10-02T12:29:00Z"))
        good={**base,"published_at_utc":"2026-09-01T00:00:00Z"}
        self.assertEqual(g.causal_calendar_entry(good,"2026-10-02T12:29:00Z")["family"],"NFP")
        self.assertIsNone(g.causal_calendar_entry({**good,"superseded_at_utc":"2026-10-01T00:00:00Z"},"2026-10-02T12:29:00Z"))
        self.assertIsNone(g.causal_calendar_entry({**good,"pre_release_schedule_evidence":False},"2026-10-02T12:29:00Z"))
        with self.assertRaises(ValueError):
            g.causal_calendar_entry({**good,"actual":14},"2026-10-02T12:29:00Z")

    def test_us_dst(self):
        self.assertEqual(g.convert_et(2026,7,6,8,30),"2026-07-06T12:30:00Z")
        self.assertEqual(g.convert_et(2026,11,6,8,30),"2026-11-06T13:30:00Z")

    def test_bounded_cold_start_not_hidden_history(self):
        self.assertTrue(g.accepted_cold_start("2026-07-06T14:10:00Z"))
        with self.assertRaises(ValueError):
            g.accepted_cold_start("2026-07-06T14:10:00Z","2026-05-01T00:00:00Z")
        with self.assertRaises(ValueError):
            g.accepted_cold_start("2026-12-01T00:00:00Z")

    def test_allowlist_rejects_leakage(self):
        f=[{"name":f"xauusd_m1_market_state.col_{i}","arm":"GOLD"} for i in range(92)]+[{"name":f"xauusd_m1_market_state.other_{i}","arm":"FULL_ONLY"} for i in range(63)]
        gold,full=g.allowlisted_columns(f)
        self.assertEqual((len(gold),len(full)),(92,155))
        with self.assertRaises(ValueError):
            g.allowlisted_columns(f+[f[0]])
        with self.assertRaises(ValueError):
            g.allowlisted_columns(f[:-1]+[{"name":"trade_risk_state_template.entry_price","arm":"FULL_ONLY"}])

if __name__=="__main__": unittest.main()
