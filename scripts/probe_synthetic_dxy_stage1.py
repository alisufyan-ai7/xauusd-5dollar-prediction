#!/usr/bin/env python3
"""Stage-1 synthetic DXY feasibility probe.

Uses the published ICE DXY formula with Dukascopy M1 BID closes.
This script performs source-feasibility diagnostics only; it does not
calculate XAUUSD outcomes, P&L, or predictive scores.
"""

from __future__ import annotations

import csv
import json
import math
import statistics
import sys
from pathlib import Path

CONSTITUENTS = {
    "eurusd": -0.576,
    "usdjpy": 0.136,
    "gbpusd": -0.119,
    "usdcad": 0.091,
    "usdsek": 0.042,
    "usdchf": 0.036,
}
CONSTANT = 50.14348112


def load_close(path: Path) -> dict[int, float]:
    if not path.exists() or path.stat().st_size == 0:
        return {}
    with path.open(encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        fields = r.fieldnames or []
        if "timestamp" not in fields or "close" not in fields:
            raise SystemExit(f"MISSING_FIELDS:{path}:{fields}")
        out = {}
        for row in r:
            out[int(row["timestamp"])] = float(row["close"])
        return out


def corr(a: list[float], b: list[float]):
    if len(a) != len(b) or len(a) < 2:
        return None
    ma = statistics.fmean(a)
    mb = statistics.fmean(b)
    da = [x - ma for x in a]
    db = [x - mb for x in b]
    sa = math.sqrt(sum(x * x for x in da))
    sb = math.sqrt(sum(x * x for x in db))
    if sa == 0 or sb == 0:
        return None
    return sum(x * y for x, y in zip(da, db)) / (sa * sb)


def stats(xs: list[float]) -> dict:
    if not xs:
        return {"n": 0}
    ys = sorted(xs)
    def qp(p: float):
        x = p * (len(ys) - 1)
        lo = math.floor(x)
        hi = math.ceil(x)
        if lo == hi:
            return ys[lo]
        w = x - lo
        return ys[lo] * (1 - w) + ys[hi] * w
    return {
        "n": len(xs),
        "min": min(xs),
        "p50": qp(0.5),
        "mean": statistics.fmean(xs),
        "max": max(xs),
    }


def main(argv: list[str]) -> None:
    if len(argv) != 9:
        raise SystemExit(
            "usage: probe_synthetic_dxy_stage1.py "
            "<eurusd.csv> <usdjpy.csv> <gbpusd.csv> <usdcad.csv> "
            "<usdsek.csv> <usdchf.csv> <dukascopy_dxy.csv> <label>"
        )

    files = dict(zip(CONSTITUENTS, map(Path, argv[1:7])))
    official_path = Path(argv[7])
    label = argv[8]

    series = {k: load_close(v) for k, v in files.items()}
    common = None
    for s in series.values():
        keys = set(s)
        common = keys if common is None else common & keys
    times = sorted(common or [])

    synth = []
    for t in times:
        v = CONSTANT
        for k, exponent in CONSTITUENTS.items():
            px = series[k][t]
            if not math.isfinite(px) or px <= 0:
                raise SystemExit(f"INVALID_PRICE:{k}:{t}:{px}")
            v *= px ** exponent
        synth.append(v)

    official = load_close(official_path)
    overlap = [t for t in times if t in official]
    sv = []
    ov = []
    for t in overlap:
        i = times.index(t)
        sv.append(synth[i])
        ov.append(official[t])

    delta_s = [b - a for a, b in zip(sv, sv[1:])]
    delta_o = [b - a for a, b in zip(ov, ov[1:])]

    normalized_diff = []
    if sv and ov and sv[0] != 0 and ov[0] != 0:
        s0, o0 = sv[0], ov[0]
        normalized_diff = [
            (100 * s / s0) - (100 * o / o0)
            for s, o in zip(sv, ov)
        ]

    out = {
        "schema_version": "IPV1_SYNTH_DXY_PROBE_V1",
        "label": label,
        "formula": {
            "constant": CONSTANT,
            "exponents": CONSTITUENTS,
            "input_side": "BID_CLOSE",
            "series_name": "SYNTHETIC_DXY_DUKASCOPY_BID",
        },
        "constituent_rows": {k: len(v) for k, v in series.items()},
        "common_timestamps": len(times),
        "first_timestamp": times[0] if times else None,
        "last_timestamp": times[-1] if times else None,
        "synthetic_level_stats": stats(synth),
        "dukascopy_dxy_rows": len(official),
        "overlap_rows": len(overlap),
        "level_pearson": corr(sv, ov),
        "first_difference_pearson": corr(delta_s, delta_o),
        "normalized_tracking_difference_stats": stats(normalized_diff),
        "note": (
            "Source-feasibility only. Synthetic ICE-method DXY using Dukascopy "
            "M1 BID closes; not an official ICE market print."
        ),
    }

    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv)
