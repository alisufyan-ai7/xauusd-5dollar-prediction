#!/usr/bin/env python3
"""Offline deterministic preflight for Information Parity V1 Stage 2.

No network access is required or permitted by this test. It generates all
inputs in a temporary directory and exercises:
- BID/ASK synchronization and one-sided reconstruction
- exact higher-timeframe aggregation including D1/W1
- synthetic DXY and <=5m backward staleness
- macro schedule/state joins, simultaneous events, and DST-aware sessions
- swing/FVG causal timing
- empty canonical-table serialization
- neutral trade/risk state
- leakage validator positive and negative paths

The purpose is to catch integration bugs before CI or provider acquisition.
"""

from __future__ import annotations

import csv
import json
import math
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.build_information_parity_stage2_year import (
    BAR_COLUMNS,
    add_m1_transforms,
    build_d1,
    build_fvg_records,
    build_macro_state,
    build_w1,
    session_state,
    swing_events,
    write_csv_gz,
)

from scripts.acquire_macro_schedule_stage2 import (
    acquire_claims,
    acquire_fomc,
    is_national_gdp_title,
    load_bls_snapshot,
    parse_bea_embargo,
    parse_date_time_et,
    parse_release_time,
)

UTC = timezone.utc
ONE_MIN = 60_000
START = datetime(2016, 3, 7, 0, 0, tzinfo=UTC)
END = datetime(2016, 4, 4, 0, 0, tzinfo=UTC)

M1_FIELDS = ["timestamp", "open", "high", "low", "close", "volume"]
MACRO_FIELDS = [
    "event_id",
    "event_family",
    "scheduled_time_utc",
    "scheduled_time_local",
    "source_timezone",
    "source_agency",
    "source_document_id_or_url",
    "release_stage",
    "historical_exception_flag",
    "normalization_version",
]


def run(cmd: list[str], *, expect_success: bool = True) -> subprocess.CompletedProcess:
    p = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if expect_success and p.returncode != 0:
        raise AssertionError(
            f"COMMAND_FAILED:{cmd}\nSTDOUT:\n{p.stdout}\nSTDERR:\n{p.stderr}"
        )
    if not expect_success and p.returncode == 0:
        raise AssertionError(f"COMMAND_UNEXPECTEDLY_PASSED:{cmd}")
    return p


def epoch_ms(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)


