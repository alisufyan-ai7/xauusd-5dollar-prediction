#!/usr/bin/env python3
"""Assemble and hard-check the compact Stage 2 full-TRAIN evidence summary."""

from __future__ import annotations

import importlib.metadata
import json
import os
import platform
import sys
from pathlib import Path

YEARS = tuple(range(2016, 2022))
FAMILIES = ("CPI", "NFP", "JOLTS", "FOMC", "CLAIMS", "GDP")


def fail(msg: str):
    raise SystemExit(f"STAGE2_FULL_SUMMARY_FAIL:{msg}")


def load(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        fail(f"missing:{p}")
    return json.loads(p.read_text(encoding="utf-8"))


def require_pass(name: str, obj: dict):
    if obj.get("status") != "PASS":
        fail(f"{name}_status:{obj.get('status')}")


def main(argv: list[str]) -> None:
    if len(argv) != 9:
        raise SystemExit(
            "usage: summarize_information_parity_stage2_full_train.py "
            "<input-verification.json> <dxy-report.json> <macro-coverage.json> "
            "<build-report.json> <integrity-report.json> <raw-manifest.json> "
            "<normalized-manifest.json> <out.json>"
        )

    inputs = load(argv[1])
    dxy = load(argv[2])
    macro = load(argv[3])
    build = load(argv[4])
    integrity = load(argv[5])
    raw_manifest = load(argv[6])
    normalized_manifest = load(argv[7])
    out_path = Path(argv[8])

    require_pass("inputs", inputs)
    require_pass("dxy", dxy)
    require_pass("build", build)
    require_pass("integrity", integrity)

    if macro.get("status") != "PASS":
        fail(f"macro_status:{macro.get('status')}")

    for obj_name, obj, key in (
        ("inputs", inputs, "sealed_xauusd_periods_accessed"),
        ("dxy", dxy, "sealed_xauusd_periods_accessed"),
        ("build", build, "sealed_periods_accessed"),
        ("integrity", integrity, "sealed_xauusd_periods_accessed"),
        ("macro", macro, "sealed_xauusd_periods_accessed"),
    ):
        if obj.get(key) != []:
            fail(f"{obj_name}_sealed_assertion:{obj.get(key)}")

    if not build.get("continuous_state_across_years"):
        fail("build_not_continuous")

    required_integrity = {
        "m1_decision_time",
        "m1_year_scope",
        "nonnegative_spread",
        "d1_h1_hierarchy",
        "w1_d1_hierarchy",
        "structural_alignment",
        "structural_causality",
        "structural_distances",
        "previous_day_asof",
        "decision_index_alignment",
        "dxy_backward_asof",
        "decision_year_continuity",
        "macro_no_outcome_fields",
        "macro_timezone_alignment",
        "macro_coverage_counts",
        "macro_state_alignment",
        "trade_state_neutral",
        "year_boundary_continuity",
        "sealed_periods",
    }
    checks = integrity.get("checks", {})
    missing_checks = sorted(
        x for x in required_integrity
        if checks.get(x) != "PASS"
    )
    if missing_checks:
        fail(f"integrity_checks_missing:{missing_checks}")

    if integrity.get("warnings"):
        fail(f"integrity_warnings:{integrity['warnings']}")

    per_year = {}
    for year in YEARS:
        ys = str(year)
        b = build.get("per_year", {}).get(ys)
        i = integrity.get("per_year", {}).get(ys)
        m = macro.get("years", {}).get(ys)
        dy = dxy.get("years", {}).get(ys)
        if None in (b, i, m, dy):
            fail(f"missing_year_summary:{year}")

        if not m.get("stage2_macro_schedule_available"):
            fail(f"macro_unavailable:{year}")
        for fam in FAMILIES:
            if int(m.get("counts", {}).get(fam, 0)) <= 0:
                fail(f"macro_family_empty:{year}:{fam}")

        if int(b.get("decision_rows", 0)) <= 0:
            fail(f"decision_rows_empty:{year}")
        if int(dy.get("common_timestamps", 0)) <= 0:
            fail(f"dxy_rows_empty:{year}")

        per_year[ys] = {
            "decision_rows": int(b["decision_rows"]),
            "feature_ready_market_share": b["feature_ready_market_share"],
            "dxy_available_share": b["dxy_available_share"],
            "previous_day_available_share": b["previous_day_available_share"],
            "bid_flat_fill_rows": int(b["bid_flat_fill_rows"]),
            "ask_flat_fill_rows": int(b["ask_flat_fill_rows"]),
            "canonical_timeframe_rows": b[
                "canonical_timeframe_rows_by_bar_start_year"
            ],
            "dxy_common_timestamps": int(dy["common_timestamps"]),
            "dxy_common_share_of_union": dy["common_share_of_union"],
            "macro_family_counts": m["counts"],
        }

    boundary = integrity.get("year_boundaries", {})
    if set(boundary) != {str(y) for y in range(2017, 2022)}:
        fail(f"boundary_years:{sorted(boundary)}")

    expected_raw_min = 6 * 8  # XAU BID+ASK plus 6 FX BID files per year.
    if int(raw_manifest.get("file_count", 0)) < expected_raw_min:
        fail(
            f"raw_manifest_file_count:"
            f"{raw_manifest.get('file_count')}<{expected_raw_min}"
        )
    if int(normalized_manifest.get("file_count", 0)) < 15:
        fail(
            "normalized_manifest_file_count:"
            f"{normalized_manifest.get('file_count')}"
        )

    runtime = {
        "python": platform.python_version(),
        "numpy": importlib.metadata.version("numpy"),
        "pandas": importlib.metadata.version("pandas"),
        "requests": importlib.metadata.version("requests"),
        "beautifulsoup4": importlib.metadata.version("beautifulsoup4"),
        "node": os.environ.get("STAGE2_NODE_VERSION"),
        "npm": os.environ.get("STAGE2_NPM_VERSION"),
        "dukascopy_node": "1.50.0",
    }

    summary = {
        "status": "PASS",
        "schema_version": "IPV1_STAGE2_FULL_SUMMARY_V1",
        "scope": "2016-2021_TRAIN_CONTINUOUS",
        "code_commit_sha": os.environ.get("GITHUB_SHA"),
        "runtime": runtime,
        "sealed_xauusd_periods_accessed": [],
        "continuous_state_across_years": True,
        "rows": build["rows"],
        "per_year": per_year,
        "year_boundaries": boundary,
        "integrity_checks": checks,
        "raw_manifest_file_count": raw_manifest["file_count"],
        "raw_manifest_total_bytes": raw_manifest["total_bytes"],
        "normalized_manifest_file_count": normalized_manifest["file_count"],
        "normalized_manifest_total_bytes": normalized_manifest["total_bytes"],
        "dxy_overall": {
            "common_timestamps_sum_by_year": dxy[
                "common_timestamps_sum_by_year"
            ],
            "common_share_of_union_sum_by_year": dxy[
                "common_share_of_union_sum_by_year"
            ],
            "complete_rolling_rows": dxy["complete_rolling_rows"],
        },
        "macro_status": macro["status"],
        "input_verification": inputs,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv)
