#!/usr/bin/env python3
"""Integrity validator for the continuous 2016-2021 Stage 2 TRAIN layer."""

from __future__ import annotations

import csv
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from validate_information_parity_stage2 import (
    MACRO_REQUIRED,
    SEALED_YEARS,
    assert_no_forbidden_columns,
    check_hierarchy,
    check_macro_state,
    check_structural,
    check_trade_state,
    fail,
    load_dxy,
    read_gz,
    strict_increasing,
)

ONE_MIN = 60_000
YEARS = tuple(range(2016, 2022))
YEAR_SET = set(YEARS)
TAG = "2016_2021"


def year_set_ms(values: np.ndarray) -> set[int]:
    if len(values) == 0:
        return set()
    return set(
        map(
            int,
            pd.to_datetime(values, unit="ms", utc=True).year,
        )
    )


def check_m1_full(df: pd.DataFrame, report: dict):
    assert_no_forbidden_columns("xauusd_m1_market_state", df.columns)
    required = {
        "timestamp_ms", "decision_time_ms",
        "bid_open", "bid_high", "bid_low", "bid_close", "bid_volume",
        "ask_open", "ask_high", "ask_low", "ask_close", "ask_volume",
        "spread_open", "spread_close", "bid_flat_fill", "ask_flat_fill",
        "core_240m_contiguous_ready",
    }
    if not required.issubset(df.columns):
        fail(f"full_m1_missing:{sorted(required-set(df.columns))}")

    ts = df["timestamp_ms"].to_numpy(np.int64)
    dec = df["decision_time_ms"].to_numpy(np.int64)
    strict_increasing(ts, "full_m1_timestamp")

    if not np.all(dec == ts + ONE_MIN):
        fail("full_decision_time_relation")
    if year_set_ms(ts) != YEAR_SET:
        fail(f"full_m1_year_scope:{sorted(year_set_ms(ts))}")
    if (df["spread_open"].astype(float) < 0).any():
        fail("full_negative_spread_open")
    if (df["spread_close"].astype(float) < 0).any():
        fail("full_negative_spread_close")

    report["checks"]["m1_decision_time"] = "PASS"
    report["checks"]["m1_year_scope"] = "PASS"
    report["checks"]["nonnegative_spread"] = "PASS"


def check_timeframe_full(df: pd.DataFrame, name: str, report: dict):
    assert_no_forbidden_columns(name, df.columns)
    required = {
        "bar_start_ms", "available_time_ms",
        "open", "high", "low", "close", "volume", "source_count",
    }
    if not required.issubset(df.columns):
        fail(f"{name}_missing:{sorted(required-set(df.columns))}")
    if df.empty:
        fail(f"{name}_unexpected_empty")

    start = df["bar_start_ms"].to_numpy(np.int64)
    av = df["available_time_ms"].to_numpy(np.int64)
    strict_increasing(av, f"{name}_available")
    if np.any(av <= start):
        fail(f"{name}_availability_not_after_start")
    bad = year_set_ms(start) - YEAR_SET
    if bad:
        fail(f"{name}_bar_start_outside_train:{sorted(bad)}")
    report["checks"][f"{name}_availability"] = "PASS"


def check_decision_index_full(
    df: pd.DataFrame,
    m1: pd.DataFrame,
    dxy: pd.DataFrame,
    report: dict,
):
    assert_no_forbidden_columns("decision_index", df.columns)
    if len(df) != len(m1):
        fail("full_decision_index_row_count")

    ts = m1["timestamp_ms"].to_numpy(np.int64)
    dec = m1["decision_time_ms"].to_numpy(np.int64)
    if not np.array_equal(df["timestamp_ms"].to_numpy(np.int64), ts):
        fail("full_decision_index_timestamp_alignment")
    if not np.array_equal(df["decision_time_ms"].to_numpy(np.int64), dec):
        fail("full_decision_index_decision_alignment")

    expected_year = pd.to_datetime(ts, unit="ms", utc=True).year.to_numpy(int)
    actual_year = df["year"].to_numpy(int)
    if not np.array_equal(actual_year, expected_year):
        fail("full_decision_index_year_alignment")
    if set(map(int, np.unique(actual_year))) != YEAR_SET:
        fail("full_decision_index_year_scope")

    available = df["dxy_available"].to_numpy(int)
    age = pd.to_numeric(df["dxy_age_minutes"], errors="coerce").to_numpy(float)
    if np.any((available != 0) & (available != 1)):
        fail("full_dxy_available_not_binary")
    mask = available == 1
    if np.any(~np.isfinite(age[mask])):
        fail("full_dxy_available_missing_age")
    if np.any(age[mask] < 0) or np.any(age[mask] > 5):
        fail("full_dxy_staleness")

    if not dxy.empty:
        dav = dxy["dxy_available_time_ms"].to_numpy(np.int64)
        pos = np.searchsorted(dav, dec, side="right") - 1
        valid = pos >= 0
        calc_age = np.full(len(dec), np.nan)
        calc_age[valid] = (dec[valid] - dav[pos[valid]]) / ONE_MIN
        calc_ok = valid & (calc_age >= 0) & (calc_age <= 5)
        if not np.array_equal(calc_ok.astype(np.int8), available.astype(np.int8)):
            fail("full_dxy_asof_availability_mismatch")
        if np.any(np.abs(calc_age[calc_ok] - age[calc_ok]) > 1e-9):
            fail("full_dxy_asof_age_mismatch")

    macro_available = df["macro_schedule_available"].to_numpy(int)
    if not np.all(macro_available == 1):
        fail("full_macro_schedule_not_available_all_rows")

    report["checks"]["decision_index_alignment"] = "PASS"
    report["checks"]["dxy_backward_asof"] = "PASS"
    report["checks"]["decision_year_continuity"] = "PASS"


