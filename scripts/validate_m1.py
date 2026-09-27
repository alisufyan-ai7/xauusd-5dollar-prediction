#!/usr/bin/env python3
import csv
import hashlib
import json
import math
import sys
from pathlib import Path

EXPECTED = ["timestamp", "open", "high", "low", "close", "volume"]
ONE_MINUTE_MS = 60_000

def fail(msg: str) -> None:
    raise SystemExit(f"VALIDATION_FAILED: {msg}")

def parse_float(value: str, name: str, row_num: int) -> float:
    try:
        x = float(value)
    except ValueError:
        fail(f"row {row_num}: {name} is not numeric")
    if not math.isfinite(x):
        fail(f"row {row_num}: {name} is not finite")
    return x

def validate(path: Path) -> dict:
    if not path.exists() or path.stat().st_size == 0:
        fail("file missing or empty")

    sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
    rows = 0
    first_ts = None
    last_ts = None
    previous_ts = None
    duplicate_timestamps = 0
    non_monotonic = 0
    off_grid = 0
    price_errors = 0

    with path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != EXPECTED:
            fail(f"unexpected columns: {reader.fieldnames!r}; expected {EXPECTED!r}")

        for row_num, row in enumerate(reader, start=2):
            rows += 1
            try:
                ts = int(row["timestamp"])
            except ValueError:
                fail(f"row {row_num}: timestamp is not integer epoch milliseconds")

            o = parse_float(row["open"], "open", row_num)
            h = parse_float(row["high"], "high", row_num)
            l = parse_float(row["low"], "low", row_num)
            c = parse_float(row["close"], "close", row_num)
            v = parse_float(row["volume"], "volume", row_num)

            if min(o, h, l, c) <= 0:
                price_errors += 1
            if h < max(o, c) or l > min(o, c) or h < l:
                price_errors += 1
            if v < 0:
                fail(f"row {row_num}: negative volume")

            if ts % ONE_MINUTE_MS != 0:
                off_grid += 1

            if previous_ts is not None:
                if ts == previous_ts:
                    duplicate_timestamps += 1
                elif ts < previous_ts:
                    non_monotonic += 1

            first_ts = ts if first_ts is None else first_ts
            last_ts = ts
            previous_ts = ts

    if rows == 0:
        fail("CSV contains no data rows")
    if duplicate_timestamps:
        fail(f"{duplicate_timestamps} duplicate timestamps")
    if non_monotonic:
        fail(f"{non_monotonic} non-monotonic timestamps")
    if off_grid:
        fail(f"{off_grid} timestamps are not aligned to exact M1 boundaries")
    if price_errors:
        fail(f"{price_errors} OHLC consistency/positivity errors")

    result = {
        "status": "PASS",
        "file": str(path),
        "sha256": sha256,
        "rows": rows,
        "first_timestamp_ms": first_ts,
        "last_timestamp_ms": last_ts,
        "schema": EXPECTED,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return result

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: validate_m1.py <csv-path>")
    validate(Path(sys.argv[1]))
