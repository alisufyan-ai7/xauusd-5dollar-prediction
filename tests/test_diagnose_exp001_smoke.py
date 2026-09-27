#!/usr/bin/env python3
import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    raw = td / "raw.csv"
    labels = td / "labels.csv"
    report = td / "report.json"

    raw.write_text(
        "timestamp,open,high,low,close,volume\n"
        "0,100,101,99,100,1\n"
        "60000,100,102,99,101,1\n"
        "120000,101,106,100,105,1\n"
        "300000,105,106,104,105,1\n",
        encoding="utf-8",
    )
    subprocess.run([sys.executable, str(ROOT/"scripts"/"label_exp001.py"), str(raw), str(labels)], check=True)
    subprocess.run([sys.executable, str(ROOT/"scripts"/"diagnose_exp001.py"), str(raw), str(labels), str(report)], check=True)
    data = json.loads(report.read_text())
    assert data["rows"] == 4
    assert data["gap_count"] == 1
    assert data["total_missing_minutes_between_observed_bars"] == 2
    assert data["raw_sha256"]
    assert data["labels_sha256"]

print("diagnostic smoke test passed")
