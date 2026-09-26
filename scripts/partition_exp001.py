#!/usr/bin/env python3
"""Frozen EXP-001 chronological partition assignment."""

from __future__ import annotations
import csv
import datetime as dt
import json
import sys
from pathlib import Path

HORIZON_MS = 60 * 60 * 1000

UTC = dt.timezone.utc

def ms(s: str) -> int:
    d=dt.datetime.fromisoformat(s.replace("Z","+00:00"))
    return int(d.timestamp()*1000)

PARTITIONS = [
    ("TRAIN", ms("2016-01-01T00:00:00Z"), ms("2022-01-01T00:00:00Z")),
    ("VALIDATION", ms("2022-01-01T00:00:00Z"), ms("2023-01-01T00:00:00Z")),
    ("DEVELOPMENT_TEST", ms("2023-01-01T00:00:00Z"), ms("2025-01-01T00:00:00Z")),
    ("FINAL_OOS", ms("2025-01-01T00:00:00Z"), ms("2026-01-01T00:00:00Z")),
]

def assign(decision_time_ms: int) -> tuple[str | None, bool]:
    for name,start,end in PARTITIONS:
        if start <= decision_time_ms < end:
            eligible = decision_time_ms + HORIZON_MS <= end
            return name, eligible
    return None, False

def annotate(input_csv: Path, output_csv: Path) -> dict:
    with input_csv.open("r",encoding="utf-8",newline="") as f:
        reader=csv.DictReader(f)
        if "decision_time_ms" not in (reader.fieldnames or []):
            raise SystemExit("input labels must contain decision_time_ms")
        fieldnames=list(reader.fieldnames)+["partition","partition_boundary_eligible"]
        rows=list(reader)

    counts={name:{"rows":0,"eligible":0,"boundary_ineligible":0} for name,_,_ in PARTITIONS}
    outside=0

    output_csv.parent.mkdir(parents=True,exist_ok=True)
    with output_csv.open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            name,eligible=assign(int(row["decision_time_ms"]))
            row["partition"]=name or "OUTSIDE"
            row["partition_boundary_eligible"]=eligible
            if name is None:
                outside+=1
            else:
                counts[name]["rows"]+=1
                if eligible:
                    counts[name]["eligible"]+=1
                else:
                    counts[name]["boundary_ineligible"]+=1
            writer.writerow(row)

    report={"status":"PASS","counts":counts,"outside_rows":outside}
    print(json.dumps(report,indent=2,sort_keys=True))
    return report

if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("usage: partition_exp001.py <labels.csv> <partitioned.csv>")
    annotate(Path(sys.argv[1]),Path(sys.argv[2]))
