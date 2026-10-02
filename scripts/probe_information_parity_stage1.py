#!/usr/bin/env python3
"""Compact Stage-1 source-feasibility probe summaries.

This script does not calculate trading outcomes or profitability. It only
summarizes schema, timestamps, continuity, spread, volume behavior, hashes,
and file-size practicality for preregistered tiny samples.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
import sys
from pathlib import Path
from typing import Iterable


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def q(values: list[float], p: float):
    if not values:
        return None
    xs = sorted(values)
    if len(xs) == 1:
        return xs[0]
    x = p * (len(xs) - 1)
    lo = int(math.floor(x))
    hi = int(math.ceil(x))
    if lo == hi:
        return xs[lo]
    w = x - lo
    return xs[lo] * (1 - w) + xs[hi] * w


def finite_stats(values: Iterable[float]) -> dict:
    xs = [float(x) for x in values if math.isfinite(float(x))]
    if not xs:
        return {"n": 0}
    return {
        "n": len(xs),
        "min": min(xs),
        "p05": q(xs, 0.05),
        "p50": q(xs, 0.50),
        "mean": statistics.fmean(xs),
        "p95": q(xs, 0.95),
        "max": max(xs),
    }


def load_csv(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        fields = r.fieldnames or []
        return fields, list(r)


def summarize_m1(path: Path) -> dict:
    fields, rows = load_csv(path)
    required = ["timestamp", "open", "high", "low", "close"]
    if any(k not in fields for k in required):
        raise SystemExit(f"M1_MISSING_REQUIRED:{path}:{fields}")

    ts = []
    vols = []
    price_errors = 0
    for i, row in enumerate(rows):
        t = int(row["timestamp"])
        ts.append(t)
        o, h, l, c = [float(row[k]) for k in ("open", "high", "low", "close")]
        if not all(math.isfinite(x) for x in (o, h, l, c)):
            price_errors += 1
        if min(o, h, l, c) <= 0 or h < max(o, c) or l > min(o, c) or h < l:
            price_errors += 1
        if "volume" in fields and row.get("volume", "") != "":
            vols.append(float(row["volume"]))

    nonmono = 0
    duplicate = 0
    offgrid = 0
    gap_count = 0
    largest_gap_minutes = 0.0
    for i, t in enumerate(ts):
        if t % 60000:
            offgrid += 1
        if i:
            d = t - ts[i - 1]
            if d < 0:
                nonmono += 1
            elif d == 0:
                duplicate += 1
            elif d > 60000:
                gap_count += 1
                largest_gap_minutes = max(largest_gap_minutes, d / 60000)

    volume_invalid = sum(1 for x in vols if not math.isfinite(x) or x < 0)
    zero_share = None
    if vols:
        zero_share = sum(1 for x in vols if x == 0) / len(vols)

    return {
        "file": path.name,
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
        "schema": fields,
        "rows": len(rows),
        "first_timestamp": ts[0] if ts else None,
        "last_timestamp": ts[-1] if ts else None,
        "off_m1_grid": offgrid,
        "duplicates": duplicate,
        "nonmonotonic": nonmono,
        "gap_count": gap_count,
        "largest_gap_minutes": largest_gap_minutes,
        "price_errors": price_errors,
        "volume_present": "volume" in fields,
        "volume_invalid": volume_invalid,
        "volume_zero_share": zero_share,
        "volume_stats": finite_stats(vols),
    }


def pearson(a: list[float], b: list[float]):
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


def summarize_m1_pair(bid_path: Path, ask_path: Path) -> dict:
    bf, br = load_csv(bid_path)
    af, ar = load_csv(ask_path)
    for f in (bf, af):
        for k in ("timestamp", "close", "volume"):
            if k not in f:
                raise SystemExit(f"PAIR_MISSING_FIELD:{k}")

    bmap = {int(r["timestamp"]): r for r in br}
    amap = {int(r["timestamp"]): r for r in ar}
    common = sorted(set(bmap) & set(amap))
    spreads = []
    bv = []
    av = []
    equal = 0
    for t in common:
        b = bmap[t]
        a = amap[t]
        spreads.append(float(a["close"]) - float(b["close"]))
        x, y = float(b["volume"]), float(a["volume"])
        bv.append(x)
        av.append(y)
        if x == y:
            equal += 1

    return {
        "bid_file": bid_path.name,
        "ask_file": ask_path.name,
        "bid_rows": len(br),
        "ask_rows": len(ar),
        "common_timestamps": len(common),
        "bid_only_timestamps": len(set(bmap) - set(amap)),
        "ask_only_timestamps": len(set(amap) - set(bmap)),
        "spread_stats": finite_stats(spreads),
        "negative_spread_rows": sum(1 for x in spreads if x < 0),
        "volume_equal_share": equal / len(common) if common else None,
        "volume_pearson": pearson(bv, av),
        "bid_volume_stats": finite_stats(bv),
        "ask_volume_stats": finite_stats(av),
    }


def summarize_ticks(path: Path) -> dict:
    fields, rows = load_csv(path)
    required = ["timestamp", "askPrice", "bidPrice"]
    if any(k not in fields for k in required):
        raise SystemExit(f"TICK_MISSING_REQUIRED:{path}:{fields}")

    ts = []
    spreads = []
    askv = []
    bidv = []
    nonmono = 0
    negative_spread = 0

    for i, row in enumerate(rows):
        t = int(row["timestamp"])
        if ts and t < ts[-1]:
            nonmono += 1
        ts.append(t)
        ask = float(row["askPrice"])
        bid = float(row["bidPrice"])
        s = ask - bid
        spreads.append(s)
        if s < 0:
            negative_spread += 1
        if "askVolume" in fields and row.get("askVolume", "") != "":
            askv.append(float(row["askVolume"]))
        if "bidVolume" in fields and row.get("bidVolume", "") != "":
            bidv.append(float(row["bidVolume"]))

    duration_minutes = None
    if len(ts) >= 2 and ts[-1] >= ts[0]:
        duration_minutes = (ts[-1] - ts[0]) / 60000
    rows_per_minute = None
    if duration_minutes and duration_minutes > 0:
        rows_per_minute = len(rows) / duration_minutes

    return {
        "file": path.name,
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
        "schema": fields,
        "rows": len(rows),
        "first_timestamp": ts[0] if ts else None,
        "last_timestamp": ts[-1] if ts else None,
        "nonmonotonic": nonmono,
        "negative_spread_rows": negative_spread,
        "spread_stats": finite_stats(spreads),
        "duration_minutes_observed": duration_minutes,
        "rows_per_observed_minute": rows_per_minute,
        "ask_volume_present": "askVolume" in fields,
        "bid_volume_present": "bidVolume" in fields,
        "ask_volume_stats": finite_stats(askv),
        "bid_volume_stats": finite_stats(bidv),
        "ask_volume_zero_share": (sum(1 for x in askv if x == 0) / len(askv)) if askv else None,
        "bid_volume_zero_share": (sum(1 for x in bidv if x == 0) / len(bidv)) if bidv else None,
    }


def main(argv: list[str]) -> None:
    if len(argv) < 3:
        raise SystemExit(
            "usage: probe_information_parity_stage1.py "
            "<m1|pair|tick> <files...>"
        )

    mode = argv[1]
    if mode == "m1":
        out = summarize_m1(Path(argv[2]))
    elif mode == "pair":
        if len(argv) != 4:
            raise SystemExit("pair requires BID.csv ASK.csv")
        out = summarize_m1_pair(Path(argv[2]), Path(argv[3]))
    elif mode == "tick":
        out = summarize_ticks(Path(argv[2]))
    else:
        raise SystemExit(f"unknown mode:{mode}")

    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv)
