#!/usr/bin/env python3
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "label_exp001.py"
spec = importlib.util.spec_from_file_location("label_exp001", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules["label_exp001"] = mod
spec.loader.exec_module(mod)

Bar = mod.Bar
label_rows = mod.label_rows
ONE = mod.ONE_MINUTE_MS


def bar(n, o, h, l, c):
    return Bar(n * ONE, o, h, l, c, 1.0)


class Exp001LabelTests(unittest.TestCase):
    def test_buy_success_before_adverse(self):
        bars = [
            bar(0, 100, 101, 99, 100),
            bar(1, 100, 103, 99, 102),
            bar(2, 102, 105.2, 101, 105),
        ]
        r = list(label_rows(bars, horizon_minutes=2))[0]
        self.assertEqual(r["buy_label"], "SUCCESS")
        self.assertEqual(r["buy_terminal_bar_offset"], 2)
        self.assertAlmostEqual(r["buy_mfe"], 5.2)
        self.assertAlmostEqual(r["buy_mae"], 1.0)

    def test_buy_failure_before_target(self):
        bars = [
            bar(0, 100, 101, 99, 100),
            bar(1, 100, 101, 96.8, 97),
            bar(2, 97, 106, 97, 105),
        ]
        r = list(label_rows(bars, horizon_minutes=2))[0]
        self.assertEqual(r["buy_label"], "FAILURE")
        self.assertEqual(r["buy_terminal_bar_offset"], 1)

    def test_same_bar_dual_touch_is_ambiguous(self):
        bars = [
            bar(0, 100, 101, 99, 100),
            bar(1, 100, 105.1, 96.9, 101),
        ]
        r = list(label_rows(bars, horizon_minutes=1))[0]
        self.assertEqual(r["buy_label"], "AMBIGUOUS")
        self.assertEqual(r["sell_label"], "AMBIGUOUS")

    def test_unresolved(self):
        bars = [
            bar(0, 100, 101, 99, 100),
            bar(1, 100, 102, 99, 101),
            bar(2, 101, 102, 98.5, 100),
        ]
        r = list(label_rows(bars, horizon_minutes=2))[0]
        self.assertEqual(r["buy_label"], "UNRESOLVED")
        self.assertEqual(r["sell_label"], "UNRESOLVED")

    def test_sell_success(self):
        bars = [
            bar(0, 100, 101, 99, 100),
            bar(1, 100, 101, 96, 97),
            bar(2, 97, 98, 94.8, 95),
        ]
        r = list(label_rows(bars, horizon_minutes=2))[0]
        self.assertEqual(r["sell_label"], "SUCCESS")
        self.assertEqual(r["sell_terminal_bar_offset"], 2)

    def test_entry_bar_high_low_are_not_used(self):
        # Decision bar itself crosses both hypothetical barriers, but its close is
        # the entry. Future bar does nothing; result must remain unresolved.
        bars = [
            bar(0, 100, 106, 96, 100),
            bar(1, 100, 101, 99, 100),
        ]
        r = list(label_rows(bars, horizon_minutes=1))[0]
        self.assertEqual(r["buy_label"], "UNRESOLVED")
        self.assertEqual(r["sell_label"], "UNRESOLVED")

    def test_gap_does_not_extend_calendar_horizon(self):
        # Bar at minute 4 is outside a 2-minute horizon from decision at minute 1.
        bars = [
            bar(0, 100, 101, 99, 100),
            bar(4, 100, 110, 90, 100),
        ]
        r = list(label_rows(bars, horizon_minutes=2))[0]
        self.assertEqual(r["bars_observed"], 0)
        self.assertFalse(r["coverage_complete"])
        self.assertEqual(r["buy_label"], "UNRESOLVED")

    def test_full_coverage_flag(self):
        bars = [bar(i, 100, 101, 99, 100) for i in range(4)]
        r = list(label_rows(bars, horizon_minutes=3))[0]
        self.assertTrue(r["coverage_complete"])
        self.assertEqual(r["bars_observed"], 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
