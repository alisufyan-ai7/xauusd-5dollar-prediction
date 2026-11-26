"""Deterministic provider-free synthetic tests for a bounded 2026 design."""
from __future__ import annotations
import importlib.util
from datetime import datetime, timezone
from pathlib import Path
import unittest
import json
import tempfile

script = Path(__file__).resolve().parents[1] / "scripts" / "stage3b_2026_preflight.py"
spec = importlib.util.spec_from_file_location("stage3b_2026_preflight", script)
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)


class TestPreflight(unittest.TestCase):
    def fail(self, fn, *args):
        with self.assertRaises(ValueError):
            fn(*args)

    def test_boundary_fence(self):
        p.check_market_request("XAUUSD_BID", "2026-06-01T00:00:00Z", "2026-10-09T00:00:00Z")
        for a, b in [("2025-12-31T23:59:00Z", "2026-01-01T00:01:00Z"),
                     ("2026-10-08T23:59:00Z", "2026-10-09T00:01:00Z"),
                     ("2026-11-01T00:00:00Z", "2026-11-02T00:00:00Z"),
                     ("2026-12-01T00:00:00Z", "2026-12-02T00:00:00Z"),
                     ("2022-01-01T00:00:00Z", "2022-01-02T00:00:00Z")]:
            self.fail(p.check_market_request, "XAUUSD_BID", a, b)
        self.fail(p.check_market_request, "US10Y_BID", "2026-07-06T00:00:00Z", "2026-07-07T00:00:00Z")
        self.fail(p.check_market_request, "XAUUSD_BID", "2026-08-02T00:00:00Z", "2026-08-01T00:00:00Z")
        self.fail(p.check_market_request, "XAUUSD_BID", "2026-08-01T00:00:00+05:00", "2026-08-02T00:00:00Z")
        self.fail(p.check_market_row, "EURUSD_BID", "2026-10-09T00:00:00Z")

    def test_budget(self):
        p.check_budget(350*1024**2, 750*1024**2, 1)
        self.fail(p.check_budget, 350*1024**2+1, 0, 1)
        self.fail(p.check_budget, 0, 750*1024**2+1, 1)
        self.fail(p.check_budget, 0, 0, 2)

    def test_interval_censoring(self):
        ev={"primary_task_a_eligible":"true", "interval_start_utc":"2026-07-06T14:10:00Z", "interval_end_utc":"2026-07-06T14:12:00Z", "interval_width_minutes":"3"}
        e=p.expand_event(ev)
        self.assertEqual([v for _,v in e], [1/3]*3)
        self.assertAlmostEqual(sum(v for _,v in e),1)
        self.assertEqual(e[0][0],datetime(2026,7,6,14,10,tzinfo=timezone.utc))
        self.assertEqual(e[-1][0],datetime(2026,7,6,14,12,tzinfo=timezone.utc))
        self.assertAlmostEqual(p.pool_event([.2,.4,.9]),.5)
        self.fail(p.expand_event,{**ev,"interval_width_minutes":"1"})
        self.fail(p.expand_event,{**ev,"interval_end_utc":"2026-07-06T14:15:00Z","interval_width_minutes":"6"})
        self.assertEqual(p.expand_event({**ev,"primary_task_a_eligible":"false"}),[])

    def test_availability(self):
        at=lambda m: datetime(2026,7,6,14,m,tzinfo=timezone.utc)
        self.assertEqual(p.align_causal(at(12),[at(11),at(13)]),at(11))
        self.assertIsNone(p.align_causal(at(10),[at(11)]))
        self.assertEqual(p.align_causal(at(12),[at(12),at(13)]),at(12))

    def test_lodo(self):
        ev=[{"event_id":"a1","source_date":"2026-07-06"},{"event_id":"a2","source_date":"2026-07-06"},{"event_id":"b1","source_date":"2026-07-07"}]
        f=p.lodo(ev)
        self.assertEqual(len(f),2)
        self.assertEqual(f[0][2],["a1","a2"])
        self.assertEqual(f[1][2],["b1"])
        self.fail(p.lodo,ev+[ev[0]])

    def test_class_mass(self):
        ev=[{"event_id":"A1","event_type":"COMMIT_LONG","primary_task_a_eligible":"true"},
            {"event_id":"A2","event_type":"COMMIT_SHORT","primary_task_a_eligible":"true"},
            {"event_id":"N","event_type":"DEFER_WAIT","primary_task_a_eligible":"true"}]
        mass=p.class_normalized_mass(ev)
        self.assertEqual(mass,{"A1":.25,"A2":.25,"N":.5})
        self.fail(p.class_normalized_mass,ev[:2])

    def test_parity(self):
        p.audit_feature_parity(["event1_m0","event1_m1"],["event1_m0","event1_m1"])
        self.fail(p.audit_feature_parity,["event1_m0"],["event1_m1"])
        self.fail(p.audit_feature_parity,["event1_m0","event1_m0"],["event1_m0","event1_m0"])

    def test_calendar_point_in_time(self):
        ev={"document_published_utc":"2026-05-01T12:00:00Z","event_family":"NFP","archive_url":"https://www.bls.gov/schedule/2026/","historical_schedule_verified":True}
        p.require_calendar_provenance(ev,"2026-07-06T14:00:00Z")
        self.fail(p.require_calendar_provenance,{**ev,"document_published_utc":"2026-08-01T00:00:00Z"},"2026-07-06T14:00:00Z")
        self.fail(p.require_calendar_provenance,{**ev,"historical_schedule_verified":False},"2026-07-06T14:00:00Z")
        self.fail(p.require_calendar_provenance,{**ev,"event_family":"SURPRISE"},"2026-07-06T14:00:00Z")

    def test_frozen_counts_and_39_fold_fixture(self):
        from datetime import timedelta
        start=datetime(2026,7,6,14,0,tzinfo=timezone.utc)
        events=[]
        for i in range(107+143):
            day=i % 39
            date=(start+timedelta(days=day)).date().isoformat()
            minute=10+(i//39)*3+(0 if i<107 else 20)
            t=(start+timedelta(days=day,minutes=minute)).isoformat().replace("+00:00","Z")
            events.append({"event_id":str(i),"source_date":date,
                           "primary_task_a_eligible":"true", "event_type":"COMMIT_LONG" if i<107 else "HARD_REJECT",
                           "interval_start_utc":t,"interval_end_utc":t,"interval_width_minutes":"1"})
        self.assertEqual(p.validate_source_manifest(events),{"eligible_act":107,"eligible_p3":143,"source_dates":39,"paired_dates":39})
        self.assertEqual(len(p.lodo(events)),39)
        self.fail(p.validate_source_manifest,events[:-1])

    def test_dst_offsets_for_macro_and_session(self):
        from zoneinfo import ZoneInfo
        ny=ZoneInfo("America/New_York")
        london=ZoneInfo("Europe/London")
        self.assertEqual(datetime(2026,7,6,8,30,tzinfo=ny).astimezone(timezone.utc).hour,12)
        self.assertEqual(datetime(2026,12,3,8,30,tzinfo=ny).astimezone(timezone.utc).hour,13)
        self.assertEqual(datetime(2026,7,6,8,0,tzinfo=london).astimezone(timezone.utc).hour,7)
        self.assertEqual(datetime(2026,12,3,8,0,tzinfo=london).astimezone(timezone.utc).hour,8)

    def test_feature_manifest_guards(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"manifest.json"
            good={"status":"PREFLIGHT_DESIGN_NO_PROVIDER","features":[
                {"name":"bid_close","arm":"GOLD","source_table":"xauusd_m1_market_state"},
                {"name":"spread_close","arm":"FULL_ONLY","source_table":"xauusd_m1_market_state"}]}
            path.write_text(json.dumps(good))
            obj=p.read_manifest(path)
            self.assertEqual(p.feature_columns(obj,"GOLD"),("bid_close",))
            self.assertEqual(p.feature_columns(obj,"FULL"),("bid_close","spread_close"))
            for bad in [[{**good["features"][0],"name":"future_return"}], good["features"]+[good["features"][0]]]:
                path.write_text(json.dumps({**good,"features":bad}))
                self.fail(p.read_manifest,path)


if __name__ == "__main__":
    unittest.main()
