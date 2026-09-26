#!/usr/bin/env python3
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ONE_MINUTE_MS = 60_000

def pct(n, d):
    return round(100.0 * n / d, 6) if d else 0.0

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def load_raw(path: Path):
    rows = list(csv.DictReader(path.open("r", encoding="utf-8-sig", newline="")))
    ts = [int(r["timestamp"]) for r in rows]
    gaps = []
    for a, b in zip(ts, ts[1:]):
        delta = b - a
        if delta != ONE_MINUTE_MS:
            gaps.append({
                "from_timestamp_ms": a,
                "to_timestamp_ms": b,
                "delta_minutes": delta / ONE_MINUTE_MS,
                "missing_minutes_between": max(0, int(delta / ONE_MINUTE_MS) - 1),
            })
    return rows, ts, gaps

def load_labels(path: Path):
    return list(csv.DictReader(path.open("r", encoding="utf-8", newline="")))

def summarize(raw_path: Path, labels_path: Path, out_path: Path):
    raw, ts, gaps = load_raw(raw_path)
    labels = load_labels(labels_path)
    if len(raw) != len(labels):
        raise SystemExit(f"row-count mismatch raw={len(raw)} labels={len(labels)}")

    buy = Counter(r["buy_label"] for r in labels)
    sell = Counter(r["sell_label"] for r in labels)
    coverage_complete = sum(r["coverage_complete"] == "True" for r in labels)
    coverage_incomplete = len(labels) - coverage_complete

    report = {
        "status": "PASS",
        "raw_file": str(raw_path),
        "labels_file": str(labels_path),
        "raw_sha256": sha256(raw_path),
        "labels_sha256": sha256(labels_path),
        "rows": len(raw),
        "first_timestamp_ms": ts[0] if ts else None,
        "last_timestamp_ms": ts[-1] if ts else None,
        "gap_count": len(gaps),
        "total_missing_minutes_between_observed_bars": sum(g["missing_minutes_between"] for g in gaps),
        "largest_gap_minutes": max((g["delta_minutes"] for g in gaps), default=1),
        "coverage_complete_rows": coverage_complete,
        "coverage_incomplete_rows": coverage_incomplete,
        "coverage_incomplete_pct": pct(coverage_incomplete, len(labels)),
        "buy_counts": dict(buy),
        "sell_counts": dict(sell),
        "buy_ambiguous_pct": pct(buy.get("AMBIGUOUS", 0), len(labels)),
        "sell_ambiguous_pct": pct(sell.get("AMBIGUOUS", 0), len(labels)),
        "buy_success_pct_all_rows": pct(buy.get("SUCCESS", 0), len(labels)),
        "sell_success_pct_all_rows": pct(sell.get("SUCCESS", 0), len(labels)),
        "gaps_preview": gaps[:20],
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return report

def main(argv):
    if len(argv) != 4:
        raise SystemExit("usage: diagnose_exp001.py <raw.csv> <labels.csv> <report.json>")
    summarize(Path(argv[1]), Path(argv[2]), Path(argv[3]))

if __name__ == "__main__":
    main(sys.argv)