def write_rows(path: Path, rows: list[list[object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(M1_FIELDS)
        w.writerows(rows)


def generate_xauusd_raw(base: Path) -> tuple[Path, Path, int]:
    bid_path = base / "xauusd-bid.csv"
    ask_path = base / "xauusd-ask.csv"

    bid_rows = []
    ask_rows = []
    i = 0
    dt = START

    # One ask-only gap and one bid-only gap exercise conservative reconstruction.
    missing_ask = epoch_ms(datetime(2016, 3, 10, 10, 17, tzinfo=UTC))
    missing_bid = epoch_ms(datetime(2016, 3, 15, 11, 23, tzinfo=UTC))
    # A timestamp absent from both sides must not be invented.
    missing_both = epoch_ms(datetime(2016, 3, 22, 9, 41, tzinfo=UTC))

    while dt < END:
        ts = epoch_ms(dt)
        trend = 1200.0 + 0.001 * i
        wave = 0.18 * math.sin(i / 37.0) + 0.07 * math.sin(i / 11.0)
        bid_close = trend + wave
        bid_open = bid_close - 0.01 * math.sin(i / 5.0)
        bid_high = max(bid_open, bid_close) + 0.08
        bid_low = min(bid_open, bid_close) - 0.08
        bid_volume = 0.02 + 0.005 * (1 + math.sin(i / 17.0))

        spread = 0.45 + 0.02 * (1 + math.sin(i / 29.0))
        ask_open = bid_open + spread
        ask_high = bid_high + spread
        ask_low = bid_low + spread
        ask_close = bid_close + spread
        ask_volume = 0.025 + 0.006 * (1 + math.cos(i / 19.0))

        if ts != missing_both and ts != missing_bid:
            bid_rows.append([
                ts, bid_open, bid_high, bid_low, bid_close, bid_volume
            ])
        if ts != missing_both and ts != missing_ask:
            ask_rows.append([
                ts, ask_open, ask_high, ask_low, ask_close, ask_volume
            ])

        i += 1
        dt += timedelta(minutes=1)

    write_rows(bid_path, bid_rows)
    write_rows(ask_path, ask_rows)
    expected_union_rows = int((END - START).total_seconds() // 60) - 1
    return bid_path, ask_path, expected_union_rows


def generate_fx_raw(base: Path) -> list[Path]:
    definitions = {
        "eurusd": (1.10, 0.0000012),
        "usdjpy": (112.0, 0.00015),
        "gbpusd": (1.42, -0.0000008),
        "usdcad": (1.33, 0.0000007),
        "usdsek": (8.45, 0.000006),
        "usdchf": (0.99, -0.0000003),
    }

    # Six missing EURUSD minutes force a DXY availability hole >5 minutes.
    gap_start = epoch_ms(datetime(2016, 3, 16, 14, 0, tzinfo=UTC))
    gap = {gap_start + i * ONE_MIN for i in range(6)}

    out = []
    for name, (base_px, slope) in definitions.items():
        rows = []
        i = 0
        dt = START
        while dt < END:
            ts = epoch_ms(dt)
            if name == "eurusd" and ts in gap:
                i += 1
                dt += timedelta(minutes=1)
                continue
            close = base_px + slope * i + 0.0002 * math.sin(i / 43.0)
            open_ = close - 0.00002 * math.sin(i / 7.0)
            pad = max(abs(close) * 1e-6, 1e-5)
            rows.append([
                ts,
                open_,
                max(open_, close) + pad,
                min(open_, close) - pad,
                close,
                1.0 + 0.1 * math.sin(i / 13.0),
            ])
            i += 1
            dt += timedelta(minutes=1)
        p = base / f"{name}.csv"
        write_rows(p, rows)
        out.append(p)
    return out


def write_macro(base: Path) -> tuple[Path, Path]:
    macro = base / "macro.csv"
    coverage = base / "macro-coverage.json"

    # Includes simultaneous CPI+NFP to exercise deterministic multi-label state.
    local_times = [
        ("evt-cpi", "CPI", "2016-03-11T08:30:00-05:00"),
        ("evt-nfp", "NFP", "2016-03-11T08:30:00-05:00"),
        ("evt-fomc", "FOMC", "2016-03-16T14:00:00-04:00"),
        ("evt-claims", "CLAIMS", "2016-03-17T08:30:00-04:00"),
        ("evt-gdp", "GDP", "2016-03-25T08:30:00-04:00"),
        ("evt-jolts", "JOLTS", "2016-03-29T10:00:00-04:00"),
    ]

    with macro.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=MACRO_FIELDS)
        w.writeheader()
        for event_id, family, local_text in local_times:
            local_dt = datetime.fromisoformat(local_text)
            utc_dt = local_dt.astimezone(UTC)
            w.writerow({
                "event_id": event_id,
                "event_family": family,
                "scheduled_time_utc": utc_dt.isoformat(),
                "scheduled_time_local": local_dt.isoformat(),
                "source_timezone": "America/New_York",
                "source_agency": "PREFLIGHT_SYNTHETIC_FIRST_PARTY",
                "source_document_id_or_url": "offline://preflight",
                "release_stage": "statement" if family == "FOMC" else "",
                "historical_exception_flag": "0",
                "normalization_version": "IPV1_MACRO_SCHEDULE_V1",
            })

    coverage.write_text(json.dumps({
        "schema_version": "IPV1_STAGE2_MACRO_COVERAGE_V1",
        "status": "PASS",
        "scope": "2016_TRAIN_ONLY_PREFLIGHT",
        "sealed_xauusd_periods_accessed": [],
        "years": {
            "2016": {
                "counts": {
                    "CPI": 12,
                    "NFP": 12,
                    "JOLTS": 12,
                    "FOMC": 8,
                    "CLAIMS": 52,
                    "GDP": 12,
                },
                "family_pass": {
                    "CPI": True,
                    "NFP": True,
                    "JOLTS": True,
                    "FOMC": True,
                    "CLAIMS": True,
                    "GDP": True,
                },
                "errors": [],
                "stage2_macro_schedule_available": True,
            }
        },
    }, indent=2) + "\n", encoding="utf-8")
    return macro, coverage


def assert_session_dst(structural: pd.DataFrame) -> None:
    by_dec = structural.set_index("decision_time_ms")

    # New York 08:00 local: 13:00Z before US DST, 12:00Z after.
    before_us = epoch_ms(datetime(2016, 3, 11, 13, 0, tzinfo=UTC))
    after_us = epoch_ms(datetime(2016, 3, 14, 12, 0, tzinfo=UTC))
    assert by_dec.loc[before_us, "session_label"] == "NEW_YORK"
    assert by_dec.loc[after_us, "session_label"] == "NEW_YORK"

    # London 08:00 local: 08:00Z before UK DST, 07:00Z after.
    before_uk = epoch_ms(datetime(2016, 3, 25, 8, 0, tzinfo=UTC))
    after_uk = epoch_ms(datetime(2016, 3, 28, 7, 0, tzinfo=UTC))
    assert by_dec.loc[before_uk, "session_label"] == "LONDON"
    assert by_dec.loc[after_uk, "session_label"] == "LONDON"


def assert_swing_and_fvg_causality() -> None:
    # Swing high at bar index 2 must not become known until bar index 4 closes.
    bars = pd.DataFrame.from_records([
        {"bar_start_ms": 0, "available_time_ms": 300_000, "open": 9.5, "high": 10.0, "low": 9.0, "close": 9.6, "volume": 1.0, "source_count": 5},
        {"bar_start_ms": 300_000, "available_time_ms": 600_000, "open": 10.0, "high": 11.0, "low": 9.8, "close": 10.5, "volume": 1.0, "source_count": 5},
        {"bar_start_ms": 600_000, "available_time_ms": 900_000, "open": 12.0, "high": 15.0, "low": 11.8, "close": 14.0, "volume": 1.0, "source_count": 5},
        {"bar_start_ms": 900_000, "available_time_ms": 1_200_000, "open": 12.5, "high": 13.0, "low": 12.0, "close": 12.4, "volume": 1.0, "source_count": 5},
        {"bar_start_ms": 1_200_000, "available_time_ms": 1_500_000, "open": 11.5, "high": 12.0, "low": 11.0, "close": 11.4, "volume": 1.0, "source_count": 5},
    ], columns=BAR_COLUMNS)
    highs, _ = swing_events(bars)
    assert highs
    event = highs[0]
    assert event[1] == 15.0
    assert event[2] == 600_000
    assert event[0] == 1_500_000
    assert event[3] == 1_500_000

    # Bullish FVG: bar 0 high=10, bar 2 low=11 => created only at bar 2 close.
    fvg_bars = pd.DataFrame.from_records([
        {"bar_start_ms": 0, "available_time_ms": 300_000, "open": 9.5, "high": 10.0, "low": 9.0, "close": 9.8, "volume": 1.0, "source_count": 5},
        {"bar_start_ms": 300_000, "available_time_ms": 600_000, "open": 10.2, "high": 10.8, "low": 10.1, "close": 10.6, "volume": 1.0, "source_count": 5},
        {"bar_start_ms": 600_000, "available_time_ms": 900_000, "open": 11.2, "high": 12.0, "low": 11.0, "close": 11.5, "volume": 1.0, "source_count": 5},
        {"bar_start_ms": 900_000, "available_time_ms": 1_200_000, "open": 10.0, "high": 10.2, "low": 9.7, "close": 9.8, "volume": 1.0, "source_count": 5},
    ], columns=BAR_COLUMNS)
    rec = build_fvg_records(fvg_bars)["bull"][0]
    assert rec["lower"] == 10.0
    assert rec["upper"] == 11.0
    assert rec["created_ms"] == 900_000
    assert rec["invalid_ms"] == 1_200_000
    assert rec["invalid_ms"] > rec["created_ms"]


def assert_macro_parser_and_snapshot_fallback() -> None:
    events, errors = load_bls_snapshot(2016)
    assert errors == []
    counts = {"CPI": 0, "NFP": 0, "JOLTS": 0}
    for event in events:
        counts[event.family] += 1
        assert event.agency == "BLS"
        assert event.source == "https://www.bls.gov/schedule/2016/home.htm"
    assert counts == {"CPI": 12, "NFP": 12, "JOLTS": 12}

    bls_dt = parse_date_time_et("Friday, March 04, 2016", "08:30 AM")
    assert bls_dt.isoformat() == "2016-03-04T08:30:00-05:00"

    assert parse_release_time("For release at 2:00 p.m. EDT") == (14, 0)

    assert is_national_gdp_title(
        "Gross Domestic Product, Third Quarter 2018 (Second Estimate)"
    )
    assert is_national_gdp_title(
        "Gross Domestic Product: First Quarter 2018 (Second Estimate)"
    )
    assert is_national_gdp_title(
        "Gross Domestic Product (Third Estimate), GDP by Industry, and Corporate Profits"
    )
    assert not is_national_gdp_title(
        "Gross Domestic Product by State, 1st Quarter 2020"
    )
    assert not is_national_gdp_title(
        "Gross Domestic Product by Industry, 4th quarter 2017"
    )

    bea = parse_bea_embargo(
        "EMBARGOED UNTIL RELEASE AT 8:30 A.M. EDT, Thursday, April 28, 2016"
    )
    assert bea is not None
    assert bea.isoformat() == "2016-04-28T08:30:00-04:00"

    bea_comma = parse_bea_embargo(
        "EMBARGOED UNTIL RELEASE AT 8:30 A.M., EDT, Thursday, June 24, 2021"
    )
    assert bea_comma is not None
    assert bea_comma.isoformat() == "2021-06-24T08:30:00-04:00"

    fomc_dates = (
        "20210127", "20210317", "20210428", "20210616",
        "20210728", "20210922", "20211103", "20211215",
    )

    class Fomc2021FallbackFixture:
        def get(self, url: str, label: str) -> str:
            del label
            if "fomchistorical2021.htm" in url:
                raise RuntimeError("FETCH_FAILED:legacy-2021:404")
            if "2021-press-fomc.htm" in url:
                links = "".join(
                    (
                        '<a href="/newsevents/pressreleases/'
                        f'monetary{ymd}a.htm">'
                        "Federal Reserve issues FOMC statement</a>"
                    )
                    for ymd in fomc_dates
                )
                return f"<html><body>{links}</body></html>"
            if "/newsevents/pressreleases/monetary2021" in url:
                return "<html><body>For release at 2:00 p.m. EDT</body></html>"
            raise AssertionError(f"unexpected FOMC fixture URL: {url}")

    fomc, fomc_errors = acquire_fomc(Fomc2021FallbackFixture(), 2021)
    assert fomc_errors == []
    assert len(fomc) == 8
    assert [e.dt_local.strftime("%Y%m%d") for e in fomc] == list(fomc_dates)

    claims, claim_errors = acquire_claims(2016)
    assert claim_errors == []
    assert len(claims) == 52
    thanksgiving_exception = [
        e for e in claims
        if e.dt_local.date().isoformat() == "2016-11-23"
    ]
    assert len(thanksgiving_exception) == 1
    assert thanksgiving_exception[0].exception == 1


def assert_macro_multilabel() -> None:
    event_ms = epoch_ms(datetime(2016, 3, 11, 13, 30, tzinfo=UTC))
    macro = pd.DataFrame({
        "scheduled_time_ms": [event_ms, event_ms],
        "event_family": ["NFP", "CPI"],
    })
    dtimes = np.array([event_ms - ONE_MIN, event_ms], dtype=np.int64)
    state = build_macro_state(dtimes, macro, True)
    assert state.iloc[0]["next_event_families"] == "CPI|NFP"
    assert state.iloc[0]["minutes_to_next_event"] == 1
    assert state.iloc[0]["events_next_120m_count"] == 2
    assert state.iloc[1]["previous_event_families"] == "CPI|NFP"
    assert state.iloc[1]["minutes_since_previous_event"] == 0
    assert state.iloc[1]["events_prior_120m_count"] == 2


def assert_empty_table_serialization(tmp: Path) -> None:
    h1 = pd.DataFrame.from_records([
        {
            "bar_start_ms": epoch_ms(datetime(2016, 3, 7, 0, 0, tzinfo=UTC)),
            "available_time_ms": epoch_ms(datetime(2016, 3, 7, 1, 0, tzinfo=UTC)),
            "open": 100.0,
            "high": 101.0,
            "low": 99.0,
            "close": 100.5,
            "volume": 1.0,
            "source_count": 60,
        }
    ], columns=BAR_COLUMNS)
    d1 = build_d1(h1)
    w1 = build_w1(d1)
    assert d1.empty and list(d1.columns) == BAR_COLUMNS
    assert w1.empty and list(w1.columns) == BAR_COLUMNS
    for name, df in (("d1", d1), ("w1", w1)):
        p = tmp / f"empty-{name}.csv.gz"
        write_csv_gz(df, p)
        rt = pd.read_csv(p, compression="gzip")
        assert rt.empty
        assert list(rt.columns) == BAR_COLUMNS


def assert_cross_year_continuity(tmp: Path) -> None:
    # 360 contiguous M1 rows cross 2016->2017. The first 2017 row has more
    # than 240 prior contiguous TRAIN minutes and must not cold-start.
    start = datetime(2016, 12, 31, 20, 0, tzinfo=UTC)
    rows = []
    for i in range(360):
        ts = epoch_ms(start + timedelta(minutes=i))
        px = 1200.0 + 0.01 * i
        rows.append({
            "timestamp_ms": ts,
            "decision_time_ms": ts + ONE_MIN,
            "bid_open": px,
            "bid_high": px + 0.05,
            "bid_low": px - 0.05,
            "bid_close": px,
            "bid_volume": 1.0,
            "ask_open": px + 0.4,
            "ask_high": px + 0.45,
            "ask_low": px + 0.35,
            "ask_close": px + 0.4,
            "ask_volume": 1.0,
            "spread_open": 0.4,
            "spread_close": 0.4,
            "bid_flat_fill": 0,
            "ask_flat_fill": 0,
        })
    m1 = add_m1_transforms(pd.DataFrame(rows))
    years = pd.to_datetime(m1["timestamp_ms"], unit="ms", utc=True).dt.year
    first_2017 = int(np.flatnonzero(years.to_numpy() == 2017)[0])
    assert m1.iloc[first_2017]["core_240m_contiguous_ready"] == 1
    assert math.isfinite(float(m1.iloc[first_2017]["volume_mean_240m"]))
    assert math.isfinite(float(m1.iloc[first_2017]["spread_mean_60m"]))

    # Full-TRAIN DXY must also carry exact rolling state across Dec/Jan.
    fx_dir = tmp / "full-dxy-fx"
    fx_dir.mkdir(parents=True, exist_ok=True)
    instruments = ("eurusd", "usdjpy", "gbpusd", "usdcad", "usdsek", "usdchf")
    base_px = {
        "eurusd": 1.10,
        "usdjpy": 112.0,
        "gbpusd": 1.42,
        "usdcad": 1.33,
        "usdsek": 8.45,
        "usdchf": 0.99,
    }
    for year in range(2016, 2022):
        for inst in instruments:
            if year == 2016:
                times = [datetime(2016, 12, 31, 23, 59, tzinfo=UTC)]
            elif year == 2017:
                times = [
                    datetime(2017, 1, 1, 0, 0, tzinfo=UTC),
                    datetime(2017, 1, 1, 0, 1, tzinfo=UTC),
                ]
            else:
                times = [datetime(year, 1, 1, 0, 0, tzinfo=UTC)]
            raw = []
            for j, dt in enumerate(times):
                px = base_px[inst] + 0.0001 * j
                raw.append([
                    epoch_ms(dt), px, px + 0.0001, px - 0.0001, px, 1.0
                ])
            write_rows(
                fx_dir / (
                    f"{inst}-{year}-01-01-{year + 1}-01-01-m1-bid.csv"
                ),
                raw,
            )

    out = tmp / "full-dxy.csv"
    report = tmp / "full-dxy-report.json"
    run([
        sys.executable,
        str(ROOT / "scripts/build_synthetic_dxy_stage2_full_train.py"),
        str(fx_dir),
        str(out),
        str(report),
    ])
    dxy = pd.read_csv(out)
    row = dxy.loc[
        dxy["dxy_bar_start_ms"]
        == epoch_ms(datetime(2017, 1, 1, 0, 0, tzinfo=UTC))
    ].iloc[0]
    assert pd.notna(row["dxy_change_1m"])
    meta = json.loads(report.read_text(encoding="utf-8"))
    assert meta["cross_year_state_preserved"] is True


def assert_raw_timestamp_guards(tmp: Path) -> None:
    dup_bid = tmp / "dup-bid.csv"
    dup_ask = tmp / "dup-ask.csv"
    write_rows(dup_bid, [
        [0, 100, 101, 99, 100.5, 1],
        [0, 100, 101, 99, 100.5, 1],
    ])
    write_rows(dup_ask, [
        [0, 100.5, 101.5, 99.5, 101.0, 1],
    ])
    bad = run([
        sys.executable,
        str(ROOT / "scripts/synchronize_information_parity_m1.py"),
        str(dup_bid), str(dup_ask), str(tmp / "dup-sync.csv"),
    ], expect_success=False)
    assert "DUPLICATE_TIMESTAMP" in (bad.stdout + bad.stderr)

    off_bid = tmp / "offgrid-bid.csv"
    write_rows(off_bid, [
        [1, 100, 101, 99, 100.5, 1],
    ])
    bad = run([
        sys.executable,
        str(ROOT / "scripts/synchronize_information_parity_m1.py"),
        str(off_bid), str(dup_ask), str(tmp / "offgrid-sync.csv"),
    ], expect_success=False)
    assert "OFF_GRID_TIMESTAMP" in (bad.stdout + bad.stderr)

    fx_paths = []
    for name in ("eurusd", "usdjpy", "gbpusd", "usdcad", "usdsek", "usdchf"):
        p = tmp / f"guard-{name}.csv"
        rows = [
            [0, 1.0, 1.1, 0.9, 1.0, 1],
            [60_000, 1.0, 1.1, 0.9, 1.0, 1],
        ]
        if name == "eurusd":
            rows.append([60_000, 1.0, 1.1, 0.9, 1.0, 1])
        write_rows(p, rows)
        fx_paths.append(p)
    bad = run([
        sys.executable,
        str(ROOT / "scripts/build_synthetic_dxy_stage2.py"),
        *map(str, fx_paths),
        str(tmp / "guard-dxy.csv"),
        str(tmp / "guard-dxy.json"),
    ], expect_success=False)
    assert "DXY_DUPLICATE_TIMESTAMP" in (bad.stdout + bad.stderr)


def end_to_end(tmp: Path) -> None:
    raw = tmp / "raw"
    derived = tmp / "derived"
    layer = tmp / "layer"
    reports = tmp / "reports"
    raw.mkdir()
    derived.mkdir()
    reports.mkdir()

    bid, ask, expected_union_rows = generate_xauusd_raw(raw)
    fx = generate_fx_raw(raw)
    macro, coverage = write_macro(raw)

    sync = derived / "xauusd-sync.csv"
    p = run([
        sys.executable,
        str(ROOT / "scripts/synchronize_information_parity_m1.py"),
        str(bid), str(ask), str(sync),
    ])
    sync_report = json.loads(p.stdout)
    assert sync_report["rows"] == expected_union_rows
    assert sync_report["bid_flat_fills"] == 1
    assert sync_report["ask_flat_fills"] == 1
    assert sync_report["invalid_flat_fill_dropped"] == 0

    dxy = derived / "synthetic-dxy.csv"
    dxy_report = reports / "synthetic-dxy.json"
    run([
        sys.executable,
        str(ROOT / "scripts/build_synthetic_dxy_stage2.py"),
        *map(str, fx),
        str(dxy),
        str(dxy_report),
    ])
    dxy_meta = json.loads(dxy_report.read_text(encoding="utf-8"))
    assert dxy_meta["status"] == "PASS"
    assert dxy_meta["common_timestamps"] > 0
    assert dxy_meta["common_share_of_union"] < 1.0

    build_report = reports / "build.json"
    run([
        sys.executable,
        str(ROOT / "scripts/build_information_parity_stage2_year.py"),
        "2016",
        str(sync),
        str(dxy),
        str(macro),
        str(coverage),
        str(layer),
        str(build_report),
    ])

    integrity = reports / "integrity.json"
    run([
        sys.executable,
        str(ROOT / "scripts/validate_information_parity_stage2.py"),
        "2016",
        str(layer),
        str(dxy),
        str(macro),
        str(coverage),
        str(integrity),
    ])
    integ = json.loads(integrity.read_text(encoding="utf-8"))
    assert integ["status"] == "PASS"
    assert integ["sealed_xauusd_periods_accessed"] == []

    decision = pd.read_csv(layer / "decision_index_2016.csv.gz", compression="gzip")
    market = pd.read_csv(layer / "xauusd_m1_market_state_2016.csv.gz", compression="gzip")
    structural = pd.read_csv(layer / "xauusd_structural_state_2016.csv.gz", compression="gzip")
    d1 = pd.read_csv(layer / "xauusd_d1_2016.csv.gz", compression="gzip")
    w1 = pd.read_csv(layer / "xauusd_w1_2016.csv.gz", compression="gzip")
    trade = pd.read_csv(layer / "trade_risk_state_template_2016.csv.gz", compression="gzip")

    # Four complete UTC weeks are generated. One M1 timestamp is absent
    # from both XAUUSD sides, which removes one H1 bar but still leaves that
    # UTC day above the frozen >=20 completed-H1 threshold.
    assert len(d1) == 28
    assert len(w1) == 4
    assert decision["dxy_available"].min() == 0
    assert decision["dxy_available"].max() == 1
    assert decision.loc[decision["dxy_available"] == 1, "dxy_age_minutes"].max() <= 5
    assert decision["macro_schedule_available"].eq(1).all()
    assert trade["position_state"].eq("FLAT").all()
    assert pd.to_numeric(trade["session_trade_count"]).eq(0).all()

    prices = market["bid_close"].to_numpy(float)
    for col in (
        "asia_high",
        "asia_low",
        "london_high",
        "london_low",
    ):
        level = pd.to_numeric(structural[f"{col}_known"], errors="coerce").to_numpy(float)
        dist = pd.to_numeric(
            structural[f"{col}_distance_from_bid_close"],
            errors="coerce",
        ).to_numpy(float)
        assert np.allclose(dist, level - prices, equal_nan=True)

    for field in ("high", "low", "open", "close"):
        level = pd.to_numeric(
            structural[f"previous_day_{field}"],
            errors="coerce",
        ).to_numpy(float)
        dist = pd.to_numeric(
            structural[f"previous_day_{field}_distance_from_bid_close"],
            errors="coerce",
        ).to_numpy(float)
        assert np.allclose(dist, level - prices, equal_nan=True)

    swing_distance_checked = False
    for tf in ("m5", "m15", "h1", "h4"):
        for side in ("high", "low"):
            level = pd.to_numeric(
                structural[f"last_confirmed_swing_{side}_{tf}_level"],
                errors="coerce",
            ).to_numpy(float)
            dist = pd.to_numeric(
                structural[f"last_confirmed_swing_{side}_{tf}_distance_from_bid_close"],
                errors="coerce",
            ).to_numpy(float)
            assert np.allclose(dist, level - prices, equal_nan=True)
            swing_distance_checked = swing_distance_checked or np.isfinite(level).any()
    assert swing_distance_checked

    assert_session_dst(structural)

    # Negative leakage test: a future-return field must be rejected.
    corrupt = tmp / "layer-corrupt"
    shutil.copytree(layer, corrupt)
    d = pd.read_csv(corrupt / "decision_index_2016.csv.gz", compression="gzip")
    d["future_return"] = 0.0
    d.to_csv(corrupt / "decision_index_2016.csv.gz", index=False, compression="gzip")
    bad = run([
        sys.executable,
        str(ROOT / "scripts/validate_information_parity_stage2.py"),
        "2016",
        str(corrupt),
        str(dxy),
        str(macro),
        str(coverage),
        str(reports / "integrity-corrupt.json"),
    ], expect_success=False)
    assert "forbidden_field" in (bad.stdout + bad.stderr)


def main() -> None:
    assert_swing_and_fvg_causality()
    assert_macro_parser_and_snapshot_fallback()
    assert_macro_multilabel()
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        assert_empty_table_serialization(tmp)
        assert_cross_year_continuity(tmp)
        assert_raw_timestamp_guards(tmp)
        end_to_end(tmp)
    print("INFORMATION_PARITY_STAGE2_OFFLINE_PREFLIGHT_PASS")


if __name__ == "__main__":
    main()
