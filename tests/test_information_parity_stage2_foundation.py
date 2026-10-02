#!/usr/bin/env python3
import csv
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def write_m1(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["timestamp", "open", "high", "low", "close", "volume"])
        w.writerows(rows)


def read_dicts(path: Path):
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def test_sync(tmp: Path):
    bid = tmp / "bid.csv"
    ask = tmp / "ask.csv"
    out = tmp / "sync.csv"

    write_m1(bid, [
        [0, 100, 101, 99, 100.5, 2],
        [60_000, 100.5, 102, 100, 101.5, 3],
        [120_000, 101.5, 103, 101, 102.5, 4],
    ])
    write_m1(ask, [
        [0, 100.2, 101.2, 99.2, 100.7, 5],
        [120_000, 101.7, 103.2, 101.2, 102.7, 6],
    ])

    subprocess.run([
        sys.executable,
        str(ROOT / "scripts/synchronize_information_parity_m1.py"),
        str(bid), str(ask), str(out)
    ], check=True, capture_output=True, text=True)

    rows = read_dicts(out)
    assert len(rows) == 3
    assert rows[0]["decision_time_ms"] == "60000"
    assert rows[1]["ask_flat_fill"] == "1"
    assert rows[1]["ask_volume"] == "0"
    assert float(rows[1]["spread_close"]) >= 0
    assert rows[2]["bid_flat_fill"] == "0"
    assert rows[2]["ask_flat_fill"] == "0"


def test_synthetic_dxy(tmp: Path):
    names = ["eurusd", "usdjpy", "gbpusd", "usdcad", "usdsek", "usdchf"]
    values = {
        "eurusd": [1.10, 1.11],
        "usdjpy": [110.0, 111.0],
        "gbpusd": [1.30, 1.31],
        "usdcad": [1.25, 1.26],
        "usdsek": [8.20, 8.21],
        "usdchf": [0.98, 0.99],
    }
    paths = []
    for name in names:
        p = tmp / f"{name}.csv"
        write_m1(p, [
            [0, values[name][0], values[name][0], values[name][0], values[name][0], 1],
            [60_000, values[name][1], values[name][1], values[name][1], values[name][1], 1],
        ])
        paths.append(p)

    out = tmp / "dxy.csv"
    report = tmp / "dxy.json"
    subprocess.run([
        sys.executable,
        str(ROOT / "scripts/build_synthetic_dxy_stage2.py"),
        *map(str, paths),
        str(out),
        str(report),
    ], check=True, capture_output=True, text=True)

    rows = read_dicts(out)
    assert len(rows) == 2
    assert rows[0]["dxy_available_time_ms"] == "60000"
    assert rows[1]["dxy_available_time_ms"] == "120000"

    constant = 50.14348112
    exponents = {
        "eurusd": -0.576,
        "usdjpy": 0.136,
        "gbpusd": -0.119,
        "usdcad": 0.091,
        "usdsek": 0.042,
        "usdchf": 0.036,
    }
    expected = constant
    for name in names:
        expected *= values[name][0] ** exponents[name]
    assert math.isclose(float(rows[0]["dxy_level"]), expected, rel_tol=1e-10)
    assert rows[0]["dxy_change_1m"] == ""
    assert math.isclose(
        float(rows[1]["dxy_change_1m"]),
        float(rows[1]["dxy_level"]) - float(rows[0]["dxy_level"]),
        rel_tol=1e-9,
        abs_tol=1e-9,
    )

    meta = json.loads(report.read_text())
    assert meta["status"] == "PASS"
    assert meta["common_timestamps"] == 2


def main():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        test_sync(tmp)
        test_synthetic_dxy(tmp)
    print("INFORMATION_PARITY_STAGE2_FOUNDATION_PASS")


if __name__ == "__main__":
    main()
