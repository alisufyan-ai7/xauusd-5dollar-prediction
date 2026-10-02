#!/usr/bin/env python3
"""Synchronize XAUUSD BID/ASK M1 for Information Parity V1 Stage 2.

This mirrors the frozen EXP-002 synchronization semantics, but writes one
combined market-state table and preserves whether either side was reconstructed.
"""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

FIELDS = [
    "timestamp_ms", "decision_time_ms",
    "bid_open", "bid_high", "bid_low", "bid_close", "bid_volume",
    "ask_open", "ask_high", "ask_low", "ask_close", "ask_volume",
    "spread_open", "spread_close",
    "bid_flat_fill", "ask_flat_fill",
]
ONE_MINUTE_MS = 60_000


def load(path: Path) -> dict[int, dict]:
    out: dict[int, dict] = {}
    with path.open(encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        required = ["timestamp", "open", "high", "low", "close", "volume"]
        if r.fieldnames != required:
            raise SystemExit(f"UNEXPECTED_SCHEMA:{path}:{r.fieldnames}")
        for row in r:
            out[int(row["timestamp"])] = row
    return out


def flat(ts: int, close: float) -> dict:
    s = f"{close:.10f}".rstrip("0").rstrip(".")
    return {
        "timestamp": str(ts),
        "open": s,
        "high": s,
        "low": s,
        "close": s,
        "volume": "0",
    }


def pair_valid(b: dict, a: dict) -> bool:
    return (
        float(a["open"]) >= float(b["open"])
        and float(a["high"]) >= float(b["high"])
        and float(a["low"]) >= float(b["low"])
        and float(a["close"]) >= float(b["close"])
    )


def fmt(x: float) -> str:
    if not math.isfinite(x):
        raise SystemExit("NONFINITE_OUTPUT")
    return f"{x:.10f}".rstrip("0").rstrip(".")


def main(argv: list[str]) -> None:
    if len(argv) != 4:
        raise SystemExit(
            "usage: synchronize_information_parity_m1.py "
            "<bid.csv> <ask.csv> <out.csv>"
        )

    bid = load(Path(argv[1]))
    ask = load(Path(argv[2]))
    times = sorted(set(bid) | set(ask))

    last_bid = None
    last_ask = None
    rows = []
    bid_flat_fills = 0
    ask_flat_fills = 0
    leading_dropped = 0
    invalid_flat_fill_dropped = 0

    for ts in times:
        rb = bid.get(ts)
        ra = ask.get(ts)

        if rb is not None:
            last_bid = float(rb["close"])
        if ra is not None:
            last_ask = float(ra["close"])

        bid_fill = False
        ask_fill = False

        if rb is None:
            if last_bid is None:
                leading_dropped += 1
                continue
            b = flat(ts, last_bid)
            bid_fill = True
        else:
            b = rb

        if ra is None:
            if last_ask is None:
                leading_dropped += 1
                continue
            a = flat(ts, last_ask)
            ask_fill = True
        else:
            a = ra

        if not pair_valid(b, a):
            if rb is not None and ra is not None:
                raise SystemExit(f"OBSERVED_PAIR_OHLC_INVERSION:{ts}")
            invalid_flat_fill_dropped += 1
            continue

        bo, bh, bl, bc, bv = (
            float(b["open"]), float(b["high"]), float(b["low"]),
            float(b["close"]), float(b["volume"])
        )
        ao, ah, al, ac, av = (
            float(a["open"]), float(a["high"]), float(a["low"]),
            float(a["close"]), float(a["volume"])
        )
        so = ao - bo
        sc = ac - bc
        if so < 0 or sc < 0:
            raise SystemExit(f"NEGATIVE_SPREAD:{ts}")

        if bid_fill:
            bid_flat_fills += 1
        if ask_fill:
            ask_flat_fills += 1

        rows.append({
            "timestamp_ms": str(ts),
            "decision_time_ms": str(ts + ONE_MINUTE_MS),
            "bid_open": fmt(bo),
            "bid_high": fmt(bh),
            "bid_low": fmt(bl),
            "bid_close": fmt(bc),
            "bid_volume": fmt(bv),
            "ask_open": fmt(ao),
            "ask_high": fmt(ah),
            "ask_low": fmt(al),
            "ask_close": fmt(ac),
            "ask_volume": fmt(av),
            "spread_open": fmt(so),
            "spread_close": fmt(sc),
            "bid_flat_fill": "1" if bid_fill else "0",
            "ask_flat_fill": "1" if ask_fill else "0",
        })

    out = Path(argv[3])
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

    print(json.dumps({
        "status": "PASS",
        "rows": len(rows),
        "bid_flat_fills": bid_flat_fills,
        "ask_flat_fills": ask_flat_fills,
        "leading_unpaired_dropped": leading_dropped,
        "invalid_flat_fill_dropped": invalid_flat_fill_dropped,
        "first_timestamp_ms": int(rows[0]["timestamp_ms"]) if rows else None,
        "last_timestamp_ms": int(rows[-1]["timestamp_ms"]) if rows else None,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv)
