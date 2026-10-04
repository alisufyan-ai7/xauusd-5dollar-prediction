#!/usr/bin/env python3
"""Build the continuous 2016-2021 Information Parity V1 TRAIN layer.

This is the full-TRAIN counterpart to the bounded/annual Stage 2 builder.
All causal state is computed on one continuous 2016-2021 history. Calendar
years are summarized after state construction; they are not cold-started.

No 2022-2025 XAUUSD data, future labels, P&L or model fitting is used.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from build_information_parity_stage2_year import (
    TF_RULES,
    add_m1_transforms,
    add_previous_day,
    add_structural_state,
    build_d1,
    build_macro_state,
    build_w1,
    dxy_alignment,
    json_number,
    load_dxy,
    load_m1,
    load_macro_events,
    resample_exact,
    session_state,
    write_csv_gz,
)

START_YEAR = 2016
END_YEAR = 2021
YEARS = tuple(range(START_YEAR, END_YEAR + 1))
TAG = "2016_2021"


def fail(msg: str):
    raise SystemExit(f"STAGE2_FULL_BUILD_FAILED:{msg}")


def sync_path(sync_dir: Path, year: int) -> Path:
    return sync_dir / (
        f"xauusd-{year}-01-01-{year + 1}-01-01-m1-synchronized.csv"
    )


def load_continuous_xauusd(sync_dir: Path) -> tuple[pd.DataFrame, dict]:
    frames = []
    source = {}
    previous_last = None

    for year in YEARS:
        path = sync_path(sync_dir, year)
        if not path.exists():
            fail(f"missing_annual_xauusd:{year}:{path}")
        df = load_m1(path)
        if df.empty:
            fail(f"empty_annual_xauusd:{year}")

        bar_year = pd.to_datetime(
            df["timestamp_ms"], unit="ms", utc=True
        ).dt.year.to_numpy()
        if set(map(int, np.unique(bar_year))) != {year}:
            fail(f"annual_xauusd_year_scope:{year}:{sorted(set(map(int, bar_year)))}")

        first_ts = int(df.iloc[0]["timestamp_ms"])
        last_ts = int(df.iloc[-1]["timestamp_ms"])
        if previous_last is not None and first_ts <= previous_last:
            fail(f"annual_xauusd_overlap:{year}:{first_ts}:{previous_last}")
        previous_last = last_ts

        source[str(year)] = {
            "path": str(path),
            "rows": int(len(df)),
            "first_timestamp_ms": first_ts,
            "last_timestamp_ms": last_ts,
        }
        frames.append(df)

    out = pd.concat(frames, ignore_index=True)
    ts = out["timestamp_ms"].to_numpy(np.int64)
    if len(ts) > 1 and np.any(np.diff(ts) <= 0):
        fail("continuous_xauusd_not_strictly_increasing")

    observed_years = set(
        map(
            int,
            pd.to_datetime(out["timestamp_ms"], unit="ms", utc=True)
            .dt.year.unique(),
        )
    )
    if observed_years != set(YEARS):
        fail(f"continuous_xauusd_years:{sorted(observed_years)}")

    return out, source


def load_macro_coverage(path: Path) -> dict:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if obj.get("sealed_xauusd_periods_accessed") != []:
        fail("macro_coverage_sealed_assertion")
    years = obj.get("years", {})
    missing = []
    for year in YEARS:
        y = years.get(str(year))
        if y is None or not bool(y.get("stage2_macro_schedule_available", False)):
            missing.append({
                "year": year,
                "record": y,
            })
    if missing:
        fail(f"macro_schedule_incomplete:{missing}")
    return obj


def year_counts_from_bar_start(df: pd.DataFrame) -> dict[str, int]:
    if df.empty:
        return {str(y): 0 for y in YEARS}
    years = pd.to_datetime(
        df["bar_start_ms"], unit="ms", utc=True
    ).dt.year
    return {
        str(y): int((years == y).sum())
        for y in YEARS
    }


def write_outputs(
    m1: pd.DataFrame,
    tf: dict[str, pd.DataFrame],
    structural: pd.DataFrame,
    macro_state: pd.DataFrame,
    decision_index: pd.DataFrame,
    trade: pd.DataFrame,
    out_dir: Path,
) -> dict[str, str]:
    outputs = {}
    out_dir.mkdir(parents=True, exist_ok=True)

    tables = {
        "xauusd_m1_market_state": m1,
        **{f"xauusd_{name}": table for name, table in tf.items()},
        "xauusd_structural_state": structural,
        "macro_event_state": macro_state,
        "decision_index": decision_index,
        "trade_risk_state_template": trade,
    }

    for name, table in tables.items():
        path = out_dir / f"{name}_{TAG}.csv.gz"
        write_csv_gz(table, path)
        outputs[name] = str(path)

    return outputs


def main(argv: list[str]) -> None:
    if len(argv) != 7:
        raise SystemExit(
            "usage: build_information_parity_stage2_full_train.py "
            "<annual-sync-dir> <continuous-dxy.csv> <macro.csv> "
            "<macro-coverage.json> <out-dir> <report.json>"
        )

    sync_dir = Path(argv[1])
    dxy_path = Path(argv[2])
    macro_path = Path(argv[3])
    macro_coverage_path = Path(argv[4])
    out_dir = Path(argv[5])
    report_path = Path(argv[6])

    raw_m1, source_sync = load_continuous_xauusd(sync_dir)
    m1 = add_m1_transforms(raw_m1)
    del raw_m1

    dtimes = m1["decision_time_ms"].to_numpy(np.int64)
    prices = m1["bid_close"].to_numpy(float)
    bar_years = pd.to_datetime(
        m1["timestamp_ms"], unit="ms", utc=True
    ).dt.year.to_numpy(int)

    tf = {}
    for name, (rule, expected) in TF_RULES.items():
        tf[name] = resample_exact(m1, rule, expected)
    tf["d1"] = build_d1(tf["h1"])
    tf["w1"] = build_w1(tf["d1"])

    structural = add_structural_state(m1, tf)
    ss = session_state(m1)
    structural = structural.merge(
        ss,
        on="decision_time_ms",
        how="left",
        validate="one_to_one",
    )
    add_previous_day(
        structural,
        dtimes,
        tf["d1"],
        prices,
    )

    dxy = load_dxy(dxy_path)
    if not dxy.empty:
        dxy_years = set(
            map(
                int,
                pd.to_datetime(
                    dxy["dxy_bar_start_ms"], unit="ms", utc=True
                ).dt.year.unique(),
            )
        )
        if dxy_years - set(YEARS):
            fail(f"dxy_year_outside_train:{sorted(dxy_years - set(YEARS))}")
    dxy_available, dxy_age = dxy_alignment(dtimes, dxy)

    coverage = load_macro_coverage(macro_coverage_path)
    macro = load_macro_events(macro_path)
    if not macro.empty:
        macro_years = set(
            map(
                int,
                pd.to_datetime(
                    macro["scheduled_time_ms"], unit="ms", utc=True
                ).dt.year.unique(),
            )
        )
        if macro_years - set(YEARS):
            fail(f"macro_year_outside_train:{sorted(macro_years - set(YEARS))}")

    macro_state = build_macro_state(
        dtimes,
        macro,
        schedule_available=True,
    )

    dec_dt = pd.to_datetime(dtimes, unit="ms", utc=True)
    decision_index = pd.DataFrame({
        "timestamp_ms": m1["timestamp_ms"].to_numpy(np.int64),
        "decision_time_ms": dtimes,
        "year": bar_years,
        "utc_date": dec_dt.strftime("%Y-%m-%d"),
        "ny_date": dec_dt.tz_convert("America/New_York").strftime("%Y-%m-%d"),
        "feature_ready_market": m1["core_240m_contiguous_ready"].to_numpy(np.int8),
        "dxy_available": dxy_available,
        "dxy_age_minutes": dxy_age,
        "macro_schedule_available": np.ones(len(m1), dtype=np.int8),
        "market_state_version": "IPV1_STAGE2_V1",
    })

    trade = pd.DataFrame({
        "decision_time_ms": dtimes,
        "position_state": "FLAT",
        "open_position_count": 0,
        "entry_price": np.nan,
        "stop_price": np.nan,
        "target_price": np.nan,
        "minutes_in_position": 0,
        "session_realized_pnl": 0.0,
        "session_trade_count": 0,
        "consecutive_loss_count": 0,
        "risk_fraction_deployed": 0.0,
        "same_thesis_attempt_count": 0,
    })

    outputs = write_outputs(
        m1,
        tf,
        structural,
        macro_state,
        decision_index,
        trade,
        out_dir,
    )

    dxy_bar_years = (
        pd.to_datetime(dxy["dxy_bar_start_ms"], unit="ms", utc=True).dt.year
        if not dxy.empty
        else pd.Series(dtype=int)
    )
    macro_event_years = (
        pd.to_datetime(macro["scheduled_time_ms"], unit="ms", utc=True).dt.year
        if not macro.empty
        else pd.Series(dtype=int)
    )

    per_year = {}
    for year in YEARS:
        mask = bar_years == year
        idx = np.flatnonzero(mask)
        if len(idx) == 0:
            fail(f"no_decision_rows:{year}")
        di = decision_index.iloc[idx]
        st = structural.iloc[idx]

        first = int(idx[0])
        per_year[str(year)] = {
            "decision_rows": int(len(idx)),
            "first_timestamp_ms": int(m1.iloc[first]["timestamp_ms"]),
            "last_timestamp_ms": int(m1.iloc[idx[-1]]["timestamp_ms"]),
            "feature_ready_market_share": float(di["feature_ready_market"].mean()),
            "dxy_available_share": float(di["dxy_available"].mean()),
            "macro_schedule_available_share": float(
                di["macro_schedule_available"].mean()
            ),
            "bid_flat_fill_rows": int(m1.iloc[idx]["bid_flat_fill"].sum()),
            "ask_flat_fill_rows": int(m1.iloc[idx]["ask_flat_fill"].sum()),
            "previous_day_available_share": float(
                pd.to_numeric(
                    st["previous_day_high"], errors="coerce"
                ).notna().mean()
            ),
            "dxy_rows": int((dxy_bar_years == year).sum()),
            "macro_event_rows": int((macro_event_years == year).sum()),
            "canonical_timeframe_rows_by_bar_start_year": {
                name: year_counts_from_bar_start(table)[str(year)]
                for name, table in tf.items()
            },
            "macro_family_counts": coverage["years"][str(year)].get("counts", {}),
        }

    boundaries = {}
    for year in range(START_YEAR + 1, END_YEAR + 1):
        idx = np.flatnonzero(bar_years == year)
        first = int(idx[0])
        row = decision_index.iloc[first]
        st = structural.iloc[first]
        boundaries[str(year)] = {
            "first_timestamp_ms": int(row["timestamp_ms"]),
            "first_decision_time_ms": int(row["decision_time_ms"]),
            "feature_ready_market": int(row["feature_ready_market"]),
            "dxy_available": int(row["dxy_available"]),
            "dxy_age_minutes": (
                None
                if pd.isna(row["dxy_age_minutes"])
                else float(row["dxy_age_minutes"])
            ),
            "previous_day_available": bool(
                pd.notna(st["previous_day_high"])
            ),
            "previous_day_high": (
                None
                if pd.isna(st["previous_day_high"])
                else float(st["previous_day_high"])
            ),
        }

    report = {
        "status": "PASS",
        "schema_version": "IPV1_STAGE2_FULL_BUILD_V1",
        "scope": "2016-2021_TRAIN_CONTINUOUS",
        "sealed_periods_accessed": [],
        "continuous_state_across_years": True,
        "source_synchronized_xauusd": source_sync,
        "rows": {
            "xauusd_m1_market_state": int(len(m1)),
            **{
                f"xauusd_{name}": int(len(table))
                for name, table in tf.items()
            },
            "xauusd_structural_state": int(len(structural)),
            "macro_event_state": int(len(macro_state)),
            "decision_index": int(len(decision_index)),
            "trade_risk_state_template": int(len(trade)),
            "synthetic_dxy_m1": int(len(dxy)),
            "macro_event_schedule": int(len(macro)),
        },
        "canonical_timeframe_rows_by_year": {
            name: year_counts_from_bar_start(table)
            for name, table in tf.items()
        },
        "per_year": per_year,
        "year_boundaries": boundaries,
        "first_timestamp_ms": int(m1.iloc[0]["timestamp_ms"]),
        "last_timestamp_ms": int(m1.iloc[-1]["timestamp_ms"]),
        "first_decision_time_ms": int(m1.iloc[0]["decision_time_ms"]),
        "last_decision_time_ms": int(m1.iloc[-1]["decision_time_ms"]),
        "outputs": outputs,
    }

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(
            report,
            indent=2,
            sort_keys=True,
            default=json_number,
        ) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True, default=json_number))


if __name__ == "__main__":
    main(sys.argv)
