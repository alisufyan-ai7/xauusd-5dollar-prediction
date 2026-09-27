#!/usr/bin/env python3
"""Validate Dukascopy XAUUSD tick CSV containing ASK and BID."""

import csv
import hashlib
import json
import math
import sys
from pathlib import Path

REQUIRED = ["timestamp", "askPrice", "bidPrice"]
OPTIONAL = ["askVolume", "bidVolume"]


def main(argv):
    if len(argv) != 2:
        raise SystemExit("usage: validate_dukascopy_ticks.py <ticks.csv>")

    p = Path(argv[1])
    n = 0
    prev = None
    bad_spread = 0
    first = None
    last = None

    with p.open(encoding="utf-8-sig", newline="") as fobj:
        reader = csv.DictReader(fobj)
        fields = reader.fieldnames or []
        if fields[:3] != REQUIRED or any(x not in REQUIRED + OPTIONAL for x in fields):
            raise SystemExit(f"UNEXPECTED_COLUMNS:{fields}")

        for row in reader:
            ts = int(row["timestamp"])
            ask = float(row["askPrice"])
            bid = float(row["bidPrice"])
            vals = [ask, bid]

            if "askVolume" in fields:
                vals.append(float(row["askVolume"]))
            if "bidVolume" in fields:
                vals.append(float(row["bidVolume"]))

            if prev is not None and ts < prev:
                raise SystemExit("NONMONOTONIC_TIMESTAMP")
            if not all(math.isfinite(x) for x in vals):
                raise SystemExit("NONFINITE")
            if ask <= 0 or bid <= 0:
                raise SystemExit("INVALID_PRICE")
            if "askVolume" in fields and float(row["askVolume"]) < 0:
                raise SystemExit("INVALID_ASK_VOLUME")
            if "bidVolume" in fields and float(row["bidVolume"]) < 0:
                raise SystemExit("INVALID_BID_VOLUME")
            if ask < bid:
                bad_spread += 1

            if first is None:
                first = ts
            last = ts
            prev = ts
            n += 1

    if n == 0:
        raise SystemExit("EMPTY_TICK_FILE")
    if bad_spread:
        raise SystemExit(f"NEGATIVE_SPREAD_ROWS:{bad_spread}")

    h = hashlib.sha256(p.read_bytes()).hexdigest()
    print(json.dumps({
        "status": "PASS",
        "rows": n,
        "first_timestamp": first,
        "last_timestamp": last,
        "sha256": h,
        "columns": fields,
    }, indent=2))


if __name__ == "__main__":
    main(sys.argv)
