#!/usr/bin/env python3
"""Deterministic offline integration test for Stage 2 full-TRAIN orchestration.

No network or provider data. Six tiny annual TRAIN fixtures are generated to
exercise the continuous DXY builder, continuous information-layer builder,
full-range validator, normalized manifest, and final compact summary gate.
"""

from __future__ import annotations

import csv
import json
import math
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
UTC = timezone.utc
YEARS = tuple(range(2016, 2022))
M1 = 60_000

SYNC_FIELDS = [
    "timestamp_ms", "decision_time_ms",
    "bid_open", "bid_high", "bid_low", "bid_close", "bid_volume",
    "ask_open", "ask_high", "ask_low", "ask_close", "ask_volume",
    "spread_open", "spread_close", "bid_flat_fill", "ask_flat_fill",
]
RAW_FIELDS = ["timestamp", "open", "high", "low", "close", "volume"]
MACRO_FIELDS = [
    "event_id", "event_family", "scheduled_time_utc", "scheduled_time_local",
    "source_timezone", "source_agency", "source_document_id_or_url",
    "release_stage", "historical_exception_flag", "normalization_version",
]

MONDAYS = {
    2016: datetime(2016, 1, 4, tzinfo=UTC),
    2017: datetime(2017, 1, 2, tzinfo=UTC),
    2018: datetime(2018, 1, 1, tzinfo=UTC),
    2019: datetime(2019, 1, 7, tzinfo=UTC),
    2020: datetime(2020, 1, 6, tzinfo=UTC),
    2021: datetime(2021, 1, 4, tzinfo=UTC),
}


def run(cmd: list[str], env=None) -> subprocess.CompletedProcess:
    p = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        capture_output=True,
        env=env,
    )
    if p.returncode != 0:
        raise AssertionError(
            f"COMMAND_FAILED:{cmd}\nSTDOUT:\n{p.stdout}\nSTDERR:\n{p.stderr}"
        )
    return p


def ms(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)


def write_sync(path: Path, year: int):
    path.parent.mkdir(parents=True, exist_ok=True)
    start = MONDAYS[year]
    minutes = 5 * 24 * 60
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SYNC_FIELDS)
        w.writeheader()
        for i in range(minutes):
            ts = ms(start + timedelta(minutes=i))
            base = 1100.0 + (year - 2016) * 20 + 0.001 * i
            wave = 0.1 * math.sin(i / 37.0)
            close = base + wave
            open_ = close - 0.01 * math.sin(i / 11.0)
            high = max(open_, close) + 0.05
            low = min(open_, close) - 0.05
            spread = 0.4
            w.writerow({
                "timestamp_ms": ts,
                "decision_time_ms": ts + M1,
                "bid_open": open_,
                "bid_high": high,
                "bid_low": low,
                "bid_close": close,
                "bid_volume": 1.0 + 0.1 * math.sin(i / 17.0),
                "ask_open": open_ + spread,
                "ask_high": high + spread,
                "ask_low": low + spread,
                "ask_close": close + spread,
                "ask_volume": 1.1 + 0.1 * math.cos(i / 19.0),
                "spread_open": spread,
                "spread_close": spread,
                "bid_flat_fill": 0,
                "ask_flat_fill": 0,
            })


def write_fx(path: Path, year: int, base: float, slope: float):
    path.parent.mkdir(parents=True, exist_ok=True)
    start = MONDAYS[year]
    minutes = 5 * 24 * 60
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(RAW_FIELDS)
        for i in range(minutes):
            ts = ms(start + timedelta(minutes=i))
            px = base + slope * i + 0.00001 * math.sin(i / 29.0)
            pad = max(abs(px) * 1e-6, 1e-5)
            w.writerow([
                ts, px, px + pad, px - pad, px, 1.0
            ])


