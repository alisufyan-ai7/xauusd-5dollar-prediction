#!/usr/bin/env python3
"""Leakage/integrity validator for Information Parity V1 Stage 2.

This validator checks causal availability, schema exclusions, alignment,
sealed-period boundaries, and neutral trade-state semantics. It does not
calculate outcomes, labels, or P&L.
"""

from __future__ import annotations

import csv
import gzip
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ONE_MIN = 60_000
ALLOWED_YEARS = set(range(2016, 2022))
SEALED_YEARS = {2022, 2023, 2024, 2025}
FORBIDDEN_TOKENS = (
    "future_return",
    "mfe",
    "mae",
    "target_before_stop",
    "profit_loss",
    "trade_label",
    "macro_actual",
    "macro_forecast",
    "macro_consensus",
    "macro_surprise",
    "actual",
    "forecast",
    "consensus",
    "surprise",
)
MACRO_REQUIRED = [
    "event_id", "event_family", "scheduled_time_utc", "scheduled_time_local",
    "source_timezone", "source_agency", "source_document_id_or_url",
    "release_stage", "historical_exception_flag", "normalization_version",
]


def fail(msg: str):
    raise SystemExit(f"IPV1_STAGE2_INTEGRITY_FAIL:{msg}")


def read_gz(path: Path) -> pd.DataFrame:
    if not path.exists():
        fail(f"missing:{path}")
    return pd.read_csv(path, compression="gzip")


def assert_no_forbidden_columns(name: str, cols):
    lower = [str(c).lower() for c in cols]
    for c in lower:
        for token in FORBIDDEN_TOKENS:
            if token in c:
                fail(f"forbidden_field:{name}:{c}")


def strict_increasing(values: np.ndarray, name: str):
    if len(values) > 1 and np.any(np.diff(values) <= 0):
        fail(f"not_strict_increasing:{name}")


def year_from_ms(values: np.ndarray) -> set[int]:
    if len(values) == 0:
        return set()
    return set(pd.to_datetime(values, unit="ms", utc=True).year.astype(int))


def check_m1(df: pd.DataFrame, year: int, report: dict):
    assert_no_forbidden_columns("xauusd_m1_market_state", df.columns)
    required = {
        "timestamp_ms", "decision_time_ms",
        "bid_open", "bid_high", "bid_low", "bid_close", "bid_volume",
        "ask_open", "ask_high", "ask_low", "ask_close", "ask_volume",
        "spread_open", "spread_close", "bid_flat_fill", "ask_flat_fill",
    }
    if not required.issubset(df.columns):
        fail(f"m1_missing:{sorted(required-set(df.columns))}")
    ts = df["timestamp_ms"].to_numpy(np.int64)
    dec = df["decision_time_ms"].to_numpy(np.int64)
    strict_increasing(ts, "m1_timestamp")
    if not np.all(dec == ts + ONE_MIN):
        fail("decision_time_relation")
    if year_from_ms(ts) != {year}:
        fail(f"m1_year_scope:{year_from_ms(ts)}")
    if (df["spread_open"].astype(float) < 0).any() or (df["spread_close"].astype(float) < 0).any():
        fail("negative_spread")
    report["checks"]["m1_decision_time"] = "PASS"
    report["checks"]["m1_year_scope"] = "PASS"
    report["checks"]["nonnegative_spread"] = "PASS"


def check_timeframe(df: pd.DataFrame, name: str, year: int, report: dict):
    assert_no_forbidden_columns(name, df.columns)
    required = {"bar_start_ms", "available_time_ms", "open", "high", "low", "close", "volume", "source_count"}
    if not required.issubset(df.columns):
        fail(f"{name}_missing:{sorted(required-set(df.columns))}")
    if df.empty:
        report["warnings"].append(f"{name}:empty")
        return
    start = df["bar_start_ms"].to_numpy(np.int64)
    av = df["available_time_ms"].to_numpy(np.int64)
    strict_increasing(av, f"{name}_available")
    if np.any(av <= start):
        fail(f"{name}_availability_not_after_start")
    bad = year_from_ms(start) - {year}
    # A W1/D1 bar may begin in late December only when annual files are built
    # from that year's own M1; with no pre-year warmup, that should not occur.
    if bad:
        fail(f"{name}_bar_start_year:{bad}")
    report["checks"][f"{name}_availability"] = "PASS"


