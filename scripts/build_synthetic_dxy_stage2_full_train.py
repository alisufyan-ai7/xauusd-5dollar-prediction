#!/usr/bin/env python3
"""Build continuous 2016-2021 synthetic DXY without annual state resets.

Reads the already-acquired annual Dukascopy BID M1 constituent files from the
Stage 2 same-snapshot directory. Processing is year-at-a-time for bounded
memory, while the rolling level history is carried across year boundaries.

No XAUUSD data or future labels are read.
"""

from __future__ import annotations

import csv
import json
import math
import sys
from collections import deque
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
START_YEAR = 2016
END_YEAR = 2021

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
            if ts % ONE_MINUTE_MS != 0:
                raise SystemExit(f"DXY_OFF_GRID_TIMESTAMP:{path}:{ts}")
            if ts in out:
                raise SystemExit(f"DXY_DUPLICATE_TIMESTAMP:{path}:{ts}")
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


def rolling_rv(level_by_ts: dict[int, float], ts: int, n: int):
    start = ts - (n - 1) * ONE_MINUTE_MS
    seq = []
    for t in range(start, ts + ONE_MINUTE_MS, ONE_MINUTE_MS):
        x = level_by_ts.get(t)
        if x is None:
            return None
        seq.append(x)
    if len(seq) != n:
        return None
    rets = [seq[i] - seq[i - 1] for i in range(1, len(seq))]
    return math.sqrt(sum(x * x for x in rets) / len(rets)) if rets else 0.0


def main(argv: list[str]) -> None:
    if len(argv) != 4:
        raise SystemExit(
            "usage: build_synthetic_dxy_stage2_full_train.py "
            "<raw-fx-bid-dir> <out.csv> <report.json>"
        )

    raw_dir = Path(argv[1])
    out_path = Path(argv[2])
    report_path = Path(argv[3])
    out_path.parent.mkdir(parents=True, exist_ok=True)

    per_year = {}
    total_common = 0
    total_union = 0
    first_ts = None
    last_ts = None
    complete_rolling = {15: 0, 60: 0, 240: 0}

    # Only the recent 240 calendar minutes can contribute to frozen DXY
    # changes/RV. Keep a bounded cross-year cache rather than all six years.
    recent: dict[int, float] = {}
    recent_order: deque[int] = deque()

    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()

        previous_output_ts = None

        for year in range(START_YEAR, END_YEAR + 1):
            nxt = year + 1
            data = {}
            paths = {}
            for name, _ in CONSTITUENTS:
                p = raw_dir / f"{name}-{year}-01-01-{nxt}-01-01-m1-bid.csv"
                if not p.exists():
                    raise SystemExit(f"DXY_MISSING_ANNUAL_INPUT:{year}:{name}:{p}")
                paths[name] = str(p)
                data[name] = load_close(p)

            union = set()
            common = None
            for name, _ in CONSTITUENTS:
                s = set(data[name])
                union.update(s)
                common = s if common is None else common & s
            times = sorted(common or [])

            if times and previous_output_ts is not None and times[0] <= previous_output_ts:
                raise SystemExit(
                    f"DXY_CROSS_YEAR_NONMONOTONIC:{year}:{times[0]}:{previous_output_ts}"
                )

            year_complete = {15: 0, 60: 0, 240: 0}
            for ts in times:
                level = CONSTANT
                for name, exponent in CONSTITUENTS:
                    level *= data[name][ts] ** exponent
                if not math.isfinite(level) or level <= 0:
                    raise SystemExit(f"DXY_NONFINITE:{ts}")

                recent[ts] = level
                recent_order.append(ts)

                # Retain enough exact timestamps to calculate the 240-minute
                # lookback at the current row, including across Dec/Jan.
                cutoff = ts - 240 * ONE_MINUTE_MS
                while recent_order and recent_order[0] < cutoff:
                    old = recent_order.popleft()
                    recent.pop(old, None)

                row = {
                    "dxy_bar_start_ms": str(ts),
                    "dxy_available_time_ms": str(ts + ONE_MINUTE_MS),
                    "dxy_level": fmt(level),
                }

                for n in (1, 5, 15, 60, 240):
                    prev = recent.get(ts - n * ONE_MINUTE_MS)
                    row[f"dxy_change_{n}m"] = fmt(level - prev) if prev is not None else ""

                for n in (15, 60, 240):
                    rv = rolling_rv(recent, ts, n)
                    row[f"dxy_rv_{n}m"] = fmt(rv)
                    if rv is not None:
                        year_complete[n] += 1
                        complete_rolling[n] += 1

                w.writerow(row)
                previous_output_ts = ts
                if first_ts is None:
                    first_ts = ts
                last_ts = ts

            per_year[str(year)] = {
                "constituent_rows": {name: len(data[name]) for name, _ in CONSTITUENTS},
                "union_timestamps": len(union),
                "common_timestamps": len(times),
                "common_share_of_union": (len(times) / len(union)) if union else None,
                "first_bar_start_ms": times[0] if times else None,
                "last_bar_start_ms": times[-1] if times else None,
                "complete_rolling_rows": {str(k): v for k, v in year_complete.items()},
                "inputs": paths,
            }
            total_common += len(times)
            total_union += len(union)

            # Release annual constituent dictionaries before next year.
            del data

    report = {
        "status": "PASS",
        "scope": "2016-2021_TRAIN_CONTINUOUS",
        "series": "SYNTHETIC_DXY_DUKASCOPY_BID",
        "formula_constant": CONSTANT,
        "exponents": {name: exponent for name, exponent in CONSTITUENTS},
        "years": per_year,
        "common_timestamps_sum_by_year": total_common,
        "union_timestamps_sum_by_year": total_union,
        "common_share_of_union_sum_by_year": (
            total_common / total_union if total_union else None
        ),
        "first_bar_start_ms": first_ts,
        "last_bar_start_ms": last_ts,
        "complete_rolling_rows": {str(k): v for k, v in complete_rolling.items()},
        "cross_year_state_preserved": True,
        "sealed_xauusd_periods_accessed": [],
        "output": str(out_path),
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv)
