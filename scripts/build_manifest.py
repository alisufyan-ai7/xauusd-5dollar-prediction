#!/usr/bin/env python3
import csv
import hashlib
import json
import sys
from pathlib import Path

ONE_MINUTE_MS = 60_000
EXPECTED = ["timestamp", "open", "high", "low", "close", "volume"]

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def inspect_csv(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader=csv.DictReader(f)
        if reader.fieldnames != EXPECTED:
            raise SystemExit(f"unexpected columns in {path}: {reader.fieldnames!r}")
        rows=0
        first=None
        last=None
        prev=None
        gaps=0
        missing_minutes=0
        largest_gap=1
        for row in reader:
            ts=int(row["timestamp"])
            rows+=1
            if first is None:
                first=ts
            if prev is not None:
                delta=ts-prev
                if delta != ONE_MINUTE_MS:
                    gaps+=1
                    mins=delta/ONE_MINUTE_MS
                    largest_gap=max(largest_gap, mins)
                    if mins > 1:
                        missing_minutes += int(mins)-1
            prev=ts
            last=ts
    if rows == 0:
        raise SystemExit(f"empty CSV: {path}")
    return {
        "file": str(path),
        "sha256": sha256(path),
        "rows": rows,
        "first_timestamp_ms": first,
        "last_timestamp_ms": last,
        "gap_count": gaps,
        "missing_minutes_between_observed_bars": missing_minutes,
        "largest_gap_minutes": largest_gap,
    }

def build(paths, out_path: Path):
    entries=[inspect_csv(Path(p)) for p in paths]
    manifest={
        "schema_version": 1,
        "instrument": "XAUUSD",
        "timeframe": "M1",
        "price_side": "BID",
        "source": "Dukascopy public historical feed",
        "chunks": entries,
        "total_rows": sum(e["rows"] for e in entries),
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(manifest, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))

if __name__=="__main__":
    if len(sys.argv) < 3:
        raise SystemExit("usage: build_manifest.py <output.json> <csv> [<csv> ...]")
    build(sys.argv[2:], Path(sys.argv[1]))