def check_structural(df: pd.DataFrame, m1: pd.DataFrame, report: dict):
    assert_no_forbidden_columns("xauusd_structural_state", df.columns)
    if len(df) != len(m1):
        fail("structural_row_count")
    dec = df["decision_time_ms"].to_numpy(np.int64)
    if not np.array_equal(dec, m1["decision_time_ms"].to_numpy(np.int64)):
        fail("structural_decision_alignment")

    for c in df.columns:
        lc = c.lower()
        if lc.endswith("_confirmation_time_ms") or lc.endswith("_creation_time_ms"):
            vals = pd.to_numeric(df[c], errors="coerce").to_numpy(float)
            mask = np.isfinite(vals)
            if np.any(vals[mask] > dec[mask]):
                fail(f"future_structural_time:{c}")
        if lc.endswith("_age_minutes"):
            vals = pd.to_numeric(df[c], errors="coerce").to_numpy(float)
            mask = np.isfinite(vals)
            if np.any(vals[mask] < 0):
                fail(f"negative_structural_age:{c}")

    report["checks"]["structural_alignment"] = "PASS"
    report["checks"]["structural_causality"] = "PASS"


def load_dxy(path: Path) -> pd.DataFrame:
    d = pd.read_csv(path)
    assert_no_forbidden_columns("synthetic_dxy_m1", d.columns)
    required = {"dxy_bar_start_ms", "dxy_available_time_ms", "dxy_level"}
    if not required.issubset(d.columns):
        fail(f"dxy_missing:{sorted(required-set(d.columns))}")
    if not d.empty:
        av = d["dxy_available_time_ms"].to_numpy(np.int64)
        start = d["dxy_bar_start_ms"].to_numpy(np.int64)
        strict_increasing(av, "dxy_available")
        if not np.all(av == start + ONE_MIN):
            fail("dxy_available_relation")
    return d


def check_decision_index(df: pd.DataFrame, m1: pd.DataFrame, dxy: pd.DataFrame, year: int, report: dict):
    assert_no_forbidden_columns("decision_index", df.columns)
    if len(df) != len(m1):
        fail("decision_index_row_count")
    if not np.array_equal(df["timestamp_ms"].to_numpy(np.int64), m1["timestamp_ms"].to_numpy(np.int64)):
        fail("decision_index_timestamp_alignment")
    if not np.array_equal(df["decision_time_ms"].to_numpy(np.int64), m1["decision_time_ms"].to_numpy(np.int64)):
        fail("decision_index_decision_alignment")
    if set(df["year"].astype(int)) != {year}:
        fail("decision_index_year")

    age = pd.to_numeric(df["dxy_age_minutes"], errors="coerce").to_numpy(float)
    available = df["dxy_available"].astype(int).to_numpy()
    if np.any((available != 0) & (available != 1)):
        fail("dxy_available_not_binary")
    mask = available == 1
    if np.any(~np.isfinite(age[mask])):
        fail("dxy_available_missing_age")
    if np.any(age[mask] < 0) or np.any(age[mask] > 5):
        fail("dxy_staleness")

    # Recompute the frozen backward as-of relationship.
    if not dxy.empty:
        dav = dxy["dxy_available_time_ms"].to_numpy(np.int64)
        dec = df["decision_time_ms"].to_numpy(np.int64)
        pos = np.searchsorted(dav, dec, side="right") - 1
        valid = pos >= 0
        calc_age = np.full(len(dec), np.nan)
        calc_age[valid] = (dec[valid] - dav[pos[valid]]) / ONE_MIN
        calc_ok = valid & (calc_age >= 0) & (calc_age <= 5)
        if not np.array_equal(calc_ok.astype(np.int8), available.astype(np.int8)):
            fail("dxy_asof_availability_mismatch")
        if np.any(np.abs(calc_age[calc_ok] - age[calc_ok]) > 1e-9):
            fail("dxy_asof_age_mismatch")

    report["checks"]["decision_index_alignment"] = "PASS"
    report["checks"]["dxy_backward_asof"] = "PASS"


