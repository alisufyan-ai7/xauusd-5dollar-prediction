#!/usr/bin/env python3
"""Build canonical SYNTHETIC_DXY_DUKASCOPY_BID M1 table.

Uses only exact synchronized constituent M1 BID closes and the published ICE
DXY formula frozen in the Stage 2 preregistration. No XAUUSD outcomes are read.
"""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

CONSTITUENTS = (
    ("eurusd", -0.576),
    ("usdjpy", 0.136),
    ("gbpusd", -0.119),
    ("usdcad", 0.091),
    ("usdsek", 0.042),
    ("usdchf", 0.036),
)
CONSTANT = 50.14348112
ONE_MINUTE_MS = 60_000

FIELDS = [
    "dxy_bar_start_ms",
    "dxy_available_time_ms",
    "dxy_level",
    "dxy_change_1m",
    "dxy_change_5m",
    "dxy_change_15m",
    "dxy_change_60m",
    "dxy_change_240m",
    "dxy_rv_15m",
    "dxy_rv_60m",
    "dxy_rv_240m",
]


def load_close(path: Path) -> dict[int, float]:
    out: dict[int, float] = {}
    with path.open(encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        if not r.fieldnames or "timestamp" not in r.fieldnames or "close" not in r.fieldnames:
            raise SystemExit(f"DXY_INPUT_SCHEMA:{path}:{r.fieldnames}")
        for row in r:
            ts = int(row["timestamp"])
            px = float(row["close"])
            if not math.isfinite(px) or px <= 0:
                raise SystemExit(f"DXY_INPUT_PRICE:{path}:{ts}:{px}")
            out[ts] = px
    return out


def fmt(x):
    if x is None:
        return ""
    if not math.isfinite(float(x)):
        return ""
    return f"{float(x):.12g}"


def main(argv: list[str]) -> None:
    if len(argv) != 9:
        raise SystemExit(
            "usage: build_synthetic_dxy_stage2.py "
            "<eurusd.csv> <usdjpy.csv> <gbpusd.csv> <usdcad.csv> "
            "<usdsek.csv> <usdchf.csv> <out.csv> <report.json>"
        )

    paths = {name: Path(p) for (name, _), p in zip(CONSTITUENTS, argv[1:7])}
    out_path = Path(argv[7])
    report_path = Path(argv[8])

    data = {name: load_close(path) for name, path in paths.items()}
    common = None
    for name, _ in CONSTITUENTS:
        s = set(data[name])
        common = s if common is None else common & s
    times = sorted(common or [])

    levels: dict[int, float] = {}
    for ts in times:
        level = CONSTANT
        for name, exponent in CONSTITUENTS:
            level *= data[name][ts] ** exponent
        if not math.isfinite(level) or level <= 0:
            raise SystemExit(f"DXY_NONFINITE:{ts}")
        levels[ts] = level

    rows = []
    complete_by_window = {15: 0, 60: 0, 240: 0}
    for ts in times:
        level = levels[ts]
        row = {
            "dxy_bar_start_ms": str(ts),
            "dxy_available_time_ms": str(ts + ONE_MINUTE_MS),
            "dxy_level": fmt(level),
        }

        for n in (1, 5, 15, 60, 240):
            prev = levels.get(ts - n * ONE_MINUTE_MS)
            row[f"dxy_change_{n}m"] = fmt(level - prev) if prev is not None else ""

        for n in (15, 60, 240):
            start = ts - (n - 1) * ONE_MINUTE_MS
            seq = []
            ok = True
            for t in range(start, ts + ONE_MINUTE_MS, ONE_MINUTE_MS):
                x = levels.get(t)
                if x is None:
                    ok = False
                    break
                seq.append(x)
            if ok and len(seq) == n:
                rets = [seq[i] - seq[i - 1] for i in range(1, len(seq))]
                rv = math.sqrt(sum(x * x for x in rets) / len(rets)) if rets else 0.0
                row[f"dxy_rv_{n}m"] = fmt(rv)
                complete_by_window[n] += 1
            else:
                row[f"dxy_rv_{n}m"] = ""

        rows.append(row)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

    union = set()
    for name, _ in CONSTITUENTS:
        union.update(data[name])

    report = {
        "status": "PASS",
        "series": "SYNTHETIC_DXY_DUKASCOPY_BID",
        "formula_constant": CONSTANT,
        "exponents": {name: exponent for name, exponent in CONSTITUENTS},
        "constituent_rows": {name: len(data[name]) for name, _ in CONSTITUENTS},
        "union_timestamps": len(union),
        "common_timestamps": len(times),
        "common_share_of_union": (len(times) / len(union)) if union else None,
        "first_bar_start_ms": times[0] if times else None,
        "last_bar_start_ms": times[-1] if times else None,
        "complete_rolling_rows": {str(k): v for k, v in complete_by_window.items()},
        "output": str(out_path),
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv)
