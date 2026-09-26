#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

with tempfile.TemporaryDirectory() as td:
    td=Path(td)
    a=td/"a.csv"
    b=td/"b.csv"
    out=td/"manifest.json"
    a.write_text(
        "timestamp,open,high,low,close,volume\n"
        "0,100,101,99,100,1\n"
        "60000,100,101,99,100,1\n",
        encoding="utf-8"
    )
    b.write_text(
        "timestamp,open,high,low,close,volume\n"
        "120000,100,101,99,100,1\n"
        "240000,100,101,99,100,1\n",
        encoding="utf-8"
    )
    subprocess.run([sys.executable, str(ROOT/"scripts"/"build_manifest.py"), str(out), str(a), str(b)], check=True)
    m=json.loads(out.read_text())
    assert m["schema_version"] == 1
    assert m["total_rows"] == 4
    assert len(m["chunks"]) == 2
    assert m["chunks"][0]["gap_count"] == 0
    assert m["chunks"][1]["gap_count"] == 1
    assert m["chunks"][1]["missing_minutes_between_observed_bars"] == 1
    assert len(m["chunks"][0]["sha256"]) == 64

print("manifest smoke test passed")