def check_macro_full(
    macro_path: Path,
    coverage_path: Path,
    report: dict,
):
    with macro_path.open(encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        fields = r.fieldnames or []
        rows = list(r)

    if fields != MACRO_REQUIRED:
        fail(f"full_macro_schema:{fields}")
    assert_no_forbidden_columns("macro_event_schedule", fields)

    actual_counts = {
        str(year): {
            "CPI": 0,
            "NFP": 0,
            "JOLTS": 0,
            "FOMC": 0,
            "CLAIMS": 0,
            "GDP": 0,
        }
        for year in YEARS
    }

    seen_ids = set()
    for row in rows:
        if row["event_id"] in seen_ids:
            fail(f"full_macro_duplicate_event_id:{row['event_id']}")
        seen_ids.add(row["event_id"])

        utc_dt = datetime.fromisoformat(row["scheduled_time_utc"])
        local_dt = datetime.fromisoformat(row["scheduled_time_local"])
        if utc_dt.tzinfo is None or local_dt.tzinfo is None:
            fail("full_macro_naive_time")
        if row["source_timezone"] != "America/New_York":
            fail(f"full_macro_timezone:{row['source_timezone']}")
        if local_dt.astimezone(timezone.utc) != utc_dt.astimezone(timezone.utc):
            fail("full_macro_local_utc_mismatch")
        if utc_dt.year not in YEAR_SET:
            fail(f"full_macro_year_outside_train:{utc_dt.year}")
        if utc_dt.year in SEALED_YEARS:
            fail("full_macro_sealed_year")
        fam = row["event_family"]
        if fam not in actual_counts[str(utc_dt.year)]:
            fail(f"full_macro_unexpected_family:{fam}")
        actual_counts[str(utc_dt.year)][fam] += 1

    coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
    if coverage.get("sealed_xauusd_periods_accessed") != []:
        fail("full_macro_coverage_sealed_assertion")

    for year in YEARS:
        y = coverage.get("years", {}).get(str(year))
        if y is None:
            fail(f"full_macro_coverage_year_missing:{year}")
        if not bool(y.get("stage2_macro_schedule_available", False)):
            fail(f"full_macro_coverage_incomplete:{year}:{y}")
        reported = y.get("counts", {})
        for fam, count in actual_counts[str(year)].items():
            if int(reported.get(fam, -1)) != int(count):
                fail(
                    f"full_macro_count_mismatch:{year}:{fam}:"
                    f"coverage={reported.get(fam)}:actual={count}"
                )

    report["macro_counts_by_year"] = actual_counts
    report["checks"]["macro_no_outcome_fields"] = "PASS"
    report["checks"]["macro_timezone_alignment"] = "PASS"
    report["checks"]["macro_coverage_counts"] = "PASS"


def check_boundaries(
    m1: pd.DataFrame,
    structural: pd.DataFrame,
    decision: pd.DataFrame,
    report: dict,
):
    ts = m1["timestamp_ms"].to_numpy(np.int64)
    years = pd.to_datetime(ts, unit="ms", utc=True).year.to_numpy(int)
    boundaries = {}

    for year in range(2017, 2022):
        idx = np.flatnonzero(years == year)
        if len(idx) == 0:
            fail(f"full_boundary_no_rows:{year}")
        i = int(idx[0])

        contiguous_from_prior = bool(
            i > 0 and ts[i] - ts[i - 1] == ONE_MIN
        )
        if contiguous_from_prior:
            # With six years of prior TRAIN history, a one-minute-contiguous
            # year boundary must not cold-start rolling market readiness.
            if int(m1.iloc[i]["core_240m_contiguous_ready"]) != 1:
                fail(f"full_boundary_market_reset:{year}")
            for col in ("volume_mean_240m", "spread_mean_60m"):
                if not math.isfinite(float(m1.iloc[i][col])):
                    fail(f"full_boundary_rolling_reset:{year}:{col}")

        boundaries[str(year)] = {
            "first_timestamp_ms": int(ts[i]),
            "first_decision_time_ms": int(decision.iloc[i]["decision_time_ms"]),
            "contiguous_from_prior_observed_minute": contiguous_from_prior,
            "feature_ready_market": int(decision.iloc[i]["feature_ready_market"]),
            "dxy_available": int(decision.iloc[i]["dxy_available"]),
            "dxy_age_minutes": (
                None
                if pd.isna(decision.iloc[i]["dxy_age_minutes"])
                else float(decision.iloc[i]["dxy_age_minutes"])
            ),
            "previous_day_available": bool(
                pd.notna(structural.iloc[i]["previous_day_high"])
            ),
        }

    report["year_boundaries"] = boundaries
    report["checks"]["year_boundary_continuity"] = "PASS"


def main(argv: list[str]) -> None:
    if len(argv) != 6:
        raise SystemExit(
            "usage: validate_information_parity_stage2_full_train.py "
            "<layer-dir> <dxy.csv> <macro.csv> <macro-coverage.json> <report.json>"
        )

    layer = Path(argv[1])
    dxy_path = Path(argv[2])
    macro_path = Path(argv[3])
    macro_coverage_path = Path(argv[4])
    report_path = Path(argv[5])

    report = {
        "status": "PASS",
        "schema_version": "IPV1_STAGE2_FULL_INTEGRITY_V1",
        "scope": "2016-2021_TRAIN_CONTINUOUS",
        "sealed_xauusd_periods_accessed": [],
        "checks": {},
        "warnings": [],
    }

    m1 = read_gz(layer / f"xauusd_m1_market_state_{TAG}.csv.gz")
    check_m1_full(m1, report)

    tf = {}
    for name in ("m3", "m5", "m15", "m30", "h1", "h4", "d1", "w1"):
        df = read_gz(layer / f"xauusd_{name}_{TAG}.csv.gz")
        check_timeframe_full(df, f"xauusd_{name}", report)
        tf[name] = df

    check_hierarchy(tf, report)

    structural = read_gz(layer / f"xauusd_structural_state_{TAG}.csv.gz")
    check_structural(structural, m1, tf["d1"], report)

    dxy = load_dxy(dxy_path)
    dxy_years = year_set_ms(
        dxy["dxy_bar_start_ms"].to_numpy(np.int64)
    ) if not dxy.empty else set()
    if dxy_years - YEAR_SET:
        fail(f"full_dxy_year_outside_train:{sorted(dxy_years - YEAR_SET)}")

    decision = read_gz(layer / f"decision_index_{TAG}.csv.gz")
    check_decision_index_full(decision, m1, dxy, report)

    check_macro_full(macro_path, macro_coverage_path, report)
    macro_state = read_gz(layer / f"macro_event_state_{TAG}.csv.gz")
    check_macro_state(macro_state, m1, report)

    trade = read_gz(layer / f"trade_risk_state_template_{TAG}.csv.gz")
    check_trade_state(trade, m1, report)

    check_boundaries(m1, structural, decision, report)

    if year_set_ms(m1["timestamp_ms"].to_numpy(np.int64)) & SEALED_YEARS:
        fail("full_sealed_xauusd_detected")
    report["checks"]["sealed_periods"] = "PASS"

    years = pd.to_datetime(
        m1["timestamp_ms"], unit="ms", utc=True
    ).dt.year.to_numpy(int)
    report["per_year"] = {}
    for year in YEARS:
        mask = years == year
        di = decision.loc[mask]
        report["per_year"][str(year)] = {
            "decision_rows": int(mask.sum()),
            "feature_ready_market_share": float(
                pd.to_numeric(di["feature_ready_market"]).mean()
            ),
            "dxy_available_share": float(
                pd.to_numeric(di["dxy_available"]).mean()
            ),
            "macro_schedule_available_share": float(
                pd.to_numeric(di["macro_schedule_available"]).mean()
            ),
            "bid_flat_fill_rows": int(
                pd.to_numeric(m1.loc[mask, "bid_flat_fill"]).sum()
            ),
            "ask_flat_fill_rows": int(
                pd.to_numeric(m1.loc[mask, "ask_flat_fill"]).sum()
            ),
        }

    report["rows"] = {
        "m1": int(len(m1)),
        **{name: int(len(df)) for name, df in tf.items()},
        "structural": int(len(structural)),
        "decision_index": int(len(decision)),
        "macro_state": int(len(macro_state)),
        "trade_state": int(len(trade)),
        "dxy": int(len(dxy)),
    }

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv)
