import importlib.util
import lzma
import struct
import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

dec = load("decoder", "scripts/decode_dukascopy_datafeed_m1.py")
gate = load("gate", "scripts/stage3b_2026_public_datafeed_preflight.py")

class TestDecoder(unittest.TestCase):
    @staticmethod
    def pack(rows):
        raw = b"".join(struct.pack(">5if", *row) for row in rows)
        return lzma.compress(raw, format=lzma.FORMAT_ALONE)

    def test_eurusd_fixture_semantics_match_pinned_v1464_field_order(self):
        payload = self.pack([
            (0, 114543, 114569, 114542, 114570, 293.760009765625),
            (60, 114569, 114575, 114565, 114580, 271.5899963378906),
        ])
        rows = dec.decode_payload(payload, "EURUSD", date(2019, 2, 4))
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0].timestamp, 1549238400000)
        self.assertAlmostEqual(rows[0].open, 1.14543)
        self.assertAlmostEqual(rows[0].high, 1.14570)
        self.assertAlmostEqual(rows[0].low, 1.14542)
        self.assertAlmostEqual(rows[0].close, 1.14569)
        self.assertAlmostEqual(rows[0].volume, 293.760009765625)
        self.assertAlmostEqual(rows[1].open, 1.14569)
        self.assertAlmostEqual(rows[1].close, 1.14575)

    def test_xauusd_factor_is_frozen_1000(self):
        payload = self.pack([(0, 2650123, 2650456, 2649987, 2650789, 12.5)])
        row = dec.decode_payload(payload, "XAUUSD", date(2026, 6, 1))[0]
        self.assertAlmostEqual(row.open, 2650.123)
        self.assertAlmostEqual(row.close, 2650.456)
        self.assertAlmostEqual(row.low, 2649.987)
        self.assertAlmostEqual(row.high, 2650.789)

    def test_malformed_and_nonminute_payloads_fail(self):
        with self.assertRaises(ValueError):
            dec.decode_payload(lzma.compress(b"x", format=lzma.FORMAT_ALONE), "EURUSD", date(2026, 6, 1))
        with self.assertRaises(ValueError):
            dec.decode_payload(self.pack([(1, 100000, 100000, 99999, 100001, 1.0)]), "EURUSD", date(2026, 6, 1))

    def test_ohlc_and_order_fail_closed(self):
        with self.assertRaises(ValueError):
            dec.decode_payload(self.pack([(0, 100000, 100010, 100020, 100005, 1.0)]), "EURUSD", date(2026, 6, 1))
        with self.assertRaises(ValueError):
            dec.decode_payload(self.pack([
                (60, 100000, 100000, 99999, 100001, 1.0),
                (0, 100000, 100000, 99999, 100001, 1.0),
            ]), "EURUSD", date(2026, 6, 1))

class TestGuard(unittest.TestCase):
    def test_zero_based_month_and_exact_url(self):
        u = gate.build_url(gate.RequestSpec("XAUUSD", "ASK", date(2026, 6, 1)))
        self.assertEqual(u, "https://datafeed.dukascopy.com/datafeed/XAUUSD/2026/05/01/ASK_candles_min_1.bi5")

    def test_scope_and_side_mutations_fail(self):
        bad = [
            gate.RequestSpec("BTCUSD", "BID", date(2026, 6, 1)),
            gate.RequestSpec("EURUSD", "ASK", date(2026, 6, 1)),
            gate.RequestSpec("XAUUSD", "BID", date(2026, 5, 31)),
            gate.RequestSpec("XAUUSD", "BID", date(2026, 10, 9)),
            gate.RequestSpec("XAUUSD", "BID", date(2025, 6, 1)),
            gate.RequestSpec("XAUUSD", "BID", date(2026, 12, 1)),
        ]
        for spec in bad:
            with self.assertRaises(PermissionError):
                gate.build_url(spec)

    def test_request_budget_is_exact_and_provider_disabled(self):
        plan = gate.static_plan()
        self.assertEqual(plan["logical_series"], 8)
        self.assertEqual(plan["calendar_days"], 130)
        self.assertEqual(plan["sanity_gets"], 8)
        self.assertEqual(plan["full_get_opportunities"], 1040)
        self.assertEqual(plan["hard_get_cap"], 1050)
        self.assertEqual(plan["max_attempts"], 1)
        self.assertEqual(plan["retries_after_provider_failure"], 0)
        self.assertFalse(plan["provider_enabled"])
        with self.assertRaises(PermissionError):
            gate.require_provider_execution_authorized()

    def test_sanity_specs_are_exactly_eight(self):
        specs = gate.sanity_specs()
        self.assertEqual(len(specs), 8)
        self.assertEqual(len({(x.instrument, x.side) for x in specs}), 8)
        self.assertTrue(all(x.day == date(2026, 6, 1) for x in specs))
        for x in specs:
            gate.validate_request(x)

if __name__ == "__main__":
    unittest.main()
