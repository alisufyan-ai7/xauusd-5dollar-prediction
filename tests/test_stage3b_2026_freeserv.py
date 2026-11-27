import json
import sys
import unittest
from urllib.parse import parse_qs, urlsplit
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import stage3b_2026_freeserv_preflight as m

class TestD148FreeServ(unittest.TestCase):
    def test_exact_frozen_series_and_provider_disabled(self):
        self.assertEqual(len(m.SERIES), 8)
        self.assertEqual(len(m.ALLOWED), 8)
        self.assertIn(("XAU/USD", "B"), m.ALLOWED)
        self.assertIn(("XAU/USD", "A"), m.ALLOWED)
        self.assertFalse(m.PROVIDER_EXECUTION_ENABLED)
        with self.assertRaises(PermissionError):
            m.require_provider_execution_authorized()

    def test_exact_m1_bid_ask_query_semantics(self):
        bid = m.RequestSpec("XAU/USD", "B", m.START_MS, 2)
        ask = m.RequestSpec("XAU/USD", "A", m.START_MS, 2)
        for spec, side in ((bid, "B"), (ask, "A")):
            url = m.build_url(spec)
            parts = urlsplit(url)
            self.assertEqual(parts.netloc, "freeserv.dukascopy.com")
            self.assertEqual(parts.path, "/2.0/index.php")
            q = parse_qs(parts.query)
            self.assertEqual(q["path"], ["chart/json3"])
            self.assertEqual(q["interval"], ["1MIN"])
            self.assertEqual(q["offer_side"], [side])
            self.assertEqual(q["time_direction"], ["N"])
            self.assertEqual(q["last_update"], [str(m.START_MS)])
            self.assertEqual(q["limit"], ["2"])
            self.assertEqual(len(q["jsonp"][0]), len("_callbacks____") + 9)

    def test_scope_limit_and_side_mutations_fail_closed(self):
        bad = [
            m.RequestSpec("BTC/USD", "B", m.START_MS, 2),
            m.RequestSpec("EUR/USD", "A", m.START_MS, 2),
            m.RequestSpec("XAU/USD", "B", m.START_MS - 1, 2),
            m.RequestSpec("XAU/USD", "B", m.END_EXCLUSIVE_MS, 2),
            m.RequestSpec("XAU/USD", "B", m.START_MS, 0),
            m.RequestSpec("XAU/USD", "B", m.START_MS, 30001),
        ]
        for spec in bad:
            with self.assertRaises(PermissionError):
                m.build_url(spec)

    def test_strict_jsonp_and_row_decode(self):
        spec = m.RequestSpec("EUR/USD", "B", m.START_MS, 2)
        cb = m.request_params(spec)["jsonp"]
        data = [
            [m.START_MS, 1.1, 1.2, 1.0, 1.15, 12.0, None],
            [m.START_MS + 60000, 1.15, 1.25, 1.1, 1.2, 13.0],
        ]
        raw = f"{cb}({json.dumps(data)});"
        rows = m.decode_candle_rows(m.parse_jsonp(raw, cb))
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0].timestamp, m.START_MS)
        self.assertEqual(rows[1].volume, 13.0)
        with self.assertRaises(ValueError):
            m.parse_jsonp(raw, cb + "x")
        with self.assertRaises(ValueError):
            m.parse_jsonp(f"{cb}({json.dumps({'x': 1})});", cb)

    def test_malformed_rows_fail_closed(self):
        cases = [
            [[m.START_MS, 1, 2, 0.5, 1.5]],
            [[m.START_MS, 1, 2, 0.5, 1.5, 2, "unexpected"]],
            [[m.START_MS, 1, 0.9, 1.1, 1.0, 2]],
            [[m.START_MS, 1, 2, 0.5, 1.5, -1]],
            [[m.START_MS, 1, 2, 0.5, 1.5, 2], [m.START_MS, 1, 2, 0.5, 1.5, 2]],
        ]
        for raw in cases:
            with self.assertRaises(ValueError):
                m.decode_candle_rows(raw)

    def test_duplicate_cursor_handling_and_nonadvancement(self):
        rows = m.decode_candle_rows([
            [m.START_MS, 1, 2, 0.5, 1.5, 2],
            [m.START_MS + 60000, 1.5, 2, 1, 1.8, 3],
        ])
        work, cursor = m.normalize_page(rows, m.START_MS, first_page=False)
        self.assertEqual(len(work), 1)
        self.assertEqual(cursor, m.START_MS + 60000)
        only_dup = m.decode_candle_rows([[m.START_MS, 1, 2, 0.5, 1.5, 2]])
        with self.assertRaises(ValueError):
            m.normalize_page(only_dup, m.START_MS, first_page=False)

    def test_half_open_row_fence(self):
        rows = m.decode_candle_rows([
            [m.START_MS, 1, 2, 0.5, 1.5, 2],
            [m.END_EXCLUSIVE_MS, 1, 2, 0.5, 1.5, 2],
        ])
        accepted = m.rows_inside_fence(rows)
        self.assertEqual([x.timestamp for x in accepted], [m.START_MS])
        before = m.decode_candle_rows([[m.START_MS - 60000, 1, 2, 0.5, 1.5, 2]])
        with self.assertRaises(PermissionError):
            m.rows_inside_fence(before)

    def test_static_budget_plan_is_bounded(self):
        p = m.static_plan()
        self.assertEqual(p["logical_series"], 8)
        self.assertEqual(p["calendar_days"], 130)
        self.assertEqual(p["theoretical_calendar_slots_per_series"], 187200)
        self.assertEqual(p["theoretical_full_pages_per_series_if_pages_fill"], 7)
        self.assertEqual(p["sanity_requests"], 8)
        self.assertEqual(p["full_page_limit"], 30000)
        self.assertEqual(p["proposed_max_full_requests_per_series"], 11)
        self.assertEqual(p["proposed_max_total_requests"], 96)
        self.assertEqual(p["retries_after_provider_failure"], 0)
        self.assertFalse(p["provider_enabled"])

if __name__ == "__main__":
    unittest.main()