def write_macro(schedule: Path, coverage: Path):
    schedule.parent.mkdir(parents=True, exist_ok=True)
    families = ("CPI", "NFP", "JOLTS", "FOMC", "CLAIMS", "GDP")
    counts = {}
    rows = []
    for year in YEARS:
        counts[str(year)] = {fam: 1 for fam in families}
        for j, fam in enumerate(families):
            local = datetime.fromisoformat(
                f"{year}-01-{10+j:02d}T08:30:00-05:00"
            )
            utc = local.astimezone(UTC)
            rows.append({
                "event_id": f"synthetic-{year}-{fam}",
                "event_family": fam,
                "scheduled_time_utc": utc.isoformat(),
                "scheduled_time_local": local.isoformat(),
                "source_timezone": "America/New_York",
                "source_agency": "SYNTHETIC_PREFLIGHT",
                "source_document_id_or_url": "offline://full-train-preflight",
                "release_stage": "statement" if fam == "FOMC" else "",
                "historical_exception_flag": "0",
                "normalization_version": "IPV1_MACRO_SCHEDULE_V1",
            })

    rows.sort(key=lambda r: (r["scheduled_time_utc"], r["event_family"]))
    with schedule.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=MACRO_FIELDS)
        w.writeheader()
        w.writerows(rows)

    coverage.write_text(json.dumps({
        "status": "PASS",
        "schema_version": "IPV1_STAGE2_MACRO_COVERAGE_V1",
        "scope": "2016-2021_TRAIN_ONLY_PREFLIGHT",
        "sealed_xauusd_periods_accessed": [],
        "years": {
            str(year): {
                "counts": counts[str(year)],
                "family_pass": {fam: True for fam in families},
                "errors": [],
                "stage2_macro_schedule_available": True,
            }
            for year in YEARS
        },
    }, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        sync_dir = root / "sync"
        fx_dir = root / "fx"
        out = root / "out"
        reports = root / "reports"
        manifests = root / "manifests"
        layer = out / "layer"
        for p in (sync_dir, fx_dir, out, reports, manifests, layer):
            p.mkdir(parents=True, exist_ok=True)

        fx_def = {
            "eurusd": (1.10, 0.0000002),
            "usdjpy": (112.0, 0.00002),
            "gbpusd": (1.42, -0.0000001),
            "usdcad": (1.33, 0.0000001),
            "usdsek": (8.45, 0.000002),
            "usdchf": (0.99, -0.00000005),
        }

        for year in YEARS:
            write_sync(
                sync_dir / (
                    f"xauusd-{year}-01-01-{year+1}-01-01-m1-synchronized.csv"
                ),
                year,
            )
            for inst, (base, slope) in fx_def.items():
                write_fx(
                    fx_dir / (
                        f"{inst}-{year}-01-01-{year+1}-01-01-m1-bid.csv"
                    ),
                    year,
                    base + (year - 2016) * slope * 10_000,
                    slope,
                )

        dxy = out / "synthetic-dxy-2016-2021.csv"
        dxy_report = reports / "synthetic-dxy-2016-2021.json"
        run([
            sys.executable,
            str(ROOT / "scripts/build_synthetic_dxy_stage2_full_train.py"),
            str(fx_dir),
            str(dxy),
            str(dxy_report),
        ])

        macro = out / "macro-event-schedule-2016-2021.csv"
        macro_coverage = reports / "macro-coverage-2016-2021.json"
        write_macro(macro, macro_coverage)

        build_report = reports / "build-2016-2021.json"
        run([
            sys.executable,
            str(ROOT / "scripts/build_information_parity_stage2_full_train.py"),
            str(sync_dir),
            str(dxy),
            str(macro),
            str(macro_coverage),
            str(layer),
            str(build_report),
        ])

        integrity = reports / "integrity-2016-2021.json"
        run([
            sys.executable,
            str(ROOT / "scripts/validate_information_parity_stage2_full_train.py"),
            str(layer),
            str(dxy),
            str(macro),
            str(macro_coverage),
            str(integrity),
        ])

        normalized_manifest = manifests / "normalized-full-train-manifest.json"
        inputs = [
            dxy,
            macro,
            *sorted(layer.glob("*.csv.gz")),
            build_report,
            integrity,
            macro_coverage,
            dxy_report,
        ]
        run([
            sys.executable,
            str(ROOT / "scripts/build_information_parity_manifest.py"),
            str(normalized_manifest),
            *map(str, inputs),
        ])

        raw_manifest = manifests / "raw-market-manifest.json"
        raw_manifest.write_text(json.dumps({
            "schema_version": "PREFLIGHT",
            "file_count": 48,
            "total_bytes": 1,
            "files": [],
        }), encoding="utf-8")

        input_verification = reports / "input-verification.json"
        input_verification.write_text(json.dumps({
            "status": "PASS",
            "schema_version": "PREFLIGHT",
            "years": list(YEARS),
            "bls_snapshots": {},
            "sealed_xauusd_periods_accessed": [],
        }), encoding="utf-8")

        summary = reports / "full-train-summary.json"
        env = os.environ.copy()
        env["GITHUB_SHA"] = "offline-full-train-preflight"
        env["STAGE2_NODE_VERSION"] = "offline"
        env["STAGE2_NPM_VERSION"] = "offline"
        run([
            sys.executable,
            str(ROOT / "scripts/summarize_information_parity_stage2_full_train.py"),
            str(input_verification),
            str(dxy_report),
            str(macro_coverage),
            str(build_report),
            str(integrity),
            str(raw_manifest),
            str(normalized_manifest),
            str(summary),
        ], env=env)

        build = json.loads(build_report.read_text())
        integ = json.loads(integrity.read_text())
        final = json.loads(summary.read_text())

        assert build["status"] == "PASS"
        assert build["continuous_state_across_years"] is True
        assert set(build["per_year"]) == {str(y) for y in YEARS}
        assert len(build["year_boundaries"]) == 5

        assert integ["status"] == "PASS"
        assert integ["warnings"] == []
        assert integ["checks"]["year_boundary_continuity"] == "PASS"
        assert integ["checks"]["d1_h1_hierarchy"] == "PASS"
        assert integ["checks"]["w1_d1_hierarchy"] == "PASS"

        assert final["status"] == "PASS"
        assert final["continuous_state_across_years"] is True
        assert final["sealed_xauusd_periods_accessed"] == []
        assert set(final["per_year"]) == {str(y) for y in YEARS}

        # Each synthetic year has a full Monday-Friday week.
        for year in YEARS:
            tf = final["per_year"][str(year)]["canonical_timeframe_rows"]
            assert tf["d1"] == 5
            assert tf["w1"] == 1
            assert final["per_year"][str(year)]["dxy_available_share"] == 1.0

    print("INFORMATION_PARITY_STAGE2_FULL_TRAIN_PREFLIGHT_PASS")


if __name__ == "__main__":
    main()