def check_macro(macro_path: Path, coverage_path: Path, year: int, report: dict):
    with macro_path.open(encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        fields = r.fieldnames or []
        rows = list(r)
    if fields != MACRO_REQUIRED:
        fail(f"macro_schema:{fields}")
    assert_no_forbidden_columns("macro_event_schedule", fields)

    for row in rows:
        utc_dt = datetime.fromisoformat(row["scheduled_time_utc"])
        local_dt = datetime.fromisoformat(row["scheduled_time_local"])
        if utc_dt.tzinfo is None or local_dt.tzinfo is None:
            fail("macro_naive_time")
        if row["source_timezone"] != "America/New_York":
            fail(f"macro_timezone:{row['source_timezone']}")
        if local_dt.astimezone(timezone.utc) != utc_dt.astimezone(timezone.utc):
            fail("macro_local_utc_mismatch")
        if utc_dt.year in SEALED_YEARS:
            fail("macro_sealed_year_in_stage2")

    cov = json.loads(coverage_path.read_text(encoding="utf-8"))
    if cov.get("sealed_xauusd_periods_accessed") != []:
        fail("coverage_sealed_assertion")
    y = cov.get("years", {}).get(str(year))
    if y is None:
        fail(f"macro_coverage_year_missing:{year}")

    report["macro_year"] = {
        "stage2_macro_schedule_available": bool(y.get("stage2_macro_schedule_available", False)),
        "counts": y.get("counts", {}),
        "errors": y.get("errors", []),
    }
    report["checks"]["macro_no_outcome_fields"] = "PASS"
    report["checks"]["macro_timezone_alignment"] = "PASS"


def check_macro_state(df: pd.DataFrame, m1: pd.DataFrame, report: dict):
    assert_no_forbidden_columns("macro_event_state", df.columns)
    if len(df) != len(m1):
        fail("macro_state_row_count")
    if not np.array_equal(df["decision_time_ms"].to_numpy(np.int64), m1["decision_time_ms"].to_numpy(np.int64)):
        fail("macro_state_alignment")

    for c in ("minutes_since_previous_event", "minutes_to_next_event"):
        vals = pd.to_numeric(df[c], errors="coerce").to_numpy(float)
        mask = np.isfinite(vals)
        if np.any(vals[mask] < 0):
            fail(f"macro_negative_distance:{c}")
    report["checks"]["macro_state_alignment"] = "PASS"


def check_trade_state(df: pd.DataFrame, m1: pd.DataFrame, report: dict):
    assert_no_forbidden_columns("trade_risk_state_template", df.columns)
    if len(df) != len(m1):
        fail("trade_state_row_count")
    if not (df["position_state"].astype(str) == "FLAT").all():
        fail("trade_state_not_flat")
    zero_cols = [
        "open_position_count", "minutes_in_position", "session_realized_pnl",
        "session_trade_count", "consecutive_loss_count",
        "risk_fraction_deployed", "same_thesis_attempt_count",
    ]
    for c in zero_cols:
        if not np.allclose(pd.to_numeric(df[c], errors="coerce").fillna(0).to_numpy(float), 0):
            fail(f"trade_state_nonzero:{c}")
    for c in ("entry_price", "stop_price", "target_price"):
        if pd.to_numeric(df[c], errors="coerce").notna().any():
            fail(f"trade_state_price_populated:{c}")
    report["checks"]["trade_state_neutral"] = "PASS"


def main(argv: list[str]) -> None:
    if len(argv) != 7:
        raise SystemExit(
            "usage: validate_information_parity_stage2.py "
            "<year> <layer-dir> <dxy.csv> <macro.csv> <macro-coverage.json> <report.json>"
        )
    year = int(argv[1])
    if year not in ALLOWED_YEARS:
        fail(f"sealed_or_invalid_year:{year}")

    layer = Path(argv[2])
    dxy_path = Path(argv[3])
    macro_path = Path(argv[4])
    macro_coverage_path = Path(argv[5])
    report_path = Path(argv[6])

    report = {
        "status": "PASS",
        "schema_version": "IPV1_STAGE2_INTEGRITY_V1",
        "year": year,
        "sealed_xauusd_periods_accessed": [],
        "checks": {},
        "warnings": [],
    }

    m1 = read_gz(layer / f"xauusd_m1_market_state_{year}.csv.gz")
    check_m1(m1, year, report)

    for name in ("m3", "m5", "m15", "m30", "h1", "h4", "d1", "w1"):
        df = read_gz(layer / f"xauusd_{name}_{year}.csv.gz")
        check_timeframe(df, f"xauusd_{name}", year, report)

    structural = read_gz(layer / f"xauusd_structural_state_{year}.csv.gz")
    check_structural(structural, m1, report)

    dxy = load_dxy(dxy_path)
    decision = read_gz(layer / f"decision_index_{year}.csv.gz")
    check_decision_index(decision, m1, dxy, year, report)

    check_macro(macro_path, macro_coverage_path, year, report)
    macro_state = read_gz(layer / f"macro_event_state_{year}.csv.gz")
    check_macro_state(macro_state, m1, report)

    trade = read_gz(layer / f"trade_risk_state_template_{year}.csv.gz")
    check_trade_state(trade, m1, report)

    all_years = year_from_ms(m1["timestamp_ms"].to_numpy(np.int64))
    if all_years & SEALED_YEARS:
        fail(f"sealed_year_detected:{sorted(all_years & SEALED_YEARS)}")
    report["checks"]["sealed_periods"] = "PASS"

    report["rows"] = {
        "m1": int(len(m1)),
        "structural": int(len(structural)),
        "decision_index": int(len(decision)),
        "macro_state": int(len(macro_state)),
        "trade_state": int(len(trade)),
        "dxy": int(len(dxy)),
    }
    report["coverage"] = {
        "feature_ready_market_share": float(pd.to_numeric(decision["feature_ready_market"]).mean()),
        "dxy_available_share": float(pd.to_numeric(decision["dxy_available"]).mean()),
        "macro_schedule_available_share": float(pd.to_numeric(decision["macro_schedule_available"]).mean()),
    }

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv)
